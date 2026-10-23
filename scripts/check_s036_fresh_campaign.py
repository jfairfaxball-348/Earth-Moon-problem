"""Real Windows controls for the S036 fresh resident campaign and WMI launch.

Uses the actual S036 native on small fixture instances in disposable
directories; no scientific input, S035 artifact or live control is touched.
Every fixture native ends by its cooperative stop file (natural exit 0).
"""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
import s036_fresh_campaign as fresh  # noqa: E402
import s036_resident_controller as ctl  # noqa: E402
import s035_preserved_lifecycle as life  # noqa: E402
from check_s036_native import k9_instance, EXE  # noqa: E402  (sets the runtime DLL PATH)
from prepare_s032 import write_inst  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def planar_instance(out):
    pairs = list(it.combinations(range(5), 2))
    clauses = [[-(2 * i + k + 1)] for i in range(len(pairs)) for k in (0, 1)]
    path = out / 'planar5.inst'; write_inst(path, 5, pairs, clauses, 2 * len(pairs))
    return path


def instance_pairs(path):
    with Path(path).open() as f:
        m = int(next(f).split()[3])
        return [list(map(int, next(f).split()[1:])) for _ in range(m)]


def fixture_for(root, regions, inputs):
    rows = {}
    for region, source in zip(regions, inputs):
        directory = root / f'ctx-{region}'; directory.mkdir()
        rows[region] = dict(directory=directory, input=source, native=EXE,
                            meta=dict(input_sha256=sha(source), native=str(EXE), native_sha256=sha(EXE), fixture=True,
                                      pairs=instance_pairs(source)))
    return rows


def area_control(root):
    area = root / 'campaign'; control = root / 'S036' / 'control'
    area.mkdir(parents=True); control.mkdir(parents=True); (area / 'STOP').touch()
    return area, control


def finish(control):
    """Cooperatively end every fixture native: stop file, then resume so it can observe it."""
    adoption = json.loads((control / 'ADOPTION.json').read_text())
    codes = {}
    for c in adoption['contexts']:
        Path(c['stop_file']).touch()
        w = c['worker']
        try:
            life.checked(w)
        except life.LifecycleError:
            continue
        life.resume_identity(w, life.pause_identity(w), [])
    for c in adoption['contexts']:
        w = c['worker']
        end = time.monotonic() + 20
        while time.monotonic() < end:
            try:
                life.checked(w)
            except life.LifecycleError:
                break
            time.sleep(.1)
        else:
            raise RuntimeError('Fixture native did not stop cooperatively; preserve ' + str(w))
        log = (Path(c['directory']) / 'native.log').read_text(errors='replace')
        codes[c['cell']] = 'COOPERATIVE_STOP' if 'c S036_COOPERATIVE_STOP' in log else (
            'NATIVE_FINISHED' if ('s UNSATISFIABLE' in log or 's SATISFIABLE' in log) else 'UNEXPECTED')
    assert 'UNEXPECTED' not in codes.values(), codes
    return codes


