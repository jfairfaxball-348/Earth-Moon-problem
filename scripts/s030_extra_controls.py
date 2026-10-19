"""Independent structural controls, no new graph verdicts outside S030 domain."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s025_check import check_split
from s030_op1b import triangle_free

out=ROOT/'artifacts/tmp/S030'
assert json.loads((out/'SMOKE.json').read_text())['verdict']=='PASS'
d=json.load(gzip.open(ROOT/'validation/S025/C5_CLASSIFY.json.gz','rt'))
r=next(r for r in d['results'] if r.get('split_checked') and r['w']==[1,1,1,1,7])
g=nx.Graph(r['E1']+r['E2']); clique=next(c for c in nx.find_cliques(g) if len(c)==8)
lab={v:i for i,v in enumerate(clique)}
ls=[]
for key in ('E1','E2'):
    edges=[(lab[a],lab[b]) for a,b in r[key] if a in lab and b in lab]
    ls.append([(a+8*k,b+8*k) for k in range(3) for a,b in edges])
check_split(24,ls[0]+ls[1],*ls)
graph=nx.Graph(ls[0]+ls[1])
assert len(list(nx.connected_components(graph)))==3
assert sorted(map(len,nx.connected_components(graph)))==[8,8,8]
assert graph.number_of_edges()==84
alpha3=not any(not any(graph.has_edge(a,b) for a,b in it.combinations(vs,2))
               for vs in it.combinations(range(24),4))
assert alpha3
(out/'POSITIVE24.json').write_text(json.dumps({'n':24,'E1':ls[0],'E2':ls[1],
        'alpha':3,'split_checked':True,'source':'three copies of checked K8 subgraph in S025 C5[1,1,1,1,7]'},indent=1)+'\n')

# Check the relabelling anchor on C7[K4] (degree11, alpha3, K9-free).
h=nx.cycle_graph(7)
g=nx.Graph();g.add_nodes_from(range(28))
for a,b in it.combinations(range(28),2):
    if a//4==b//4 or h.has_edge(a//4,b//4):g.add_edge(a,b)
v=0; anti=set(g)-set(g[v])-{v}
x,y=next((a,b) for a,b in it.combinations(sorted(anti),2) if not g.has_edge(a,b))
order=[v,x,y]+sorted(g[v])+sorted(anti-{x,y}); lab={v:i for i,v in enumerate(order)}
es={tuple(sorted((lab[a],lab[b]))) for a,b in g.edges()}
assert all(((0,j) in es)==(3<=j<=13) for j in range(1,28)) and (1,2) not in es
tf=triangle_free(g)
assert not any(nx.triangles(nx.Graph(tf)).values())

# Check downloaded CC0 file hashes against the fetched public manifest.
api=json.loads((out/'sources/paper59-api.json').read_text())['data']
for item in api['supplement_manifest']:
    data=(out/'sources/supplement'/item['path']).read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
(out/'EXTRA_CONTROLS.json').write_text(json.dumps({'positive24':'PASS','anchor_C7K4':'PASS',
        'triangle_free_generator':'PASS','supplement_manifest_files':len(api['supplement_manifest']),
        'source17_alpha2':'NOT_RETRIEVED; J1 was correctly found to have alpha3',
        'source18_alpha2':'SOURCE_STATED; no purported positive alpha2 witness asserted'},indent=2)+'\n')
print('PASS: explicit planar alpha3 graph at n24; anchor; triangle-free set; supplement file hashes')
