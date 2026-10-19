"""Owner-invoked S028 local obstruction-closure campaign (CAM-0034/CAM-0035).

Full local 271+K9 smoke gates all science. One externally supervised process tree
at <=11GiB; any graph <=4h absolute; whole campaign <=8h after smoke.
Stages (sessions/S028/PLAN.md): controls; deletion descent from certified S027
negatives (120s each, <=2400s per root, <=7200s total); refilter the 84 S027
filter-clean graphs; rerun the seed-270018 source with all certified
obstructions; profile-domain proofs; serial exact processing of clean graphs.
Caps and errors are UNKNOWN, never negative decisions or exhaustion.
"""
import ctypes
from datetime import datetime, timezone
import gzip
from importlib import metadata
import itertools as it
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
OUT = ROOT / 'artifacts/tmp/S028-local'
OUT.mkdir(parents=True, exist_ok=True)
os.environ['EMP_S026_OUTPUT'] = str(OUT)
MEM = 11 * 1024 * 1024
os.environ['EMP_S026_MEMORY_KIB'] = str(MEM)
os.environ['EMP_CADICAL'] = str(ROOT / 'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM'] = str(ROOT / 'artifacts/tmp/S004/drat-trim-mingw.exe')
EXTRA = OUT / 'EXTRA_OBSTRUCTIONS.json'
KNOWN = OUT / 'KNOWN_SURVIVORS.json'
os.environ['EMP_S027_EXTRA_OBSTRUCTIONS'] = str(EXTRA)
os.environ['EMP_S028_KNOWN'] = str(KNOWN)
from s026_supervision import atomic_json, journal, run_step   # noqa: E402
import s026_campaign as camp                                  # noqa: E402

WHOLE, GRAPH_ABS = 8 * 3600, 4 * 3600
DESCENT_EACH, DESCENT_ROOT, DESCENT_TOTAL = 120, 2400, 7200
EXACT, TWO_BRANCH, TWO_SIZE, NATIVE = 1800, 1800, 3, 1800
S27 = ROOT / 'validation/S027/local'
NATIVE_SHA = {'EMP_CADICAL': '120d2c53bf14a8b70cce78be980824651922d53523228d9f0f026998caea7e48',
              'EMP_DRAT_TRIM': '970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e'}


def say(msg):
    print(datetime.now(timezone.utc).isoformat(), msg, flush=True)


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


py, child, sha = camp.py, camp.child, camp.sha


def initial_extra():
    ex = []
    for t in ('23435', '24344', '24425'):
        d = S27 / ('C5-' + t)
        ex.append({'name': 'C5-' + t, 'g6': 'Dhc', 'u': list(map(int, t)), 'edges': rel(d / 'graph.edges'),
                   'certificate': rel(d / 'SUMMARY.json')})
    d = S27 / 'descent/del-bag12'
    c = json.loads((ROOT / 'validation/S026/filter-recovery/candidate/CANDIDATE.json').read_text())
    u = list(c['w']); u[12] -= 1
    ex.append({'name': 'P29-del-bag12', 'g6': c['g6'], 'u': u, 'edges': rel(d / 'graph.edges'),
               'certificate': rel(d / 'SUMMARY.json')})
    for n in ('P26-B11-0051', 'P27-B12-0040'):
        d = S27 / 'source/candidates' / n
        r = json.loads((d / 'CANDIDATE.json').read_text())
        ex.append({'name': n, 'g6': r['g6'], 'u': r['w'], 'edges': rel(d / 'graph.edges'),
                   'certificate': rel(d / 'SUMMARY.json')})
    return ex


def add_extra(state, rec):
    ex = json.loads(EXTRA.read_text())
    ex.append(rec)
    atomic_json(EXTRA, ex)
    state.setdefault('new_obstructions', []).append(rec['name'])


def obstructions():
    from s027_contain import load_obstructions
    return load_obstructions()


