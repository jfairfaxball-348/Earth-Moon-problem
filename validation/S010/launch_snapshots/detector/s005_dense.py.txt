#!/usr/bin/env python3
"""CAM-0006 E: witness controls and certificates for reduced D=0 CNFs."""
import itertools
import json
import random
from pathlib import Path

import networkx as nx
from pysat.solvers import Cadical153
from dense_face_cnf import encode
from s004_certify import write_cnf
from s005_replay import sha
from s005_search import run_logged,compress
from check_layers import certify_layer


def faces(n,edges):
    certify_layer(n,edges)
    g=nx.Graph(edges)
    ok,emb=nx.check_planarity(g)
    assert ok
    seen=set()
    result=set()
    for a,b in sorted(g.edges()):
        for start in ((a,b),(b,a)):
            if start in seen:
                continue
            cycle=emb.traverse_face(*start,mark_half_edges=seen)
            assert len(cycle)==len(set(cycle))==3
            result.add(tuple(sorted(cycle)))
    assert len(result)==2*n-4
    return result


def main():
    root=Path('validation/S005/dense')
    root.mkdir(parents=True,exist_ok=True)
    scratch=Path('artifacts/tmp/S005/dense')
    scratch.mkdir(parents=True,exist_ok=True)
    d=json.loads(Path('validation/degree11_witness.json').read_text())
    n=d['num_vertices']
    rng=random.Random(5005)
    controls=[]
    for idx in range(11):
        perm=list(range(n))
        if idx:
            rng.shuffle(perm)
        layers=[sorted(tuple(sorted((perm[a],perm[b]))) for a,b in d[key])
                for key in ('edges_part1','edges_part2')]
        assert not set(layers[0])&set(layers[1])
        selected=faces(n,layers[0])|faces(n,layers[1])
        edges=sorted(layers[0]+layers[1])
        for global_only in (True,False):
            nv,cls,f,x=encode(edges,global_only)
            assumptions=[v if q in selected else -v for q,v in f.items()]
            if not global_only:
                assumptions.extend(v if e in set(layers[0]) else -v for e,v in x.items())
            with Cadical153(bootstrap_with=cls) as s:
                assert s.solve(assumptions=assumptions)
        controls.append({'index':idx,'permutation':perm,'n':n,'m':len(edges),
                         'faces_selected':len(selected),'both_encodings':'witness extends to SAT'})
    (root/'controls.json').write_text(json.dumps(controls,indent=1),newline='\n')
    print('PASS 11 actual D=0 witnesses/rotations/face assignments in both encodings',flush=True)
    targets=[r for r in json.loads(Path('validation/S005/targets.json').read_text()) if r['D']==0]
    solver=str(Path('artifacts/tmp/S004/cadical.exe').resolve())
    checker=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
    rows=[]
    for global_only in (True,False):
        consecutive_caps=0
        for target in targets:
            idx=target['index']
            mode='global' if global_only else 'layer'
            prefix=scratch/f'{mode}-row{idx}'
            from biplanar_cnf import read_edges
            nv,cls,_,_=encode(read_edges(target['edgefile']),global_only)
            cnf=Path(str(prefix)+'.cnf')
            proof=Path(str(prefix)+'.drat')
            write_cnf(cnf,nv,cls)
            row={'index':idx,'mode':mode,'variables':nv,'clauses':len(cls),
                 'cnf_sha256':sha(cnf),'verdict':'UNKNOWN'}
            # Excessive-cost pivot is prospective in Amendment E's stop rule.
            if consecutive_caps>=2:
                row['reason']='route stopped after two consecutive caps; not run'
                rows.append(row)
                continue
            solve=run_logged([solver,'-q','--no-binary',str(cnf),str(proof)],180,str(prefix)+'.solve.log')
            row['solve']=solve
            consecutive_caps=consecutive_caps+1 if solve['returncode'] not in (10,20) else 0
            if solve['returncode']==10:
                row['verdict']='SAT_RELAXATION'
            elif solve['returncode']==20:
                check=run_logged([checker,str(cnf),str(proof),'-t','600'],620,str(prefix)+'.check.log')
                row['check']=check
                if 's VERIFIED' in Path(str(prefix)+'.check.log').read_text():
                    row['verdict']='NON_BIPLANAR_DRAT_VERIFIED'
                    dest=root/prefix.name
                    compress(proof,str(dest)+'.drat.gz')
                    # Independent fresh regeneration of the same reduced generator.
                    regen=scratch/(prefix.name+'.regenerated.cnf')
                    nv2,cls2,_,_=encode(read_edges(target['edgefile']),global_only)
                    write_cnf(regen,nv2,cls2)
                    assert regen.read_bytes()==cnf.read_bytes()
                    row.update(proof_sha256=sha(proof),proof_bytes=proof.stat().st_size,
                               archive=str(dest)+'.drat.gz',archive_sha256=sha(str(dest)+'.drat.gz'),
                               regenerated='byte identical')
                    for suffix in ('.check.log','.solve.log'):
                        Path(str(dest)+suffix).write_bytes(Path(str(prefix)+suffix).read_bytes())
            rows.append(row)
            (root/'results.json').write_text(json.dumps(rows,indent=1),newline='\n')
            print(mode,idx,row['verdict'],solve['seconds'],flush=True)
    (root/'results.json').write_text(json.dumps(rows,indent=1),newline='\n')


if __name__=='__main__':
    main()
