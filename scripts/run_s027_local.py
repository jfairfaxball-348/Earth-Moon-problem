"""Owner-invoked S027 local serial campaign (CAM-0032/CAM-0033); no model calls.

Full local 271+K9 smoke gates all science. One externally supervised process tree
at <=11GiB; per-graph four-hour absolute cap; whole campaign <=8h after smoke.
Stage order (registered in sessions/S027/PLAN.md): controls, P29 deletion descent
(<=1800s), learned-obstruction source (<=7200s), profile-domain proofs, admitted
candidates, then serial C5 two-branch size-4 continuation with the remainder.
Caps and errors are UNKNOWN, never negative decisions or exhaustion.
"""
import ctypes
from datetime import datetime, timezone
import gzip
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
OUT = ROOT / 'artifacts/tmp/S027-local'
OUT.mkdir(parents=True, exist_ok=True)
os.environ['EMP_S026_OUTPUT'] = str(OUT)
MEM = 11 * 1024 * 1024
os.environ['EMP_S026_MEMORY_KIB'] = str(MEM)
os.environ['EMP_CADICAL'] = str(ROOT / 'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM'] = str(ROOT / 'artifacts/tmp/S004/drat-trim-mingw.exe')
EXTRA = OUT / 'EXTRA_OBSTRUCTIONS.json'
os.environ['EMP_S027_EXTRA_OBSTRUCTIONS'] = str(EXTRA)
from s026_supervision import atomic_json, journal, run_step   # noqa: E402
import s026_campaign as camp                                  # noqa: E402

WHOLE = 8 * 3600
GRAPH_ABS = 4 * 3600
DESCENT_TOTAL, DESCENT_EACH = 1800, 60
C5_TAGS = ['33434', '23435', '24344', '24425', '33344']
C5_SEARCH, NATIVE = 3600, 1800
NATIVE_SHA = {'EMP_CADICAL': '120d2c53bf14a8b70cce78be980824651922d53523228d9f0f026998caea7e48',
              'EMP_DRAT_TRIM': '970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e'}


def sha(p):
    return camp.sha(p)


def say(msg):
    print(datetime.now(timezone.utc).isoformat(), msg, flush=True)


def py(tool, *a):
    return camp.py(tool, *a)


def child(args, cap, log):
    return camp.child(args, cap, log)


def certified(rec):
    return rec.get('proof', {}).get('certified') or rec.get('verdict') == 'NONBIPLANAR_CERTIFIED'


