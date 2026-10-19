"""Independent finite arithmetic controls for the hand delta11 exclusion.

No coverage or planarity claim. Uses explicit C5 blow-ups and local integer
identities; does not import the research producer or a graph package.
"""
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import json

out = Path(__file__).resolve().parent
forms = []
for a,b in product(range(2,7), repeat=2):
    if a+b>8 or min(a,b)!=2:
        continue
    sizes = [8-a,7-b,a,2,b]
    bags=[]; nxt=0
    for s in sizes:
        bags.append(list(range(nxt,nxt+s))); nxt+=s
    edges=set()
    for i in range(5):
        for u in bags[i]:
            for v in bags[(i+1)%5]:
                edges.add(tuple(sorted((u,v))))
    adj=[set() for _ in range(17)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    assert len(edges)==60
    assert all(not(adj[u]&adj[v]) for u,v in edges)
    deg=[len(s) for s in adj]
    found=[]
    for u,v in edges:
        if deg[u]!=7 or deg[v]!=7: continue
        common_non = set(range(17))-{u,v}-adj[u]-adj[v]
        assert len(common_non)==3
        assert all(deg[w]==7 for w in common_non)
        found.append((u,v))
    if found:
        assert (a,b) in [(3,2),(5,2)]
    forms.append({'a':a,'b':b,'sizes':sizes,'degree_by_bag':[deg[g[0]] for g in bags],
                  'adjacent_degree7_pairs':len(found)})
assert {(r['a'],r['b']) for r in forms if r['adjacent_degree7_pairs']}=={(3,2),(5,2)}

pair_profiles=[]
for s,t,k in product(range(2,4),range(2,4),range(6)):
    sizes=sorted([12-s-t,s+k,t+k])
    if sizes==[7,7,8]: pair_profiles.append([s,t,k])
assert pair_profiles==[[2,2,5],[2,3,5],[3,2,5]]

# Check the scalar consequences for an exceptional A-side with 11 vertices.
# t full-H vertices, each r=5. Every other positive r has r+s<=4,
# s in{2,3}, and degree r+s<=t because J_A has no outside-outside edges.
# Include all allowed r=0 choices, including true twins (s=0).
exception_patterns=[]
for t in range(4):
    choices=[(0,0)]
    choices += [(r,s) for r in range(3) for s in (2,3) if r+s<=min(4,t)]
    for vals in combinations_with_replacement(choices,11-t):
        if 5*t+sum(r for r,s in vals)!=20: continue
        positive=[(r,s) for r,s in vals if r]
        assert t==3 and positive==[(1,2)]*5
        exception_patterns.append({'full_H':t,'outside_pairs':list(vals)})
assert exception_patterns

# Core R2 vertices have G-degree16-a-b and all outside edges in E0.
# Whenever a+b>=6, neither a degree11 vertex (E0-degree2or3) nor a
# degree>=12 vertex can spend fewer than2 outside edges.
for row in forms:
    z=16-row['a']-row['b']
    for final_deg in range(11,17):
        outside=final_deg-z
        if outside<0: continue
        if final_deg==11 and outside not in (2,3): continue
        if row['a']+row['b']>=6: assert outside>=2
        else: assert final_deg>=12

receipt={'status':'PASS','scope':'finite arithmetic/literal controls; hand coverage not encoded',
         'forms':forms,'private_pair_profiles':pair_profiles,
         'exception_scalar_patterns':exception_patterns}
(out/'order29_equality_parameters_verified.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'status':'PASS','forms':len(forms),'pair_profiles':len(pair_profiles),
                  'exception_scalar_patterns':len(exception_patterns)}))
