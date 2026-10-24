"""S041 probe P1: every order-13 layer-symmetric 156-edge biplanar pair at order28.

Vertices N=0, S=1, a_i=2+i, b_i=15+i (i in Z13); sigma: a_i->a_{i+1}, b_i->b_{i+1}.
A layer is a union of six sigma-orbits of pairs. Pair lemma: each layer of a valid
pair has exactly one of NA/NB and one of SA/SB. Every candidate is certified planar
(rotation) or nonplanar (failed necessary triangulation test or Kuratowski subdivision).
"""
import itertools as it
import json
from pathlib import Path
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import rotation, subdivision

N, S = 0, 1
A = [2+i for i in range(13)]
B = [15+i for i in range(13)]


def sigma(v):
    if v < 2:
        return v
    return 2+(v-2+1) % 13 if v < 15 else 15+(v-15+1) % 13


def orbits():
    orb = {'NA': [(N, a) for a in A], 'NB': [(N, b) for b in B], 'SA': [(S, a) for a in A], 'SB': [(S, b) for b in B]}
    for d in range(1, 7):
        orb[f'AA{d}'] = sorted(tuple(sorted((A[i], A[(i+d) % 13]))) for i in range(13))
        orb[f'BB{d}'] = sorted(tuple(sorted((B[i], B[(i+d) % 13]))) for i in range(13))
    for t in range(13):
        orb[f'AB{t}'] = [(A[i], B[(i+t) % 13]) for i in range(13)]
    pairs = [e for o in orb.values() for e in o]
    assert len(pairs) == len(set(pairs)) == 377 and set(pairs) == set(it.combinations(range(28), 2))-{(N, S)}
    for o in orb.values():
        assert {tuple(sorted((sigma(a), sigma(b)))) for a, b in o} == set(o) and len(o) == 13
    return orb


def t_tests(edges):
    """Necessary conditions for a 78-edge simple planar graph (a triangulation) on 28 vertices."""
    adj = {v: set() for v in range(28)}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    for v in range(28):
        if len(adj[v]) < 3:
            return dict(test='T1', vertex=v)
    for a, b in edges:
        if len(adj[a] & adj[b]) < 2:
            return dict(test='T2', edge=[a, b])
    for v in range(28):
        nb = adj[v]
        sub = {u: adj[u] & nb for u in nb}
        low = next((u for u in sorted(nb) if len(sub[u]) < 2), None)
        if low is not None:
            return dict(test='T3_degree', vertex=v, neighbour=low)
        start = min(nb)
        seen, todo = {start}, [start]
        while todo:
            u = todo.pop()
            for w in sub[u]:
                if w not in seen:
                    seen.add(w); todo.append(w)
        if seen != nb:
            return dict(test='T3_connected', vertex=v, component=sorted(seen))
    return None


def classify(names, orb):
    edges = sorted(e for n in names for e in orb[n])
    assert len(edges) == 78
    cert = t_tests(edges)
    if cert:
        return dict(orbits=list(names), planar=False, certificate=cert)
    g = nx.Graph(); g.add_nodes_from(range(28)); g.add_edges_from(edges)
    planar, emb = nx.check_planarity(g)
    if planar:
        rot = {v: list(ws) for v, ws in emb.get_data().items()}
        faces = rotation(28, edges, rot)
        assert len(faces) == 52 and all(len(f) == 3 for f in faces)
        return dict(orbits=list(names), planar=True, rotation=rot)
    _, sub = nx.check_planarity(g, counterexample=True)
    kedges = sorted(tuple(sorted(e)) for e in sub.edges())
    kind = subdivision(kedges)
    assert set(kedges) <= set(edges)
    return dict(orbits=list(names), planar=False, certificate=dict(test='KURATOWSKI', kind=kind, edges=kedges))


def layers(orb):
    rest = [n for n in orb if n[:2] in ('AA', 'BB', 'AB')]
    assert len(rest) == 25
    for x in ('NA', 'NB'):
        for y in ('SA', 'SB'):
            for four in it.combinations(rest, 4):
                yield (x, y)+four


def independent_four(edges, through=(N, S, A[0], B[0])):
    adj = [0]*28
    for a, b in edges:
        adj[a] |= 1 << b; adj[b] |= 1 << a
    full = (1 << 28)-1
    non = [full & ~adj[v] & ~(1 << v) for v in range(28)]

    def bits(m):
        while m:
            low = m & -m
            yield low.bit_length()-1
            m ^= low
    for v in through:
        for u in bits(non[v]):
            for w in bits(non[v] & non[u] & ~((1 << (u+1))-1)):
                rest = non[v] & non[u] & non[w] & ~((1 << (w+1))-1)
                if rest:
                    return [v, u, w, (rest & -rest).bit_length()-1]
    return None


def count_four(edges):
    adj = [0]*28
    for a, b in edges:
        adj[a] |= 1 << b; adj[b] |= 1 << a
    full = (1 << 28)-1
    non = [full & ~adj[v] & ~(1 << v) for v in range(28)]
    total = 0
    for v in range(28):
        m1 = non[v] & ~((1 << (v+1))-1)
        while m1:
            u = (m1 & -m1).bit_length()-1; m1 &= m1-1
            m2 = non[v] & non[u] & ~((1 << (u+1))-1)
            while m2:
                w = (m2 & -m2).bit_length()-1; m2 &= m2-1
                total += (non[v] & non[u] & non[w] & ~((1 << (w+1))-1)).bit_count()
    return total
