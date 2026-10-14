#!/usr/bin/env python3
"""CAM-0006 exact two-component swap challenge to the S004 lock."""
import json
from pathlib import Path

import networkx as nx
from check_layers import certify_layer


def main():
    d=json.loads(Path('validation/S004/double_wheel_lock.json').read_text())
    edges=[tuple(e) for e in d['E1']+d['E2']]
    assert len(edges)==len(set(edges))
    for key in ('E1','E2'):
        certify_layer(d['n'],d[key])
    g=nx.Graph(edges)
    g.remove_node(0)
    col={int(v):c for v,c in d['rainbow_colouring_G_minus_0'].items()}
    initial=dict(col)
    def proper():
        assert all(col[a]!=col[b] for a,b in g.edges())
    proper()
    i,j,k=1,6,2
    gadget=next(r for r in d['pair_gadgets'] if r[:2]==[i,j])
    p=gadget[2]
    swaps=[]
    for colours,vertex in (((initial[j],initial[k]),p),((initial[i],initial[j]),i)):
        a,b=colours
        two=g.subgraph([v for v in g if col[v] in colours])
        component=sorted(nx.node_connected_component(two,vertex))
        if vertex==p:
            assert component==[p]
        else:
            assert j not in component
        for v in component:
            col[v]=b if col[v]==a else a
        proper()
        swaps.append({'colours':list(colours),'component':component,
                      'colouring':[None]+[col[v] for v in range(1,d['n'])]})
    free=initial[i]
    assert free not in {col[v] for v in range(1,12)}
    col[0]=free
    assert all(col[a]!=col[b] for a,b in edges)
    Path('validation/S005/two_kempe_swaps.json').write_text(json.dumps({
        'input':'validation/S004/double_wheel_lock.json','n':d['n'],'m':len(edges),
        'pair':[i,j],'third_colour_vertex':k,'gadget':gadget,'swaps':swaps,
        'extended_colouring':[col[v] for v in range(d['n'])],
        'verified':'complete induced two-colour components; proper at every stage; full extension'},indent=1),newline='\n')
    print('PASS two complete Kempe swaps extend the S004 lock colouring',len(swaps[1]['component']))


if __name__=='__main__':
    main()
