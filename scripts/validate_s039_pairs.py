"""Independent saved-pair planarity, colouring, core and independence checks."""
import hashlib
import itertools as it
import json
from pathlib import Path
import sys
import time
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_check_pair import check


def colour9(data):
    n = data['n']
    es = set(map(tuple, data['E1'])) | set(map(tuple, data['E2']))
    x = {(v, c): 1+v*9+c for v in range(n) for c in range(9)}
    clauses = [[x[v, c] for c in range(9)] for v in range(n)]
    clauses += [[-x[v, a], -x[v, b]] for v in range(n) for a, b in it.combinations(range(9), 2)]
    clauses += [[-x[a, c], -x[b, c]] for a, b in es for c in range(9)]
    start = time.process_time()
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        solver.conf_budget(5000)
        sat = solver.solve_limited()
        stats = solver.accum_stats()
        colouring = None
        if sat:
            model = set(solver.get_model())
            colouring = {v: next(c for c in range(9) if x[v, c] in model) for v in range(n)}
            assert all(colouring[a] != colouring[b] for a, b in es)
    return dict(status='SAT_COLOURING_CHECKED' if colouring else 'UNKNOWN_NO_NEGATIVE_CERTIFICATE',
                colouring=colouring, stats=stats, cpu_seconds=time.process_time()-start)


if __name__ == '__main__':
    start = time.process_time()
    specs = [(str(p.relative_to(ROOT)).replace('\\', '/'), ['best'])
             for folder in ('arms', 'protected') for p in sorted((ROOT/f'validation/S039/{folder}').glob('*.json'))
             if p.name != 'SUMMARY.json']
    specs += [(f'validation/S039/neighborhood-{d}.json', ['best', 'pair']) for d in (156, 155)]
    specs += [(f'validation/S039/seeds/{number}.json', pointer) for number in (3910, 3911, 3912, 3913)
              for pointer in (['pair'], ['variant'])]
    core = json.loads((ROOT/'validation/sulanke.json').read_text())
    core_es = [set(map(tuple, core[k])) for k in ('edges_part1', 'edges_part2')]
    rows = []
    for name, pointer in specs:
        path = ROOT/name
        source = json.loads(path.read_text())
        data = source
        for key in pointer:
            data = data[key]
        density = len(data['E1'])+len(data['E2'])
        result = check(data, density if density in (155, 156) else None)
        es = set(map(tuple, data['E1'])) | set(map(tuple, data['E2']))
        assert result['independent_four_sets'] > 0, 'Potential alpha3 witness: preserve and validate immediately'
        first5 = next((vs for vs in it.combinations(range(28), 5) if not any(e in es for e in it.combinations(vs, 2))), None)
        result['alpha_exact'] = 4 if first5 is None else None
        result['independent_five_example'] = first5
        protected = name.startswith(('validation/S039/seeds/', 'validation/S039/protected/'))
        if protected:
            assert all(core_es[i] <= set(map(tuple, data[k])) for i, k in enumerate(('E1', 'E2')))
            result['core_chromatic_lower_bound'] = 9
        if result['proper_coloring_upper_bound'] > 9:
            attempt = colour9(data)
            result['colour9_attempt'] = attempt
            if attempt['colouring']:
                result['proper_coloring'] = attempt['colouring']
                result['proper_coloring_upper_bound'] = 1+max(attempt['colouring'].values())
        if protected and result['proper_coloring_upper_bound'] == 9:
            result['chromatic_exact'] = 9
        result.update(path=name, pointer=pointer, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(result)
        print(name, pointer, 'I4', result['independent_four_sets'], 'alpha', result['alpha_exact'],
              'colour upper', result['proper_coloring_upper_bound'], 'core lower', result.get('core_chromatic_lower_bound'), flush=True)
    output = dict(status='PASS', records=len(rows), rows=rows, cpu_seconds=time.process_time()-start,
                  witness_found=False, colour9_attempts=sum('colour9_attempt' in r for r in rows))
    (ROOT/'validation/S039/PAIR_CHECKS.json').write_text(json.dumps(output, indent=2)+'\n', newline='\n')
