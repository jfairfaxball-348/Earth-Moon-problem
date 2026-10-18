#!/usr/bin/env python3
"""S025 independent checker (no import of s025_tricover).

check_triangulation(n, faces): the triangle set is a sphere triangulation on ALL
n labelled vertices: orient faces consistently by BFS over shared edges, build
the combinatorial rotation at each vertex from the oriented faces, trace every
dart exactly once and require V-E+F=2, connectivity, simple edges, and finally a
second test with networkx.check_planarity of the 1-skeleton.
check_split(n, edges, E1, E2): partition, both layers planar (networkx LR test
plus explicit rotation-system face tracing of a returned embedding).
check_colouring(n, edges, col, k): proper, at most k colours.
random_triangulation(n, rng, flips): stacked start + random valid edge flips.
"""
import itertools
import json
import random
import sys

import networkx as nx


def _orient(faces):
    """Return consistently oriented copies of the faces or raise."""
    faces = [tuple(f) for f in faces]
    by_edge = {}
    for k, f in enumerate(faces):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            by_edge.setdefault(frozenset((a, b)), []).append(k)
    for e, ks in by_edge.items():
        if len(ks) != 2:
            raise ValueError(f'edge {sorted(e)} lies in {len(ks)} faces')
    orient = [None] * len(faces)
    for root in range(len(faces)):
        if orient[root] is not None:
            continue
        orient[root] = faces[root]
        stack = [root]
        while stack:
            k = stack.pop()
            a, b, c = orient[k]
            for u, v in ((a, b), (b, c), (c, a)):
                for j in by_edge[frozenset((u, v))]:
                    if j == k:
                        continue
                    f = faces[j]
                    w = next(z for z in f if z not in (u, v))
                    want = (v, u, w)          # neighbour must traverse u-v reversed
                    if orient[j] is None:
                        orient[j] = want
                        stack.append(j)
                    else:
                        darts = {(orient[j][0], orient[j][1]), (orient[j][1], orient[j][2]),
                                 (orient[j][2], orient[j][0])}
                        if (v, u) not in darts:
                            raise ValueError('non-orientable or inconsistent faces')
    return orient


def check_triangulation(n, faces):
    faces = [tuple(sorted(f)) for f in faces]
    assert len(set(faces)) == len(faces), 'repeated face'
    assert all(len(set(f)) == 3 and all(0 <= v < n for v in f) for f in faces)
    assert len(faces) == 2 * n - 4, f'{len(faces)} faces, need {2*n-4}'
    orient = _orient(faces)
    succ = {}                       # rotation: at vertex v, neighbour a -> next neighbour
    for a, b, c in orient:
        for v, p, q in ((a, b, c), (b, c, a), (c, a, b)):
            assert (v, p) not in succ, 'corner repeated'
            succ[v, p] = q
    edges = {frozenset(f[i:i + 2]) for f in orient for i in range(2)} | \
            {frozenset((f[2], f[0])) for f in orient}
    assert len(edges) == 3 * n - 6
    rot = {}
    for v in range(n):
        nbrs = [a for (w, a) in succ if w == v]
        assert len(nbrs) >= 3, f'vertex {v} degree {len(nbrs)}'
        cyc = [nbrs[0]]
        while True:
            nxt = succ[v, cyc[-1]]
            if nxt == cyc[0]:
                break
            cyc.append(nxt)
        assert len(cyc) == len(nbrs), f'vertex {v} link is not one cycle'
        rot[v] = cyc
    # independent face tracing over darts using the rotation only
    nxt_dart = {}
    for v, cyc in rot.items():
        for j, a in enumerate(cyc):
            nxt_dart[(a, v)] = (v, cyc[(j + 1) % len(cyc)])
    seen, nfaces = set(), 0
    for d in nxt_dart:
        if d in seen:
            continue
        nfaces += 1
        length, e = 0, d
        while e not in seen:
            seen.add(e)
            e = nxt_dart[e]
            length += 1
        assert length == 3, 'non-triangular traced face'
    assert len(seen) == 2 * len(edges)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(tuple(e) for e in edges)
    assert nx.is_connected(g)
    assert n - len(edges) + nfaces == 2, 'Euler characteristic is not 2'
    assert nx.check_planarity(g)[0]
    return sorted(tuple(sorted(e)) for e in edges), rot


def planar_rotation_check(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    ok, emb = nx.check_planarity(g)
    if not ok:
        return False
    emb.check_structure()
    # Euler per component on the returned rotation system
    seen = set()
    faces = 0
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        emb.traverse_face(u, v, mark_half_edges=seen)
        faces += 1
    nontrivial = [c for c in nx.connected_components(g) if len(c) > 1]
    nv = sum(len(c) for c in nontrivial)
    # Euler's formula V - E + F = 2 on each component that has an edge
    return nv - g.number_of_edges() + faces == 2 * len(nontrivial)


def check_split(n, edges, E1, E2):
    edges = {tuple(sorted(e)) for e in edges}
    A = {tuple(sorted(e)) for e in E1}
    B = {tuple(sorted(e)) for e in E2}
    assert not (A & B) and (A | B) == edges, 'not a partition of the input edges'
    assert planar_rotation_check(n, A) and planar_rotation_check(n, B)
    return True


def check_colouring(n, edges, col, k):
    assert len(col) == n and all(0 <= c < k for c in col)
    assert all(col[a] != col[b] for a, b in edges)
    return len(set(col))


def random_triangulation(n, rng, flips=None):
    faces = {(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)}
    for v in range(4, n):
        f = rng.choice(sorted(faces))
        faces.remove(f)
        a, b, c = f
        faces |= {tuple(sorted((a, b, v))), tuple(sorted((a, c, v))), tuple(sorted((b, c, v)))}
    for _ in range(flips if flips is not None else 20 * n):
        by_edge = {}
        for f in faces:
            for e in itertools.combinations(f, 2):
                by_edge.setdefault(e, []).append(f)
        e = rng.choice(sorted(by_edge))
        f1, f2 = by_edge[e]
        c = next(z for z in f1 if z not in e)
        d = next(z for z in f2 if z not in e)
        if tuple(sorted((c, d))) in by_edge:
            continue
        a, b = e
        faces -= {f1, f2}
        faces |= {tuple(sorted((a, c, d))), tuple(sorted((b, c, d)))}
    return sorted(faces)


if __name__ == '__main__':
    rec = json.load(open(sys.argv[1]))
    n = rec['n']
    out = {}
    if 'layers_faces' in rec:
        for i, fs in enumerate(rec['layers_faces']):
            es, _ = check_triangulation(n, fs)
            assert es == sorted(tuple(e) for e in rec['layers_edges'][i])
        out['triangulations'] = 'PASS'
    if 'E1' in rec:
        from pathlib import Path
        edges = [tuple(map(int, l.split()[:2])) for l in Path(rec['input']).read_text().split('\n') if l.split()]
        check_split(n, edges, rec['E1'], rec['E2'])
        out['split'] = 'PASS'
    print(json.dumps(out))
