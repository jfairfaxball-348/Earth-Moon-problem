#!/usr/bin/env python3
"""S025 CAM-0027 arm A: anneal pairs of sphere triangulations towards alpha(T0 u T1) <= ALPHA.

Objective: number of independent sets of total weight >= ALPHA+1 in the union graph,
where the first K "anchor" vertices weigh 2 and all others 1 (K=0: plain independent
(ALPHA+1)-sets).  Objective 0 means every colour class has weight <= ALPHA, hence
chi >= ceil((n+K)/ALPHA); with n+K > 9*ALPHA this is chi >= 10 -- an elementary,
SAT-free lower-bound certificate, re-checked by brute force before any report.
Moves: an edge flip inside one layer (keeps a simplicial sphere triangulation), or
relabelling layer 1 by a transposition.  Layers are rebuilt from face sets for checking.
Usage: s025_indep_anneal.py N ALPHA SEED SECONDS OUT.json [K]
"""
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path


def stacked(n, rng):
    faces = {(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)}
    for v in range(4, n):
        f = rng.choice(sorted(faces))
        faces.remove(f)
        a, b, c = f
        faces |= {tuple(sorted((a, b, v))), tuple(sorted((a, c, v))), tuple(sorted((b, c, v)))}
    return faces


class Layer:
    def __init__(self, n, faces):
        self.n = n
        self.faces = set(faces)
        self.edge_faces = {}
        for f in self.faces:
            for e in itertools.combinations(f, 2):
                self.edge_faces.setdefault(e, set()).add(f)

    def edges(self):
        return list(self.edge_faces)

    def flip_candidate(self, e):
        f1, f2 = self.edge_faces[e]
        c = next(z for z in f1 if z not in e)
        d = next(z for z in f2 if z not in e)
        cd = (c, d) if c < d else (d, c)
        if cd in self.edge_faces:
            return None
        a, b = e
        # keep every vertex degree >= 3 (a and b each lose one edge)
        return cd, (f1, f2), (tuple(sorted((a, c, d))), tuple(sorted((b, c, d))))

    def apply(self, e, cd, old, new):
        for f in old:
            self.faces.remove(f)
            for x in itertools.combinations(f, 2):
                self.edge_faces[x].discard(f)
        del self.edge_faces[e]
        for f in new:
            self.faces.add(f)
            for x in itertools.combinations(f, 2):
                self.edge_faces.setdefault(x, set()).add(f)


