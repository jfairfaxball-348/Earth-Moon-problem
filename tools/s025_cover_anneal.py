#!/usr/bin/env python3
"""S025 CAM-0028 arm B: flip-annealing of two labelled sphere triangulations covering G.

G has thickness <= 2 iff two sphere triangulations T0,T1 on V(G) cover E(G)
(CLM-0087).  State: (T0,T1); objective: number of G-edges in neither layer.
An edge flip ab->cd in one layer changes the objective by at most one in each
direction, in O(1).  Objective 0 yields the split E1 = E(G) n E(T0),
E2 = E(G) - E1, which is independently re-checked by tools/s025_check.py.
Positive-only heuristic: a positive objective at the cap is NEVER evidence of
non-biplanarity.
Usage: s025_cover_anneal.py EDGEFILE SEED SECONDS OUT.json [--start PARTIAL.json]
"""
import argparse
import hashlib
import itertools
import json
import math
import random
import time
from pathlib import Path

import networkx as nx


def stacked(n, rng):
    faces = {(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)}
    for v in range(4, n):
        f = rng.choice(sorted(faces))
        faces.remove(f)
        a, b, c = f
        faces |= {tuple(sorted((a, b, v))), tuple(sorted((a, c, v))), tuple(sorted((b, c, v)))}
    return faces


def complete_to_triangulation(n, edges, rng):
    """Faces of a sphere triangulation containing the planar edge set `edges`."""
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    order = list(itertools.combinations(range(n), 2))
    rng.shuffle(order)
    for a, b in order:
        if not g.has_edge(a, b):
            g.add_edge(a, b)
            if not nx.check_planarity(g)[0]:
                g.remove_edge(a, b)
    assert g.number_of_edges() == 3 * n - 6
    ok, emb = nx.check_planarity(g)
    faces, seen = set(), set()
    for u, v in emb.edges():
        if (u, v) in seen:
            continue
        f = emb.traverse_face(u, v, mark_half_edges=seen)
        assert len(f) == 3
        faces.add(tuple(sorted(f)))
    assert len(faces) == 2 * n - 4
    return faces


class Layer:
    def __init__(self, faces):
        self.faces = set(faces)
        self.ef = {}
        for f in self.faces:
            for e in itertools.combinations(f, 2):
                self.ef.setdefault(e, []).append(f)
        self.elist = list(self.ef)
        self.pos = {e: k for k, e in enumerate(self.elist)}

    def flip(self, e):
        f1, f2 = self.ef[e]
        c = next(z for z in f1 if z not in e)
        d = next(z for z in f2 if z not in e)
        cd = (c, d) if c < d else (d, c)
        if cd in self.ef:
            return None
        a, b = e
        return cd, (f1, f2), (tuple(sorted((a, c, d))), tuple(sorted((b, c, d))))

    def apply(self, e, cd, old, new):
        for f in old:
            self.faces.remove(f)
            for x in itertools.combinations(f, 2):
                if x != e:
                    self.ef[x].remove(f)
        del self.ef[e]
        k = self.pos.pop(e)
        self.elist[k] = cd
        self.pos[cd] = k
        self.ef[cd] = []
        for f in new:
            self.faces.add(f)
            for x in itertools.combinations(f, 2):
                self.ef[x].append(f)


def anneal(n, gedges, seed, seconds, start=None, t0=1.2, t1=0.08, restart=None):
    rng = random.Random(seed)
    G = set(gedges)
    if start:
        L = [Layer(complete_to_triangulation(n, start[i], rng)) for i in range(2)]
    else:
        L = [Layer(stacked(n, rng)) for _ in range(2)]
        perm = list(range(n))
        rng.shuffle(perm)
        L[1] = Layer({tuple(sorted(perm[v] for v in f)) for f in L[1].faces})
    cov = {e: sum(e in Li.ef for Li in L) for e in G}
    score = sum(1 for e in G if cov[e] == 0)
    best = (score, [sorted(Li.faces) for Li in L])
    t_start = time.monotonic()
    moves = 0
    while score > 0:
        if moves % 4096 == 0:
            el = time.monotonic() - t_start
            if el > seconds:
                break
            T = t0 * (t1 / t0) ** ((el % restart) / restart if restart else el / seconds)
            thr = [math.exp(-1 / T), math.exp(-2 / T)]
        moves += 1
        i = rng.getrandbits(1)
        Li = L[i]
        e = Li.elist[rng.randrange(len(Li.elist))]
        cand = Li.flip(e)
        if cand is None:
            continue
        cd, old, new = cand
        delta = 0
        if e in G and cov[e] == 1:
            delta += 1
        if cd in G and cov[cd] == 0:
            delta -= 1
        if delta <= 0 or rng.random() < thr[delta - 1]:
            Li.apply(e, cd, old, new)
            if e in G:
                cov[e] -= 1
            if cd in G:
                cov[cd] += 1
            score += delta
            if score < best[0]:
                best = (score, [sorted(Lj.faces) for Lj in L])
    return {'seed': seed, 'moves': moves, 'seconds': round(time.monotonic() - t_start, 2),
            'best_uncovered': best[0], 'best_faces': best[1]}


def read_edges(path):
    es = []
    for line in Path(path).read_text().split('\n'):
        p = line.split()
        if len(p) >= 2:
            a, b = int(p[0]), int(p[1])
            es.append((min(a, b), max(a, b)))
    return es


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('edges')
    ap.add_argument('seed', type=int)
    ap.add_argument('seconds', type=float)
    ap.add_argument('out')
    ap.add_argument('--start')
    ap.add_argument('--restart', type=float)
    a = ap.parse_args()
    es = read_edges(a.edges)
    n = max(max(e) for e in es) + 1
    start = None
    if a.start:
        rec = json.loads(Path(a.start).read_text())
        start = [[tuple(e) for e in rec[k]] for k in ('A', 'B')]
    res = anneal(n, es, a.seed, a.seconds, start, restart=a.restart)
    res.update(input=a.edges, n=n, m=len(es),
               input_sha256=hashlib.sha256(Path(a.edges).read_bytes()).hexdigest())
    if res['best_uncovered'] == 0:
        T0 = {e for f in res['best_faces'][0] for e in itertools.combinations(f, 2)}
        res['E1'] = sorted(e for e in es if e in T0)
        res['E2'] = sorted(e for e in es if e not in T0)
        res['layers_faces'] = res['best_faces']
    Path(a.out).write_text(json.dumps(res))
    print(json.dumps({k: v for k, v in res.items() if k not in ('best_faces', 'E1', 'E2', 'layers_faces')}))


if __name__ == '__main__':
    main()
