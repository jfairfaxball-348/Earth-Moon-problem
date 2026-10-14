#!/usr/bin/env python3
"""Cold archive/colour/map validation. DRAT is checked separately."""
import gzip
import hashlib
import json
from pathlib import Path

import networkx as nx
from blowup_chi_cnf import bag_cnf


def edges(g6,w):
    g=nx.from_graph6_bytes(g6.encode())
    bag=[i for i,c in enumerate(w) for _ in range(c)]
    return {(a,b) for a in range(len(bag)) for b in range(a+1,len(bag))
            if bag[a]==bag[b] or g.has_edge(bag[a],bag[b])}


def main():
    source=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    results=json.loads(Path('validation/S004/chi10_results.json').read_text())
    assert len(results)==len(source)==271
    for idx,row in enumerate(results):
        g6,w,_=source[idx]
        assert row['index']==idx and row['g6']==g6 and row['w']==w
        col=row['ten_colouring']
        assert len(col)==sum(w) and all(type(c)==int and 0<=c<10 for c in col)
        assert len(set(col))==10
        assert all(col[a]!=col[b] for a,b in edges(g6,w))
        nv,cls=bag_cnf(g6,w,9)
        cnf=f'p cnf {nv} {len(cls)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in cls)
        assert hashlib.sha256(cnf.encode()).hexdigest()==row['bag']['cnf_sha256']
        assert row['bag']['checker']==row['vertex']['checker']=='VERIFIED'
        raw=gzip.decompress(Path(row['bag']['archive']).read_bytes())
        assert len(raw)==row['bag']['drat_bytes']
        assert hashlib.sha256(raw).hexdigest()==row['bag']['drat_sha256']
    tr=json.loads(Path('validation/S004/obstruction_transfers.json').read_text())
    ob=tr['obstruction']
    forbidden=edges(ob['g6'],ob['w'])
    for row in tr['results']:
        if row['verdict']=='UNKNOWN':
            continue
        g6,w,_=source[row['source_index']]
        target=edges(g6,w)
        mp=row['vertex_map']
        assert len(mp)==len(set(mp))==ob['n']
        assert all(0<=v<sum(w) for v in mp)
        assert all(tuple(sorted((mp[a],mp[b]))) in target for a,b in forbidden)
    print('PASS 271 cold colourings/CNF hashes/archived proofs; positive transfer maps')


if __name__=='__main__':
    main()
