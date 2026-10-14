#!/usr/bin/env python3
"""CAM-0005 Amendment A: a biplanar double-wheel rainbow Kempe lock."""
import itertools
import json
from pathlib import Path

import networkx as nx
from check_layers import certify_layer


def construct():
    e1 = [(0,i) for i in range(1,6)]
    e2 = [(0,i) for i in range(6,12)]
    for layer, rim in ((e1,list(range(1,6))), (e2,list(range(6,12)))):
        layer += [tuple(sorted((a,b))) for a,b in zip(rim,rim[1:]+rim[:1])]
    lock = {i:i-1 for i in range(1,12)}
    colour = {0:3, **dict(zip(range(1,6),[0,1,0,1,2])),
              **dict(zip(range(6,12),[0,1,0,1,0,1]))}
    pairs = []
    for i,j in itertools.combinations(range(1,12),2):
        p,q = len(colour),len(colour)+1
        e1.extend([(i,p),(j,q)])
        e2.append((p,q))
        lock[p],lock[q] = j-1,i-1
        colour[p] = 3
        colour[q] = 1 if colour[j] == 0 else 0
        pairs.append([i,j,p,q])
    e1,e2 = sorted(e1),sorted(e2)
    n = len(colour)
    assert n == 122 and len(e1)+len(e2) == 187
    assert not set(e1)&set(e2)
    assert all(colour[a] != colour[b] for a,b in e1+e2)
    assert all(lock[a] != lock[b] for a,b in e1+e2 if 0 not in (a,b))
    assert {colour[i] for i in range(1,6)} == {0,1,2}
    assert certify_layer(n,e1) and certify_layer(n,e2)
    graph = nx.Graph(e1+e2)
    graph.remove_node(0)
    for i,j,_,_ in pairs:
        two = graph.subgraph([v for v in graph if lock[v] in (i-1,j-1)])
        assert nx.has_path(two,i,j)
    return {'n':n,'E1':e1,'E2':e2,'four_colouring':[colour[v] for v in range(n)],
            'rainbow_colouring_G_minus_0':{str(v):c for v,c in lock.items()},
            'pair_gadgets':pairs,'single_Kempe_swap_obstruction':'55/55 checked',
            'D':6*n-12-len(e1)-len(e2)}


if __name__ == '__main__':
    data=construct()
    Path('validation/S004/double_wheel_lock.json').write_text(json.dumps(data,indent=1))
    print('PASS n=122 m=187 D=533, chi=4 by colouring/odd wheel, 55 Kempe pairs')