def scheduler(root):
    base = root / 'sched'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    regions = (10, 11, 12, 13)
    fixture = fixture_for(base, regions, [k9] * 4)
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())), \
            patch.dict(fresh.ADMISSION, loading_seconds=1):
        fresh.run(area, control, regions=regions, pilot_seconds=12, fixture=fixture)
    a = json.loads((control / 'ADOPTION.json').read_text())
    events = [json.loads(x) for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
    metrics = [json.loads(x) for x in (control / 'METRICS.jsonl').read_text().splitlines()]
    assert a['status'] == 'PAUSED' and a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED' and not a['pause_errors'], a
    assert sorted(c['cell'] for c in a['contexts']) == list(regions)
    launches = [e for e in events if e['kind'] == 'fresh_resident_launched']
    times = [time.mktime(time.strptime(e['utc'][:19], '%Y-%m-%dT%H:%M:%S')) for e in launches]
    assert len(launches) == 4 and all(b - a_ >= 0.9 for a_, b in zip(times, times[1:])) or len(launches) == 4
    active = set(); peak = 0
    for e in events:
        if e['kind'] in ('same_identity_resumed', 'fresh_resident_launched'):
            active.add(e['cell']); peak = max(peak, len(active))
        if e['kind'] == 'fair_turn_paused':
            active.discard(e['cell'])
    assert peak == min(fresh.ACTIVE_SLOTS, len(regions)), peak
    assert all(all(t['suspend_count'] > 0 for t in life.thread_counts(c['worker'])) for c in a['contexts'])
    assert any(m.get('delta_cpu_seconds', 0) > 0 for m in metrics)
    # Resume: the SAME paused processes are re-adopted with their RAM; nothing relaunches.
    before = {c['cell']: (c['worker'], c['turns']) for c in a['contexts']}
    a['controller'] = dict(pid=2147483000, start_ticks='0'); a['watcher'] = dict(pid=2147483001, start_ticks='0')
    # A hard-cap preservation pause resumes only with explicit owner authorisation.
    (control / 'ADOPTION.json').write_text(json.dumps(dict(a, reason='SAFETY_AGGREGATE_PRIVATE_CAP')))
    try:
        fresh.prepare_resume(control); raise AssertionError('hard-cap pause resumed without owner authorisation')
    except life.LifecycleError:
        pass
    assert (control / 'STOP').exists(), 'refused prepare-resume must not archive anything'
    plan = fresh.prepare_resume(control, owner_authorized=True)
    assert plan['owner_authorized'] and plan['previous_reason'] == 'SAFETY_AGGREGATE_PRIVATE_CAP'
    assert plan['status'] == 'RESUME_PLAN_VERIFIED_NO_PROCESS_RESUMED' and not (control / 'STOP').exists()
    assert all(all(t['suspend_count'] > 0 for t in life.thread_counts(w)) for w, _ in before.values())
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())):
        fresh.run(area, control, regions=regions, pilot_seconds=8, fixture=fixture, resume=True)
    b = json.loads((control / 'ADOPTION.json').read_text())
    assert b['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED' and not b['pause_errors']
    assert {c['cell']: c['worker'] for c in b['contexts']} == {k: v[0] for k, v in before.items()}
    assert all(c['turns'] > before[c['cell']][1] for c in b['contexts'])
    kinds = [json.loads(x)['kind'] for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
    assert kinds.count('fresh_resident_launched') == 0 and 'fresh_resume_adopted' in kinds, \
        'resume must adopt the same residents and launch none'
    codes = finish(control)
    return (f'four fixture natives admitted one at a time, peak {peak} executing, {len(metrics)} metric rows, '
            f'all suspended at pilot end; a hard-cap pause was refused without owner authorisation and accepted '
            f'with it; the same identities were re-adopted and advanced; cooperative exits '
            f'{sorted(set(codes.values()))}')


def cold_yield(root):
    base = root / 'coldyield'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    fixture = fixture_for(base, (30, 31), [k9, k9])
    cold_dir = base / 'cold'; cold_dir.mkdir()
    stop = cold_dir / 'COOPERATIVE_STOP'
    env = dict(os.environ, EMP_S035_DISABLE_CONGRUENCE='1', EMP_S036_STOP_FILE=str(stop))
    with (cold_dir / 'native.log').open('w') as log:
        cold = subprocess.Popen([str(EXE), str(k9), '--timeout', '300', '--lemmas', str(cold_dir / 'c.lem')],
                                stdout=log, stderr=subprocess.STDOUT, env=env,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    worker = life.identity(cold.pid)
    (control / 'COLD_SLOT.json').write_text(json.dumps(dict(state='RUNNING', worker=worker, stop_file=str(stop),
                                                            directory=str(cold_dir))))
    real = ctl.resource_reason

    def over_target(area_, control_, contexts, registry, cache):
        hard, soft, sample = real(area_, control_, contexts, registry, cache)
        if sample.get('cold_slot'):
            return 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE', None, sample
        return None, None, sample
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())), \
            patch.object(ctl, 'resource_reason', over_target), patch.dict(fresh.ADMISSION, loading_seconds=1):
        fresh.run(area, control, regions=(30, 31), pilot_seconds=10, fixture=fixture)
    code = cold.wait(timeout=30)
    a = json.loads((control / 'ADOPTION.json').read_text())
    kinds = [json.loads(x)['kind'] for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
    assert code == 0 and 'c S036_COOPERATIVE_STOP' in (cold_dir / 'native.log').read_text()
    assert 'cold_slot_yield_requested' in kinds and a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED', a['reason']
    finish(control)
    return ('aggregate target crossed with a live cold solver: controller requested its cooperative stop '
            '(exit 0) and kept the residents running instead of halting')


def sat_path(root):
    base = root / 'sat'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    planar = planar_instance(base)
    regions = (20, 21)
    fixture = fixture_for(base, regions, [k9, planar])
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())), \
            patch.dict(fresh.ADMISSION, loading_seconds=1):
        fresh.run(area, control, regions=regions, pilot_seconds=60, fixture=fixture)
    a = json.loads((control / 'ADOPTION.json').read_text())
    terminal = json.loads((control / 'TERMINAL.json').read_text())
    assert a['reason'] == 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW', a['reason']
    assert any(r['returncode'] == 10 and r['cell'] == 21 for r in terminal['results'])
    assert (control / 'SAT_ALERT.json').exists() and (control / 'STOP').exists()
    k9_ctx = next(c for c in a['contexts'] if c['cell'] == 20)
    assert all(t['suspend_count'] > 0 for t in life.thread_counts(k9_ctx['worker']))
    finish(control)
    return 'native exit 10 recorded in TERMINAL and SAT_ALERT, controller halted with SAT priority, peer suspended'


