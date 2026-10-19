"""Audit archived S030 models, formula clauses and cut semantics.

Kuratowski validity uses suppression to K5/K3,3, independently of the
search's LR planarity predicate. Does not infer exhaustion from a cap.
"""
import argparse
import gzip
import itertools as it
import json
from pathlib import Path

import networkx as nx

ROOT=Path(__file__).resolve().parents[1]


def subdivision(es):
    h=nx.Graph(es)
    assert nx.is_connected(h)
    while any(d==2 for _,d in h.degree()):
        v=next(v for v,d in h.degree() if d==2)
        a,b=list(h[v]); h.remove_node(v)
        assert a!=b and not h.has_edge(a,b)
        h.add_edge(a,b)
    if len(h)==5 and h.number_of_edges()==10 and all(d==4 for _,d in h.degree()):return 'K5'
    assert len(h)==6 and h.number_of_edges()==9 and all(d==3 for _,d in h.degree())
    assert nx.is_bipartite(h)
    return 'K33'


def read(p):
    if p.exists():return p.read_text()
    return gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()).decode()


def audit(base):
    variables=json.loads(read(base/'VARIABLES.json'))
    g={(a,b):x for a,b,x in variables['g']}
    ls=[{(a,b):x for a,b,x in d} for d in variables['layers']]
    cuts=json.loads(read(base/'CUTS.json')); types={}
    for c in cuts:
        es=[tuple(sorted(e)) for e in c['edges']]; types[c['kind']]=types.get(c['kind'],0)+1
        assert len(set(es))==len(es) and all(e in g for e in es)
        if c['kind']=='Kuratowski':
            subdivision(es); want=[-ls[c['layer']][e] for e in es]
        elif c['kind']=='K9':
            vs=set(it.chain.from_iterable(es))
            assert len(vs)==9 and len(es)==36
            want=[-g[e] for e in es]
        elif c['kind']=='triangle_free':
            assert len(es)>104
            neighbors={v:set() for v in range(28)}
            for a,b in es:neighbors[a].add(b);neighbors[b].add(a)
            assert all(not neighbors[a]&neighbors[b] for a,b in es)
            want=[-g[e] for e in es]
        elif c['kind']=='library':
            vm=c['map']; src=c['source_edges']
            assert len(vm)==len(set(vm)) and all(0<=v<28 for v in vm)
            assert es==[tuple(sorted((vm[a],vm[b]))) for a,b in src]
            summary=json.loads((ROOT/c['certificate']).read_text())
            if isinstance(summary,list):
                record=next(r for r in summary if 'C5-'+r['tag']==c['name'])
                assert record['certified']
                path=ROOT/'validation/S025/certs'/(c['name']+'.edges')
                import hashlib
                assert hashlib.sha256(path.read_bytes()).hexdigest()==record['edges_sha256']
            else:
                assert summary['verdict']=='NONBIPLANAR_CERTIFIED' and summary['proof']['certified']
                path=(ROOT/c['certificate']).with_name('graph.edges')
            stored=[tuple(map(int,line.split())) for line in path.read_text().splitlines()]
            assert set(stored)==set(map(tuple,src))
            want=[-g[e] for e in es]
        else:raise AssertionError(c['kind'])
        assert want==c['clause']
    # Literal formula parses and every saved cut equals the final suffix.
    lines=read(base/'final.cnf').splitlines()
    header=next(l for l in lines if l.startswith('p ')).split()
    cls=[list(map(int,l.split()[:-1])) for l in lines if l and l[0] not in 'cp']
    assert len(cls)==int(header[3])
    assert cls[-len(cuts):]==[c['clause'] for c in cuts] if cuts else True
    basecls=cls[:-len(cuts)] if cuts else cls
    result=json.loads(read(base/'RESULT.json')); checked=0
    for i,r in enumerate(result['iterations']):
        if r['returncode']!=10:continue
        log=read(base/f'solve-{i:04d}.log')
        model={int(x) for l in log.splitlines() if l.startswith('v ') for x in l.split()[1:] if int(x)>0}
        es={e for e,x in g.items() if x in model}
        deg=[sum(v in e for e in es) for v in range(28)]
        assert len(es) in (155,156) and min(deg)==11 and deg[0]==11
        assert all(any(e in es for e in it.combinations(vs,2)) for vs in it.combinations(range(28),4))
        parts=[{e for e,x in d.items() if x in model} for d in ls]
        assert not(parts[0]&parts[1]) and parts[0]|parts[1]==es and all(len(s)<=78 for s in parts)
        assert all(any((x>0)==(abs(x) in model) for x in c) for c in basecls)
        if result.get('strengthened'):
            assert (1,2) not in es and all(((0,v) in es)==(3<=v<=13) for v in range(1,28))
            assert (0,3) in parts[0]
        if result.get('sorted_anchor'):
            for block in (range(3,14),range(14,28)):
                keys=[2*((1,v) in es)+((2,v) in es) for v in block]
                assert keys==sorted(keys)
        checked+=1
    return {'directory':str(base.relative_to(ROOT)),'models_checked':checked,'cuts_checked':len(cuts),
            'cut_types':types,'base_clauses':len(basecls),'variables':int(header[2]),
            'verdict':result['verdict'],'exhaustion':False,'status':'PASS'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('directories',nargs='+');args=ap.parse_args()
    out=[audit(ROOT/p) for p in args.directories]
    print(json.dumps(out,indent=2))
    (ROOT/'artifacts/tmp/S030/SEARCH_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
