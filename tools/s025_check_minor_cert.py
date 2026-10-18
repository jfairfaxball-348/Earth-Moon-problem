#!/usr/bin/env python3
"""S025 independent re-justification of a CAM-0029 minor-CEGAR UNSAT CNF (except DRAT).

Every clause of PREFIX.cnf must be one of:
  * a base clause of tools/biplanar_cegar.Cegar (layer-swap unit, lex-leader clauses for
    automorphisms that Cegar asserts are automorphisms) -- regenerated here;
  * a Kuratowski lemma pair (K is a K5/K3,3 subdivision inside E(G), non-planar);
  * a spanning-tree clause (T a spanning tree of G[R] for a recorded branch set R):
      (OR_{e in T} -x_e) | c[R,1]   or   (OR_{e in T} x_e) | c[R,2];
  * an adjacency implication  (+-x_{qy}) | a[q,R,j]  with y in R, qy in E(G);
  * a Lemma C clause  -c[R,j] | OR_{q in Q - N(r)} -a[q,R,j]  with Q a K8 of G,
    R disjoint from Q, r in R, every such q having a G-neighbour in R;
  * a Lemma B clause  OR_i (-c[R_i,1] | -c[R_i,2])  with |Q| + k = 9, Q a clique,
    R_i pairwise disjoint, disjoint from Q, each dominating Q, pairwise joined.
Auxiliary variables must be fresh (above the base namespace) and pairwise distinct.
The DRAT proof is checked separately by drat-trim (tools/s025_certify.py).
Usage: s025_check_minor_cert.py EDGEFILE PREFIX
"""
import itertools
import json
import sys

import networkx as nx

sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
from biplanar_cegar import Cegar, is_kuratowski_subdivision   # noqa: E402
from biplanar_cnf import read_edges                            # noqa: E402


def main(edgefile, prefix):
    edges = read_edges(edgefile)
    data = json.load(open(prefix + '.lemmas.json'))
    assert [tuple(e) for e in data['edges']] == edges
    G = nx.Graph(edges)
    E = {tuple(sorted(e)) for e in edges}
    adj = {v: set(G[v]) for v in G}
    base = Cegar(edges)
    idx = base.idx
    nbase = base.nv
    allowed = set(frozenset(c) for c in base.base)
    # Kuratowski lemmas
    for k in data['lemmas']:
        k = [tuple(e) for e in k]
        assert set(k) <= E and is_kuratowski_subdivision(sorted(k))
        assert not nx.check_planarity(nx.Graph(k))[0]
        lits = [idx[e] for e in k]
        allowed.add(frozenset(-l for l in lits))
        allowed.add(frozenset(lits))
    # branch sets and their tree clauses
    cvar, used = {}, set()
    for R, (c1, c2), trees in data['branch_sets']:
        R = frozenset(R)
        assert len(R) >= 2 and nx.is_connected(G.subgraph(R))
        for v in (c1, c2):
            assert v > nbase and v not in used
            used.add(v)
        cvar[R] = (c1, c2)
        for T in trees:
            T = [tuple(e) for e in T]
            h = nx.Graph(T)
            assert set(T) <= E and len(T) == len(R) - 1 and set(h) == set(R) and nx.is_connected(h)
            lits = [idx[e] for e in T]
            allowed.add(frozenset([-l for l in lits] + [c1]))
            allowed.add(frozenset(lits + [c2]))
    # adjacency variables
    avar = {}
    for q, R, j, v in data.get('adjacency_vars', []):
        R = frozenset(R)
        assert v > nbase and v not in used and q not in R and j in (1, 2)
        used.add(v)
        avar[q, R, j] = v
        for y in adj[q] & R:
            x = idx[tuple(sorted((q, y)))]
            allowed.add(frozenset([-x if j == 1 else x, v]))
    # Lemma C models
    for Q, R, r, j in data.get('cmodels', []):
        Q, R = frozenset(Q), frozenset(R)
        assert len(Q) == 8 and all(b in adj[a] for a, b in itertools.combinations(Q, 2))
        assert not (Q & R) and r in R
        need = sorted(q for q in Q if r not in adj[q])
        assert need and all(adj[q] & R for q in need)
        allowed.add(frozenset([-cvar[R][j - 1]] + [-avar[q, R, j] for q in need]))
    # Lemma B models
    for Q, Rs in data.get('models', []):
        Q = frozenset(Q)
        Rs = [frozenset(R) for R in Rs]
        assert len(Q) + len(Rs) == 9
        assert all(b in adj[a] for a, b in itertools.combinations(Q, 2))
        for R in Rs:
            assert not (R & Q) and all(adj[q] & R for q in Q)
        for R, S in itertools.combinations(Rs, 2):
            assert not (R & S) and any(adj[x] & S for x in R)
        allowed.add(frozenset(l for R in Rs for l in (-cvar[R][0], -cvar[R][1])))
    # every CNF clause must be justified
    n_cls = 0
    with open(prefix + '.cnf') as f:
        header = f.readline().split()
        assert header[:2] == ['p', 'cnf']
        nv, nc = int(header[2]), int(header[3])
        assert nv >= max([nbase] + list(used))
        for line in f:
            lits = [int(t) for t in line.split()]
            assert lits[-1] == 0
            cl = frozenset(lits[:-1])
            assert cl in allowed, f'unjustified clause {sorted(cl)[:12]}'
            n_cls += 1
    assert n_cls == nc
    out = {'verdict': 'ALL_CLAUSES_JUSTIFIED', 'clauses': nc, 'variables': nv,
           'kuratowski_lemmas': len(data['lemmas']), 'branch_sets': len(cvar),
           'lemmaC_models': len(data.get('cmodels', [])), 'lemmaB_models': len(data.get('models', [])),
           'automorphisms_for_lex': len(base.perms)}
    print(json.dumps(out))
    return out


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
