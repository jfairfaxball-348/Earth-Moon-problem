#!/usr/bin/env python3
"""CAM-0007 explicit adversarial examples; not a universal proof by testing."""
import itertools
import json
from pathlib import Path
import networkx as nx
from check_layers import certify_layer
from s006_run import save


def add_clique(g, vertices):
    g.add_edges_from(itertools.combinations(vertices,2))


def block_controls():
    rows=[]
    k8=json.loads(Path('validation/S003/splits/K8.split.json').read_text())
    for b in range(9):
        g=nx.Graph()
        layers=[set(),set()]
        colours={}
        def clique(vs):
            add_clique(g,vs)
            if len(vs)==8:
                split=[k8['E1'],k8['E2']]
            else:
                assert len(vs)==5
                split=[[e for e in itertools.combinations(range(5),2) if e!=(3,4)],[(3,4)]]
            for i,es in enumerate(split):
                layers[i].update(tuple(sorted((vs[a],vs[z]))) for a,z in es)
            if vs[0] not in colours:
                colours[vs[0]]=0
            options=[j for j in range(8) if j!=colours[vs[0]]]
            for v,col in zip(vs[1:],options):
                assert v not in colours
                colours[v]=col
        clique(list(range(8)))
        unused=[list(range(8))]
        for _ in range(b):
            # A free vertex of the latest K8 gets a connector K5.
            v=unused[-1].pop()
            fresh=list(range(len(g),len(g)+4))
            clique([v]+fresh)
            for x in fresh:
                seven=list(range(len(g),len(g)+7))
                clique([x]+seven)
                unused.append(seven)
        n,m=len(g),g.number_of_edges()
        blocks=list(nx.biconnected_components(g))
        assert n==32*b+8 and m==122*b+28
        assert sorted(map(len,blocks))==[5]*b+[8]*(4*b+1)
        assert all(g.subgraph(B).number_of_edges()==len(B)*(len(B)-1)//2 for B in blocks)
        assert max(dict(g.degree()).values())<=11
        assert 16*m==61*n-40
        assert not layers[0]&layers[1] and layers[0]|layers[1]==set(g.edges())
        assert all(colours[a]!=colours[z] for a,z in g.edges())
        faces=[certify_layer(n,sorted(es)) for es in layers]
        row=dict(connectors=b,n=n,m=m,delta_max=max(dict(g.degree()).values()),
                 K5_blocks=b,K8_blocks=4*b+1,sharp_bound_scaled=61*n-40,
                 false_29_over8_bound_scaled=29*n-8,actual_edges_scaled8=8*m,
                 V=list(range(n)),E1=sorted(layers[0]),E2=sorted(layers[1]),
                 proper_eight_colouring=colours,component_faces=faces,
                 edges=[list(e) for e in sorted(g.edges())])
        rows.append(row)
    assert rows[1]['actual_edges_scaled8']>rows[1]['false_29_over8_bound_scaled']
    save('validation/S006/Gallai_controls.json',rows)
    print('PASS nine exact block controls; b=1 refutes (29/8)n-1',flush=True)


def palette_control():
    k8=json.loads(Path('validation/S003/splits/K8.split.json').read_text())
    e1={tuple(e) for e in k8['E1']};e2={tuple(e) for e in k8['E2']}
    boundary={};core={v:v for v in range(8)}
    neighbourhoods={}
    for v in range(8):
        leaves=[8+4*v+j for j in range(4)]
        neighbourhoods[str(v)]=leaves
        for j,x in enumerate(leaves):
            boundary[x]=j
            e1.add((v,x))
            # Unrestricted eight-colouring, independent of fixed boundary.
            core[x]=(v+1)%8
    edges=e1|e2
    assert not e1&e2 and len(edges)==60
    assert all(core[a]!=core[b] for a,b in edges)
    assert all(len({boundary[x] for x in xs})==4 for xs in neighbourhoods.values())
    assert len(set().union(*(set(xs) for xs in neighbourhoods.values())))==32
    # Fixed boundary leaves each of the eight clique vertices the same seven colours.
    available=set(range(11))-set(boundary.values())
    assert available==set(range(4,11)) and len(available)==7
    f1=certify_layer(40,sorted(e1));f2=certify_layer(40,sorted(e2))
    save('validation/S006/palette_trap.json',dict(n=40,V=list(range(40)),E1=sorted(e1),E2=sorted(e2),
         core=list(range(8)),external_neighbours=neighbourhoods,fixed_boundary=boundary,
         proper_eight_colouring=core,available_core_colours=sorted(available),
         component_faces=[f1,f2],nonextension_proof='K8 needs eight distinct colours; only seven available',
         scope='biplanar and core degree11, external degree1; chi8, not12-critical'))
    print('PASS exact palette trap layers/rotations/eight-colouring; fixed boundary cannot extend',flush=True)


if __name__=='__main__':
    block_controls()
    palette_control()
