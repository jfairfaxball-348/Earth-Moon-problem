#!/usr/bin/env python3
"""S025 CAM-0029: Kuratowski CEGAR strengthened by cross-layer K9-minor lemmas.

Lemma B (CLM-0090).  Let (L1, L2) be a biplanar decomposition of G, Q a clique of G,
R_1..R_k pairwise disjoint vertex sets disjoint from Q with |Q| + k = 9, every R_i
dominating Q (each q in Q has a G-neighbour in R_i) and every pair R_i, R_j joined by a
G-edge.  Then some L_j[R_i] is disconnected.  (Otherwise contract every R_i in both
layers: each layer stays planar and the union contains K9, which has thickness 3.)

Encoding (x_e true = layer 1, as in tools/biplanar_cegar.py): for each branch set R two
auxiliary variables c[R,1], c[R,2] with, for every listed spanning tree T of G[R],
   (OR_{e in T} -x_e) | c[R,1]        (T inside layer 1 => c[R,1])
   (OR_{e in T}  x_e) | c[R,2]        (T inside layer 2 => c[R,2])
and for each minor model  OR_i (-c[R_i,1] | -c[R_i,2]).  In any biplanar split the
assignment c[R,j] := [L_j[R] connected] satisfies all of these clauses, so an UNSAT
verdict (after DRAT checking) certifies non-biplanarity given K9 non-biplanarity.
The model families are closed under Aut(G) and the layer swap, so the inherited
lex-leader symmetry breaking stays sound.
Lemma C (CLM-0091, one-layer contraction).  Let Q be a K8 of G, R a vertex set disjoint
from Q with a representative r in R, and j a layer.  If L_j[R] is connected and every
q in Q - N_G(r) has an L_j-neighbour in R, then G is not biplanar: contract R in L_j,
delete R - {r} in the other layer; every q in Q n N_G(r) is joined to the R-node in
L_j or to r in the other layer, so the union contains K9.  Encoded with c[R,j] as
above and a[q,R,j] <= (q y in L_j) for y in R:   -c[R,j] | OR_q -a[q,R,j].
Usage: s025_minor_cegar.py EDGEFILE OUTPREFIX SECONDS [--rmax 5] [--k2] [--k3] [--lemmaC R]
"""
import itertools
import json
import sys
import time

import networkx as nx
from pysat.solvers import Solver

sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
from biplanar_cegar import Cegar          # noqa: E402
from biplanar_cnf import read_edges       # noqa: E402


