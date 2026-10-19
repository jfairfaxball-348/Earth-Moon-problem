"""Exact private-neighborhood count check; topology is proved separately."""
from itertools import product
from itertools import combinations
from pathlib import Path
import json

PAIRS = [(0, 1), (0, 2), (1, 2)]

def profiles(n, degrees, linking=True):
    rows = []
    for private in product(range(8), repeat=3):
        triple = sum(degrees) - 2 * (n - 3) + sum(private)
        if triple < 0:
            continue
        residual = [degrees[i] - private[i] - triple for i in range(3)]
        twice = [residual[i] + residual[j] - residual[3-i-j]
                 for i, j in PAIRS]
        if any(x < 0 or x % 2 for x in twice):
            continue
        doubles = [x // 2 for x in twice]
        if 3 + sum(private) + sum(doubles) + triple != n:
            continue
        if linking and any(private[i] == private[j] == 7 and doubles[k]
                           for k, (i, j) in enumerate(PAIRS)):
            continue
        rows.append({'private': private, 'double_01_02_12': doubles,
                     'triple': triple})
    return rows

def main():
    checks = []
    cases = [(30, (11, 11, 11)), (29, (10, 10, 10)),
             (29, (10, 10, 11)), (29, (10, 11, 11)),
             (29, (10, 10, 12)), (29, (11, 11, 11))]
    for n, degrees in cases:
        rows = profiles(n, degrees)
        checks.append({'n': n, 'degrees': degrees, 'profiles': rows})
    assert all(not checks[i]['profiles'] for i in range(4))
    assert checks[4]['profiles'] == [
        {'private': (7, 7, 6), 'double_01_02_12': [0, 3, 3], 'triple': 0}]
    assert len(checks[5]['profiles']) == 3
    assert all(sorted(r['private']) == [6, 6, 7] and r['triple'] == 0
               for r in checks[5]['profiles'])
    raw = profiles(30, (11, 11, 11), linking=False)
    assert raw == [{'private': (7, 7, 7),
                    'double_01_02_12': [2, 2, 2], 'triple': 0}]
    # Independent edge-category count behind the overlap identity:
    # an edge belongs to Z_i iff neither endpoint meets root i.
    groups = [(8, {0}), (7, {1}), (7, {2}),
              (2, {0, 1}), (2, {0, 2}), (3, {1, 2})]
    membership = [s for size, s in groups for _ in range(size)]
    multiplicities = [3-len(membership[u] | membership[v])
                      for u, v in combinations(range(29), 2)]
    assert multiplicities.count(2) == 70
    assert multiplicities.count(0) == 68
    assert multiplicities.count(1) == 268
    result = {'checks': checks, 'positive_control_without_linking': raw,
              'all_406_edge_multiplicities': {
                  'twice_internal_private': 70,
                  'zero_opposite_or_distinct_double': 68, 'once_other': 268},
              'status': 'PASS',
              'scope': 'integer accounting only; no graph realizability claim'}
    path = Path(__file__).with_name('alpha3_private_profiles_verified.json')
    path.write_text(json.dumps(result, indent=2))
    print(json.dumps({'status': result['status'], 'cases': len(cases),
                      'profile_counts': [len(c['profiles']) for c in checks]}))

if __name__ == '__main__':
    main()
