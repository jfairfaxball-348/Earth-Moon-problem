#!/usr/bin/env python3
"""CAM-0006 F: one-surplus-pair global facial cover, necessary for D=1."""
import itertools
from pysat.card import CardEnc,EncType
from pysat.formula import IDPool


def encode(edges):
    edges=sorted(edges)
    n=1+max(max(e) for e in edges)
    assert n>=4 and len(edges)==len(set(edges))==6*n-13
    eset=set(edges)
    pairs=list(itertools.combinations(range(n),2))
    pool=IDPool()
    extra={e:pool.id(('extra',e)) for e in pairs}
    triangles=[q for q in itertools.combinations(range(n),3)
               if sum(e not in eset for e in itertools.combinations(q,2))<=1]
    f={q:pool.id(('face',q)) for q in triangles}
    cls=CardEnc.equals(list(extra.values()),bound=1,vpool=pool,encoding=EncType.seqcounter).clauses
    for q in triangles:
        for e in itertools.combinations(q,2):
            if e not in eset:
                cls.append([-f[q],extra[e]])
    for e in pairs:
        incident=[f[q] for q in triangles if e[0] in q and e[1] in q]
        if e in eset:
            cases=((2,extra[e]),(4,-extra[e]))
        else:
            # False extra forces every incident face false via implications.
            cases=((2,-extra[e]),)
        for demand,gate_false in cases:
            if len(incident)<demand:
                cls.append([gate_false])
            else:
                enc=CardEnc.equals(incident,bound=demand,vpool=pool,encoding=EncType.seqcounter)
                cls.extend([gate_false]+c for c in enc.clauses)
    return pool.top,cls,f,extra
