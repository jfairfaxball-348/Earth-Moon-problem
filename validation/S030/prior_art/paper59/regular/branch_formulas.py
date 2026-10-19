"""Literal units for all three hand-covered universal/K3,3 interfaces.

Pure standard-library formula construction, independent of any solver.
"""
from itertools import combinations
from encode import build

def formula(q):
    assert q in (2,3,4)
    f=build();E=f.edge;start=len(f.clauses)
    # Universal side: A+t is K8 and P+{x1,x2} is K8.
    for a in range(6,13):f.add([E(20,a)])
    for p in range(6):
        for x in (21,22):f.add([E(p,x)])
    f.add([E(21,22)])
    r={14,15,16};i={13,17,18,19};y={23,24,25};s=r|i|y
    for u,v in combinations(sorted(s),2):
        present=not((u in r and v in y)or(u in y and v in r))
        f.add([E(u,v)*(1 if present else -1)])
    for p in range(6):
        chosen=y if p<q else r
        for v in sorted(s):f.add([E(p,v)*(1 if v in chosen else -1)])
    f.counts['universal_K33_branch_units']=len(f.clauses)-start
    return f