def controls(state):
    from s027_two_branch import TwoBranchK
    from s025_check import check_split
    from blowup_graph import blowup
    from biplanar_cnf import read_edges
    from s028_closure import child as kid, same
    import networkx as nx
    d = OUT / 'controls'
    d.mkdir(exist_ok=True)
    p = ROOT / 'validation/S003/splits/J1.split.json'
    cases = [('J1', json.loads(p.read_text()), read_edges(str(p.with_name('J1.edges'))))]
    c5s = json.load(gzip.open(ROOT / 'validation/S025/C5_CLASSIFY.json.gz', 'rt'))['results']
    r = next(r for r in c5s if r['w'] == [3, 3, 3, 3, 4] and r.get('split_checked'))
    cases.append(('C5-33334', {'n': 16, 'E1': r['E1'], 'E2': r['E2']}, blowup('Dhc', r['w'])[0]))
    res = []
    for name, split, es in cases:
        check_split(split['n'], es, split['E1'], split['E2'])
        c = TwoBranchK(es, TWO_SIZE)
        layers = []
        for k in ('E1', 'E2'):
            g = nx.Graph(); g.add_nodes_from(range(split['n'])); g.add_edges_from(split[k]); layers.append(g)
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
        c.dump(d / name)
        for mode, args in [('check', py('s026_check_two_branch.py', edge, d / name)),
                           ('regen', py('s027_two_branch.py', 'regen', edge, d / name, d / (name + '.regen.cnf')))]:
            q = child(args, 600, d / (name + '.' + mode + '.log'))
            assert q['returncode'] == 0, q
        res.append({'name': name, 'two_models_size3': len(c.two_models), 'all_minor_clauses_true': True})
    # deletion-child control: P29 bag12 child equals the certified S027 descent graph
    pc = json.loads((ROOT / 'validation/S026/filter-recovery/candidate/CANDIDATE.json').read_text())
    g6, u = kid(pc['g6'], pc['w'], 12)
    es, _ = blowup(g6, u)
    stored = (S27 / 'descent/del-bag12/graph.edges').read_text().replace('\r\n', '\n')
    assert ''.join(f'{a} {b}\n' for a, b in es) == stored
    assert same((g6, u), (pc['g6'], u)) and not same((g6, u), (pc['g6'], pc['w']))
    q = child(py('s027_selftest.py', d / 'selftest'), 1800, d / 'selftest.log')
    assert q['returncode'] == 0, q
    atomic_json(d / 'SUMMARY.json', {'two_branch_size3': res, 'deletion_child_control': 'PASS',
                                     'selftest': json.loads((d / 'selftest/SELFTEST.json').read_text())})
    state['controls'] = 'PASS'


def descent(state, deadline):
    from blowup_graph import blowup
    from s028_closure import child as kid, same, first_contained
    base = OUT / 'descent'
    base.mkdir(exist_ok=True)
    t0 = time.monotonic()
    rows, seen = [], []
    roots = [r for r in json.loads(EXTRA.read_text()) if not r['name'].startswith('C5-')]
    counter = [0]

    def visit(name, g6, u, root_deadline, depth):
        for i in range(len(u)):
            now = time.monotonic()
            if now >= root_deadline or now - t0 >= DESCENT_TOTAL - DESCENT_EACH or now >= deadline:
                return
            cg6, cu = kid(g6, u, i)
            if any(same((cg6, cu), s) for s in seen):
                continue
            seen.append((cg6, cu))
            counter[0] += 1
            cname = f'D{counter[0]:03d}'
            hit, _, _ = first_contained(obstructions(), cg6, cu)
            row = {'name': cname, 'parent': name, 'deleted_bag': i, 'g6': cg6, 'u': cu, 'n': sum(cu), 'depth': depth}
            if hit:
                row['verdict'] = 'CONTAINS_CERTIFIED_' + hit
                rows.append(row)
                atomic_json(base / 'DESCENT.json', {'rows': rows})
                continue
            d = base / cname
            d.mkdir(exist_ok=True)
            es, _ = blowup(cg6, cu)
            edge = d / 'graph.edges'
            edge.write_text(''.join(f'{a} {b}\n' for a, b in es), newline='\n')
            say(f'descent {cname} from {name}: {sum(cu)} vertices, {len(es)} edges')
            rec = camp.exact(edge, d, DESCENT_EACH)
            row.update(verdict=rec['verdict'], edges=len(es), search=rec.get('result', {}))
            rows.append(row)
            atomic_json(base / 'DESCENT.json', {'rows': rows})
            say(f'descent {cname}: {rec["verdict"]}')
            if rec['verdict'] == 'NONBIPLANAR_CERTIFIED':
                atomic_json(d / 'CANDIDATE.json', {'name': cname, 'g6': cg6, 'w': cu})
                add_extra(state, {'name': cname, 'g6': cg6, 'u': cu, 'edges': rel(edge),
                                  'certificate': rel(d / 'SUMMARY.json')})
                visit(cname, cg6, cu, root_deadline, depth + 1)
            elif rec['verdict'] == 'BIPLANAR_SPLIT_CHECKED':
                row['note'] = 'biplanar subgraph of a non-biplanar root; not a witness (counting certificate lost)'

    for r in roots:
        seen.append((r['g6'], r['u']))
    for r in roots:
        visit(r['name'], r['g6'], r['u'], time.monotonic() + DESCENT_ROOT, 1)
    state['descent'] = {'tested': sum('search' in r for r in rows), 'rows': len(rows),
                        'certified': [r['name'] for r in rows if r.get('verdict') == 'NONBIPLANAR_CERTIFIED'],
                        'min_certified_order': min([r['n'] for r in rows if r.get('verdict') == 'NONBIPLANAR_CERTIFIED'],
                                                   default=None),
                        'seconds': round(time.monotonic() - t0, 1)}