def controls(state):
    """Positive controls for size-4 two-branch clauses and the learned checker."""
    from s027_two_branch import TwoBranchK
    from s025_check import check_split
    from blowup_graph import blowup
    from biplanar_cnf import read_edges
    import itertools as it
    import networkx as nx
    d = OUT / 'controls'
    d.mkdir(exist_ok=True)
    cases = []
    p = ROOT / 'validation/S003/splits/J1.split.json'
    cases.append(('J1', json.loads(p.read_text()), read_edges(str(p.with_name('J1.edges')))))
    c5s = json.load(gzip.open(ROOT / 'validation/S025/C5_CLASSIFY.json.gz', 'rt'))['results']
    r = next(r for r in c5s if r['w'] == [3, 3, 3, 3, 4] and r.get('split_checked'))
    es, _ = blowup('Dhc', r['w'])
    cases.append(('C5-33334', {'n': 16, 'E1': r['E1'], 'E2': r['E2']}, es))
    results = []
    for name, split, es in cases:
        check_split(split['n'], es, split['E1'], split['E2'])
        c = TwoBranchK(es, 4)
        layers = []
        for k in ('E1', 'E2'):
            g = nx.Graph()
            g.add_nodes_from(range(split['n']))
            g.add_edges_from(split[k])
            layers.append(g)
        true = {c.idx[tuple(e)] for e in split['E1']}
        for R, cs in c.cvar.items():
            for j, v in enumerate(cs):
                if nx.is_connected(layers[j].subgraph(R)):
                    true.add(v)
        for (q, R, j), v in c.avar.items():
            if any(layers[j - 1].has_edge(q, y) for y in R):
                true.add(v)
        for (R, S, j), v in c.pvar.items():
            if any(layers[j - 1].has_edge(a, b) for a, b in it.product(R, S)):
                true.add(v)
        assert all(any((x > 0) == (abs(x) in true) for x in cl) for cl in c.minor_clauses)
        edge = d / (name + '.edges')
        edge.write_text(''.join(f'{a} {b}\n' for a, b in es), newline='\n')
        prefix = d / name
        c.dump(prefix)
        for mode, args in [('check', py('s026_check_two_branch.py', edge, prefix)),
                           ('regen', py('s027_two_branch.py', 'regen', edge, prefix, d / (name + '.regen.cnf')))]:
            res = child(args, 600, d / (name + '.' + mode + '.log'))
            assert res['returncode'] == 0, res
        results.append({'name': name, 'known_split': 'PASS', 'all_minor_clauses_satisfied': True,
                        'two_models_size4': len(c.two_models), 'checker_and_byte_regeneration': 'PASS'})
    assert sum(r['two_models_size4'] for r in results) > 0
    smoke = json.loads((ROOT / 'artifacts/tmp/cloud_smoke/RESULT.json').read_text())
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    # Learned-clause checker negative control and in-loop containment control.
    res = child(py('s027_selftest.py', d / 'selftest'), 1200, d / 'selftest.log')
    assert res['returncode'] == 0, res
    rec = {'two_branch_size4_positive_controls': results, 'K9_retained_and_fresh': 'PASS_IN_SAME_RUN_SMOKE',
           'selftest': json.loads((d / 'selftest' / 'SELFTEST.json').read_text())}
    atomic_json(d / 'SUMMARY.json', rec)
    state['controls'] = 'PASS'


def descent(state, deadline):
    """P29 one-vertex deletions; twins make 14 bag classes cover all 28 deletions."""
    from blowup_graph import blowup
    c = json.loads((ROOT / 'validation/S026/filter-recovery/candidate/CANDIDATE.json').read_text())
    base = OUT / 'descent'
    base.mkdir(exist_ok=True)
    start = time.monotonic()
    rows, extra = [], []
    for i in range(len(c['w'])):
        if time.monotonic() - start >= DESCENT_TOTAL - DESCENT_EACH or time.monotonic() >= deadline:
            rows.append({'bag': i, 'status': 'NOT_RUN_DESCENT_CAP'})
            continue
        u = list(c['w'])
        u[i] -= 1
        d = base / f'del-bag{i:02d}'
        d.mkdir(exist_ok=True)
        es, _ = blowup(c['g6'], u)
        edge = d / 'graph.edges'
        edge.write_text(''.join(f'{a} {b}\n' for a, b in es), newline='\n')
        say(f'descent bag{i}: 27 vertices, {len(es)} edges')
        rec = camp.exact(edge, d, DESCENT_EACH)
        row = {'bag': i, 'u': u, 'edges': len(es), 'verdict': rec['verdict'],
               'search': rec.get('result', {}), 'elapsed': round(time.monotonic() - start, 1)}
        rows.append(row)
        if rec['verdict'] == 'NONBIPLANAR_CERTIFIED':
            extra.append({'name': f'P29-del-bag{i:02d}', 'g6': c['g6'], 'u': u,
                          'edges': str(edge.relative_to(ROOT)).replace('\\', '/'),
                          'certificate': str((d / 'SUMMARY.json').relative_to(ROOT)).replace('\\', '/')})
            atomic_json(EXTRA, extra)
        atomic_json(base / 'DESCENT.json', {'rows': rows, 'twin_classes': 14,
                                            'note': 'deleting either vertex of a two-vertex twin bag gives isomorphic graphs'})
        say(f'descent bag{i}: {rec["verdict"]}')
    if not EXTRA.exists():
        atomic_json(EXTRA, extra)
    state['descent'] = {'certified_negatives': len(extra), 'rows': len(rows),
                        'seconds': round(time.monotonic() - start, 1)}


