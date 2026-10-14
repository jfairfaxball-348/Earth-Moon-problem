#!/usr/bin/env python3
"""CAM-0006: no-lex direct-incidence CEGAR with checked planar obstructions.

Uses S004's separately numbered direct clauses/totalizers. New separation and
cut translation do not use Cover. Nonplanar SAT models are never witnesses.
"""
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx
from pysat.solvers import Cadical153
from biplanar_cegar import is_kuratowski_subdivision
from biplanar_cnf import read_edges
from check_layers import certify_layer
from independent_cover_cnf import encode
from s004_certify import write_cnf


class Independent:
    def __init__(self, edges, cuts=()):
        self.input = sorted(edges)
        self.n = max(max(e) for e in edges)+1
        self.pairs = list(itertools.combinations(range(self.n),2))
        self.triples = list(itertools.combinations(range(self.n),3))
        stride = len(self.pairs)+len(self.triples)
        self.e = {(i,q):1+i*stride+j for i in range(2) for j,q in enumerate(self.pairs)}
        self.f = {(i,q):1+i*stride+len(self.pairs)+j for i in range(2) for j,q in enumerate(self.triples)}
        self.nv,self.base = encode(edges, [])
        self.cuts = list(cuts)
        self.seen = {json.dumps(c,sort_keys=True) for c in self.cuts}
        self.initial = len(self.cuts)
        for c in self.cuts:
            self.clause(c)

    def E(self,i,a,b):
        return self.e[i,tuple(sorted((a,b)))]

    def F(self,i,a,b,c):
        return self.f[i,tuple(sorted((a,b,c)))]

    def clause(self,c):
        i = c['layer']
        assert type(i) is int and i in (0,1)
        if c['kind']=='connected':
            X=set(c['X'])
            assert len(X)==len(c['X']) and 0<len(X)<self.n
            assert all(type(v) is int and v in range(self.n) for v in X)
            return [self.E(i,a,b) for a,b in self.pairs if (a in X)!=(b in X)]
        if c['kind']=='link':
            v,w,cycle=c['v'],c['w'],c['cycle']
            assert type(v) is int and type(w) is int and v in range(self.n) and w in range(self.n)
            assert v!=w and len(cycle)>=3 and len(cycle)==len(set(cycle))
            assert v not in cycle and w not in cycle
            assert all(type(a) is int and a in range(self.n) for a in cycle)
            return [-self.F(i,v,a,b) for a,b in zip(cycle,cycle[1:]+cycle[:1])]+[-self.E(i,v,w)]
        assert c['kind']=='kuratowski'
        edges=[tuple(e) for e in c['edges']]
        assert all(type(a) is int and type(b) is int and 0<=a<b<self.n for a,b in edges)
        assert len(edges)==len(set(edges)) and is_kuratowski_subdivision(edges)
        return [-self.E(i,a,b) for a,b in edges]

    def cnf(self,path):
        write_cnf(Path(path),self.nv,self.base+[self.clause(c) for c in self.cuts])

    def save(self,prefix,verdict,iterations,start):
        meta={'verdict':verdict,'iterations':iterations,'seconds':time.monotonic()-start,
              'initial_cuts':self.initial,'cuts':len(self.cuts),'variables':self.nv,
              'clauses':len(self.base)+len(self.cuts)}
        Path(prefix+'.cuts.json').write_text(json.dumps({'encoding':'independent-direct-no-lex-v1',
            'cuts':self.cuts},indent=1),newline='\n')
        Path(prefix+'.result.json').write_text(json.dumps(meta,indent=1),newline='\n')
        if verdict=='UNSAT':
            self.cnf(prefix+'.cnf')
        return meta

    def run(self,prefix,seconds):
        start=time.monotonic()
        it=0
        with Cadical153(bootstrap_with=self.base+[self.clause(c) for c in self.cuts]) as s:
            while time.monotonic()-start<seconds:
                it+=1
                if not s.solve():
                    return self.save(prefix,'UNSAT',it,start)
                model={x for x in s.get_model() if x>0}
                layers=[]
                pending=[]
                for i in (0,1):
                    le=[q for q in self.pairs if self.E(i,*q) in model]
                    layers.append(le)
                    g=nx.empty_graph(self.n)
                    g.add_edges_from(le)
                    for comp in nx.connected_components(g):
                        if len(comp)<self.n:
                            pending.append({'kind':'connected','layer':i,'X':sorted(comp)})
                    fs=[q for q in self.triples if self.F(i,*q) in model]
                    for v in range(self.n):
                        link=nx.Graph()
                        link.add_nodes_from(g[v])
                        link.add_edges_from([tuple(a for a in q if a!=v) for q in fs if v in q])
                        assert all(d==2 for _,d in link.degree())
                        components=list(nx.connected_components(link))
                        if len(components)>1:
                            for comp in components:
                                # A connected 2-regular simple graph is one cycle.
                                ordered=[min(comp)]
                                prev=None
                                while True:
                                    choices=sorted(a for a in link[ordered[-1]] if a!=prev)
                                    nxt=choices[0]
                                    if nxt==ordered[0]:
                                        break
                                    prev=ordered[-1]
                                    ordered.append(nxt)
                                assert set(ordered)==comp
                                for w in sorted(set(g[v])-comp):
                                    pending.append({'kind':'link','layer':i,'v':v,'w':w,'cycle':ordered})
                    ok,cert=nx.check_planarity(g,counterexample=True)
                    if not ok:
                        ke=sorted(tuple(sorted(e)) for e in cert.edges())
                        assert is_kuratowski_subdivision(ke)
                        pending.append({'kind':'kuratowski','layer':i,'edges':ke})
                if not pending:
                    for le in layers:
                        certify_layer(self.n,le)
                    e1=sorted(set(self.input)&set(layers[0]))
                    e2=sorted(set(self.input)-set(e1))
                    for le in (e1,e2):
                        certify_layer(self.n,le)
                    Path(prefix+'.split.json').write_text(json.dumps({'n':self.n,'E1':e1,'E2':e2}),newline='\n')
                    return self.save(prefix,'SAT_CHECKED',it,start)
                for c in pending:
                    clause=self.clause(c)
                    assert all((-x in model if x<0 else x not in model) for x in clause)
                    key=json.dumps(c,sort_keys=True)
                    if key not in self.seen:
                        self.seen.add(key)
                        self.cuts.append(c)
                        s.add_clause(clause)
                self.save(prefix,'RUNNING',it,start)
        return self.save(prefix,'UNKNOWN',it,start)


def main():
    if sys.argv[1]=='check':
        edgefile,prefix=sys.argv[2:4]
        data=json.loads(Path(prefix+'.cuts.json').read_text())
        c=Independent(read_edges(edgefile),data['cuts'])
        c.cnf(prefix+'.regenerated.cnf')
        assert Path(prefix+'.cnf').read_bytes()==Path(prefix+'.regenerated.cnf').read_bytes()
        print('independent CNF/cut structure PASS',len(c.cuts))
    else:
        edgefile,prefix,seconds,*args=sys.argv[1:]
        cuts=json.loads(Path(args[0]).read_text())['cuts'] if args else []
        print(json.dumps(Independent(read_edges(edgefile),cuts).run(prefix,float(seconds))))


if __name__=='__main__':
    main()