def survivors():
    s = json.loads((S27 / 'source/SUMMARY.json').read_text())
    out = []
    for kind, recs in (('S027_ADMITTED', s['admitted']), ('S027_SURPLUS', s['surplus_filter_clean'])):
        for r in recs:
            out.append({'name': 'S027-' + r['name'], 'kind': kind, 'g6': r['g6'], 'w': r['w'],
                        'edges': [list(e) for e in r['base_edges']]})
    return out


def refilter(state, graphs, label):
    from s028_closure import first_contained
    obs = obstructions()
    out = []
    for g in graphs:
        hit, f, unknown = first_contained(obs, g['g6'], g['w'])
        out.append({**{k: g[k] for k in ('name', 'kind', 'g6', 'w')},
                    'verdict': ('NONBIPLANAR_BY_CERTIFIED_SUBGRAPH' if hit else
                                'SCREEN_UNKNOWN' if unknown else 'CLEAN_SCREEN'),
                    'obstruction': hit, 'f': f})
    atomic_json(OUT / f'REFILTER_{label}.json', out)
    state[f'refilter_{label}'] = {k: sum(r['verdict'] == k for r in out) for k in
                                  ('NONBIPLANAR_BY_CERTIFIED_SUBGRAPH', 'CLEAN_SCREEN', 'SCREEN_UNKNOWN')}
    return out


def domains(state, src, resolved):
    s = json.loads((src / 'SUMMARY.json').read_text())
    out = []
    for st in s['profiles']:
        d = src / f"profile{st['profile']:02d}"
        unsat = st.get('stop') == 'GENERATOR_UNSAT'
        chk = child(py('s027_check_learned.py', d / 'LEARNED.json.gz', *([d / 'domain.cnf'] if unsat else [])),
                    1800, d / 'learned_check.log')
        deps = st.get('domain_blocking_dependencies', [])
        row = {'profile': st['profile'], 'w': st['weights'], 'stop': st.get('stop'),
               'learned_check_returncode': chk['returncode'], 'blocking_dependencies': deps,
               'unresolved_dependencies': [x for x in deps if x not in resolved]}
        if unsat and chk['returncode'] == 0:
            child(py('s025_certify.py', d / 'domain.cnf', d, 600, 1200), 1900, d / 'domain_proof.log')
            cp = d / 'domain.certificate.json'
            cert = json.loads(cp.read_text()) if cp.exists() else {'verdict': 'UNKNOWN'}
            row['domain_proof'] = cert.get('verdict')
            if cert.get('verdict') == 'UNSAT_DRAT_VERIFIED':
                with open(d / 'domain.cnf', 'rb') as f, gzip.open(d / 'domain.cnf.gz', 'wb', 9) as g:
                    shutil.copyfileobj(f, g)
                (d / 'domain.cnf').unlink()
        out.append(row)
        atomic_json(src / 'DOMAINS.json', out)
    state['domains'] = {'checked': sum(r['learned_check_returncode'] == 0 for r in out),
                        'closed_drat': [r['profile'] for r in out if r.get('domain_proof') == 'UNSAT_DRAT_VERIFIED'],
                        'closed_unconditional': [r['profile'] for r in out if r.get('domain_proof') == 'UNSAT_DRAT_VERIFIED'
                                                 and not r['unresolved_dependencies']]}