def domains(state, src):
    """Native DRAT for closed profile domains after clause justification."""
    s = json.loads((src / 'SUMMARY.json').read_text())
    out = []
    for st in s['profiles']:
        d = src / f"profile{st['profile']:02d}"
        chk = child(py('s027_check_learned.py', d / 'LEARNED.json.gz',
                       *( [d / 'domain.cnf'] if st.get('stop') == 'GENERATOR_UNSAT' else [])),
                    1800, d / 'learned_check.log')
        row = {'profile': st['profile'], 'w': st['weights'], 'stop': st.get('stop'),
               'learned_check_returncode': chk['returncode'],
               'blocking_dependencies': st.get('domain_blocking_dependencies', [])}
        if st.get('stop') == 'GENERATOR_UNSAT' and chk['returncode'] == 0:
            res = child(py('s025_certify.py', d / 'domain.cnf', d, 600, 1200), 1900, d / 'domain_proof.log')
            cp = d / 'domain.certificate.json'
            cert = json.loads(cp.read_text()) if cp.exists() else {'verdict': 'UNKNOWN'}
            row['domain_proof'] = cert.get('verdict')
            row['domain_cnf_sha256'] = sha(d / 'domain.cnf')
            if cert.get('verdict') == 'UNSAT_DRAT_VERIFIED':
                with open(d / 'domain.cnf', 'rb') as f, gzip.open(d / 'domain.cnf.gz', 'wb', 9) as g:
                    shutil.copyfileobj(f, g)
                (d / 'domain.cnf').unlink()
        out.append(row)
        atomic_json(src / 'DOMAINS.json', out)
    state['domains'] = {'checked_profiles': sum(r['learned_check_returncode'] == 0 for r in out),
                        'closed_drat': sum(r.get('domain_proof') == 'UNSAT_DRAT_VERIFIED' for r in out)}


def candidates(state, src, deadline):
    from s025_check import check_split
    s = json.loads((src / 'SUMMARY.json').read_text())
    todo = [r['name'] for r in s['admitted']]
    out = []
    for name in todo:
        d = src / 'candidates' / name
        if time.monotonic() >= deadline:
            out.append({'name': name, 'verdict': 'NOT_RUN_WHOLE_CAP'})
            continue
        t0 = time.monotonic()
        say(f'candidate {name}: audit')
        a = child(py('s027_audit.py', 'cnf', d), 3600, d / 'audit_cnf.log')
        b = child(py('s027_audit.py', 'backtrack', d), 300, d / 'audit_backtrack.log')
        audit = json.loads((d / 'AUDIT_CNF.json').read_text()) if (d / 'AUDIT_CNF.json').exists() else []
        row = {'name': name, 'audit_returncode': a['returncode'], 'backtrack_returncode': b['returncode'],
               'audit': {r['obstruction']: r['verdict'] for r in audit}}
        hit = [r for r in audit if r['verdict'] == 'CONTAINS_EXPLICIT_CHECKED']
        if hit:
            row['verdict'] = 'NONBIPLANAR_BY_CERTIFIED_SUBGRAPH'
            row['obstruction'] = hit[0]['obstruction']
            out.append(row)
            atomic_json(src / 'CANDIDATES.json', out)
            continue
        edge = d / 'graph.edges'
        for seed in (1, 2):
            child(py('s025_cover_anneal.py', edge, seed, 60, d / f'anneal{seed}.json'), 75, d / f'anneal{seed}.log')
            ap = d / f'anneal{seed}.json'
            if ap.exists():
                ar = json.loads(ap.read_text())
                row[f'anneal{seed}_uncovered'] = ar['best_uncovered']
                if ar['best_uncovered'] == 0:
                    es = [tuple(map(int, l.split())) for l in edge.read_text().split('\n') if l.strip()]
                    check_split(28, es, ar['E1'], ar['E2'])
                    row['verdict'] = 'BIPLANAR_SPLIT_CHECKED'
                    break
        if row.get('verdict') != 'BIPLANAR_SPLIT_CHECKED':
            rec = camp.exact(edge, d, 600)
            row['exact'] = {'verdict': rec['verdict'], 'result': rec.get('result')}
            row['verdict'] = rec['verdict']
        row['seconds'] = round(time.monotonic() - t0, 1)
        assert row['seconds'] < GRAPH_ABS + 600
        out.append(row)
        atomic_json(src / 'CANDIDATES.json', out)
        say(f'candidate {name}: {row["verdict"]}')
    state['candidates'] = {r['name']: r['verdict'] for r in out}


