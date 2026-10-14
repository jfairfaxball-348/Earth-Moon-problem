#!/usr/bin/env python3
"""CAM-0005 I: second necessary face-incidence CNF, independently numbered.

Direct face-cardinality clauses, totalizer edge counters, no symmetry or
excess identity. Uses the input cut list only after independent syntax checks.
Usage: independent_cover_cnf.py EDGEFILE CUTS.json OUTPUT.cnf
"""
import itertools
import json
import sys
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from biplanar_cnf import read_edges


def encode(edges, cuts):
    n=max(max(e) for e in edges)+1
    assert n>=4
    pairs=list(itertools.combinations(range(n),2))
    triples=list(itertools.combinations(range(n),3))
    # Alternate edge and face blocks by layer, unlike the first generator.
    stride=len(pairs)+len(triples)
    edge_ids={(layer,e):1+layer*stride+j for layer in range(2) for j,e in enumerate(pairs)}
    face_ids={(layer,f):1+layer*stride+len(pairs)+j for layer in range(2) for j,f in enumerate(triples)}
    pool=IDPool(start_from=2*stride+1)
    E=lambda i,u,v:edge_ids[i,tuple(sorted((u,v)))]
    F=lambda i,a,b,c:face_ids[i,tuple(sorted((a,b,c)))]
    cls=[]
    for i in range(2):
        for a,b,c in triples:
            fv=F(i,a,b,c)
            cls.extend([[-fv,E(i,u,v)] for u,v in itertools.combinations((a,b,c),2)])
        for a,b in pairs:
            ev=E(i,a,b)
            fs=[F(i,a,b,c) for c in range(n) if c!=a and c!=b]
            # At least two: if fewer than two are true, omit the unique
            # true variable (or any variable if zero) to falsify one clause.
            for omitted in range(len(fs)):
                cls.append([-ev]+[fv for j,fv in enumerate(fs) if j!=omitted])
            cls.extend([[-a,-b,-c] for a,b,c in itertools.combinations(fs,3)])
        cls.extend(CardEnc.equals(lits=[E(i,a,b) for a,b in pairs],bound=3*n-6,
                   vpool=pool,encoding=EncType.totalizer).clauses)
        for v in range(n):
            cls.append([E(i,u,v) for u in range(n) if u!=v])
    cls.extend([[E(0,a,b),E(1,a,b)] for a,b in edges])
    for cut in cuts:
        assert cut['layer'] in (0,1)
        layer=cut['layer']
        if cut['kind']=='connected':
            vertices=cut['X']
            X=frozenset(vertices)
            assert len(X)==len(vertices) and X and X!=frozenset(range(n))
            assert X<=frozenset(range(n))
            cls.append([E(layer,a,b) for a,b in pairs if (a in X)!=(b in X)])
        else:
            assert cut['kind']=='link'
            v,w,cycle=cut['v'],cut['w'],cut['cycle']
            assert len(cycle)>=3 and len(set(cycle))==len(cycle)
            assert set(cycle)<=set(range(n)) and v in range(n) and w in range(n)
            assert v!=w and v not in cycle and w not in cycle
            clause=[-F(layer,v,cycle[j],cycle[(j+1)%len(cycle)]) for j in range(len(cycle))]
            cls.append(clause+[-E(layer,v,w)])
    return pool.top,cls


def main(edgefile,cutfile,output):
    nv,cls=encode(read_edges(edgefile),json.loads(Path(cutfile).read_text())['cuts'])
    Path(output).write_text(f'p cnf {nv} {len(cls)}\n'+
        ''.join(' '.join(map(str,c))+' 0\n' for c in cls),newline='\n')
    print(nv,'variables',len(cls),'clauses')


if __name__=='__main__':
    main(*sys.argv[1:4])
