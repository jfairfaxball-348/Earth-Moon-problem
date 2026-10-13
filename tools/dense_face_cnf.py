#!/usr/bin/env python3
"""CAM-0006 E: small independently reduced necessary CNFs for D=0 inputs.

No automorphisms, no completion edges, no link cuts. A SAT model is only a
relaxation. global_only forgets face layer consistency deliberately.
"""
import itertools
import sys
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from biplanar_cnf import read_edges
from s004_certify import write_cnf


def encode(edges,global_only=False):
    edges=sorted(edges)
    n=1+max(max(e) for e in edges)
    assert n>=4 and len(edges)==len(set(edges))==6*n-12
    eset=set(edges)
    triangles=[q for q in itertools.combinations(range(n),3)
               if all(e in eset for e in itertools.combinations(q,2))]
    pool=IDPool()
    f={q:pool.id(('face',q)) for q in triangles}
    x={} if global_only else {e:pool.id(('layer',e)) for e in edges}
    cls=[]
    for e in edges:
        incident=[f[q] for q in triangles if e[0] in q and e[1] in q]
        if len(incident)<2:
            cls.append([])
        else:
            cls.extend(CardEnc.equals(incident,bound=2,vpool=pool,
                       encoding=EncType.seqcounter).clauses)
    if not global_only:
        for q in triangles:
            a,b,c=[x[e] for e in itertools.combinations(q,2)]
            for other in (b,c):
                cls.extend([[-f[q],-a,other],[-f[q],a,-other]])
        cls.extend(CardEnc.equals(list(x.values()),bound=3*n-6,vpool=pool,
                   encoding=EncType.totalizer).clauses)
    return pool.top,cls,f,x


if __name__=='__main__':
    _,edgefile,output,*args=sys.argv
    nv,cls,_,_=encode(read_edges(edgefile),'--global' in args)
    write_cnf(Path(output),nv,cls)
    print(nv,len(cls))
