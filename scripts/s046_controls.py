"""S046 encoding and native controls (verification cost, not experimental budget)."""
import itertools as it
import json
from pathlib import Path
import shutil
import sys
import time

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import s046_encode as enc
import s046_analyse as A
from s045_verify import check_pair

OUT = ROOT / 'validation/S046/CONTROLS.json'
WORK = ROOT / 'artifacts/tmp/S046/controls'


def counter_control():
    cases = 0
    for L in range(1, 9):
        for d in range(0, L + 2):
            cnf = enc.CNF(L)
            enc.at_least(cnf, list(range(1, L + 1)), d)
            with Solver(name='cadical195', bootstrap_with=cnf.clauses) as s:
                for bits in it.product((0, 1), repeat=L):
                    assum = [i + 1 if b else -(i + 1) for i, b in enumerate(bits)]
                    assert s.solve(assumptions=assum) == (sum(bits) >= d), (L, d, bits)
                    cases += 1
    return cases


def rows_ok(n, adj):
    for i, j in it.combinations(range(n), 2):
        cols = [c for c in range(n) if c not in (i, j)]
        a, b = [adj[i][c] for c in cols], [adj[j][c] for c in cols]
        if a < b:
            return False
    return True


def predicate(n, pairs, assign, k):
    """assign[i] in {0 absent, 1 layer1, 2 layer2}."""
    adj = [[0] * n for _ in range(n)]
    for (a, b), x in zip(pairs, assign):
        if x:
            adj[a][b] = adj[b][a] = 1
    if any(sum(r) < k for r in adj):
        return False
    first = next((x for x in assign if x), None)
    return rows_ok(n, adj) and first in (None, 1)


def cs_exhaustive(n, k):
    pairs, cnf = enc.clauses(n, 'CS', k)
    m = len(pairs)
    agree = 0
    with Solver(name='cadical195', bootstrap_with=cnf.clauses) as s:
        for assign in it.product((0, 1, 2), repeat=m):
            assum = []
            for i, x in enumerate(assign):
                assum += [2 * i + 1 if x == 1 else -(2 * i + 1), 2 * i + 2 if x == 2 else -(2 * i + 2)]
            assert s.solve(assumptions=assum) == predicate(n, pairs, assign, k), assign
            agree += 1
    return agree


def cs_soundness(n, k):
    """Every class under vertex relabelling x layer swap has a member accepted by CS."""
    pairs = list(it.combinations(range(n), 2))
    index = {p: i for i, p in enumerate(pairs)}
    perms = list(it.permutations(range(n)))
    maps = [[index[tuple(sorted((p[a], p[b])))] for a, b in pairs] for p in perms]
    seen, classes, bad = set(), 0, 0
    for assign in it.product((0, 1, 2), repeat=len(pairs)):
        if assign in seen:
            continue
        orbit = set()
        for mp in maps:
            img = [0] * len(pairs)
            for i, x in enumerate(assign):
                img[mp[i]] = x
            img = tuple(img)
            orbit.add(img)
            orbit.add(tuple((3 - x) % 3 if x else 0 for x in img))
        seen |= orbit
        deg = [0] * n
        for (a, b), x in zip(pairs, assign):
            if x:
                deg[a] += 1
                deg[b] += 1
        if min(deg) < k:
            continue  # outside the C/CS domain; degree is relabelling/swap invariant
        classes += 1
        if not any(predicate(n, pairs, o, k) for o in orbit):
            bad += 1
    assert bad == 0
    return classes


def union_soundness(n):
    pairs = list(it.combinations(range(n), 2))
    perms = list(it.permutations(range(n)))
    graphs = 0
    for bits in it.product((0, 1), repeat=len(pairs)):
        es = [p for p, b in zip(pairs, bits) if b]
        for p in perms:
            adj = [[0] * n for _ in range(n)]
            for a, b in es:
                adj[p[a]][p[b]] = adj[p[b]][p[a]] = 1
            if rows_ok(n, adj):
                break
        else:
            raise AssertionError(('no lex representative', es))
        graphs += 1
    return graphs


