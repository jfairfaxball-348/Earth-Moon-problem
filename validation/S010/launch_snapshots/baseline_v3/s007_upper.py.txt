#!/usr/bin/env python3
"""CAM-0008 explicit heavy-endblock controls and two local split challenges."""
import itertools
import json
import sys
from pathlib import Path
import networkx as nx
from s007_run import ROOT,TMP,save,certificate
from s005_search import run_logged
from s005_replay import sha
from check_layers import certify_layer,main as check_split


def finite():
    rows=[]
    for single in (False,True):
        for s in range(2,9):
            r=s if single else s-1
            a=12-s
            core=list(range(r));external=list(range(r,r+a))
            edges=set(itertools.combinations(core,2))|{(x,y) for x in core for y in external}
            if not single:
                cut=r+a;edges|={(x,cut) for x in core}
            n=12 if not single else 12
            g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(edges)
            # For endblocks, cut and the independent external set share one colour.
            colour=[v if v<r else r for v in range(n)]
            assert all(colour[u]!=colour[v] for u,v in edges)
            clique=max(nx.find_cliques(g),key=len)
            rows.append(dict(single_block=single,s=s,n=n,m=len(edges),D=6*n-12-len(edges),
                V=list(range(n)),edges=sorted(edges),core=core,external=external,
                degrees=dict(g.degree()),proper_colouring=colour,chi=r+1,
                explicit_clique=clique,euler_pass=len(edges)<=6*n-12,K9_present=len(clique)>=9))
    for r in (3,5,7,9):
        edges={tuple(sorted((v,(v+1)%r))) for v in range(r)}
        edges|={(x,y) for x in range(1,r) for y in range(r,r+9)}
        n=r+9;m=len(edges)
        rows.append(dict(odd_endblock_order=r,V=list(range(n)),edges=sorted(edges),n=n,m=m,
            D=6*n-12-m,euler_pass=m<=6*n-12,
            noncut_degrees=[sum(v in e for e in edges) for v in range(1,r)]))
    save(ROOT/'heavy_controls.json',rows)
    print('PASS14 clique/endblock and4 odd-cycle count/colour controls',flush=True)


def local():
    (ROOT/'heavy').mkdir(exist_ok=True);(TMP/'heavy').mkdir(exist_ok=True)
    save(ROOT/'upper_launch_hashes.json',{p:sha(p) for p in ('tools/s007_upper.py','tools/s007_cover.py','tools/s007_run.py')})
    rows=[];consecutive=0
    for r,a in ((7,5),(6,6)):
        tag=f'K{r}-I{a}'
        edges=sorted(set(itertools.combinations(range(r),2))|{(x,y) for x in range(r) for y in range(r,r+a)})
        ef=ROOT/'heavy'/(tag+'.edges');ef.write_text(''.join(f'{x} {y}\n' for x,y in edges),newline='\n')
        prefix=TMP/'heavy'/tag
        row=dict(tag=tag,n=r+a,m=len(edges),edgefile=str(ef),edge_sha256=sha(ef),verdict='UNKNOWN')
        if consecutive>=2:
            row['reason']='NOT_RUN after two final UNKNOWNs'
        else:
            run=run_logged([sys.executable,'tools/s007_cover.py',str(ef),str(prefix),'300','--lex'],320,str(prefix)+'.run.log')
            row['run']=run
            if Path(str(prefix)+'.result.json').exists():row['search']=json.loads(Path(str(prefix)+'.result.json').read_text())
            if run['returncode']==0 and row.get('search',{}).get('verdict')=='SAT_CHECKED':
                split=json.loads(Path(str(prefix)+'.split.json').read_text())
                check_split(str(ef),str(prefix)+'.split.json')
                colour=[v if v<r else r for v in range(r+a)]
                assert all(colour[x]!=colour[y] for x,y in edges)
                row.update(verdict='BIPLANAR_CONTROL',V=list(range(r+a)),split=split,
                    component_faces=[certify_layer(r+a,split[k]) for k in ('E1','E2')],
                    proper_colouring=colour,chi=r+1,clique_lower=list(range(r))+[r])
            elif run['returncode']==0 and row.get('search',{}).get('verdict')=='UNSAT':
                # Acceptance is deferred until complete S007 baseline has passed.
                row['certificate']=certificate(ef,prefix);row['verdict']=row['certificate']['verdict']
            consecutive=consecutive+1 if row['verdict']=='UNKNOWN' else 0
            import shutil
            for suffix in ('.cuts.json','.result.json','.run.log'):
                p=Path(str(prefix)+suffix)
                if p.exists():shutil.copyfile(p,ROOT/'heavy'/(tag+suffix))
        rows.append(row);save(ROOT/'heavy_search.json',rows)
        print(tag,row['verdict'],flush=True)


if __name__=='__main__':
    ROOT.mkdir(exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
    finite();local()