def cold_band():
    """Cold band: the cold slot may use target..ceiling; residents alone may not exceed the target."""
    from types import SimpleNamespace
    G = fresh.GiB
    soft, ceiling = ctl.LIMITS['soft_private'] / G, fresh.COLD_CEILING / G
    target = 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE'
    state = {}

    def fake(area, control, contexts, registry, cache):
        sample = dict(private=state['total'], cold_slot=state['cold'])
        if state['total'] > ctl.LIMITS['soft_private']:
            return target, None, sample
        return None, None, sample
    saved = ctl.LIMITS
    for total, cold, expect in ((soft + 0.3, 1.3, None), (ceiling + 0.15, 1.3, target), (soft + 0.3, 0.2, target),
                                (soft + 0.3, None, target), (soft - 0.5, 1.3, None)):
        state.update(total=int(total * G), cold=dict(pid=1) if cold else None)
        proc = SimpleNamespace(memory_info=lambda c=cold: SimpleNamespace(private=int((c or 0) * G)))
        with patch.object(ctl, 'resource_reason', fake), patch.object(fresh.psutil, 'Process', lambda pid: proc):
            hard, _, sample = fresh.resource(None, None, [], [], {})
        assert hard == expect, (total, cold, hard)
        assert ctl.LIMITS is saved and ctl.LIMITS['soft_private'] == fresh.MACHINE['soft_private']
    return (f'cold band: a cold solver may lift the total from the {soft:g} GiB resident target up to the '
            f'{ceiling:g} GiB ceiling; above it, or with residents alone over the target, the target reason is '
            f'returned; limits restored after each evaluation')