def native(label, n, k, arm, seconds, expect):
    from s046_driver import run_slice
    out = WORK / label
    shutil.rmtree(out, ignore_errors=True)
    r = run_slice(out, n, k, seconds, arm, startup_ceiling=60)
    row = dict(label=label, n=n, k=k, arm=arm, reason=r['reason'], state=r['state'], candidates=r['candidates'],
               returncode=r['native_returncode'], solve_seconds=r['solve_seconds'], expect=expect)
    if expect == 'ALERT':
        assert r['reason'] == 'NONCOLOUR_ALERT_UNVERIFIED', r
        alert = json.loads((out / 'ALERT.json').read_text())
        check_pair(n, alert['layers'], alert['rotations'])
        edges = sorted({tuple(e) for ls in alert['layers'] for e in ls})
        s = A.structure(n, edges)
        verdict, sec = A.drat_certify(n, edges, k, s['clique'], out / 'drat', 60, 120)
        assert verdict == 'VERIFIED_NON_K_COLOURABLE', verdict
        row.update(found_edges=edges, omega=s['omega'], drat=verdict, min_degree=s['min_degree'])
    elif expect == 'UNSAT':
        assert r['reason'] == 'NATIVE_UNSAT_UNCERTIFIED' and r['native_returncode'] == 20, r
        pairs, cnf = enc.clauses(n, arm, k)
        # The infeasibility is purely the degree encoding; certify that CNF alone.
        work = out / 'drat'
        work.mkdir(parents=True, exist_ok=True)
        top = max(abs(x) for c in cnf.clauses for x in c)
        (work / 'enc.cnf').write_text(f'p cnf {top} {len(cnf.clauses)}\n' +
                                      ''.join(' '.join(map(str, c)) + ' 0\n' for c in cnf.clauses))
        import subprocess
        run = subprocess.run([str(A.CADICAL), '-q', '--no-binary', str(work / 'enc.cnf'), str(work / 'enc.drat')],
                             capture_output=True, text=True, timeout=60)
        chk = subprocess.run([str(A.DRAT_TRIM), str(work / 'enc.cnf'), str(work / 'enc.drat')],
                             capture_output=True, text=True, timeout=120)
        assert run.returncode == 20 and 's VERIFIED' in chk.stdout
        row.update(encoding_unsat_drat='VERIFIED')
    elif expect == 'ALERT_OR_UNKNOWN':
        if r['reason'] == 'NONCOLOUR_ALERT_UNVERIFIED':
            return native_verify(row, out, n, k)
        row.update(outcome='NOT_FOUND_IN_CAP_UNKNOWN')
    return row


def native_verify(row, out, n, k):
    alert = json.loads((out / 'ALERT.json').read_text())
    check_pair(n, alert['layers'], alert['rotations'])
    edges = sorted({tuple(e) for ls in alert['layers'] for e in ls})
    s = A.structure(n, edges)
    verdict, sec = A.drat_certify(n, edges, k, s['clique'], out / 'drat', 120, 300)
    row.update(found_edges=edges, omega=s['omega'], drat=verdict, min_degree=s['min_degree'], outcome=verdict)
    return row


def main():
    assert A.pinned_ok()
    t0 = time.monotonic()
    res = dict(counter_cases=counter_control())
    res['cs_exhaustive_n4_k0'] = cs_exhaustive(4, 0)
    res['cs_exhaustive_n4_k2'] = cs_exhaustive(4, 2)
    res['cs_exhaustive_n5_k2'] = cs_exhaustive(5, 2)
    res['cs_soundness_classes_n4_k0'] = cs_soundness(4, 0)
    res['cs_soundness_classes_n5_k2'] = cs_soundness(5, 2)
    res['lex_union_soundness_n5'] = union_soundness(5)
    res['lex_union_soundness_n6'] = union_soundness(6)
    res['encoding_seconds'] = round(time.monotonic() - t0, 3)
    t1 = time.monotonic()
    res['native'] = [native('k4-C', 4, 3, 'C', 20, 'ALERT'), native('k4-CS', 4, 3, 'CS', 20, 'ALERT'),
                     native('k5-CS', 5, 4, 'CS', 20, 'ALERT'), native('k4-B-n6', 6, 3, 'B', 20, 'ALERT'),
                     native('deg4-n4-C', 4, 4, 'C', 20, 'UNSAT'),
                     native('sulanke-level-n11-CS', 11, 8, 'CS', 120, 'ALERT_OR_UNKNOWN')]
    res['native_seconds'] = round(time.monotonic() - t1, 3)
    res['status'] = 'PASS'
    res['scope'] = 'encoding/protocol controls; no Earth-Moon graph verdict'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
