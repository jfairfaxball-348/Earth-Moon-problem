"""Standard-library necessary CNF for the regular zero-(5,6,6) case.

The implementation is independent of the exploratory PySAT/CardEnc builder.
Every counter is a forward prefix lower-bound recurrence, with a final cap.
No solver, graph library, discovery verdict, or side-shape assumption is used.
"""
from pathlib import Path
from itertools import combinations
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
N=28
PARTS=[list(range(6)),list(range(6,13)),list(range(13,20))]
TYPES={(0,1):list(range(20,23)),(0,2):list(range(23,26)),(1,2):[26,27]}

class Formula:
    def __init__(self):
        self.ev={e:i+1 for i,e in enumerate(combinations(range(N),2))}
        self.top=len(self.ev);self.clauses=[];self.counts={}
    def var(self):self.top+=1;return self.top
    def edge(self,u,v):return self.ev[tuple(sorted((u,v)))]
    def add(self,c):self.clauses.append(list(c))
    def cap(self,lits,bound,guard=()):
        # If the first i inputs contain at least j true literals, s[i,j]
        # must be true. Nothing requires an arbitrary s to be minimal.
        # Set each s to its actual threshold value for the converse.
        prev={}
        for i,x in enumerate(lits,1):
            cur={j:self.var() for j in range(1,min(i,bound+1)+1)}
            self.add([-x,cur[1]])
            for j in cur:
                if j in prev:self.add([-prev[j],cur[j]])
                if j>1:self.add([-x,-prev[j-1],cur[j]])
            prev=cur
        if bound+1 in prev:self.add(list(guard)+[-prev[bound+1]])
    def stage(self,name,before):self.counts[name]=len(self.clauses)-before

def build():
    f=Formula();E=f.edge
    old=len(f.clauses)
    for part in PARTS:
        for u,v in combinations(part,2):f.add([E(u,v)])
    for i,part in enumerate(PARTS):
        r=part[0];neighbors=set(part)-{r}
        for ij,vs in TYPES.items():
            if i in ij:neighbors.update(vs)
        assert len(neighbors)==11
        for v in range(N):
            if v!=r:f.add([E(r,v)*(1 if v in neighbors else -1)])
    f.stage('private_cliques_and_root_types',old)
    old=len(f.clauses)
    for v in range(N):
        inc=[E(v,w) for w in range(N) if w!=v]
        f.cap(inc,11);f.cap([-x for x in inc],16)
    f.stage('degree_exactly_eleven',old)
    old=len(f.clauses)
    for vs in combinations(range(N),4):f.add([E(u,v) for u,v in combinations(vs,2)])
    f.stage('no_independent_four_set',old)
    old=len(f.clauses)
    for u,v in combinations(range(N),2):
        common=[]
        for w in range(N):
            if w in (u,v):continue
            c=f.var();common.append(c)
            f.add([-c,E(u,w)]);f.add([-c,E(v,w)])
            f.add([c,-E(u,w),-E(v,w)])
        # E(u,v) guards only the bound; the prefix implications are always
        # satisfiable and do not impose a cap on adjacent pairs.
        f.cap(common,4,[E(u,v)])
    f.stage('nonedge_common_neighbor_cap_four',old)
    old=len(f.clauses)
    for part in PARTS:
        rest=sorted(set(range(N))-set(part))
        for extra in combinations(rest,9-len(part)):
            nine=part+list(extra)
            f.add([-E(u,v) for u,v in combinations(nine,2)])
    f.stage('K9_extensions_of_private_cliques',old)
    return f

def main():
    f=build();path=HERE/'regular566.cnf'
    with path.open('w') as out:
        out.write(f'p cnf {f.top} {len(f.clauses)}\n')
        for c in f.clauses:out.write(' '.join(map(str,c))+' 0\n')
    meta={'n':N,'parts':PARTS,'pair_types':[[list(k),v] for k,v in TYPES.items()],
          'variables':f.top,'clauses':len(f.clauses),'clause_families':f.counts,
          'bytes':path.stat().st_size,'sha256':sha256(path.read_bytes()).hexdigest(),
          'scope':'necessary abstract regular zero-(5,6,6) conditions; no planar or solver premise'}
    (HERE/'formula.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)
if __name__=='__main__':main()