class MinorCegar(Cegar):
    def __init__(self, edges, rmax=5, k2=False, k3=False, tree_cap=2000, cmax=0, kB=True):
        super().__init__(edges)
        self.G = nx.Graph(edges)
        self.n = self.G.number_of_nodes()
        self.adj = {v: set(self.G[v]) for v in self.G}
        self.cvar = {}            # frozenset R -> (c1, c2)
        self.trees = {}           # frozenset R -> list of spanning trees (edge lists)
        self.models = []          # (Q, [R...]) lists
        self.minor_clauses = []
        self.rmax, self.tree_cap = rmax, tree_cap
        self.avar = {}
        self.cmodels = []
        if kB:
            self.build(k2, k3)
        if cmax:
            self.build_c(cmax)

    def edge(self, a, b):
        return (a, b) if a < b else (b, a)

    def connected_sets(self, pool, smax):
        """connected (in G) subsets of `pool` of size 2..smax, as frozensets."""
        pool = set(pool)
        out = set()
        for v in pool:
            frontier = [frozenset([v])]
            seen = set(frontier)
            while frontier:
                nxt = []
                for S in frontier:
                    if len(S) >= 2:
                        out.add(S)
                    if len(S) == smax:
                        continue
                    for u in set().union(*(self.adj[x] for x in S)) & pool:
                        if u not in S and u > v:   # v is the minimum element
                            T = S | {u}
                            if T not in seen:
                                seen.add(T)
                                nxt.append(T)
                frontier = nxt
        return out

    def spanning_trees(self, R):
        g = self.G.subgraph(R)
        es = [self.edge(*e) for e in g.edges()]
        k = len(R) - 1
        trees = []
        for T in itertools.combinations(es, k):
            h = nx.Graph(T)
            if h.number_of_nodes() == len(R) and nx.is_connected(h):
                trees.append(list(T))
                if len(trees) >= self.tree_cap:
                    break
        return trees

    def cv(self, R):
        if R not in self.cvar:
            self.nv += 1
            c1 = self.nv
            self.nv += 1
            c2 = self.nv
            self.cvar[R] = (c1, c2)
            self.trees[R] = self.spanning_trees(R)
            for T in self.trees[R]:
                lits = [self.idx[e] for e in T]
                self.minor_clauses.append([-l for l in lits] + [c1])
                self.minor_clauses.append(lits + [c2])
        return self.cvar[R]

    def dominates(self, R, Q):
        return all(self.adj[q] & R for q in Q)

    def joined(self, R, S):
        return any(self.adj[x] & S for x in R)

    def add_model(self, Q, Rs):
        lits = []
        for R in Rs:
            c1, c2 = self.cv(R)
            lits += [-c1, -c2]
        self.models.append((sorted(Q), [sorted(R) for R in Rs]))
        self.minor_clauses.append(lits)

    def build(self, k2, k3):
        cliques = [frozenset(c) for c in nx.enumerate_all_cliques(self.G) if len(c) in (8, 7, 6)]
        V = set(self.G)
        for Q in cliques:
            if len(Q) == 8:
                for R in self.connected_sets(V - Q, self.rmax):
                    if self.dominates(R, Q):
                        self.add_model(Q, [R])
            if len(Q) == 7 and k2:
                sets = [R for R in self.connected_sets(V - Q, self.rmax) if self.dominates(R, Q)]
                for R, S in itertools.combinations(sets, 2):
                    if not (R & S) and self.joined(R, S):
                        self.add_model(Q, [R, S])
            if len(Q) == 6 and k3:
                sets = [R for R in self.connected_sets(V - Q, min(self.rmax, 3)) if self.dominates(R, Q)]
                for R, S, U in itertools.combinations(sets, 3):
                    if not (R & S or R & U or S & U) and self.joined(R, S) and \
                            self.joined(R, U) and self.joined(S, U):
                        self.add_model(Q, [R, S, U])

    def av(self, q, R, j):
        key = (q, R, j)
        if key not in self.avar:
            self.nv += 1
            self.avar[key] = self.nv
            for y in sorted(self.adj[q] & R):
                x = self.idx[self.edge(q, y)]
                self.minor_clauses.append([-x if j == 1 else x, self.nv])
        return self.avar[key]

    def build_c(self, cmax):
        V = set(self.G)
        for Q in (frozenset(c) for c in nx.enumerate_all_cliques(self.G) if len(c) == 8):
            for R in self.connected_sets(V - Q, cmax):
                for r in sorted(R):
                    need = sorted(q for q in Q if r not in self.adj[q])
                    if not need or not all(self.adj[q] & R for q in need):
                        continue
                    c1, c2 = self.cv(R)
                    for j, cj in ((1, c1), (2, c2)):
                        self.minor_clauses.append([-cj] + [-self.av(q, R, j) for q in need])
                        self.cmodels.append((sorted(Q), sorted(R), r, j))

    def run(self, timeout, solver_name='cadical195'):
        start = time.time()
        with Solver(name=solver_name, bootstrap_with=self.base + self.minor_clauses) as s:
            it = 0
            while True:
                it += 1
                if time.time() - start > timeout:
                    return 'UNKNOWN', it
                if not s.solve():
                    return 'UNSAT', it
                m = set(l for l in s.get_model() if l > 0)
                l1 = [e for e in self.edges if self.idx[e] in m]
                l2 = [e for e in self.edges if self.idx[e] not in m]
                added = self.lemmas_from(l1, s, 12) + self.lemmas_from(l2, s, 12)
                if added == 0:
                    self.split = (l1, l2)
                    return 'SAT', it

    def clauses(self):
        cls = list(self.base) + list(self.minor_clauses)
        for k in self.lemmas:
            lits = [self.idx[e] for e in k]
            cls += [[-l for l in lits], lits]
        return cls


def main():
    edgefile, prefix, timeout = sys.argv[1], sys.argv[2], float(sys.argv[3])
    flags = sys.argv[4:]
    rmax = int(flags[flags.index('--rmax') + 1]) if '--rmax' in flags else 5
    cmax = int(flags[flags.index('--lemmaC') + 1]) if '--lemmaC' in flags else 0
    edges = read_edges(edgefile)
    t0 = time.time()
    c = MinorCegar(edges, rmax=rmax, k2='--k2' in flags, k3='--k3' in flags, cmax=cmax,
                   kB='--noB' not in flags)
    build = time.time() - t0
    verdict, it = c.run(timeout)
    info = {'verdict': verdict, 'iterations': it, 'kuratowski_lemmas': len(c.lemmas),
            'minor_models': len(c.models), 'lemmaC_models': len(c.cmodels), 'branch_sets': len(c.cvar),
            'minor_clauses': len(c.minor_clauses), 'build_seconds': round(build, 1),
            'seconds': round(time.time() - t0, 1), 'symmetries': len(c.perms), 'rmax': rmax,
            'k2': '--k2' in flags, 'k3': '--k3' in flags}
    n = 1 + max(max(e) for e in edges)
    if verdict == 'SAT':
        json.dump({'n': n, 'E1': c.split[0], 'E2': c.split[1]}, open(prefix + '.split.json', 'w'))
    if verdict == 'UNSAT':
        cls = c.clauses()
        with open(prefix + '.cnf', 'w', newline='\n') as f:
            f.write(f'p cnf {c.nv} {len(cls)}\n')
            f.write(''.join(' '.join(map(str, cl)) + ' 0\n' for cl in cls))
        json.dump({'edges': edges, 'lemmas': c.lemmas, 'perms': c.perms,
                   'branch_sets': [[sorted(R), list(c.cvar[R]), c.trees[R]] for R in c.cvar],
                   'models': c.models, 'cmodels': c.cmodels,
                   'adjacency_vars': [[q, sorted(R), j, v] for (q, R, j), v in c.avar.items()],
                   'flags': flags}, open(prefix + '.lemmas.json', 'w'))
    json.dump(info, open(prefix + '.result.json', 'w'))
    print(json.dumps(info))


if __name__ == '__main__':
    main()
