"""Literal local contact controls for the order29 hand proof.

Enumerates small neighborhood graphs independently of the displayed bounds.
No biplanarity, global coverage, or theorem is certified by this script.
"""
from itertools import combinations, product
from pathlib import Path
import json
P=Path(__file__).resolve().parent

def graphs(n):
    pairs=list(combinations(range(n),2))
    for mask in range(1<<len(pairs)):
        yield {e for j,e in enumerate(pairs) if mask>>j&1}

def clique(E,vertices):
    return all(tuple(sorted(e)) in E for e in combinations(vertices,2))

def extend_k9(E,complete_to_p,p):
    return any(clique(E,s) for s in combinations(complete_to_p,9-p))

rows8=[]
for p in range(1,9):
    best=100
    for flags in product((False,True),repeat=3):
        if p==8 and any(flags):continue
        Wsum=sum(8 if f else 9 for f in flags)
        for E in graphs(3):
            if extend_k9(E,[i for i,f in enumerate(flags) if f],p): continue
            best=min(best,Wsum-len(E))
    assert best>14+p
    rows8.append({'p':p,'minimum_removed':best,'maximum_allowed':14+p})

rows7=[]
for p in range(1,8):
    for r in range(3):
        best=100
        for flags in product((False,True),repeat=4-r):
            if p==7 and any(flags):continue
            complete_to_p=list(range(r))+[r+i for i,f in enumerate(flags) if f]
            partial_sum=sum(8 if f else 9 for f in flags)
            for E in graphs(4):
                if r==2 and (0,1) in E:continue  # K7 plus an edge is K9.
                if extend_k9(E,complete_to_p,p):continue
                if r==0: fullsum=0
                elif r==1:fullsum=5
                else:
                    common=sum((0,i) in E and (1,i) in E for i in (2,3))
                    fullsum=12+common # nonadjacent full degrees sum>=26+common.
                best=min(best,fullsum+partial_sum-len(E))
        assert best>18+p
        rows7.append({'p':p,'complete_contacts':r,'minimum_removed':best,
                      'maximum_allowed':18+p})

rows6=[]
for r in range(3):
    best=100; equality=[]
    for E in graphs(5):
        if not clique(E,range(r)):continue
        removed=6*r+9*(5-r)-len(E)
        best=min(best,removed)
        if removed==29:
            equality.append(sorted(map(list,E)))
            assert r==2 and len(E)==10
    assert best==35-3*r
    rows6.append({'complete_contacts':r,'minimum_removed':best,
                  'maximum_allowed':29,'equality_graphs':equality})

result={'status':'PASS','scope':'literal local arithmetic controls, not coverage or planarity',
        'low_K8':rows8,'low_K7':rows7,'two_K6_final':rows6}
(P/'order29_contact_budgets_verified.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'status':'PASS','K8_cases':len(rows8),'K7_cases':len(rows7),
                  'K6_cases':len(rows6),'final_equality_graphs':sum(len(r['equality_graphs']) for r in rows6)}))