def c5_certify(edge, prefix, d):
    rec = {}
    for name, args in [('justification', py('s026_check_two_branch.py', edge, prefix)),
                       ('regeneration', py('s027_two_branch.py', 'regen', edge, prefix, d / 'rebuilt.cnf'))]:
        rec[name] = child(args, 1800, d / (name + '.log'))
        if rec[name]['returncode'] != 0:
            return rec
    rec['cnf_byte_match'] = sha(str(prefix) + '.cnf') == sha(d / 'rebuilt.cnf')
    if not rec['cnf_byte_match']:
        return rec
    rec['native'] = child(py('s025_certify.py', str(prefix) + '.cnf', d, NATIVE, NATIVE), 2 * NATIVE + 300,
                          d / 'native.log')
    cp = d / (Path(prefix).name + '.certificate.json')
    if cp.exists():
        rec['certificate'] = json.loads(cp.read_text())
    rec['certified'] = rec.get('certificate', {}).get('verdict') == 'UNSAT_DRAT_VERIFIED'
    if rec['certified']:
        with open(str(prefix) + '.lemmas.json', 'rb') as f, gzip.open(d / 'lemmas.json.gz', 'wb', 9) as g:
            shutil.copyfileobj(f, g)
        for p in [Path(str(prefix) + '.lemmas.json'), Path(str(prefix) + '.cnf'), d / 'rebuilt.cnf']:
            p.unlink()
    return rec


def c5_arm(state, deadline):
    from s025_check import check_split
    from biplanar_cnf import read_edges
    out = []
    for tag in C5_TAGS:
        d = OUT / ('C5-' + tag)
        d.mkdir(exist_ok=True)
        left = deadline - time.monotonic()
        if left < 900:
            out.append({'tag': tag, 'verdict': 'NOT_RUN_WHOLE_CAP'})
            atomic_json(OUT / 'C5_ARM.json', out)
            continue
        seconds = int(min(C5_SEARCH, left - 600))
        src = ROOT / f'validation/S026/local/C5-{tag}'
        edge = d / 'graph.edges'
        shutil.copyfile(src / 'graph.edges', edge)
        ck = src / 'minor.checkpoint.json.gz'
        prefix = d / 'minor'
        say(f'C5-{tag}: size-4 two-branch search {seconds}s seeded from S026 checkpoint')
        s = child(py('s027_two_branch.py', edge, prefix, seconds, 4, ck), seconds + 900, d / 'search.log')
        rp = Path(str(prefix) + '.result.json')
        res = json.loads(rp.read_text()) if rp.exists() else {'verdict': 'UNKNOWN', 'returncode': s['returncode']}
        row = {'tag': tag, 'search': res, 'search_process': s,
               'seed_checkpoint_sha256': sha(ck)}
        if res['verdict'] == 'UNSAT':
            row['proof'] = c5_certify(edge, prefix, d)
            row['verdict'] = 'NONBIPLANAR_CERTIFIED' if row['proof'].get('certified') else 'UNKNOWN'
        elif res['verdict'] == 'SAT':
            sp = json.loads(Path(str(prefix) + '.split.json').read_text())
            check_split(sp['n'], read_edges(str(edge)), sp['E1'], sp['E2'])
            row['verdict'] = 'BIPLANAR_SPLIT_CHECKED_REFUTES_SUM17_THRESHOLD'
        else:
            row['verdict'] = 'UNKNOWN'
        atomic_json(d / 'SUMMARY.json', row)
        out.append(row)
        atomic_json(OUT / 'C5_ARM.json', out)
        say(f'C5-{tag}: {row["verdict"]}')
    state['c5'] = {r['tag']: r['verdict'] for r in out}


