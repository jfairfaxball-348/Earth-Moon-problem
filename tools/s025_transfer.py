#!/usr/bin/env python3
"""S025: transfer a certified non-biplanar clique blow-up H[u] into corpus rows B[w].

Subgraphs of biplanar graphs are biplanar, so if H[u] is a SUBGRAPH of B[w] and H[u]
is certified non-biplanar, B[w] is non-biplanar.  Search: assign to each H-bag i a
vector c_i of counts over B-vertices with sum_v c_i(v) = u_i, sum_i c_i(v) <= w_v,
every pair of B-vertices used inside one H-bag equal or adjacent in B, and for every
H-edge ij every pair (v in supp c_i, v' in supp c_j) equal or adjacent in B.
Every found map is expanded to an explicit injective vertex map and EVERY obstruction
edge is checked to be a row edge (independent of the search).
Usage: s025_transfer.py H_GRAPH6 u1,u2,... OUT.json [rows...]
"""
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from blowup_graph import blowup   # noqa: E402


def compositions(total, parts_caps):
    """All count vectors over the given (vertex, cap) list summing to total."""
    if not parts_caps:
        if total == 0:
            yield ()
        return
    (v, cap), rest = parts_caps[0], parts_caps[1:]
    for k in range(min(cap, total), -1, -1):
        for tail in compositions(total - k, rest):
            yield ((v, k),) + tail if k else tail


def find_map(H, u, B, w):
    nb = {v: set(B[v]) | {v} for v in B}
    cliques = [c for c in nx.enumerate_all_cliques(B)]
    order = sorted(range(len(u)), key=lambda i: -u[i])
    assign = {}
    cap = list(w)

    def ok_pair(S, T):
        return all(t in nb[s] for s in S for t in T)

    def rec(k):
        if k == len(order):
            return True
        i = order[k]
        for cl in cliques:
            caps = [(v, cap[v]) for v in cl if cap[v] > 0]
            if sum(c for _, c in caps) < u[i]:
                continue
            for comp in compositions(u[i], caps):
                S = [v for v, _ in comp]
                if set(S) != set(cl):
                    continue          # each support is enumerated once, as its own clique
                if not all(ok_pair(S, [v for v, _ in assign[j]]) for j in H[i] if j in assign):
                    continue
                for v, c in comp:
                    cap[v] -= c
                assign[i] = comp
                if rec(k + 1):
                    return True
                del assign[i]
                for v, c in comp:
                    cap[v] += c
        return False

    return dict(assign) if rec(0) else None


def explicit_check(Hg6, u, Bg6, w, assign):
    H = nx.from_graph6_bytes(Hg6.encode())
    hedges, hbags = blowup(Hg6, u)
    gedges, gbags = blowup(Bg6, w)
    G = set(gedges)
    used = {v: 0 for v in range(len(w))}
    vmap = {}
    for i, comp in assign.items():
        hv = iter(hbags[i])
        for v, c in comp:
            for _ in range(c):
                vmap[next(hv)] = gbags[v][used[v]]
                used[v] += 1
    assert len(vmap) == sum(u) and len(set(vmap.values())) == sum(u)
    for a, b in hedges:
        x, y = sorted((vmap[a], vmap[b]))
        assert (x, y) in G, (a, b, x, y)
    return vmap


def main():
    Hg6, u, outp = sys.argv[1], [int(t) for t in sys.argv[2].split(',')], sys.argv[3]
    corpus = json.loads((ROOT / 'validation/S003/survivors_alpha_ge3.json').read_text())
    rows = [int(r) for r in sys.argv[4:]] or list(range(len(corpus)))
    H = nx.from_graph6_bytes(Hg6.encode())
    Hadj = {i: set(H[i]) for i in H}
    out = []
    for r in rows:
        Bg6, w = corpus[r][0], corpus[r][1]
        B = nx.from_graph6_bytes(Bg6.encode())
        a = find_map(Hadj, u, B, w)
        rec = {'row': r, 'contains': a is not None}
        if a is not None:
            vmap = explicit_check(Hg6, u, Bg6, w, a)
            rec['vertex_map'] = {str(k): v for k, v in sorted(vmap.items())}
            rec['bag_map'] = {str(i): comp for i, comp in a.items()}
        out.append(rec)
    Path(outp).write_text(json.dumps({'obstruction': [Hg6, u], 'rows': out}))
    print(sum(r['contains'] for r in out), 'of', len(out), 'rows contain', Hg6, u)


if __name__ == '__main__':
    main()
