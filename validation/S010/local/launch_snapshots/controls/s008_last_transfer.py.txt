"""CAM-0009E newly checked sources159/162 to last selected target155."""
import itertools
import json
from pathlib import Path
import networkx as nx
from blowup_graph import blowup
from s005_replay import sha
from s007_run import save

root=Path('validation/S008')
corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
completed=json.loads((root/'tree/search_results.json').read_text())
target=next(r for r in json.loads((root/'targets.json').read_text()) if r['index']==155)
assert target['chromatic_check']['returncode']==0 and 's VERIFIED' in (root/'chi-row155.check.log').read_text()
g2,w2,_=corpus[155];edges2,bags2=blowup(g2,w2);base2=nx.from_graph6_bytes(g2.encode());eset=set(edges2)
assert target['g6']==g2 and target['w']==w2 and sha(target['edgefile'])==target['edge_sha256']
assert all(target['ten_colouring'][a]!=target['ten_colouring'][b] for a,b in edges2)
rows=[]
for idx in (159,162):
    certrow=next(r for r in completed if r['target']['index']==idx)
    assert certrow['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
    cert=certrow['certificate']
    assert cert['check']['returncode']==cert['core_check']['returncode']==cert['cold_retained_check']['returncode']==0
    assert sha(cert['archive'])==cert['archive_sha256']
    assert 's VERIFIED' in (root/'tree/search'/f'cover-row{idx}.cold.check.log').read_text()
    g,w,_=corpus[idx];edges,bags=blowup(g,w);base=nx.from_graph6_bytes(g.encode())
    rec=dict(source=idx,target=155,verdict='NO_MAP_IN_REGISTERED_FAMILY',permutations=0)
    for p in itertools.permutations(range(8)):
        rec['permutations']+=1
        if not all(w[i]<=w2[p[i]] for i in range(8)):continue
        if not all(base2.has_edge(p[a],p[b]) for a,b in base.edges()):continue
        injection={v:bags2[p[i]][j] for i,bag in enumerate(bags) for j,v in enumerate(bag)}
        assert len(set(injection.values()))==len(injection)==sum(w)
        assert all(tuple(sorted((injection[a],injection[b]))) in eset for a,b in edges)
        rec.update(verdict='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED',bag_permutation=p,vertex_map=injection,
            source_certificate=cert,source_edge_sha256=certrow['target']['edge_sha256'],
            target_edge_sha256=target['edge_sha256'],target_chromatic_check=target['chromatic_check'])
        break
    rows.append(rec)
    save(root/'last_transfers.json',rows)
print('Last-target transfer results',[(r['source'],r['verdict'],r['permutations']) for r in rows])