def main():
    if os.name != 'nt':
        raise RuntimeError('owner local launcher targets the Windows workstation')
    import msvcrt
    lock = (OUT / 'RUN.lock').open('a+b')
    lock.write(b'0'); lock.flush(); lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    power = ctypes.windll.kernel32
    power.SetThreadExecutionState(0x80000001)
    state = {'session': 'S027', 'authority': "owner 'run next session' 2026-10-18 (D047), local Claude Code",
             'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'memory_kib': MEM, 'whole_campaign_seconds': WHOLE, 'graph_absolute_seconds': GRAPH_ABS}
    try:
        for k, v in NATIVE_SHA.items():
            assert sha(os.environ[k]) == v, (k, 'native digest mismatch')
        env = {'kind': 'LOCAL_WINDOWS_OWNER_INVOKED_S027', 'python': sys.version,
               'packages': {k: metadata.version(k) for k in ('python-sat', 'networkx', 'numpy')},
               'native_sha256': {k: sha(os.environ[k]) for k in NATIVE_SHA}, 'native_paths':
               {k: os.environ[k] for k in NATIVE_SHA}, 'memory_cap_kib': MEM, 'cpu_threads': os.cpu_count(),
               'source_commit': state['source_commit'], 'source_sha256': {
                   str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
                   for pat in ('s025_*.py', 's026_*.py', 's027_*.py', 'biplanar_cegar.py', 'biplanar_cnf.py',
                               'blowup_graph.py') for p in sorted((ROOT / 'tools').glob(pat))} |
               {'scripts/run_s027_local.py': sha(__file__)}}
        atomic_json(OUT / 'ENVIRONMENT.json', env)
        atomic_json(OUT / 'STATE.json', state)
        say('S027: FULL 271+K9 smoke starting; one worker, 11GiB cap')
        smoke = run_step([sys.executable, str(ROOT / 'scripts/cloud_smoke.py')], 2400, OUT / 'smoke.log',
                         OUT / 'RUN_JOURNAL.jsonl', memory_kib=MEM)
        state['smoke_process'] = smoke
        if smoke['returncode'] != 0:
            raise RuntimeError('full smoke failed; science BLOCKED')
        res = ROOT / 'artifacts/tmp/cloud_smoke/RESULT.json'
        assert json.loads(res.read_text())['verdict'] == 'PASS'
        shutil.copyfile(res, OUT / 'SMOKE.json')
        t0 = time.monotonic()
        deadline = t0 + WHOLE
        state['science_start_utc'] = datetime.now(timezone.utc).isoformat()
        say('smoke PASS; controls'); controls(state); atomic_json(OUT / 'STATE.json', state)
        say('P29 deletion descent'); descent(state, deadline); atomic_json(OUT / 'STATE.json', state)
        src = OUT / 'source'
        say('learned-obstruction source')
        state['source_process'] = child(py('s027_source.py', src, 7200), 7200 + 900, OUT / 'source.log')
        atomic_json(OUT / 'STATE.json', state)
        say('domain proofs and learned-clause audit'); domains(state, src); atomic_json(OUT / 'STATE.json', state)
        say('admitted candidates'); candidates(state, src, deadline); atomic_json(OUT / 'STATE.json', state)
        say('C5 arm'); c5_arm(state, deadline)
        state['status'] = 'CAMPAIGN_FINISHED_NOT_A_SESSION_CLOSEOUT'
        state['science_seconds'] = round(time.monotonic() - t0, 1)
        atomic_json(OUT / 'STATE.json', state)
        atomic_json(OUT / 'HANDBACK.json', state)
        journal(OUT / 'RUN_JOURNAL.jsonl', 'campaign_end', **{k: str(v)[:500] for k, v in state.items()})
        say('S027 campaign finished; handback saved')
    except BaseException as e:
        state['status'] = 'INTERRUPTED_OR_BLOCKED'
        state['error'] = repr(e)
        atomic_json(OUT / 'STATE.json', state)
        journal(OUT / 'RUN_JOURNAL.jsonl', 'campaign_error', error=repr(e))
        raise
    finally:
        power.SetThreadExecutionState(0x80000000)
        lock.close()


if __name__ == '__main__':
    main()