def two_branch_certify(edge, prefix, d):
    rec = {}
    for name, args in [('justification', py('s026_check_two_branch.py', edge, prefix)),
                       ('regeneration', py('s027_two_branch.py', 'regen', edge, prefix, d / 'rebuilt2.cnf'))]:
        rec[name] = child(args, 1800, d / (name + '2.log'))
        if rec[name]['returncode'] != 0:
            return rec
    rec['cnf_byte_match'] = sha(str(prefix) + '.cnf') == sha(d / 'rebuilt2.cnf')
    if not rec['cnf_byte_match']:
        return rec
    child(py('s025_certify.py', str(prefix) + '.cnf', d, NATIVE, NATIVE), 2 * NATIVE + 300, d / 'native2.log')
    cp = d / (Path(prefix).name + '.certificate.json')
    rec['certificate'] = json.loads(cp.read_text()) if cp.exists() else {}
    rec['certified'] = rec['certificate'].get('verdict') == 'UNSAT_DRAT_VERIFIED'
    if rec['certified']:
        with open(str(prefix) + '.lemmas.json', 'rb') as f, gzip.open(d / 'twobranch.lemmas.json.gz', 'wb', 9) as g:
            shutil.copyfileobj(f, g)
        for p in [Path(str(prefix) + '.lemmas.json'), Path(str(prefix) + '.cnf'), d / 'rebuilt2.cnf']:
            p.unlink()
    return rec


