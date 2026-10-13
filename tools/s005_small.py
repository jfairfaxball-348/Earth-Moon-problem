#!/usr/bin/env python3
"""CAM-0006 H: one induced smaller obstruction and optional checked transfers."""
import json
import sys
import time
from pathlib import Path

import networkx as nx
from blowup_graph import blowup
from s005_search import run_logged,certify
from check_layers import main as check_split
from transfer_obstruction import find_map


def main():
    g6='G|fH_K';w=[2,3,2,2,4,2,4,4]
    edges,bags=blowup(g6,w)
    assert sum(w)==23 and len(edges)==123
    root=Path('validation/S005')
    edgefile=root/'targets/small-row158.edges'
    edgefile.write_text(''.join(f'{a} {b}\n' for a,b in edges),newline='\n')
    target={'g6':g6,'w':w,'n':23,'m':123,'D':3,'chromatic':'not investigated'}
    (root/'small_target.json').write_text(json.dumps(target,indent=1),newline='\n')
    prefix=Path('artifacts/tmp/S005/search/small-row158')
    r=run_logged([sys.executable,'tools/triangulation_cover.py',str(edgefile),str(prefix),'180','--lex'],
                 200,str(prefix)+'.run.log')
    row={'target':target,'run':r,'verdict':'UNKNOWN'}
    p=Path(str(prefix)+'.result.json')
    if p.exists():
        meta=json.loads(p.read_text());row['search']=meta
        if r['returncode']==0 and meta['verdict']=='UNSAT':
            row['certificate']=certify(edgefile,prefix)
            row['verdict']=row['certificate']['verdict']
        elif r['returncode']==0 and meta['verdict']=='SAT_CHECKED':
            check_split(str(edgefile),str(prefix)+'.split.json')
            row['verdict']='BIPLANAR_CHECKED_NO_CHROMATIC_ADVANCE'
            (root/'search/small-row158.split.json').write_bytes(Path(str(prefix)+'.split.json').read_bytes())
    for suffix in ('.cuts.json','.result.json','.run.log'):
        p=Path(str(prefix)+suffix)
        if p.exists():
            (root/('search/small-row158'+suffix)).write_bytes(p.read_bytes())
    (root/'small_result.json').write_text(json.dumps(row,indent=1),newline='\n')
    print('SMALL',row['verdict'],flush=True)
    if row['verdict']!='NON_BIPLANAR_DRAT_VERIFIED':
        return
    targets=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    results=[];start=time.monotonic()
    for idx,(tg,tw,_) in enumerate(targets):
        result={'index':idx,'verdict':'UNKNOWN'}
        mp=find_map(nx.from_graph6_bytes(g6.encode()),w,nx.from_graph6_bytes(tg.encode()),tw,2) if time.monotonic()-start<600 else None
        if mp is not None:
            te,tbags=blowup(tg,tw);used=[0]*len(tw);vm={}
            for a in range(len(w)):
                b=mp[a]
                vm.update(zip(bags[a],tbags[b][used[b]:used[b]+w[a]]));used[b]+=w[a]
            vector=[vm[v] for v in range(sum(w))]
            assert len(set(vector))==len(vector)==sum(w)
            assert all(tuple(sorted((vector[a],vector[b]))) in set(te) for a,b in edges)
            result.update(verdict='NON_BIPLANAR_BY_CHECKED_SUBGRAPH',vertex_map=vector,edges_checked=len(edges))
        results.append(result)
    (root/'small_transfers.json').write_text(json.dumps({'source':target,'seconds':time.monotonic()-start,'results':results},indent=1),newline='\n')
    print('SMALL transfers',sum(r['verdict']!='UNKNOWN' for r in results),flush=True)


if __name__=='__main__':
    main()