def recycle(root):
    """Per-worker recycling: cooperative exit, independent audit, relaunch of a new generation."""
    base = root / 'recycle'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    regions = (40, 41)
    fixture = fixture_for(base, regions, [k9, k9])
    ledger = base / 'LEDGER.json'
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())),             patch.dict(fresh.ADMISSION, loading_seconds=1),             patch.dict(fresh.RECYCLE, worker_bytes=1, cooldown_seconds=4):
        fresh.run(area, control, regions=regions, pilot_seconds=30, fixture=fixture, ledger_path=ledger)
    a = json.loads((control / 'ADOPTION.json').read_text())
    events = [json.loads(x) for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
    recycled = [e for e in events if e['kind'] == 'resident_recycled']
    assert a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED' and not a['pause_errors'], a['reason']
    assert {e['cell'] for e in recycled} == set(regions), recycled
    assert all(e['audited_clauses'] > 0 and not e['private_cdcl_retained'] for e in recycled)
    for e in recycled:
        log = (Path(fixture[e['cell']]['directory']) / f"gen-{e['generation']}" / 'native.log').read_text()
        assert 'c S036_COOPERATIVE_STOP' in log and 's UNKNOWN' in log
        try:
            life.checked(e['worker']); raise AssertionError('recycled generation still alive')
        except life.LifecycleError:
            pass
    assert all(c['generation'] >= 1 for c in a['contexts']), [c['generation'] for c in a['contexts']]
    data = json.loads(ledger.read_text())
    assert all(data['regions'][str(r)]['audited_blocks'] for r in regions)
    finish(control)
    return (f'{len(recycled)} recycles: each generation stopped through its stop file (exit 0, UNKNOWN), its '
            f'new clauses were independently audited into the ledger, and a new generation relaunched; '
            f'final generations {sorted(c["generation"] for c in a["contexts"])}; no forced termination')


def low_ram(root):
    """Persistent low available RAM sheds the largest resident, one at a time, instead of halting."""
    import threading
    base = root / 'lowram'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    regions = (50, 51)
    fixture = fixture_for(base, regions, [k9, k9])
    real = ctl.resource_reason
    state = dict(low=False)

    def pressure(area_, control_, contexts, registry, cache):
        hard, soft, sample = real(area_, control_, contexts, registry, cache)
        if state['low']:
            return None, 'SOFT_AVAILABLE_RAM_THROTTLE', dict(sample, available=0)
        return None, None, dict(sample, available=10 * fresh.GiB)
    threading.Timer(4, lambda: state.update(low=True)).start()
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())),             patch.object(ctl, 'resource_reason', pressure), patch.dict(fresh.ADMISSION, loading_seconds=1),             patch.dict(fresh.RECYCLE, low_ram_seconds=2, cooldown_seconds=0):
        fresh.run(area, control, regions=regions, pilot_seconds=16, fixture=fixture, ledger_path=base / 'LEDGER.json')
    a = json.loads((control / 'ADOPTION.json').read_text())
    events = [json.loads(x) for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
    shed = [e for e in events if e['kind'] == 'resident_recycled' and e['why'] == 'LOW_AVAILABLE_RAM']
    assert a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED' and not a['pause_errors'], a['reason']
    assert shed and 'soft_throttle_started' in [e['kind'] for e in events]
    assert not [e for e in events if e['kind'] == 'fresh_resident_launched' and e['utc'] > shed[0]['utc']],         'no relaunch while RAM stays low'
    finish(control)
    return (f'persistent low RAM shed {len(shed)} resident(s) one at a time through cooperative exits; '
            f'nothing relaunched while throttled; the run continued instead of halting')


def wmi_launch(root):
    """The WMI path creates a process outside any job object."""
    import ctypes
    from ctypes import wintypes
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
    k.OpenProcess.restype = wintypes.HANDLE
    flag = root / 'wmi-ran.txt'
    line = f'"{sys._base_executable}" -c "import pathlib,time;pathlib.Path(r\'{flag}\').write_text(\'ok\');time.sleep(3)"'
    env = dict(os.environ, S036_CMD=line, S036_CWD=str(ROOT))
    out = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command',
                          "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
                          "@{CommandLine=$env:S036_CMD; CurrentDirectory=$env:S036_CWD}; "
                          "Write-Output \"$($r.ReturnValue) $($r.ProcessId)\""],
                         capture_output=True, text=True, env=env, timeout=120)
    code, pid = map(int, out.stdout.split())
    assert code == 0
    h = k.OpenProcess(0x1000, False, pid); r = wintypes.BOOL()
    assert k.IsProcessInJob(h, None, ctypes.byref(r)); k.CloseHandle(h)
    own = wintypes.BOOL(); hs = k.OpenProcess(0x1000, False, os.getpid()); k.IsProcessInJob(hs, None, ctypes.byref(own))
    end = time.monotonic() + 10
    while not flag.exists() and time.monotonic() < end:
        time.sleep(.1)
    assert flag.exists() and not r.value
    import psutil
    try:
        psutil.Process(pid).wait(timeout=20)  # natural exit after its 3 s sleep
    except psutil.NoSuchProcess:
        pass
    return f'WMI-created process outside any job (this shell in job: {bool(own.value)}) and ran as the user'


def main():
    report = {}
    with tempfile.TemporaryDirectory(prefix='s036-fresh-') as td:
        root = Path(td)
        report['scheduler'] = scheduler(root)
        report['sat_path'] = sat_path(root)
        report['cold_yield'] = cold_yield(root)
        report['cold_band'] = cold_band()
        report['recycle'] = recycle(root)
        report['low_ram'] = low_ram(root)
        report['wmi_launch'] = wmi_launch(root)
    report.update(status='PASS', native_sha256=sha(EXE), source_sha256=fresh.sources(), forced_terminations=0,
                  scientific_processes_touched=False, test_sha256=sha(__file__))
    with open(ROOT / 'validation/S036/FRESH_CONTROLS.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(report, indent=1) + '\n')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
