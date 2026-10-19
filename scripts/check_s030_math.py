"""Independent S030 semantic controls and external RUP step replay.

No imported external propagator/checker. No claim that RUP implies coverage
of the full regular graph stratum.
"""
import hashlib
import importlib.util
import itertools as it
import json
from pathlib import Path
import sys
import time

from pysat.solvers import Solver

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s030_op1b import encode


def naive_rup(clauses, clause):
    values={}
    for x in clause:
        v=abs(x); b=x<0
        if v in values and values[v]!=b:
            return True
        values[v]=b
    while True:
        changed=False
        for c in clauses:
            if any(abs(x) in values and values[abs(x)]==(x>0) for x in c):
                continue
            unset=[x for x in c if abs(x) not in values]
            if not unset:
                return True
            if len(unset)==1:
                x=unset[0]; values[abs(x)]=x>0; changed=True
        if not changed:
            return False


def main():
    out=ROOT/'artifacts/tmp/S030'
    assert json.loads((out/'SMOKE.json').read_text())['verdict']=='PASS'
    start=time.monotonic(); tested=0
    for degree in range(4):
        f,g,ls=encode(4,degree,0,6)
        with Solver(name='cadical195',bootstrap_with=f) as s:
            for labels in it.product(range(3),repeat=6):
                es={e for (e,x),k in zip(g.items(),labels) if k}
                deg=[sum(v in e for e in es) for v in range(4)]
                expected=bool(es) and min(deg)>=degree and deg[0]==degree and labels[0]!=2
                ass=[]
                for (e,x),k in zip(g.items(),labels):
                    ass += [x if k else -x, ls[0][e] if k==1 else -ls[0][e],
                            ls[1][e] if k==2 else -ls[1][e]]
                assert s.solve(assumptions=ass)==expected,(degree,labels)
                tested+=1
    # External encoder is read and hashed separately; this replays each literal
    # RUP step using a different, simple fixed-point scan implementation.
    supplement=out/'sources/supplement/regular'
    sys.path.insert(0,str(supplement))
    from branch_formulas import formula
    packet=json.loads((supplement/'regular566_rup.json').read_text())
    replay=[]
    for row in packet['branches']:
        f=formula(row['q']); cs=[f.clauses[i] for i in row['core_clause_indices']]
        assert len(f.clauses)==row['input_clauses'] and f.top==row['variables']
        for step,c in enumerate(row['rup_additions']):
            assert naive_rup(cs,c),(row['q'],step)
            cs.append(c)
        assert row['rup_additions'][-1]==[]
        replay.append({'q':row['q'],'steps':len(row['rup_additions']),'verified':True})
    result={'status':'PASS','exhaustive_n4_partition_controls':tested,
            'independent_rup':replay,'seconds':round(time.monotonic()-start,3),
            'regular_stratum':'NOT_PROMOTED; hand coverage not independently verified'}
    (out/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
