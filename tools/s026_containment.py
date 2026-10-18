#!/usr/bin/env python3
"""Independent, proof-producing C5-subgraph test on a clique-blow-up target.

X[v,b] assigns each obstruction vertex to a target bag. Exactly-one row,
literal subset capacity clauses, and nonedge incompatibilities are equivalent
to an injective subgraph map. Within each obstruction twin bag the assigned
target bag indices can be sorted, so nondecreasing rows are safe symmetry.
No CardEnc, minor CEGAR or bag-assignment backtracking is imported.
"""
import itertools as it
import json
from pathlib import Path
import sys

import networkx as nx
from pysat.solvers import Solver
from s026_check_source import graph


def encode(data,out):
    w=data['w']; u=list(map(int,data['tag']))
    assert len(u)==5 and sum(u)==17 and all(x>0 for x in w)
    B=nx.from_graph6_bytes(data['g6'].encode()); nb=len(w)
    assert len(B)==nb
    hbag=[i for i,x in enumerate(u) for _ in range(x)]
    H=[(a,b) for a,b in it.combinations(range(17),2)
       if hbag[a]==hbag[b] or (hbag[a]-hbag[b])%5 in (1,4)]
    x=lambda v,b:1+v*nb+b
    clauses=[]
    for v in range(17):
        clauses.append([x(v,b) for b in range(nb)])
        clauses.extend([-x(v,a),-x(v,b)] for a,b in it.combinations(range(nb),2))
    for b,cap in enumerate(w):
        clauses.extend([-x(v,b) for v in S] for S in it.combinations(range(17),cap+1))
    for v,z in H:
        for a,b in it.product(range(nb),repeat=2):
            if a!=b and not B.has_edge(a,b): clauses.append([-x(v,a),-x(z,b)])
    for v in range(16):
        if hbag[v]==hbag[v+1]:
            clauses.extend([-x(v,a),-x(v+1,b)] for a in range(nb) for b in range(a))
    text=f'p cnf {17*nb} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)
    Path(out).write_text(text,newline='\n')
    return clauses,H


def decide(inp,out):
    d=json.loads(Path(inp).read_text()); out=Path(out); out.mkdir(parents=True,exist_ok=True)
    cnf=out/'contain.cnf'; clauses,H=encode(d,cnf); nb=len(d['w'])
    # Equality with the actual certified obstruction's labelled edge file is
    # checked by the audit driver before calling this tool.
    with Solver(name='cadical195',bootstrap_with=clauses) as s:
        s.conf_budget(20000); answer=s.solve_limited()
        if answer is True:
            positive={v for v in s.get_model() if v>0}
            start=[sum(d['w'][:b]) for b in range(nb)]; used=[0]*nb; vm={}
            for v in range(17):
                b=next(b for b in range(nb) if 1+v*nb+b in positive)
                vm[v]=start[b]+used[b]; used[b]+=1
            G=graph(d['g6'],d['w'])
            assert len(set(vm.values()))==17 and all(used[b]<=d['w'][b] for b in range(nb))
            assert all(tuple(sorted((vm[a],vm[b]))) in G for a,b in H)
            result={'verdict':'CONTAINS_EXPLICIT_CHECKED','vertex_map':vm}
        elif answer is False:
            from s025_certify import certify
            proof=certify(cnf,out,10,20)
            result={'verdict':'AVOIDS_DRAT_VERIFIED' if proof['verdict']=='UNSAT_DRAT_VERIFIED' else 'UNKNOWN',
                    'proof':proof}
        else:
            result={'verdict':'UNKNOWN','reason':'20000_conflict_search_cap'}
    (out/'RESULT.json').write_text(json.dumps(result,indent=1))
    print(json.dumps({'verdict':result['verdict']}),flush=True)


if __name__=='__main__':
    if sys.argv[1]=='encode':encode(json.loads(Path(sys.argv[2]).read_text()),sys.argv[3])
    else:decide(sys.argv[2],sys.argv[3])
