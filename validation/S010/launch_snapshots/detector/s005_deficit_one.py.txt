#!/usr/bin/env python3
"""CAM-0006 F: actual D=1 controls and the eight fixed global relaxations."""
import itertools
import json
from pathlib import Path

import networkx as nx
from pysat.solvers import Cadical153
from deficit_one_cnf import encode
from s004_certify import write_cnf
from s005_dense import faces
from s005_search import run_logged,compress
from s005_replay import sha
from biplanar_cnf import read_edges


def main():
    root=Path('validation/S005/deficit_one')
    root.mkdir(parents=True,exist_ok=True)
    scratch=Path('artifacts/tmp/S005/deficit_one')
    scratch.mkdir(parents=True,exist_ok=True)
    d=json.loads(Path('validation/degree11_witness.json').read_text())
    n=d['num_vertices']
    layers=[{tuple(e) for e in d[key]} for key in ('edges_part1','edges_part2')]
    fs=[faces(n,sorted(es)) for es in layers]
    controls=[]
    def control(removed,extra,selected,kind):
        graph=sorted((layers[0]|layers[1])-{removed})
        nv,cls,f,x=encode(graph)
        assert selected<=set(f)
        assumptions=[v if q in selected else -v for q,v in f.items()]
        assumptions.extend(v if e==extra else -v for e,v in x.items())
        with Cadical153(bootstrap_with=cls) as s:
            assert s.solve(assumptions=assumptions)
        controls.append({'kind':kind,'removed':removed,'surplus_pair':extra,
                         'n':n,'m':len(graph),'variables':nv,'clauses':len(cls),
                         'actual_face_assignment':'SAT assumptions checked'})
    removed=min(layers[0])
    control(removed,removed,fs[0]|fs[1],'new noninput completion edge')
    found=False
    for uv in sorted(layers[0]):
        incident=[q for q in fs[0] if set(uv)<=set(q)]
        assert len(incident)==2
        opposite=tuple(sorted(next(v for v in q if v not in uv) for q in incident))
        if opposite not in layers[1]:
            continue
        changed=(layers[0]-{uv})|{opposite}
        # Independent rotations and actual triangular faces certify the flip.
        newfaces=faces(n,sorted(changed))
        control(uv,opposite,newfaces|fs[1],'doubled input completion edge')
        found=True
        break
    (root/'controls.json').write_text(json.dumps({'controls':controls,'doubled_control_found':found},indent=1),newline='\n')
    print('PASS deficit-one actual face controls',len(controls),flush=True)
    solver=str(Path('artifacts/tmp/S004/cadical.exe').resolve())
    checker=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
    results=[]
    caps=0
    for idx in (177,179,180,102,103,117,123,143):
        prefix=scratch/f'row{idx}'
        edgefile=f'validation/S005/targets/row{idx}.edges'
        nv,cls,_,_=encode(read_edges(edgefile))
        cnf=Path(str(prefix)+'.cnf');proof=Path(str(prefix)+'.drat')
        write_cnf(cnf,nv,cls)
        row={'index':idx,'verdict':'UNKNOWN','variables':nv,'clauses':len(cls),'cnf_sha256':sha(cnf)}
        if caps>=2:
            row['reason']='not run after two consecutive route caps'
        else:
            run=run_logged([solver,'-q','--no-binary',str(cnf),str(proof)],180,str(prefix)+'.solve.log')
            row['solve']=run
            caps=caps+1 if run['returncode'] not in (10,20) else 0
            if run['returncode']==10:
                row['verdict']='SAT_RELAXATION'
            elif run['returncode']==20:
                checked=run_logged([checker,str(cnf),str(proof),'-t','600'],620,str(prefix)+'.check.log')
                row['check']=checked
                if 's VERIFIED' in Path(str(prefix)+'.check.log').read_text():
                    row['verdict']='NON_BIPLANAR_DRAT_VERIFIED'
                    regen=Path(str(prefix)+'.regenerated.cnf')
                    write_cnf(regen,*encode(read_edges(edgefile))[:2])
                    assert regen.read_bytes()==cnf.read_bytes()
                    dest=root/f'row{idx}'
                    compress(proof,str(dest)+'.drat.gz')
                    row.update(proof_sha256=sha(proof),proof_bytes=proof.stat().st_size,
                               archive=str(dest)+'.drat.gz',archive_sha256=sha(str(dest)+'.drat.gz'))
                    Path(str(dest)+'.check.log').write_bytes(Path(str(prefix)+'.check.log').read_bytes())
            Path(root/f'row{idx}.solve.log').write_bytes(Path(str(prefix)+'.solve.log').read_bytes())
        results.append(row)
        (root/'results.json').write_text(json.dumps(results,indent=1),newline='\n')
        print('D1global',idx,row['verdict'],flush=True)


if __name__=='__main__':
    main()
