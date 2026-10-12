#!/usr/bin/env python3
"""List induced connected sub-blow-ups of a survivor B[w] (whole bags).

Usage: subblowup_scan.py GRAPH6 w0,..,wk MINBAGS MAXBAGS MAXN
Prints one line per induced connected bag subset: bags, weights, N, graph6 of
the induced base (relabelled 0..), weights in that labelling.
"""
import itertools
import sys

import networkx as nx

g6, ws, lo, hi, maxn = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
w = [int(t) for t in ws.split(",")]
g = nx.from_graph6_bytes(g6.encode())
for r in range(lo, hi + 1):
    for S in itertools.combinations(range(len(w)), r):
        h = g.subgraph(S)
        N = sum(w[i] for i in S)
        if not nx.is_connected(h) or N > maxn:
            continue
        h = nx.convert_node_labels_to_integers(h, ordering="sorted")
        sub = nx.to_graph6_bytes(h, header=False).decode().strip()
        print(" ".join(map(str, S)), sub, ",".join(str(w[i]) for i in S), N)
