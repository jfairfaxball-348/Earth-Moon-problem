#!/usr/bin/env python3
"""CAM-0003 independent check of a decoded two-layer split.

Usage: check_layers.py EDGEFILE SPLIT.json
Checks: exact edge partition of the input graph; each layer planar by
NetworkX LR; each layer component (>=2 vertices) re-certified as a sphere
rotation by the separate stdlib checker tools/check_rotation.py.
"""
import json
import sys

import networkx as nx

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from biplanar_cnf import read_edges  # noqa: E402
from check_rotation import check  # noqa: E402


def certify_layer(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    ok, emb = nx.check_planarity(g)
    assert ok, "layer not planar"
    faces = 0
    for comp in nx.connected_components(g):
        if len(comp) < 2:
            continue
        order = sorted(comp)
        idx = {v: i for i, v in enumerate(order)}
        sub = [(idx[u], idx[v]) for u, v in edges if u in comp]
        sub = [tuple(sorted(e)) for e in sub]
        rot = {str(idx[v]): [idx[u] for u in emb.neighbors_cw_order(v)] for v in order}
        faces += check(len(order), sub, rot)["faces"]
    return faces


def main(edgefile, splitfile):
    graph = set(map(tuple, read_edges(edgefile)))
    data = json.load(open(splitfile))
    e1 = {tuple(sorted(e)) for e in data["E1"]}
    e2 = {tuple(sorted(e)) for e in data["E2"]}
    assert not (e1 & e2) and (e1 | e2) == graph, "not an exact partition"
    n = data["n"]
    f1, f2 = certify_layer(n, sorted(e1)), certify_layer(n, sorted(e2))
    print(f"PASS n={n} layers={len(e1)}/{len(e2)} component-faces={f1}/{f2}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
