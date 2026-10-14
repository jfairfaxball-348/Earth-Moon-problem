#!/usr/bin/env python3
"""CAM-0006 K: decode and directly audit saved relaxed SAT models."""
import hashlib
import itertools
import json
from pathlib import Path

import networkx as nx
from biplanar_cegar import is_kuratowski_subdivision
from biplanar_cnf import read_edges
from dense_face_cnf import encode
from check_s005_archives import cnf_bytes


def main():
    rows=json.loads(Path('validation/S005/dense/results.json').read_text())
    out=[]
    for row in rows:
        if row['verdict']!='SAT_RELAXATION':
            continue
        idx,mode=row['index'],row['mode']
        p=Path(f'artifacts/tmp/S005/dense/{mode}-row{idx}.solve.log')
        positive={int(v) for line in p.read_text().splitlines() if line.startswith('v ')
                  for v in line.split()[1:] if int(v)>0}
        edges=read_edges(f'validation/S005/targets/row{idx}.edges')
        n=max(max(e) for e in edges)+1
        nv,cls,f,x=encode(edges,mode=='global')
        assert hashlib.sha256(cnf_bytes(nv,cls)).hexdigest()==row['cnf_sha256']
        assert all(any(v in positive if v>0 else -v not in positive for v in cl) for cl in cls)
        selected=sorted(q for q,var in f.items() if var in positive)
        assert all(sum(a in q and b in q for q in selected)==2 for a,b in edges)
        audit={'index':idx,'mode':mode,'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
               'cnf_clauses_directly_satisfied':len(cls),'selected_triangles':selected,'edge_incidence':'exactly two'}
        archive=Path(f'validation/S005/dense/models/{mode}-row{idx}.log')
        archive.parent.mkdir(parents=True,exist_ok=True)
        archive.write_bytes(p.read_bytes())
        audit['model_archive']=str(archive)
        if mode=='layer':
            layers=[[e for e,var in x.items() if (var in positive)==flag] for flag in (True,False)]
            assert all(len(le)==3*n-6 for le in layers)
            assert all(len({x[e] in positive for e in itertools.combinations(q,2)})==1 for q in selected)
            statuses=[]
            for le in layers:
                g=nx.empty_graph(n);g.add_edges_from(le)
                planar,cert=nx.check_planarity(g,counterexample=True)
                info={'planar':planar,'isolates':list(nx.isolates(g)),
                      'components':len(list(nx.connected_components(g))),'edges':le}
                if not planar:
                    obstruction=sorted(tuple(sorted(e)) for e in cert.edges())
                    assert is_kuratowski_subdivision(obstruction)
                    info['checked_Kuratowski_subdivision']=obstruction
                statuses.append(info)
            assert not all(s['planar'] for s in statuses),'CONTRADICTION: requires full audit'
            audit['layers']=statuses
        out.append(audit)
    Path('validation/S005/relaxed_model_audit.json').write_text(json.dumps(out,indent=1),newline='\n')
    print('PASS directly checked',len(out),'relaxed SAT models; every displayed two-layer model nonplanar')


if __name__=='__main__':
    main()
