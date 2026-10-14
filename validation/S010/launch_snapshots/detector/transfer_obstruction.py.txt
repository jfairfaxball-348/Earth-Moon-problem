#!/usr/bin/env python3
"""CAM-0005 H: positive, capacity-respecting subgraph embedding certificates."""
import json
import time
from pathlib import Path

import networkx as nx
from blowup_graph import blowup


def find_map(base, demands, target, capacities, seconds=5):
    order=sorted(base,key=lambda v:(-demands[v],-base.degree(v),v))
    remaining=list(capacities)
    mapping={}
    start=time.monotonic()

    def rec(at):
        if time.monotonic()-start > seconds:
            raise TimeoutError
        if at == len(order):
            return dict(mapping)
        v=order[at]
        for t in target:
            if remaining[t]<demands[v]:
                continue
            if any(mapping[u]!=t and not target.has_edge(mapping[u],t)
                   for u in base[v] if u in mapping):
                continue
            mapping[v]=t
            remaining[t]-=demands[v]
            result=rec(at+1)
            if result is not None:
                return result
            remaining[t]+=demands[v]
            del mapping[v]
        return None
    try:
        return rec(0)
    except TimeoutError:
        return None


def main():
    registered=json.loads(Path('validation/S004/full_survivor_target.json').read_text())
    g6,w=registered['g6'],registered['w']
    base=nx.from_graph6_bytes(g6.encode())
    forbidden_edges,forbidden_bags=blowup(g6,w)
    rows=[]
    start=time.monotonic()
    for idx,(target_g6,capacities,_) in enumerate(json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())):
        target=nx.from_graph6_bytes(target_g6.encode())
        m=find_map(base,w,target,capacities) if time.monotonic()-start < 600 else None
        row={'source_index':idx,'verdict':'UNKNOWN'}
        if m is not None:
            target_edges,target_bags=blowup(target_g6,capacities)
            used=[0]*len(capacities)
            vertex_map={}
            for bag in range(len(w)):
                t=m[bag]
                selected=target_bags[t][used[t]:used[t]+w[bag]]
                assert len(selected)==w[bag]
                used[t]+=w[bag]
                vertex_map.update(zip(forbidden_bags[bag],selected))
            assert len(set(vertex_map.values()))==sum(w)
            target_eset=set(target_edges)
            assert all(tuple(sorted((vertex_map[a],vertex_map[b]))) in target_eset
                       for a,b in forbidden_edges)
            row.update(verdict='NON_BIPLANAR_BY_SUBGRAPH',bag_map=m,
                       vertex_map=[vertex_map[v] for v in range(sum(w))],
                       edges_checked=len(forbidden_edges))
        rows.append(row)
    Path('validation/S004/obstruction_transfers.json').write_text(json.dumps({
        'obstruction':registered,'seconds':time.monotonic()-start,'results':rows},indent=1))
    print('checked exclusions',sum(r['verdict']!='UNKNOWN' for r in rows),'of',len(rows))


if __name__ == '__main__':
    main()
