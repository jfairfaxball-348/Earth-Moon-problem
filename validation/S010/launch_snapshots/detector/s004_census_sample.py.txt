#!/usr/bin/env python3
"""CAM-0005 independent chunked enumeration of two fixed 8-vertex bases.

Plain 8^8 enumeration, no DFS or symmetry pruning. Different weighted
colouring recursion (memoised independent-set covers) and triangle-free
branching from the S003 independent checker. Also run the main census on
the same graph6 input; compare counts and isomorphic labelled survivors.
"""
import functools
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np
from blowup_census_check import tri_free_ok


def audit(g6):
    start = time.monotonic()
    g = nx.from_graph6_bytes(g6.encode())
    k = len(g)
    assert k == 8
    cliques = list(nx.find_cliques(g))
    mis = [tuple(c) for c in nx.find_cliques(nx.complement(g))]

    @functools.lru_cache(maxsize=500000)
    def colourable(w, left):
        if max(w) <= 0:
            return True
        if left <= 0 or max(w) > left or sum(w) > left*max(map(len, mis)):
            return False
        if any(sum(w[i] for i in c) > left for c in cliques):
            return False
        i = max(range(k), key=lambda j: w[j])
        return any(colourable(tuple(max(0, w[j]-(j in c)) for j in range(k)), left-1)
                   for c in mis if i in c)

    stats = {'g6': g6, 'vectors': 0, 'kept': 0, 'colourable': 0, 'F3': 0, 'survivors': []}
    for lo in range(0, 8**k, 65536):
        a = np.arange(lo, min(lo+65536, 8**k), dtype=np.int64)
        W = np.stack([(a // (8**(k-1-i))) % 8 + 1 for i in range(k)], axis=1)
        stats['vectors'] += len(W)
        keep = np.ones(len(W), dtype=bool)
        for c in cliques:
            keep &= W[:, c].sum(axis=1) <= 8
        for v in range(k):
            keep &= W[:, [v]+list(g[v])].sum(axis=1) >= 10
        W = W[keep]
        for mask in range(1, 1 << k):
            if not len(W):
                break
            S = [i for i in range(k) if mask >> i & 1]
            n = W[:, S].sum(axis=1)
            e = (W[:, S]*(W[:, S]-1)//2).sum(axis=1)
            for x, y in g.subgraph(S).edges():
                e += W[:, x]*W[:, y]
            W = W[(n < 3) | (e <= 6*n-12)]
        stats['kept'] += len(W)
        for w in W.tolist():
            if colourable(tuple(w), 9):
                stats['colourable'] += 1
            elif not tri_free_ok(g, w):
                stats['F3'] += 1
            else:
                stats['survivors'].append(w)
        assert time.monotonic()-start < 1800, 'registered sample wall cap'
    assert stats['vectors'] == 8**8
    stats['seconds'] = time.monotonic()-start
    return stats


def main():
    results = []
    for part in (0, 1):
        old = json.loads(Path(f'validation/S003/census_k8_part{part}.json').read_text())['survivors']
        g6 = next(r['g6'] for r in old if
                  max(map(len, nx.find_cliques(nx.complement(nx.from_graph6_bytes(r['g6'].encode()))))) >= 3)
        print('sample', part, g6, flush=True)
        result = audit(g6)
        mainfile = f'validation/S004/census_sample_main{part}.json'
        run = subprocess.run([sys.executable, 'tools/blowup_census.py', mainfile],
                             input=g6+'\n', text=True, capture_output=True, timeout=1800)
        assert run.returncode == 0, run.stderr
        main = json.loads(Path(mainfile).read_text())
        counts = main['stats']
        assert result['kept'] == counts['COL']+counts['F3']+counts['SURV']
        assert result['colourable'] == counts['COL'] and result['F3'] == counts['F3']
        assert len(result['survivors']) == counts['SURV']
        # Compare via every isomorphism, because the main census relabels.
        def same_row(row, w):
            h = nx.from_graph6_bytes(row['g6'].encode())
            a = nx.from_graph6_bytes(g6.encode())
            nx.set_node_attributes(a, dict(enumerate(w)), 'weight')
            nx.set_node_attributes(h, dict(enumerate(row['w'])), 'weight')
            return nx.is_isomorphic(a, h, node_match=lambda x, y: x['weight'] == y['weight'])
        assert all(any(same_row(r, w) for r in main['survivors']) for w in result['survivors'])
        inherited = [r for r in old if r['g6'] == g6]
        assert sorted(result['survivors']) == sorted(r['w'] for r in inherited)
        result['main_counts_match'] = True
        result['inherited_rows_match'] = True
        results.append(result)
        Path('validation/S004/census_samples.json').write_text(json.dumps(results, indent=1))
        print('sample PASS', {x:y for x,y in result.items() if x != 'survivors'}, flush=True)


if __name__ == '__main__':
    main()