def process(state, queue, deadline):
    from blowup_graph import blowup
    from s025_check import check_split
    from s028_closure import first_contained
    out = []
    base = OUT / 'candidates'
    for g in queue:
        if deadline - time.monotonic() < 1200:
            out.append({'name': g['name'], 'verdict': 'NOT_RUN_WHOLE_CAP'})
            atomic_json(OUT / 'CANDIDATES.json', out)
            continue
        hit, _, _ = first_contained(obstructions(), g['g6'], g['w'])
        if hit:
            out.append({'name': g['name'], 'verdict': 'NONBIPLANAR_BY_CERTIFIED_SUBGRAPH', 'obstruction': hit})
            atomic_json(OUT / 'CANDIDATES.json', out)
            continue
        d = base / g['name']
        d.mkdir(parents=True, exist_ok=True)
        es, _ = blowup(g['g6'], g['w'])
        atomic_json(d / 'CANDIDATE.json', {**g, 'num_vertices': sum(g['w']), 'edge_count': len(es)})
        edge = d / 'graph.edges'
        edge.write_text(''.join(f'{a} {b}\n' for a, b in es), newline='\n')
        t0 = time.monotonic()
        say(f'candidate {g["name"]}: audit')
        child(py('s027_audit.py', 'cnf', d), 3600, d / 'audit_cnf.log')
        child(py('s027_audit.py', 'backtrack', d), 300, d / 'audit_backtrack.log')
        audit = json.loads((d / 'AUDIT_CNF.json').read_text()) if (d / 'AUDIT_CNF.json').exists() else []
        row = {'name': g['name'], 'kind': g['kind'], 'audit': {r['obstruction']: r['verdict'] for r in audit}}
        hits = [r for r in audit if r['verdict'] == 'CONTAINS_EXPLICIT_CHECKED']
        if hits:
            row.update(verdict='NONBIPLANAR_BY_CERTIFIED_SUBGRAPH', obstruction=hits[0]['obstruction'])
        else:
            for seed in (1, 2):
                child(py('s025_cover_anneal.py', edge, seed, 60, d / f'anneal{seed}.json'), 75, d / f'anneal{seed}.log')
                ap = d / f'anneal{seed}.json'
                if ap.exists():
                    ar = json.loads(ap.read_text())
                    row[f'anneal{seed}_uncovered'] = ar['best_uncovered']
                    if ar['best_uncovered'] == 0:
                        check_split(sum(g['w']), es, ar['E1'], ar['E2'])
                        row['verdict'] = 'BIPLANAR_SPLIT_CHECKED_WITNESS_CANDIDATE'
                        break
            if 'verdict' not in row:
                rec = camp.exact(edge, d, EXACT)
                row['exact'] = {'verdict': rec['verdict'], 'result': rec.get('result')}
                row['verdict'] = rec['verdict']
                if rec['verdict'] == 'BIPLANAR_SPLIT_CHECKED':
                    row['verdict'] = 'BIPLANAR_SPLIT_CHECKED_WITNESS_CANDIDATE'
                if row['verdict'] == 'UNKNOWN' and deadline - time.monotonic() > TWO_BRANCH + 1200:
                    prefix = d / 'twobranch'
                    s = child(py('s027_two_branch.py', edge, prefix, TWO_BRANCH, TWO_SIZE),
                              TWO_BRANCH + 900, d / 'twobranch.log')
                    rp = Path(str(prefix) + '.result.json')
                    res = json.loads(rp.read_text()) if rp.exists() else {'verdict': 'UNKNOWN', 'rc': s['returncode']}
                    row['two_branch'] = res
                    if res['verdict'] == 'UNSAT':
                        row['two_branch_proof'] = two_branch_certify(edge, prefix, d)
                        if row['two_branch_proof'].get('certified'):
                            row['verdict'] = 'NONBIPLANAR_CERTIFIED'
                            atomic_json(d / 'SUMMARY.json', {'verdict': 'NONBIPLANAR_CERTIFIED',
                                                             'proof': row['two_branch_proof']})
                    elif res['verdict'] == 'SAT':
                        sp = json.loads(Path(str(prefix) + '.split.json').read_text())
                        check_split(sp['n'], es, sp['E1'], sp['E2'])
                        row['verdict'] = 'BIPLANAR_SPLIT_CHECKED_WITNESS_CANDIDATE'
            if row['verdict'] == 'NONBIPLANAR_CERTIFIED':
                add_extra(state, {'name': g['name'], 'g6': g['g6'], 'u': g['w'], 'edges': rel(edge),
                                  'certificate': rel(d / 'SUMMARY.json')})
        row['seconds'] = round(time.monotonic() - t0, 1)
        out.append(row)
        atomic_json(OUT / 'CANDIDATES.json', out)
        say(f'candidate {g["name"]}: {row["verdict"]}')
        if row['verdict'].startswith('BIPLANAR_SPLIT_CHECKED'):
            say('WITNESS CANDIDATE FOUND: stop and report before anything else')
            state['witness_candidate'] = g['name']
            break
    state['candidates'] = {r['name']: r['verdict'] for r in out}


