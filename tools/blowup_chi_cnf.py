#!/usr/bin/env python3
"""CNFs whose unsatisfiability certifies chi(B[w]) >= K+1 (default K=9).

  bag    : x[c][i] = colour c is used on bag i; adjacent bags share no
           colour; each bag i gets at least w_i colours (sequential counter).
           B[w] is K-colourable iff this CNF is satisfiable (choose w_i
           distinct colours from the set of bag i).
  vertex : plain K-colouring CNF of the explicit graph from
           tools/blowup_graph.py; one maximum clique is precoloured
           0,1,... (sound by colour permutation).
Usage: blowup_chi_cnf.py bag|vertex GRAPH6 w0,w1,... OUT.cnf [K]
"""
import itertools
import sys

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from blowup_graph import blowup  # noqa: E402


def bag_cnf(g6, w, K):
    g = nx.from_graph6_bytes(g6.encode())
    pool = IDPool()
    x = {(c, i): pool.id(("x", c, i)) for c in range(K) for i in range(len(w))}
    cls = [[-x[c, i], -x[c, j]] for c in range(K) for i, j in g.edges()]
    for i in range(len(w)):
        cls += CardEnc.atleast([x[c, i] for c in range(K)], bound=w[i], vpool=pool,
                               encoding=EncType.seqcounter).clauses
    return pool.top, cls


def vertex_cnf(g6, w, K):
    edges, bag = blowup(g6, w)
    n = sum(w)
    G = nx.Graph(edges)
    var = lambda v, c: v * K + c + 1
    cls = [[var(v, c) for c in range(K)] for v in range(n)]
    cls += [[-var(u, c), -var(v, c)] for u, v in edges for c in range(K)]
    clique = max(nx.find_cliques(G), key=len)
    cls += [[var(v, c)] for c, v in enumerate(sorted(clique))]
    return n * K, cls


if __name__ == "__main__":
    mode, g6, ws, out = sys.argv[1:5]
    K = int(sys.argv[5]) if len(sys.argv) > 5 else 9
    w = [int(t) for t in ws.split(",")]
    nv, cls = (bag_cnf if mode == "bag" else vertex_cnf)(g6, w, K)
    with open(out, "w") as f:
        f.write(f"p cnf {nv} {len(cls)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in cls))
    print(f"{mode} vars={nv} clauses={len(cls)}")
