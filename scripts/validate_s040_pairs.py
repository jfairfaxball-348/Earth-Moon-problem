"""Independent S040 saved-pair planarity, colouring and independence classification."""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_check_pair import check

SOLVER = os.environ.get('EMP_CADICAL', str(ROOT/'artifacts/tmp/S004/cadical.exe'))
CHECKER = os.environ.get('EMP_DRAT_TRIM', str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'))


def colour9(data, cap=300):
    """Pinned CaDiCaL 9-colouring attempt; a model is decoded and checked, UNSAT needs drat-trim."""
    n = data['n']
    es = set(map(tuple, data['E1'])) | set(map(tuple, data['E2']))
    x = {(v, c): 1+v*9+c for v in range(n) for c in range(9)}
    clauses = [[x[v, c] for c in range(9)] for v in range(n)]
    clauses += [[-x[v, a], -x[v, b]] for v in range(n) for a, b in it.combinations(range(9), 2)]
    clauses += [[-x[a, c], -x[b, c]] for a, b in es for c in range(9)]
    clauses += [[x[0, 0]]]
    with tempfile.TemporaryDirectory() as tmp:
        cnf, proof = Path(tmp)/'c.cnf', Path(tmp)/'c.drat'
        cnf.write_text(f'p cnf {9*n} {len(clauses)}\n'+''.join(' '.join(map(str, c))+' 0\n' for c in clauses))
        start = time.time()
        try:
            run = subprocess.run([SOLVER, '--no-binary', str(cnf), str(proof)], capture_output=True, text=True, timeout=cap)
        except subprocess.TimeoutExpired:
            return dict(status='UNKNOWN_NO_NEGATIVE_CERTIFICATE', returncode=None, seconds=time.time()-start, cap_seconds=cap)
        result = dict(returncode=run.returncode, seconds=time.time()-start, cap_seconds=cap,
                      solver_sha256=hashlib.sha256(Path(SOLVER).read_bytes()).hexdigest())
        if run.returncode == 10:
            model = {int(t) for line in run.stdout.splitlines() if line.startswith('v') for t in line.split()[1:]}
            colouring = {v: next(c for c in range(9) if x[v, c] in model) for v in range(n)}
            assert all(colouring[a] != colouring[b] for a, b in es)
            result.update(status='SAT_COLOURING_CHECKED', colouring=colouring)
        elif run.returncode == 20:
            chk = subprocess.run([CHECKER, str(cnf), str(proof)], capture_output=True, text=True)
            result.update(status='UNSAT_DRAT_VERIFIED' if 's VERIFIED' in chk.stdout else 'UNSAT_UNVERIFIED_UNKNOWN',
                          drat_returncode=chk.returncode)
        else:
            result.update(status='UNKNOWN_NO_NEGATIVE_CERTIFICATE')
    return result


def specs():
    out = [(f'validation/S040/neighborhood-{d}.json', ['bests', kind, 'pair']) for d in (156, 155)
           for kind in ('single', 'type0', 'type1', 'type2')]
    out += [(str(p.relative_to(ROOT)).replace('\\', '/'), ['best'])
            for p in sorted((ROOT/'validation/S040/arms').glob('*.json')) if p.name != 'SUMMARY.json']
    return out


def main():
    start = time.process_time()
    core = json.loads((ROOT/'validation/sulanke.json').read_text())
    core_es = [set(map(tuple, core[k])) for k in ('edges_part1', 'edges_part2')]
    rows = []
    for name, pointer in specs():
        path = ROOT/name
        data = json.loads(path.read_text())
        for key in pointer:
            data = data[key]
        result = check(data, data['density'])
        es = set(map(tuple, data['E1'])) | set(map(tuple, data['E2']))
        if result['independent_four_sets'] == 0:
            print('POTENTIAL ALPHA3 WITNESS', name, flush=True)
            result['alpha_exact'] = 3
            result['independent_five_example'] = None
        else:
            first5 = next((vs for vs in it.combinations(range(28), 5) if not any(e in es for e in it.combinations(vs, 2))), None)
            result['alpha_exact'] = 4 if first5 is None else None
            result['independent_five_example'] = first5
        if '/protected-' in name:
            assert all(core_es[i] <= set(map(tuple, data[k])) for i, k in enumerate(('E1', 'E2')))
            result['core_chromatic_lower_bound'] = 9
        if result['proper_coloring_upper_bound'] > 9:
            attempt = colour9(data)
            result['colour9_attempt'] = attempt
            if attempt.get('colouring'):
                result['proper_coloring'] = attempt['colouring']
                result['proper_coloring_upper_bound'] = 1+max(attempt['colouring'].values())
        if result.get('core_chromatic_lower_bound') and result['proper_coloring_upper_bound'] == 9:
            result['chromatic_exact'] = 9
        result.update(path=name, pointer=pointer, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(result)
        print(name, pointer, 'I4', result['independent_four_sets'], 'alpha', result['alpha_exact'],
              'colour upper', result['proper_coloring_upper_bound'], flush=True)
    output = dict(status='PASS', records=len(rows), rows=rows, cpu_seconds=time.process_time()-start,
                  witness_found=any(r['independent_four_sets'] == 0 for r in rows),
                  colour9_attempts=sum('colour9_attempt' in r for r in rows))
    (ROOT/'validation/S040/PAIR_CHECKS.json').write_text(json.dumps(output, indent=2)+'\n', newline='\n')
    print('PAIR CHECKS', output['records'], 'witness', output['witness_found'], 'colour attempts', output['colour9_attempts'])


if __name__ == '__main__':
    main()