class State:
    def __init__(self, n, alpha, rng, weights=None):
        self.n, self.alpha, self.rng = n, alpha, rng
        self.w = list(weights) if weights else [1] * n
        self.L = [Layer(n, stacked(n, rng)), Layer(n, stacked(n, rng))]
        perm = list(range(n))
        rng.shuffle(perm)
        self.L[1] = Layer(n, {tuple(sorted(perm[v] for v in f)) for f in self.L[1].faces})
        self.mult = {}
        for L in self.L:
            for e in L.edge_faces:
                self.mult[e] = self.mult.get(e, 0) + 1
        self.full = (1 << n) - 1
        self.adj = [0] * n
        for (a, b), k in self.mult.items():
            if k:
                self.adj[a] |= 1 << b
                self.adj[b] |= 1 << a
        self.score = self.count_all()

    def nonadj(self, v):
        return self.full & ~self.adj[v] & ~(1 << v)

    def bad(self, mask, need, left):
        """independent T within mask, |T| <= left, weight(T) >= need (subsets in increasing order)."""
        total = 1 if need <= 0 else 0
        if left == 0:
            return total
        while mask:
            v = (mask & -mask).bit_length() - 1
            mask &= mask - 1
            total += self.bad(mask & self.nonadj(v), need - self.w[v], left - 1)
        return total

    def count_all(self):
        return self.bad(self.full, self.alpha + 1, self.alpha + 1)

    def pair_count(self, a, b):
        """bad independent sets containing both a and b (a,b nonadjacent)."""
        return self.bad(self.nonadj(a) & self.nonadj(b) & ~(1 << a) & ~(1 << b),
                        self.alpha + 1 - self.w[a] - self.w[b], self.alpha - 1)

    def set_edge(self, a, b, present):
        if present:
            self.adj[a] |= 1 << b
            self.adj[b] |= 1 << a
        else:
            self.adj[a] &= ~(1 << b)
            self.adj[b] &= ~(1 << a)

    def exact_delta(self, i, e, cd):
        a, b = e
        c, d = cd
        lose = self.mult[e] == 1
        gain = self.mult.get(cd, 0) == 0
        if lose and gain and len({a, b, c, d}) == 4:
            # G' = G - ab + cd.  new - old = P_ab(G') - P_cd(G) where P_xy(H) counts
            # independent sets of H containing x,y (with xy a nonedge of H).
            self.set_edge(a, b, False)
            self.set_edge(c, d, True)
            new_ab = self.pair_count(a, b)
            self.set_edge(c, d, False)
            self.set_edge(a, b, True)
            old_cd = self.pair_count(c, d)
            return new_ab - old_cd, lose, gain
        if gain:
            return -self.pair_count(c, d), lose, gain
        if lose:
            self.set_edge(a, b, False)
            v = self.pair_count(a, b)
            self.set_edge(a, b, True)
            return v, lose, gain
        return 0, lose, gain

    def do_flip(self, i, e, cd, old, new, lose, gain):
        self.L[i].apply(e, cd, old, new)
        self.mult[e] -= 1
        if self.mult[e] == 0:
            del self.mult[e]
            self.set_edge(*e, False)
        self.mult[cd] = self.mult.get(cd, 0) + 1
        if self.mult[cd] == 1:
            self.set_edge(*cd, True)

    def union_edges(self):
        return sorted(self.mult)


def anneal(n, alpha, seed, seconds, t0=2.0, t1=0.05, weights=None):
    rng = random.Random(seed)
    st = State(n, alpha, rng, weights)
    best = (st.score, [sorted(L.faces) for L in st.L])
    start = time.monotonic()
    moves = acc = 0
    while True:
        el = time.monotonic() - start
        if el > seconds or st.score == 0:
            break
        T = t0 * (t1 / t0) ** (el / seconds)
        i = rng.randrange(2)
        L = st.L[i]
        e = rng.choice(L.edges()) if moves % 64 == 0 or not hasattr(L, '_cache') else rng.choice(L._cache)
        if moves % 64 == 0:
            L._cache = L.edges()
        if e not in L.edge_faces:
            moves += 1
            continue
        cand = L.flip_candidate(e)
        moves += 1
        if cand is None:
            continue
        cd, old, new = cand
        delta, lose, gain = st.exact_delta(i, e, cd)
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            st.do_flip(i, e, cd, old, new, lose, gain)
            st.score += delta
            acc += 1
            if st.score < best[0]:
                best = (st.score, [sorted(L.faces) for L in st.L])
    # independent recount of the best state
    check = State.__new__(State)
    check.n, check.alpha, check.full = n, alpha, (1 << n) - 1
    check.w = st.w
    check.adj = [0] * n
    for fs in best[1]:
        for f in fs:
            for a, b in itertools.combinations(f, 2):
                check.adj[a] |= 1 << b
                check.adj[b] |= 1 << a
    recount = check.count_all()
    assert recount == best[0], (recount, best[0])
    return {'n': n, 'alpha': alpha, 'weights': st.w, 'seed': seed, 'seconds': seconds, 'moves': moves,
            'accepted': acc, 'best_indep_sets': best[0], 'final_score': st.score,
            'best_faces': best[1]}


if __name__ == '__main__':
    n, alpha, seed, secs, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    k = int(sys.argv[6]) if len(sys.argv) > 6 else 0      # number of weight-2 anchors 0..k-1
    res = anneal(n, alpha, seed, secs, weights=[2] * k + [1] * (n - k))
    Path(out).write_text(json.dumps(res))
    print(json.dumps({k: v for k, v in res.items() if k != 'best_faces'}))