def main():
    if os.name != 'nt':
        raise RuntimeError('owner local launcher targets the Windows workstation')
    import msvcrt
    lock = (OUT / 'RUN.lock').open('a+b')
    lock.write(b'0'); lock.flush(); lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    power = ctypes.windll.kernel32
    power.SetThreadExecutionState(0x80000001)
    state = {'session': 'S028', 'authority': "owner 'run next session' 2026-10-19 (D047), local Claude Code",
             'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
             'memory_kib': MEM, 'whole_campaign_seconds': WHOLE, 'graph_absolute_seconds': GRAPH_ABS}
    try:
        for k, v in NATIVE_SHA.items():
            assert sha(os.environ[k]) == v, (k, 'native digest mismatch')
        env = {'kind': 'LOCAL_WINDOWS_OWNER_INVOKED_S028', 'python': sys.version,
               'packages': {k: metadata.version(k) for k in ('python-sat', 'networkx', 'numpy')},
               'native_sha256': {k: sha(os.environ[k]) for k in NATIVE_SHA},
               'native_paths': {k: os.environ[k] for k in NATIVE_SHA}, 'memory_cap_kib': MEM,
               'cpu_threads': os.cpu_count(), 'source_commit': state['source_commit'],
               'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for pat in
                                 ('s025_*.py', 's026_*.py', 's027_*.py', 's028_*.py', 'biplanar_cegar.py',
                                  'biplanar_cnf.py', 'blowup_graph.py') for p in sorted((ROOT / 'tools').glob(pat))} |
               {'scripts/run_s028_local.py': sha(__file__)}}
        atomic_json(OUT / 'ENVIRONMENT.json', env)
        atomic_json(EXTRA, initial_extra())
        atomic_json(OUT / 'STATE.json', state)
        say('S028: FULL 271+K9 smoke starting; one worker, 11GiB cap')
        smoke = run_step([sys.executable, str(ROOT / 'scripts/cloud_smoke.py')], 2400, OUT / 'smoke.log',
                         OUT / 'RUN_JOURNAL.jsonl', memory_kib=MEM)
        if smoke['returncode'] != 0:
            raise RuntimeError('full smoke failed; science BLOCKED')
        res = ROOT / 'artifacts/tmp/cloud_smoke/RESULT.json'
        assert json.loads(res.read_text())['verdict'] == 'PASS'
        shutil.copyfile(res, OUT / 'SMOKE.json')
        t0 = time.monotonic(); deadline = t0 + WHOLE
        state['science_start_utc'] = datetime.now(timezone.utc).isoformat()
        say('smoke PASS; controls'); controls(state); atomic_json(OUT / 'STATE.json', state)
        say('deletion descent'); descent(state, deadline); atomic_json(OUT / 'STATE.json', state)
        say('refilter S027 survivors')
        old = refilter(state, survivors(), 'S027')
        atomic_json(KNOWN, survivors())
        say('source rerun')
        src = OUT / 'source'
        state['source_process'] = child(py('s028_source.py', src, 7200), 7200 + 900, OUT / 'source.log')
        atomic_json(OUT / 'STATE.json', state)
        s = json.loads((src / 'SUMMARY.json').read_text())
        new = [{'name': 'S028-' + r['name'], 'kind': 'S028_ADMITTED', 'g6': r['g6'], 'w': r['w'],
                'edges': r['base_edges']} for r in s['admitted']]
        state['source'] = {'admitted': len(new), 'surplus': len(s['surplus_filter_clean'])}
        queue = ([g for g in old if g['verdict'] != 'NONBIPLANAR_BY_CERTIFIED_SUBGRAPH' and g['kind'] == 'S027_ADMITTED'] +
                 new + [g for g in old if g['verdict'] != 'NONBIPLANAR_BY_CERTIFIED_SUBGRAPH' and g['kind'] == 'S027_SURPLUS'])
        queue = [{k: g[k] for k in ('name', 'kind', 'g6', 'w')} for g in queue]
        atomic_json(OUT / 'QUEUE.json', queue)
        resolved = {g['name'] for g in old if g['verdict'] == 'NONBIPLANAR_BY_CERTIFIED_SUBGRAPH'}
        say('domain proofs'); domains(state, src, resolved); atomic_json(OUT / 'STATE.json', state)
        say(f'candidate queue: {len(queue)} graphs'); process(state, queue, deadline)
        state['status'] = 'CAMPAIGN_FINISHED_NOT_A_SESSION_CLOSEOUT'
        state['science_seconds'] = round(time.monotonic() - t0, 1)
        atomic_json(OUT / 'STATE.json', state); atomic_json(OUT / 'HANDBACK.json', state)
        journal(OUT / 'RUN_JOURNAL.jsonl', 'campaign_end', status=state['status'])
        say('S028 campaign finished; handback saved')
    except BaseException as e:
        state['status'] = 'INTERRUPTED_OR_BLOCKED'; state['error'] = repr(e)
        atomic_json(OUT / 'STATE.json', state)
        journal(OUT / 'RUN_JOURNAL.jsonl', 'campaign_error', error=repr(e))
        raise
    finally:
        power.SetThreadExecutionState(0x80000000)
        lock.close()


if __name__ == '__main__':
    main()
