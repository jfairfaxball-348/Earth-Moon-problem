#!/usr/bin/env python3
"""Independently justify extended clauses; legacy checker handles all others.

Does not import the two-branch generator. Its regeneration mode is separate:
it reconstructs the complete formula and requires byte identity.
"""
import itertools as it
import json
from pathlib import Path
import sys
import tempfile

import networkx as nx
from s025_check_minor_cert import main as old_check
from biplanar_cegar import Cegar


def check(edgefile, prefix):
    d = json.loads(Path(prefix+'.lemmas.json').read_text())
    G = nx.Graph(d['edges'])
    adj = {v: set(G[v]) for v in G}
    edges = [tuple(e) for e in d['edges']]
    idx = {e: i+1 for i, e in enumerate(edges)}
    nbase = Cegar(edges).nv
    cv = {frozenset(R): cs for R, cs, trees in d['branch_sets']}
    av = {(q, frozenset(R), j): v for q, R, j, v in d['adjacency_vars']}
    used = {v for cs in cv.values() for v in cs} | set(av.values())
    pv, allowed = {}, set()
    for R0, S0, j, v in d['pair_vars']:
        R, S = frozenset(R0), frozenset(S0)
        assert not R & S and j in (1, 2) and v > nbase and v not in used
        assert (R, S, j) not in pv
        used.add(v)
        pv[R, S, j] = v
        for a, b in it.product(R, S):
            if G.has_edge(a, b):
                x = idx[tuple(sorted((a, b)))]
                allowed.add(frozenset([-x if j == 1 else x, v]))
    for Q0, R0, S0, r, s, j in d['two_models']:
        Q, R, S = map(frozenset, (Q0, R0, S0))
        assert len(Q) == 7 and all(G.has_edge(a, b) for a, b in it.combinations(Q, 2))
        assert not (Q & R or Q & S or R & S) and r in R and s in S and j in (1, 2)
        assert R in cv and S in cv and nx.is_connected(G.subgraph(R)) and nx.is_connected(G.subgraph(S))
        lits = [-cv[R][j-1], -cv[S][j-1]]
        for U, rep in ((R, r), (S, s)):
            for q in Q-adj[rep]:
                assert adj[q] & U
                lits.append(-av[q, U, j])
        if not G.has_edge(r, s):
            assert any(G.has_edge(a, b) for a, b in it.product(R, S))
            lits.append(-pv[R, S, j])
        allowed.add(frozenset(lits))
    # Strip ONLY clauses justified above, and ask the unchanged independent S025
    # checker to validate every remaining clause and auxiliary namespace.
    lines = Path(prefix+'.cnf').read_text().splitlines()
    nv, nc = map(int, lines[0].split()[2:])
    assert nc == len(lines)-1
    assert all(l.split()[-1] == '0' for l in lines[1:])
    assert all(1 <= abs(int(x)) <= nv for l in lines[1:] for x in l.split()[:-1])
    rest = [l for l in lines[1:] if frozenset(map(int, l.split()[:-1])) not in allowed]
    with tempfile.TemporaryDirectory() as td:
        p = str(Path(td)/'legacy')
        Path(p+'.lemmas.json').write_text(json.dumps(d))
        Path(p+'.cnf').write_text(f'p cnf {nv} {len(rest)}\n'+'\n'.join(rest)+'\n',newline='\n')
        old_check(edgefile, p)
    rec = {'verdict': 'ALL_CLAUSES_JUSTIFIED', 'clauses': nc,
           'two_models': len(d['two_models']), 'extended_clauses_checked': nc-len(rest)}
    print(json.dumps(rec))


def regen(edgefile, prefix, out):
    from s026_two_branch import TwoBranch
    from biplanar_cnf import read_edges
    d = json.loads(Path(prefix+'.lemmas.json').read_text())
    c = TwoBranch(read_edges(edgefile))
    generated = c.data()
    for key in generated:
        if key != 'lemmas':
            assert json.loads(json.dumps(generated[key])) == d[key], key
    c.lemmas = [[tuple(e) for e in K] for K in d['lemmas']]
    cls = c.clauses()
    text = f'p cnf {c.nv} {len(cls)}\n'+''.join(' '.join(map(str, cl))+' 0\n' for cl in cls)
    Path(out).write_text(text,newline='\n')
    assert Path(out).read_bytes() == Path(prefix+'.cnf').read_bytes()
    print('BYTE_IDENTICAL')


if __name__ == '__main__':
    if sys.argv[1] == 'regen':
        regen(*sys.argv[2:5])
    else:
        check(*sys.argv[1:3])
