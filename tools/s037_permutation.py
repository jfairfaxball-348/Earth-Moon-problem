"""Exact finite fixed-template formulation; planarity holds for every model.

x[u,a] is a vertex bijection from template T2 to labels of fixed T1.
Packing clauses forbid mapped edges of T1; four-set separation forbids every
bijection between an independent four-set of T2 and one of T1. No planarity
oracle/cuts or unconstrained edge variables occur. Bounded UNKNOWN is not UNSAT.
"""
import itertools as it
import json
from pathlib import Path
import sys
import time
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_check_pair import check


def formula(n, e1, template):
    x = {(u, a): 1+u*n+a for u in range(n) for a in range(n)}
    clauses = []
    for rows in ([[x[u, a] for a in range(n)] for u in range(n)],
                 [[x[u, a] for u in range(n)] for a in range(n)]):
        for row in rows:
            clauses.append(row)
            clauses.extend([-a, -b] for a, b in it.combinations(row, 2))
    for u, v in template:
        for a, b in e1:
            clauses.extend(([-x[u, a], -x[v, b]], [-x[u, b], -x[v, a]]))
    return x, clauses


def separated_clauses(x, preimage, image):
    return [[-x[u, a] for u, a in zip(preimage, perm)] for perm in it.permutations(image)]


def run(data, seconds=20, conflict_cap=20000):
    n, e1, template = data['n'], data['E1'], data['E2']
    check(data)
    start_cpu, start_wall = time.process_time(), time.monotonic()
    x, clauses = formula(n, e1, template)
    e1 = set(map(tuple, e1))
    base = len(clauses)
    models = 0
    best = None
    seen = set()
    stop = 'CPU_CAP'
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        solver.set_phases([x[u, u] for u in range(n)])
        while time.process_time()-start_cpu < seconds:
            remaining = conflict_cap-solver.accum_stats()['conflicts']
            if remaining <= 0:
                stop = 'CONFLICT_CAP'
                break
            solver.conf_budget(min(1000, remaining))
            sat = solver.solve_limited()
            if sat is None:
                continue
            if sat is False:
                stop = 'BARE_UNSAT_UNCERTIFIED_FIXED_TEMPLATE_ONLY'
                break
            models += 1
            positives = set(v for v in solver.get_model() if v > 0)
            p = {u: next(a for a in range(n) if x[u, a] in positives) for u in range(n)}
            assert len(set(p.values())) == n
            inverse = {a: u for u, a in p.items()}
            e2 = {tuple(sorted((p[u], p[v]))) for u, v in template}
            assert not e1 & e2
            bad = [vs for vs in it.combinations(range(n), 4)
                   if all(e not in e1 and e not in e2 for e in it.combinations(vs, 2))]
            if best is None or len(bad) < best['independent_four_sets']:
                best = dict(n=n, V=list(range(n)), E1=sorted(e1), E2=sorted(e2),
                            independent_four_sets=len(bad), permutation=p,
                            metadata=dict(model=models))
            if not bad:
                stop = 'INDEPENDENT_VALIDATION_REQUIRED'
                break
            for vs in bad:
                us = tuple(sorted(inverse[v] for v in vs))
                key = us, vs
                if key in seen:
                    continue
                seen.add(key)
                for clause in separated_clauses(x, us, vs):
                    solver.add_clause(clause)
        stats = solver.accum_stats()
    validation = check(best) if best else None
    return dict(status='UNKNOWN' if stop != 'INDEPENDENT_VALIDATION_REQUIRED' else 'CHECKED_ALPHA3_PAIR',
                stop=stop, n=n, density=len(e1)+len(template), models=models,
                variables=n*n, base_clauses=base, separated_four_set_pairs=len(seen),
                separated_clauses=24*len(seen), stats=stats, best=best,
                best_checked_violations=validation['independent_four_sets'] if validation else None,
                cpu_seconds=time.process_time()-start_cpu, wall_seconds=time.monotonic()-start_wall,
                proof_exported=False)


def controls():
    # Compare the SAT encoding against all 5! permutations, with and without
    # four-set clauses, instead of testing the encoder against itself.
    n = 5
    e1 = [(0, 1), (1, 2)]
    template = [(0, 2), (2, 4)]
    x, clauses = formula(n, e1, template)
    mapping_count = 0
    for separated in (False, True):
        cs = list(clauses)
        if separated:
            cs += separated_clauses(x, (0, 1, 3, 4), (0, 2, 3, 4))
        with Solver(name='cadical195', bootstrap_with=cs) as s:
            for p in it.permutations(range(n)):
                mapped = {tuple(sorted((p[a], p[b]))) for a, b in template}
                expected = set(e1).isdisjoint(mapped)
                if separated and {p[u] for u in (0, 1, 3, 4)} == {0, 2, 3, 4}:
                    expected = False
                assert s.solve(assumptions=[x[u, p[u]] for u in range(n)]) == expected
                mapping_count += 1
    # Impossible packing of two K4 templates: exact tiny control, no research verdict.
    x, cs = formula(4, list(it.combinations(range(4), 2)), list(it.combinations(range(4), 2)))
    with Solver(name='cadical195', bootstrap_with=cs) as s:
        assert s.solve() is False
    return dict(status='PASS', all_permutations_checked=mapping_count, impossible_K4_pair=True)


def main():
    gate = json.loads((ROOT/'validation/S037/SMOKE.json').read_text())
    assert gate['verdict'] == 'PASS'
    control = controls()
    out = ROOT/'validation/S037/permutation'
    out.mkdir(parents=True, exist_ok=True)
    (out/'CONTROLS.json').write_text(json.dumps(control, indent=2)+'\n', newline='\n')
    rows = []
    for arm in (0, 3, 2, 11):
        source = ROOT/f'validation/S037/pairs/arm-{arm:02d}.json'
        r = run(json.loads(source.read_text())['best'])
        r['source_pair'] = str(source.relative_to(ROOT)).replace('\\', '/')
        (out/f'arm-{arm:02d}.json').write_text(json.dumps(r, indent=2)+'\n', newline='\n')
        rows.append({k: v for k, v in r.items() if k != 'best'})
        print(json.dumps(rows[-1]), flush=True)
        (out/'SUMMARY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
        if r['status'] == 'CHECKED_ALPHA3_PAIR':
            break


if __name__ == '__main__':
    main()
