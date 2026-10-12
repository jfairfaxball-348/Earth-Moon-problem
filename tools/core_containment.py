#!/usr/bin/env python3
"""Check that every CAM-0004 survivor B[w] contains one of the cores
J1=K2v(K4+K6+K6), J2=K2v(K5+K5+K6), J3=K3v(K5+K5+K5) as a subgraph.

A core K_a v (K_b + K_c + K_d) sits inside B[w] whenever B has a bag x and
three pairwise non-adjacent bags y1,y2,y3 adjacent to x with w_x>=a and
(w_y1,w_y2,w_y3) dominating (b,c,d) after sorting.
Usage: core_containment.py SURVIVORS.json
"""
import itertools
import json
import sys

import networkx as nx

CORES = {"J1": (2, (4, 6, 6)), "J2": (2, (5, 5, 6)), "J3": (3, (5, 5, 5))}


def contains(g, w):
    for x in g.nodes():
        for ys in itertools.combinations(sorted(g[x]), 3):
            if any(g.has_edge(a, b) for a, b in itertools.combinations(ys, 2)):
                continue
            ws = sorted(w[y] for y in ys)
            for name, (a, bcd) in CORES.items():
                if w[x] >= a and all(p >= q for p, q in zip(ws, bcd)):
                    return name, x, ys
    return None


if __name__ == "__main__":
    rows = json.load(open(sys.argv[1]))["survivors"]
    for s in rows:
        g = nx.from_graph6_bytes(s["g6"].encode())
        hit = contains(g, s["w"])
        print(s["g6"], s["w"], hit)
        assert hit, "survivor without a registered core"
