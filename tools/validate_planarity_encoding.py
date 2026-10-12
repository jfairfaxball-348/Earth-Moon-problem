#!/usr/bin/env python3
"""CAM-0003 encoding cross-validation: one-layer Schnyder CNF vs NetworkX LR.

Seeded random graphs n=6..10 with varied densities; the CNF must be SAT
exactly when NetworkX reports planarity.  Also checks that every SAT model
really yields three suitable orders (decoded and re-verified directly).
"""
import itertools
import random
import sys

import networkx as nx
from pysat.solvers import Cadical153

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from biplanar_cnf import Encoder  # noqa: E402


def suitable(enc, model, L=0):
    pos = set(l for l in model if l > 0)
    for (u, v) in enc.edges:
        for w in range(enc.n):
            if w in (u, v):
                continue
            ok = False
            for i in range(3):
                def lt(a, b):
                    lit = enc.below(L, i, a, b)
                    return (lit in pos) if lit > 0 else (-lit not in pos)
                if lt(u, w) and lt(v, w):
                    ok = True
            if not ok:
                return False
    return True


def main():
    rng = random.Random(3)
    counts = {"planar": 0, "nonplanar": 0}
    for t in range(300):
        n = rng.randint(6, 10)
        pairs = list(itertools.combinations(range(n), 2))
        m = rng.randint(n, min(len(pairs), 3 * n))
        edges = sorted(rng.sample(pairs, m))
        if max(max(e) for e in edges) != n - 1:
            edges.append((0, n - 1)) if (0, n - 1) not in edges else None
            edges = sorted(set(edges))
        g = nx.Graph(edges)
        planar = nx.check_planarity(g)[0]
        enc = Encoder(edges, layers=1).build()
        with Cadical153(bootstrap_with=enc.clauses) as s:
            sat = s.solve()
            model = s.get_model() if sat else None
        assert sat == planar, (t, edges)
        if sat:
            assert suitable(enc, model)
        counts["planar" if planar else "nonplanar"] += 1
    print("cross-validation PASS", counts)


if __name__ == "__main__":
    main()
