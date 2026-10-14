#!/usr/bin/env python3
"""CAM-0006 Amendment B: checked transfer of six new full obstructions."""
import json
import time
from pathlib import Path

import networkx as nx
from blowup_graph import blowup
from transfer_obstruction import find_map


def main():
    src=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    rows=[]
    start=time.monotonic()
    for idx,(g6,w,_) in enumerate(src):
        row={'index':idx,'verdict':'UNKNOWN'}
        for obidx in (161,163,164,154,158,160):
            if time.monotonic()-start>600:
                row['reason']='aggregate cap'
                break
            og6,ow,_=src[obidx]
            if sum(ow)>sum(w):
                continue
            mp=find_map(nx.from_graph6_bytes(og6.encode()),ow,nx.from_graph6_bytes(g6.encode()),w,2)
            if mp is None:
                continue
            oe,ob=blowup(og6,ow)
            te,tb=blowup(g6,w)
            used=[0]*len(w)
            vm={}
            for u in range(len(ow)):
                v=mp[u]
                vm.update(zip(ob[u],tb[v][used[v]:used[v]+ow[u]]))
                used[v]+=ow[u]
            vector=[vm[v] for v in range(sum(ow))]
            assert len(vector)==len(set(vector))==sum(ow)
            assert all(tuple(sorted((vector[a],vector[b]))) in set(te) for a,b in oe)
            row.update(verdict='NON_BIPLANAR_BY_CHECKED_SUBGRAPH',obstruction_index=obidx,
                       vertex_map=vector,bag_map=mp,edges_checked=len(oe))
            break
        rows.append(row)
    Path('validation/S005/bag_transfers.json').write_text(json.dumps({
        'source_indices':[161,163,164,154,158,160],'seconds':time.monotonic()-start,'results':rows},indent=1),newline='\n')
    print('bag transfers',sum(r['verdict']!='UNKNOWN' for r in rows),flush=True)


if __name__=='__main__':
    main()
