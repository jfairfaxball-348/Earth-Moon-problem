#!/usr/bin/env python3
"""S025 independent elementary check of a weighted-independence chromatic certificate.

Input JSON with n, best_faces (two face lists) or E1/E2, weights, alpha (=W).
Checks: each layer is a sphere triangulation (s025_check), the union graph G,
every independent set of G has weight <= W (exhaustive, by brute force over all
subsets of size <= W+1 -- weights are >= 1), hence chi(G) >= ceil(w(V)/W)
because each colour class is independent.  No SAT solver is involved.
Usage: s025_weighted_check.py CERT.json
"""
import itertools
import json
import math
import sys

from s025_check import check_triangulation


def max_indep_weight_violations(n, edges, w, W):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    bad = 0
    for size in range(1, W + 2):
        for S in itertools.combinations(range(n), size):
            if sum(w[v] for v in S) <= W:
                continue
            if all(b not in adj[a] for a, b in itertools.combinations(S, 2)):
                # count only minimal violations: removing any vertex fixes the weight
                if all(sum(w[v] for v in S) - w[u] <= W for u in S):
                    bad += 1
    return bad


def main(path):
    rec = json.load(open(path))
    n, W = rec['n'], rec['alpha']
    w = rec.get('weights') or [1] * n
    assert len(w) == n and all(x >= 1 for x in w)
    E = set()
    for fs in rec['best_faces']:
        es, _ = check_triangulation(n, fs)
        E |= set(es)
    bad = max_indep_weight_violations(n, sorted(E), w, W)
    out = {'n': n, 'm_union': len(E), 'W': W, 'total_weight': sum(w),
           'minimal_heavy_independent_sets': bad,
           'chi_lower_bound': math.ceil(sum(w) / W) if bad == 0 else None}
    print(json.dumps(out))
    return out


if __name__ == '__main__':
    main(sys.argv[1])
