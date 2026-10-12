#!/usr/bin/env python3
"""Independently re-check a CAM-0003 v4 UNSAT certificate (except DRAT).

Given EDGEFILE, PREFIX.lemmas.json and PREFIX.cnf:
  * every lemma is a subset of E(G) and is non-planar (NetworkX LR) and a
    K5/K3,3 subdivision (structural checker);
  * the CNF is regenerated from scratch (lex-leader clauses for the listed
    permutations recomputed from the graph's closed-twin classes, layer-swap
    unit, two clauses per lemma) and must be byte-identical to PREFIX.cnf.
DRAT checking of PREFIX.cnf is done separately with drat-trim.
"""
import json
import sys

import networkx as nx

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from biplanar_cegar import Cegar, is_kuratowski_subdivision  # noqa: E402
from biplanar_cnf import read_edges  # noqa: E402


def main(edgefile, prefix):
    edges = read_edges(edgefile)
    data = json.load(open(prefix + ".lemmas.json"))
    assert [tuple(e) for e in data["edges"]] == edges
    E = set(edges)
    for k in data["lemmas"]:
        k = [tuple(e) for e in k]
        assert set(k) <= E
        assert not nx.check_planarity(nx.Graph(k))[0]
        assert is_kuratowski_subdivision(k)
    c = Cegar(edges)
    assert c.perms == data["perms"]
    eset = set(edges)
    for p in c.perms:  # independent automorphism re-check
        assert sorted(p) == list(range(len(p)))
        assert all((min(p[u], p[v]), max(p[u], p[v])) in eset for u, v in edges)
    clauses = list(c.base)
    for k in data["lemmas"]:
        lits = [c.idx[tuple(e)] for e in k]
        clauses += [[-l for l in lits], lits]
    text = f"p cnf {c.nv} {len(clauses)}\n" + "".join(" ".join(map(str, cl)) + " 0\n" for cl in clauses)
    assert text == open(prefix + ".cnf").read(), "CNF mismatch"
    print(f"certificate structure PASS: {len(data['lemmas'])} lemmas, CNF regenerated identically")


if __name__ == "__main__":
    main(*sys.argv[1:3])
