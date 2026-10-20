"""Independent literal-cut/model checker for the S031 persistent worker.

No import of its encoder or search loop. Subdivision suppression is the
independent Kuratowski check used in the archived S030 audit.
"""
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from replay_s030_search import subdivision


def cut(c,g,layers):
    es=[tuple(sorted(e)) for e in c['edges']]
    assert len(es)==len(set(es)) and all(e in g for e in es)
    if c['kind']=='K9':
        assert len(set(it.chain.from_iterable(es)))==9 and len(es)==36
        want=[-g[e] for e in es]
    elif c['kind']=='Kuratowski':
        assert c['layer'] in (0,1)
        subdivision(es);want=[-layers[c['layer']][e] for e in es]
    elif c['kind']=='triangle_free':
        assert len(es)>104
        adj={v:set() for v in range(28)}
        for a,b in es:adj[a].add(b);adj[b].add(a)
        assert all(not adj[a]&adj[b] for a,b in es)
        want=[-g[e] for e in es]
    elif c['kind']=='library':
        vm=c['map']; src=c['source_edges']
        assert len(vm)==len(set(vm)) and all(0<=v<28 for v in vm)
        assert es==[tuple(sorted((vm[a],vm[b]))) for a,b in src]
        record=json.loads((ROOT/c['certificate']).read_text())
        if isinstance(record,list):
            row=next(r for r in record if 'C5-'+r['tag']==c['name'])
            assert row['certified']
            path=ROOT/'validation/S025/certs'/(c['name']+'.edges')
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['edges_sha256']
        else:
            assert record['verdict']=='NONBIPLANAR_CERTIFIED' and record['proof']['certified']
            path=(ROOT/c['certificate']).with_name('graph.edges')
        stored=[tuple(map(int,l.split())) for l in path.read_text().splitlines()]
        assert set(stored)==set(map(tuple,src))
        want=[-g[e] for e in es]
    else:raise AssertionError(c['kind'])
    assert want==c['clause']


def model(positive,g,layers,formula):
    edges={e for e,x in g.items() if x in positive}
    assert len(edges) in (155,156)
    deg=[sum(v in e for e in edges) for v in range(28)]
    assert min(deg)==11 and deg[0]==11
    assert all(any(e in edges for e in it.combinations(vs,2)) for vs in it.combinations(range(28),4))
    parts=[{e for e,x in layer.items() if x in positive} for layer in layers]
    assert not parts[0]&parts[1] and parts[0]|parts[1]==edges and all(len(s)<=78 for s in parts)
    assert all(any((x>0)==(abs(x) in positive) for x in c) for c in formula.clauses)
    assert (1,2) not in edges and all(((0,v) in edges)==(3<=v<=13) for v in range(1,28))
    assert (0,3) in parts[0]
    for block in (range(3,14),range(14,28)):
        keys=[2*((1,v) in edges)+((2,v) in edges) for v in block]
        assert keys==sorted(keys)
    graph=nx.Graph();graph.add_nodes_from(range(28));graph.add_edges_from(edges)
    return graph,parts
