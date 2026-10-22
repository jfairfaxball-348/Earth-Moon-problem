"""Real-native scheduler, exact partition, crash, proof and deadline controls."""
import itertools
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s035_windows import read_json, atomic_json, stop_group
from s035_regions import (claim, create, ledger, live_identity, process_identity,
                          recover, release, report, sha, validate_partition)

OUT = ROOT/'artifacts/tmp/S035/resident-acceptance'
NATIVE = ROOT/'artifacts/tmp/S035/native-resident/bipsat_s032.exe'
CADICAL = ROOT/'artifacts/tmp/S004/cadical.exe'
CHECKER = ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'
PROCESSES = []


def fixture(root, n=5, seconds=20, workers=1):
    root.mkdir(parents=True)
    pairs = list(itertools.combinations(range(n), 2)); m = len(pairs)
    graph = list(range(2*m+1, 3*m+1))
    cs = []
    for i, g in enumerate(graph):
        a, b = 2*i+1, 2*i+2
        cs.extend([[g, -a], [g, -b], [-g, a, b], [-a, -b]])
    units = {graph[0]: True}
    if n == 9:
        units = {g: True for g in graph}
    cs.extend([[g if b else -g] for g, b in units.items()])
    if n == 5:
        cs.append([-graph[2], -graph[3]])
    base = root/'base.cnf'
    base.write_text(f'p cnf {3*m} {len(cs)}\n'+''.join(' '.join(map(str, c))+' 0\n' for c in cs))
    empty = root/'seed.lem'; empty.write_text('')
    cfg = dict(root=str(ROOT), scientific=False, deadline=time.time()+seconds,
               n=n, pairs=pairs, variables=3*m, graph_variables=graph, graph_units=units,
               bits=3 if n == 5 else 0, edge_low=0, edge_high=m,
               base=str(base), base_clauses=len(cs), base_sha256=sha(base), mapping_sha256='CONTROL',
               seed=dict(path=str(empty), count=0, sha256=sha(empty)),
               native=str(NATIVE), native_sha256=sha(NATIVE), cadical=str(CADICAL),
               checker=str(CHECKER), checker_sha256=sha(CHECKER), source_sha256={},
               workers=workers, min_visit_seconds=2 if n == 5 else 20,
               max_visit_seconds=2 if n == 5 else 20, rss_cap_kib=1048576,
               available_floor_kib=0, disk_reserve_bytes=64*1024**2, temperature_cap_c=100,resident_turn_seconds=2,resident_cache_private_bytes=5*1024**3,resident_available_floor_kib=1024*1024)
    area = root/'campaign'; create(area, cfg)
    return area, cfg


