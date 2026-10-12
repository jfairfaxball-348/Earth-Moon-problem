#!/usr/bin/env python3
"""CAM-0004 independent cross-check (different method from blowup_census.py).

For each connected true-twin-free base (graph6 on stdin) it materialises ALL
weight vectors in {1..8}^k with numpy, keeps those that pass
  (a) every clique of B has weight <= 8           (F1, cliques via NetworkX)
  (b) every bag has closed weighted degree >= 10  (10-core)
  (c) every bag subset X with |X|>=3 has e(X) <= 6|X|-12   (F2)
and for each kept vector decides 9-colourability by a separate exact search
over multisets of maximal independent sets (NetworkX find_cliques on the
complement), then applies the triangle-free cross-edge filter only to the
non-9-colourable ones.  Prints per-k totals: kept, colourable, F3, survivors.
The kept total must equal COL+F3+SURV of the main census.

Usage: geng -c K | blowup_census_check.py
"""
import itertools
import json
import sys

import networkx as nx
import numpy as np

WMAX, K = 8, 9


def parse_g6(line):
    g = nx.from_graph6_bytes(line.strip().encode())
    return g


def true_twins(g):
    return any(set(g[u]) | {u} == set(g[v]) | {v} for u, v in g.edges())


def colourable(g, w):
    """Exact: can the bags be covered by <=9 independent sets, bag i >= w_i times."""
    comp = nx.complement(g)
    mis = [frozenset(c) for c in nx.find_cliques(comp)]
    need = dict(enumerate(w))

    def rec(left, need):
        open_bags = [i for i in need if need[i] > 0]
        if not open_bags:
            return True
        if left == 0:
            return False
        i = max(open_bags, key=lambda b: (need[b], -b))
        if need[i] > left:
            return False
        for s in mis:
            if i in s:
                new = {b: (need[b] - 1 if b in s else need[b]) for b in need}
                if rec(left - 1, new):
                    return True
        return False
    return rec(K, need)


def max_tf(edges, w):
    """Max weight triangle-free edge subset by branching on a triangle's edges."""
    h = nx.Graph(edges)
    for a, b in h.edges():
        common = set(h[a]) & set(h[b])
        if common:
            c = min(common)
            best = 0
            for drop in ((a, b), (a, c), (b, c)):
                rest = [e for e in edges if set(e) != set(drop)]
                best = max(best, max_tf(rest, w))
            return best
    return sum(w[a] * w[b] for a, b in edges)


def tri_free_ok(g, w):
    nodes = list(g.nodes())
    for r in range(1, len(nodes) + 1):
        for S in itertools.combinations(nodes, r):
            N = sum(w[i] for i in S)
            if N >= 3 and max_tf(list(g.subgraph(S).edges()), w) > 4 * N - 8:
                return False
    return True


def main():
    tot = {"bases": 0, "kept": 0, "colourable": 0, "F3": 0, "survivors": []}
    for line in sys.stdin:
        if not line.strip() or line.startswith(">"):
            continue
        g = parse_g6(line)
        if true_twins(g):
            continue
        tot["bases"] += 1
        k = g.number_of_nodes()
        W = np.array(list(itertools.product(range(1, WMAX + 1), repeat=k)), dtype=np.int16)
        keep = np.ones(len(W), dtype=bool)
        for c in nx.enumerate_all_cliques(g):
            keep &= W[:, c].sum(axis=1) <= WMAX
        for v in range(k):
            keep &= W[:, [v] + list(g[v])].sum(axis=1) >= K + 1
        W = W[keep]
        for r in range(1, k + 1):
            for S in itertools.combinations(range(k), r):
                S = list(S)
                N = W[:, S].sum(axis=1)
                e = (W[:, S] * (W[:, S] - 1) // 2).sum(axis=1)
                for a, b in g.subgraph(S).edges():
                    e = e + W[:, a] * W[:, b]
                W = W[~((N >= 3) & (e > 6 * N - 12))]
        tot["kept"] += len(W)
        for w in W.tolist():
            if colourable(g, w):
                tot["colourable"] += 1
            elif not tri_free_ok(g, w):
                tot["F3"] += 1
            else:
                tot["survivors"].append([line.strip(), w])
    print(json.dumps(tot))


if __name__ == "__main__":
    main()
