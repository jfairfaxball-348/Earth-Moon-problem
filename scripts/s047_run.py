#!/usr/bin/env python3
"""S047 controls, E1 seed certification and E2 extension ladder (D079).

Usage: python scripts/s047_run.py controls|e1|e2
Runtime under artifacts/tmp/S047; receipts under validation/S047.
"""
import gzip
import hashlib
import itertools as it
import json
import os
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

import networkx as nx
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s047_extend import build, decode, dimacs  # noqa: E402

RT = ROOT / 'artifacts/tmp/S047'
V = ROOT / 'validation/S047'
CADICAL = os.environ.get('EMP_CADICAL', str(ROOT / 'artifacts/tmp/native/bin/cadical'))
DRAT = os.environ.get('EMP_DRAT_TRIM', str(ROOT / 'artifacts/tmp/native/bin/drat-trim'))
REG = json.loads((V / 'REGISTRATION.json').read_text())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def child_cpu():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def self_cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def colourable(n, edges, k):
    """Independent backtracking k-colouring (does not use the partition lemma)."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    col = [-1] * n

    def rec(i, used):
        if i == n:
            return True
        v = order[i]
        bad = {col[u] for u in adj[v]}
        for c in range(min(k, used + 1)):
            if c not in bad:
                col[v] = c
                if rec(i + 1, max(used, c + 1)):
                    return True
        col[v] = -1
        return False

    return rec(0, 0), list(col)


def colour_cnf(n, edges, k):
    x = lambda v, c: v * k + c + 1  # noqa: E731
    cl = [[x(v, c) for c in range(k)] for v in range(n)]
    cl += [[-x(u, c), -x(v, c)] for u, v in edges for c in range(k)]
    return n * k, cl


def write_cnf(path, nv, cl):
    with open(path, 'w') as fh:
        fh.write(f'p cnf {nv} {len(cl)}\n')
        for c in cl:
            fh.write(' '.join(map(str, c)) + ' 0\n')


def cadical(cnf, proof, cap):
    t0, c0 = time.time(), child_cpu()
    try:
        p = subprocess.run([CADICAL, '-q', '--no-binary', '-t', str(cap), str(cnf), str(proof)],
                           capture_output=True, text=True, timeout=cap + 60)
        code, out = p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        code, out = 0, ''
    return code, out, time.time() - t0, child_cpu() - c0


def drat(cnf, proof):
    t0, c0 = time.time(), child_cpu()
    p = subprocess.run([DRAT, str(cnf), str(proof), '-t', '20000'], capture_output=True, text=True)
    ok = 's VERIFIED' in p.stdout
    return ok, time.time() - t0, child_cpu() - c0


def faces_ok(edges, rot):
    """Euler check of a rotation system on each connected component."""
    rot = {int(k): v for k, v in rot.items()}
    darts = {(u, v) for u, v in edges} | {(v, u) for u, v in edges}
    for u, nb in rot.items():
        assert sorted(nb) == sorted(v for (a, v) in darts if a == u), u
    seen, F = set(), 0
    for d in darts:
        if d in seen:
            continue
        F += 1
        cur = d
        while cur not in seen:
            seen.add(cur)
            u, v = cur
            nb = rot[v]
            cur = (v, nb[(nb.index(u) + 1) % len(nb)])
    g = nx.Graph(edges)
    C = nx.number_connected_components(g)
    return g.number_of_nodes() - g.number_of_edges() + F == 1 + C


def controls():
    out = {'started_utc': utc()}
    res = {}
    for name, k, t, fl, expect in [('C1', 9, 1, False, 1), ('C2', 8, 1, True, 1),
                                   ('C1b', 9, 1, True, 0)]:
        f = build(k, t, fl)
        s = Solver(name='cd15', bootstrap_with=f['clauses'])
        models = []
        while s.solve():
            m = [l for l in s.get_model() if 0 < abs(l) <= f['nvars0']]
            models.append(decode(f, m))
            s.add_clause([-l for l in m])
        s.delete()
        info = {'k': k, 't': t, 'filters': fl, 'models': len(models), 'expected': expect}
        if models:
            g = nx.Graph(models[0])
            seed_target = nx.complete_graph(k - 2)
            info['first_model_edges'] = len(models[0])
            info['first_model_is_K(k-2)vC5'] = nx.is_isomorphic(
                g, nx.complement(nx.disjoint_union(nx.empty_graph(k - 2), nx.complement(nx.cycle_graph(5)))))
            del seed_target
            info['first_model_k_colourable'] = colourable(g.number_of_nodes(), models[0], k)[0]
        info['pass'] = len(models) == expect and all(
            not colourable(len(nx.Graph(m)), m, k)[0] for m in models)
        res[name] = info
    # C3: brute force over all 2^11 neighbourhoods, independent colouring routine
    A, B = list(range(6)), list(range(6, 11))
    base = list(build(9, 1, False)['seed_edges'])
    bad = []
    for mask in range(1 << 11):
        edges = base + [(v, 11) for v in range(11) if mask >> v & 1]
        if not colourable(12, edges, 9)[0]:
            bad.append(mask)
    res['C3'] = {'neighbourhoods': 1 << 11, 'non_9_colourable': [bin(b) for b in bad],
                 'pass': bad == [(1 << 11) - 1]}
    out['controls'] = res
    out['status'] = 'PASS' if all(r['pass'] for r in res.values()) else 'FAIL'
    out['finished_utc'] = utc()
    (V / 'CONTROLS.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def e1():
    alert = json.loads((ROOT / 'validation/S046/calibration/runs/k8-n11-C/ALERT.json').read_text())
    L = [[tuple(e) for e in layer] for layer in alert['layers']]
    out = {'source': 'validation/S046/calibration/runs/k8-n11-C/ALERT.json',
           'source_sha256': sha(ROOT / 'validation/S046/calibration/runs/k8-n11-C/ALERT.json')}
    out['layer_edges'] = [len(l) for l in L]
    out['disjoint'] = not ({tuple(sorted(e)) for e in L[0]} & {tuple(sorted(e)) for e in L[1]})
    out['lr_planar'] = [nx.check_planarity(nx.Graph(l))[0] for l in L]
    out['rotation_euler'] = [faces_ok(L[i], alert['rotations'][i]) for i in range(2)]
    union = sorted({tuple(sorted(e)) for e in L[0] + L[1]})
    target = nx.complement(nx.disjoint_union(nx.empty_graph(6), nx.complement(nx.cycle_graph(5))))
    out['union_is_K6vC5'] = nx.is_isomorphic(nx.Graph(union), target)
    ok, col = colourable(11, union, 9)
    out['explicit_9_colouring'] = col if ok else None
    out['colouring_checked'] = ok and all(col[u] != col[v] for u, v in union) and max(col) < 9
    RT.mkdir(parents=True, exist_ok=True)
    nv, cl = colour_cnf(11, union, 8)
    write_cnf(RT / 'e1_k8.cnf', nv, cl)
    code, _, w, c = cadical(RT / 'e1_k8.cnf', RT / 'e1_k8.drat', 60)
    vok, vw, vc = drat(RT / 'e1_k8.cnf', RT / 'e1_k8.drat')
    out['non_8_colourable'] = {'cadical_exit': code, 'drat_trim_verified': vok,
                               'cnf_sha256': sha(RT / 'e1_k8.cnf'), 'proof_sha256': sha(RT / 'e1_k8.drat'),
                               'verification_wall_s': round(w + vw, 3)}
    with open(RT / 'e1_k8.drat', 'rb') as src, gzip.open(V / 'e1_k8.drat.gz', 'wb') as dst:
        shutil.copyfileobj(src, dst)
    out['union_edges'] = union
    out['status'] = 'PASS' if (out['disjoint'] and all(out['lr_planar']) and all(out['rotation_euler'])
                               and out['union_is_K6vC5'] and out['colouring_checked'] and code == 20
                               and vok) else 'FAIL'
    (V / 'E1_SEED.json').write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != 'union_edges'}, indent=1))


def e2():
    reg = REG['e2']
    reg_epoch = time.mktime(time.strptime(REG['registered_utc'], '%Y-%m-%dT%H:%M:%SZ')) - time.timezone
    deadline = reg_epoch + 3600 * REG['budget']['deadline_hours_after_registration']
    ledger_path = V / 'E2_LADDER.json'
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {'rows': []}
    done = {r['t'] for r in ledger['rows']}
    spent_cpu = sum(r['experimental_cpu_s'] for r in ledger['rows'])
    spent_wall = sum(r['experimental_wall_s'] for r in ledger['rows'])
    RT.mkdir(parents=True, exist_ok=True)
    for t in reg['ladder_t']:
        if t in done:
            continue
        if any(r['verdict'] not in ('UNSAT_VERIFIED',) for r in ledger['rows']):
            print('ladder stopped at an earlier non-UNSAT row')
            break
        if time.time() > deadline or spent_cpu >= REG['budget']['e2_cpu_s'] or spent_wall >= REG['budget']['e2_wall_s']:
            print('budget/deadline reached')
            break
        cap = min(reg['per_t_wall_cap_s'], int(REG['budget']['e2_wall_s'] - spent_wall))
        row = {'t': t, 'start_utc': utc()}
        w0, s0 = time.time(), self_cpu()
        f = build(9, t, True)
        cnf = RT / f'e2_t{t}.cnf'
        cnf.write_text(dimacs(f))
        row['gen_wall_s'], row['gen_cpu_s'] = round(time.time() - w0, 3), round(self_cpu() - s0, 3)
        row['vars'], row['clauses'] = f['nvars'], len(f['clauses'])
        row['cnf_sha256'] = sha(cnf)
        proof = RT / f'e2_t{t}.drat'
        code, outp, w, c = cadical(cnf, proof, cap)
        row['solver_exit'], row['solver_wall_s'], row['solver_cpu_s'] = code, round(w, 3), round(c, 3)
        row['experimental_wall_s'] = round(row['gen_wall_s'] + w, 3)
        row['experimental_cpu_s'] = round(row['gen_cpu_s'] + c, 3)
        if code == 20:
            vok, vw, vc = drat(cnf, proof)
            row['proof_bytes'] = proof.stat().st_size
            row['proof_sha256'] = sha(proof)
            row['drat_trim_verified'], row['verify_wall_s'], row['verify_cpu_s'] = vok, round(vw, 3), round(vc, 3)
            row['verdict'] = 'UNSAT_VERIFIED' if vok else 'UNSAT_UNVERIFIED'
            if vok and row['proof_bytes'] < 40 * 2 ** 20:
                with open(proof, 'rb') as src, gzip.open(V / f'e2_t{t}.drat.gz', 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                row['proof_archive'] = f'validation/S047/e2_t{t}.drat.gz'
        elif code == 10:
            model = [int(x) for line in outp.splitlines() if line.startswith('v') for x in line.split()[1:]]
            edges = decode(f, [l for l in model if 0 < abs(l) <= f['nvars0']])
            n = f['n0'] + t
            row['model_edges'] = edges
            row['model_9_colourable_independent'] = colourable(n, edges, 9)[0]
            row['verdict'] = 'SAT_CANDIDATE_BIPLANARITY_UNKNOWN'
        else:
            row['verdict'] = 'CAPPED_UNKNOWN'
        row['end_utc'] = utc()
        spent_cpu += row['experimental_cpu_s']
        spent_wall += row['experimental_wall_s']
        ledger['rows'].append(row)
        ledger['totals'] = {'experimental_cpu_s': round(spent_cpu, 3), 'experimental_wall_s': round(spent_wall, 3)}
        ledger_path.write_text(json.dumps(ledger, indent=1))
        print(json.dumps({k: v for k, v in row.items() if k != 'model_edges'}), flush=True)
        for p in (proof,):
            if p.exists() and row['verdict'] == 'UNSAT_VERIFIED':
                p.unlink()


if __name__ == '__main__' and sys.argv[1] in ('controls', 'e1', 'e2'):
    {'controls': controls, 'e1': e1, 'e2': e2}[sys.argv[1]]()


def a1_row(t, cap, filters=True):
    from s047_cegar import run
    w0, s0 = time.time(), self_cpu()
    verdict, f, cl, learned, cand = run(t, time.time() + cap, filters=filters)
    row = {'t': t, 'filters': filters, 'cegar_verdict': verdict, 'learned': len(learned),
           'cegar_wall_s': round(time.time() - w0, 3), 'cegar_cpu_s': round(self_cpu() - s0, 3)}
    if verdict == 'CANDIDATE':
        row['candidate_edges'] = cand
        row['candidate_9_colourable_independent'] = colourable(f['n0'] + t, cand, 9)[0]
    return row, f, cl, learned


def a1_certify(row, f, cl, learned, tag):
    from s047_cegar import colour_clause
    e = lambda u, v: f['pool'].obj2id[('e', min(u, v), max(u, v))]  # noqa: E731
    final = [colour_clause(f, e, *sp) for sp in learned] + cl
    nv = max([f['pool'].top] + [abs(l) for c in final for l in c])
    cnf, proof = RT / f'{tag}.cnf', RT / f'{tag}.drat'
    write_cnf(cnf, nv, final)
    code, _, w, c = cadical(cnf, proof, 600)
    vok, vw, vc = drat(cnf, proof) if code == 20 else (False, 0, 0)
    row.update({'final_clauses': len(final), 'final_cnf_sha256': sha(cnf), 'native_exit': code,
                'native_wall_s': round(w, 3), 'proof_bytes': proof.stat().st_size if proof.exists() else 0,
                'proof_sha256': sha(proof) if proof.exists() else None, 'drat_trim_verified': vok,
                'verify_wall_s': round(vw, 3)})
    with open(cnf, 'rb') as src, gzip.open(V / f'{tag}.cnf.gz', 'wb') as dst:
        shutil.copyfileobj(src, dst)
    if vok and row['proof_bytes'] < 60 * 2 ** 20:
        with open(proof, 'rb') as src, gzip.open(V / f'{tag}.drat.gz', 'wb') as dst:
            shutil.copyfileobj(src, dst)
        row['proof_archive'] = f'validation/S047/{tag}.drat.gz'
    (V / f'{tag}.learned.json').write_text(json.dumps([[s, list(p)] for s, p in learned]))
    row['verdict'] = 'UNSAT_VERIFIED' if vok else 'UNSAT_UNVERIFIED'
    for p in (cnf, proof):
        if p.exists():
            p.unlink()


def a1controls():
    out = {'started_utc': utc(), 'rows': []}
    for t in (2, 3, 4):
        row, f, cl, learned = a1_row(t, 120)
        if row['cegar_verdict'] == 'UNSAT':
            a1_certify(row, f, cl, learned, f'a1c_t{t}')
        out['rows'].append(row)
    row, f, cl, learned = a1_row(1, 60, filters=False)
    target = nx.complement(nx.disjoint_union(nx.empty_graph(7), nx.complement(nx.cycle_graph(5))))
    row['candidate_is_K7vC5'] = row['cegar_verdict'] == 'CANDIDATE' and nx.is_isomorphic(nx.Graph(row['candidate_edges']), target)
    out['rows'].append(row)
    out['status'] = 'PASS' if (all(r.get('verdict') == 'UNSAT_VERIFIED' for r in out['rows'][:3])
                               and row['candidate_is_K7vC5'] and not row['candidate_9_colourable_independent']) else 'FAIL'
    out['finished_utc'] = utc()
    (V / 'A1_CONTROLS.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def a1():
    am = json.loads((V / 'AMENDMENT_A1.json').read_text())
    path = V / 'A1_LADDER.json'
    lad = json.loads(path.read_text()) if path.exists() else {'rows': []}
    cpu = sum(r['experimental_cpu_s'] for r in lad['rows'])
    wall = sum(r['experimental_wall_s'] for r in lad['rows'])
    for t in am['ladder_t']:
        if t in {r['t'] for r in lad['rows']}:
            continue
        if any(r['verdict'] != 'UNSAT_VERIFIED' for r in lad['rows']):
            print('A1 ladder stopped at an earlier non-UNSAT row')
            break
        if cpu >= am['budget']['cpu_s'] or wall >= am['budget']['wall_s']:
            print('A1 budget reached')
            break
        cap = min(am['per_t_wall_cap_s'], am['budget']['wall_s'] - wall)
        start = utc()
        row, f, cl, learned = a1_row(t, cap)
        row['start_utc'] = start
        row['experimental_cpu_s'], row['experimental_wall_s'] = row['cegar_cpu_s'], row['cegar_wall_s']
        if row['cegar_verdict'] == 'UNSAT':
            a1_certify(row, f, cl, learned, f'a1_t{t}')
        elif row['cegar_verdict'] == 'CANDIDATE':
            row['verdict'] = 'CANDIDATE_BIPLANARITY_UNKNOWN'
        else:
            row['verdict'] = 'CAPPED_UNKNOWN'
        row['end_utc'] = utc()
        cpu += row['experimental_cpu_s']
        wall += row['experimental_wall_s']
        lad['rows'].append(row)
        lad['totals'] = {'experimental_cpu_s': round(cpu, 3), 'experimental_wall_s': round(wall, 3)}
        path.write_text(json.dumps(lad, indent=1))
        print(json.dumps({k: v for k, v in row.items() if k != 'candidate_edges'}), flush=True)


if __name__ == '__main__' and sys.argv[1] in ('a1', 'a1controls'):
    {'a1': a1, 'a1controls': a1controls}[sys.argv[1]]()