def start(area):
    log = (area/'test-guard.log').open('a')
    p = subprocess.Popen([sys.executable, str(ROOT/'scripts/s035_resident_campaign.py'), 'guard',
                          '--directory', str(area)], stdout=log, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
    log.close()
    PROCESSES.append((p, area))
    return p


def wait_for(fn, seconds=30):
    end = time.monotonic()+seconds
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(.05)
    raise AssertionError('Control condition did not arrive')


def active(area):
    data = read_json(area/'REGIONS.json')
    return next((c['claim']['worker'] for c in data['cells'] if c['claim'] and c['claim']['worker']), None)


def stopped(p, area):
    (area/'STOP').touch()
    p.wait(timeout=30)
    assert not any(c['claim'] for c in read_json(area/'REGIONS.json')['cells'])


def main():
    start_time = time.monotonic()
    root = OUT/f'scheduler-controls-{time.time_ns()}'
    area, cfg = fixture(root/'ledger')
    data = read_json(area/'REGIONS.json')
    assert validate_partition(cfg, data['cells'])
    counts = [0]*8
    for values in itertools.product((False, True), repeat=9):
        assignment = {cfg['graph_variables'][0]: True, **dict(zip(cfg['graph_variables'][1:], values))}
        hits = [c['id'] for c in data['cells'] if all(assignment[abs(x)] == (x > 0) for x in c['assumptions'])]
        assert len(hits) == 1
        counts[hits[0]] += 1
    assert counts == [int(c['weight']) for c in data['cells']]
    with ThreadPoolExecutor(max_workers=4) as pool:
        cells = list(pool.map(lambda i: claim(area, os.getpid(), owner=str(i)), range(8)))
    assert len({c['id'] for c in cells}) == 8 and claim(area, os.getpid()) is None
    try:
        release(area, cells[0]['id'], 'wrong-token')
        raise AssertionError('Wrong claim accepted')
    except AssertionError as exc:
        assert 'Claim mismatch' in str(exc)
    recover(area)
    assert all(c['status'] == 'UNKNOWN' and c['claim'] is None for c in read_json(area/'REGIONS.json')['cells'])

    # Two independent real native workers are safe on this tiny synthetic domain only.
    area, cfg = fixture(root/'parallel', seconds=15, workers=2)
    p = start(area)
    wait_for(lambda: (area/'GUARDIAN.json').exists())
    duplicate = start(area); duplicate.wait(timeout=15)
    assert duplicate.returncode != 0 and p.poll() is None
    wait_for(lambda: report(area)['proof_closed_regions'] == 2, seconds=30)
    stopped(p, area)
    snapshot = {name: (area/name).read_bytes() for name in ('REGIONS.json', 'CONFIG.json', 'CONTROLLER.json')}
    subprocess.run([sys.executable, str(ROOT/'scripts/s035_resident_campaign.py'), 'status', '--directory', str(area)],
                   check=True, stdout=subprocess.DEVNULL)
    assert snapshot == {name: (area/name).read_bytes() for name in snapshot}

    # Crashed controller leaves no false closure; guardian kills orphan and resumes.
    area, cfg = fixture(root/'crash', n=9, seconds=30)
    p = start(area)
    old_worker = wait_for(lambda: active(area))
    wait_for(lambda: any(p.stat().st_size for p in area.glob('attempts/cell-*/*/new-cuts.lem')))
    guard = read_json(area/'GUARDIAN.json')
    old_controller = guard['controller']['pid']
    # Kill only the actual controller, leaving its native child orphaned.
    import psutil
    actual_controller=wait_for(lambda:read_json(area/'CONTROLLER.json').get('pid'))
    psutil.Process(actual_controller).kill()
    wait_for(lambda: read_json(area/'GUARDIAN.json').get('restarts', 0) >= 1, seconds=30)
    def resumed():
        worker = active(area)
        return worker if worker and worker['pid'] != old_worker['pid'] else None
    wait_for(resumed, seconds=30)
    assert not live_identity(old_worker['pid'], old_worker['start_ticks'])
    assert report(area)['proof_closed_regions'] == 0
    assert report(area)['accepted_new_clauses'] > 0
    stopped(p, area)
    assert list(area.glob('attempts/cell-*/*/RECOVERY.json'))

    # Native finite timeout independently terminates a bounded visit.
    area, cfg = fixture(root/'native-timeout', n=9, seconds=20)
    from s035_engine import materialise, recipe
    inst = root/'timeout.inst'; materialise(inst, recipe(cfg, [], []), native=True)
    t = time.monotonic()
    native = subprocess.run([str(NATIVE),str(inst),'--timeout','2'],capture_output=True,text=True,timeout=30)
    assert native.returncode == 0 and 's UNKNOWN' in native.stdout and time.monotonic()-t < 8

    # Guardian deadline stops all groups, checkpoints and records UNKNOWN.
    area, cfg = fixture(root/'deadline', n=9, seconds=30)
    p = start(area)
    wait_for(lambda: active(area), seconds=20)
    p.wait(timeout=30)
    result = json.loads((area/'STOPPED.json').read_text())
    assert result['reason'] == 'DEADLINE' and report(area)['proof_closed_regions'] == 0
    assert not any(c['claim'] for c in read_json(area/'REGIONS.json')['cells'])

    # A non-unit-propagation UNSAT formula needs its actual proof: empty proof fails.
    cnf = root/'proof-control.cnf'; proof = root/'proof-control.drat'; damaged = root/'damaged.drat'
    clauses = list(itertools.product((-1, 1), (-2, 2), (-3, 3)))
    cnf.write_text('p cnf 3 8\n'+''.join(' '.join(map(str, c))+' 0\n' for c in clauses))
    r = subprocess.run([str(CADICAL), '--no-binary', str(cnf), str(proof)], capture_output=True, text=True)
    assert r.returncode == 20
    r = subprocess.run([str(CHECKER), str(cnf), str(proof)], capture_output=True, text=True)
    assert r.returncode == 0 and 's VERIFIED' in r.stdout
    damaged.write_text('')
    r = subprocess.run([str(CHECKER), str(cnf), str(damaged)], capture_output=True, text=True)
    assert r.returncode != 0 or 's VERIFIED' not in r.stdout
    names = ['tools/s035_resident_engine.py','scripts/s035_resident_campaign.py', 'tools/s035_regions.py', 'tools/s035_engine.py', 'scripts/s035_resident_campaign.py',
             'tools/s035_windows.py', 'tools/s035_storage.py']
    value = dict(status='PASS', native_sha256=sha(NATIVE), exact_small_graph_assignments=512,
                 concurrent_unique_claims=8, two_small_native_workers='PASS_SYNTHETIC_ONLY_NOT_REAL_SCIENCE_BENCHMARK',
                 proof_closed_small_regions=2, duplicate_guard_rejected=True,
                 wrong_token_rejected=True, controller_kill_restart='PASS',
                 read_only_status=True, native_finite_timeout='PASS_UNKNOWN',
                 guardian_deadline='PASS_UNKNOWN', damaged_proof_rejected=True,
                 controls_directory=str(root), seconds=time.monotonic()-start_time,
                 source_sha256={name: sha(ROOT/name) for name in names})
    atomic_json(OUT/'SCHEDULER_CONTROLS.json', value)
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    try:
        main()
    finally:
        for process, area in PROCESSES:
            if process.poll() is None:
                stopped(process, area)
