"""Independent standard-library check of the three literal RUP refutations.

Rebuild the necessary formulas, select their named input clauses, and check
each addition by direct unit propagation under its negation. Deletions are
unneeded: retaining extra prior RUP consequences cannot invalidate a RUP step.
There is no solver, DRAT implementation, discovery import or online input.
"""
from pathlib import Path
from collections import defaultdict,deque
from hashlib import sha256
import json,time
from branch_formulas import formula
P=Path(__file__).resolve().parent

class Propagator:
    def __init__(self):
        self.clauses=[];self.occs=defaultdict(list);self.units=[];self.empty=False
    def add(self,clause):
        c=tuple(sorted(set(clause)));i=len(self.clauses);self.clauses.append(c)
        if not c:self.empty=True
        if len(c)==1:self.units.append(c[0])
        for v in c:self.occs[v].append(i)
    def contradicts(self,assumptions):
        if self.empty:return True
        values={};queue=deque(self.units+list(assumptions))
        while queue:
            lit=queue.popleft();v=abs(lit);value=1 if lit>0 else -1
            if v in values:
                if values[v]!=value:return True
                continue
            values[v]=value
            for i in self.occs[-lit]:
                unset=[];satisfied=False
                for x in self.clauses[i]:
                    val=values.get(abs(x))
                    if val is None:unset.append(x)
                    elif val==(1 if x>0 else -1):satisfied=True;break
                if satisfied:continue
                if not unset:return True
                if len(unset)==1:queue.append(unset[0])
        return False

def main():
    if not __debug__:
        raise RuntimeError('Run without -O: proof assertions must remain enabled.')
    start=time.monotonic();data=json.loads((P/'regular566_rup.json').read_text())
    assert data['format']=='regular566-rup-v1'
    assert [r['q'] for r in data['branches']]==[2,3,4]
    results=[]
    for row in data['branches']:
        q=row['q'];f=formula(q)
        assert f.top==row['variables'] and len(f.clauses)==row['input_clauses']
        ids=row['core_clause_indices'];assert all(type(i) is int and 0<=i<len(f.clauses) for i in ids)
        p=Propagator()
        for i in ids:p.add(f.clauses[i])
        # No initial core is accepted as contradictory without propagation.
        proof=row['rup_additions'];assert proof and proof[-1]==[]
        for step,clause in enumerate(proof):
            assert all(type(v) is int and 0<abs(v)<=f.top for v in clause)
            assert p.contradicts([-v for v in clause]),(q,step,clause)
            p.add(clause)
        assert p.empty
        results.append({'q':q,'input_clauses':len(f.clauses),'used_input_clauses':len(ids),'RUP_additions':len(proof),'empty_clause_verified':True})
    out={'status':'PASS','branches':results,'seconds':round(time.monotonic()-start,3),
         'packet_bytes':(P/'regular566_rup.json').stat().st_size,'packet_sha256':sha256((P/'regular566_rup.json').read_bytes()).hexdigest(),
         'scope':'all three hand-covered universal/K3,3 interface branches; hand reductions remain separate premises'}
    (P/'rup_verified.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
if __name__=='__main__':main()
