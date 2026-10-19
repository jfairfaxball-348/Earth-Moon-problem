"""Labelled, unrestricted order-28 two-layer CEGAR. Caps are UNKNOWN.

No imported s008_tree/CardEnc monkey patch. No sampled-model blocking.
"""
import argparse
import gzip
import hashlib
import itertools as it
import json
import os
import random
from pathlib import Path
import subprocess
import sys
import time

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s026_supervision import atomic_json, run_step


def encode(n, degree, low, high, anchor=False):
    pairs = list(it.combinations(range(n), 2))
    pool = IDPool()
    g = {e: pool.id(('g', e)) for e in pairs}
    layers = [{e: pool.id((k, e)) for e in pairs} for k in (0, 1)]
    f = CNF()
    for e in pairs:
        x, a, b = g[e], layers[0][e], layers[1][e]
        f.extend([[-a, x], [-b, x], [-x, a, b], [-a, -b]])
    for vs in it.combinations(range(n), 4):
        f.append([g[e] for e in it.combinations(vs, 2)])

    def bound(xs, lo, hi):
        if lo > 0:
            f.extend(CardEnc.atleast(xs, lo, vpool=pool, encoding=EncType.totalizer).clauses)
        if hi < len(xs):
            f.extend(CardEnc.atmost(xs, hi, vpool=pool, encoding=EncType.totalizer).clauses)
    bound(list(g.values()), low, high)
    for v in range(n):
        bound([x for e, x in g.items() if v in e], degree, degree if v == 0 else n-1)
    for layer in layers:
        bound(list(layer.values()), 0, 3*n-6)
    # Relabel a minimum-degree vertex to 0, then swap layers if 01 is in layer 2.
    f.append([-layers[1][(0, 1)]])
    if anchor:
        assert n==28 and degree==11
        for v in range(1,28):
            f.append([g[(0,v)] if 3<=v<=13 else -g[(0,v)]])
        f.append([-g[(1,2)]])
        f.append([layers[0][(0,3)]])
    return f, g, layers


def dump(path, f):
    f.to_file(str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_graph(n, es):
    graph = nx.Graph(); graph.add_nodes_from(range(n)); graph.add_edges_from(es)
    alpha_ok = not any(not any(graph.has_edge(a, b) for a, b in it.combinations(vs, 2))
                       for vs in it.combinations(range(n), 4))
    return graph, alpha_ok


def controls(out):
    # Retained J1 is alpha3, not an alpha2 source. Do not mislabel it.
    from s025_check import check_split
    split = json.loads((ROOT / 'validation/S003/splits/J1.split.json').read_text())
    positives = []
    for n in (17, 18):
        ls = [[e for e in split[k] if max(e) < n] for k in ('E1', 'E2')]
        es = ls[0] + ls[1]
        graph, a3 = verify_graph(n, es)
        a2 = all(any(graph.has_edge(a, b) for a, b in it.combinations(vs, 2))
                 for vs in it.combinations(range(n), 3))
        assert a3
        check_split(n, es, *ls)
        positives.append({'n': n, 'alpha_at_most_2': a2, 'alpha_at_most_3':a3, 'split_checked': True})
    # Unconditional C7[K4] negative, no reliance on source regular theorem.
    es = [[4*i+a, 4*j+b] for i, j in [(i, (i+1)%7) for i in range(7)]
          for a in range(4) for b in range(4)]
    graph = nx.Graph(es)
    assert len(es) == 112 and not any(nx.triangles(graph).values())
    # Meaningful base encoding controls: constrain to retained exact positive split.
    f, g, layers = encode(18, min(dict(verify_graph(18, split['E1']+split['E2'])[0].degree()).values()), 0, 153)
    # Vertex zero is a minimum-degree anchor, so relabel the retained graph first.
    graph = verify_graph(18, split['E1']+split['E2'])[0]
    v = min(graph, key=graph.degree)
    perm = {i: i for i in range(18)}; perm[0], perm[v] = v, 0
    ls = [{tuple(sorted((perm[a], perm[b]))) for a, b in split[k]} for k in ('E1', 'E2')]
    if (0, 1) in ls[1]:
        ls.reverse()
    assumptions = [x if e in ls[0] | ls[1] else -x for e, x in g.items()]
    assumptions += [x if e in ls[k] else -x for k in range(2) for e, x in layers[k].items()]
    with Solver(name='cadical195', bootstrap_with=f) as s:
        assert s.solve(assumptions=assumptions)
    atomic_json(out / 'CONTROLS.json', {'positive': positives, 'C7K4': {'triangle_free_edges':112,
                'bound':104,'nonbiplanar':True}, 'retained_split_encoding_satisfiable':True,
                'near25': 'NOT_CONSTRUCTED; no invented positive control'})


def triangle_free(graph):
    best=[]
    for seed in range(8):
        es=list(graph.edges()); random.Random(seed).shuffle(es)
        h=nx.Graph(); h.add_nodes_from(graph)
        for a,b in es:
            if not (set(h[a]) & set(h[b])):
                h.add_edge(a,b)
        if h.number_of_edges()>len(best): best=list(h.edges())
    return [tuple(sorted(e)) for e in best]


def library_cut(graph,g):
    from s027_contain import load_obstructions, obstruction, encode as contain, decode
    obs=load_obstructions()
    # Add S027/S028 library entries from their explicit, certified summary records.
    extra=ROOT/'validation/S028/local/EXTRA_OBSTRUCTIONS.json'
    if extra.exists():
        for r in json.loads(extra.read_text()):
            s=json.loads((ROOT/r['certificate']).read_text())
            assert s['verdict']=='NONBIPLANAR_CERTIFIED' and s['proof']['certified']
            h=obstruction(r['name'],r['g6'],r['u']); h['certificate']=r['certificate']
            assert (ROOT/r['edges']).read_text().replace('\r\n','\n')==h['edge_text']
            obs.append(h)
    for h in obs:
        if h['n']>28: continue
        cls,top,x,_=contain(h,[1]*28,B=graph)
        with Solver(name='cadical195',bootstrap_with=cls) as s:
            s.conf_budget(200)
            if s.solve_limited() is not True: continue
            vm=decode(h,[1]*28,{v for v in s.get_model() if v>0},x)
        assert len(vm)==len(set(vm))==h['n']
        es=[tuple(sorted((vm[a],vm[b]))) for a,b in h['edges']]
        assert all(graph.has_edge(*e) for e in es)
        return {'kind':'library','name':h['name'],'certificate':h['certificate'],
                'source_edges':h['edges'],'map':vm,'edges':es,'clause':[-g[e] for e in es]}
    return None


def search(out, cap, strengthened=False):
    f, g, ls = encode(28, 11, 155, 156,anchor=strengthened)
    started = time.monotonic(); cuts = []; iterations = []
    atomic_json(out / 'VARIABLES.json', {'g': [[*e,x] for e,x in g.items()],
                'layers':[[[*e,x] for e,x in d.items()] for d in ls]})
    result = {'stratum':'S11_m155_156','verdict':'UNKNOWN','coverage':'all labelled graphs, vertex0 degree11',
              'S10':'NOT_RUN','S9':'NOT_RUN','regular154':'SOURCE_STATED_NOT_IMPORTED',
              'strengthened':strengthened}
    while time.monotonic()-started < cap:
        cnf = out / 'current.cnf'; digest = dump(cnf, f)
        atomic_json(out / 'CUTS.json', cuts)
        proof = out / 'current.drat'
        remaining = cap - (time.monotonic()-started)
        if remaining <= 0: break
        r = run_step([str(ROOT/'artifacts/tmp/S004/cadical.exe'),str(cnf),str(proof)],
                     remaining, out/f'solve-{len(iterations):04d}.log', out/'SEARCH_JOURNAL.jsonl',
                     memory_kib=11*1024*1024)
        r['cnf_sha256'] = digest; iterations.append(r)
        if r['returncode'] == 20:
            q = run_step([str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'),str(cnf),str(proof)],
                         300,out/'drat-check.log',out/'SEARCH_JOURNAL.jsonl',memory_kib=11*1024*1024)
            result['proof_check'] = q
            result['verdict'] = 'UNSAT_DRAT_VERIFIED_PENDING_INDEPENDENT_ENCODING_REVIEW' if q['returncode']==0 and 'VERIFIED' in (out/'drat-check.log').read_text() else 'UNKNOWN'
            break
        if r['returncode'] != 10:
            result['stop'] = r['returncode']; break
        model = set(int(x) for line in (out/f'solve-{len(iterations)-1:04d}.log').read_text().splitlines()
                    if line.startswith('v ') for x in line.split()[1:] if int(x)>0)
        edges = [e for e,x in g.items() if x in model]
        graph, a3 = verify_graph(28,edges)
        assert a3 and len(edges) in (155,156) and min(dict(graph.degree()).values())==11
        decoded = [[e for e,x in d.items() if x in model] for d in ls]
        assert set(decoded[0]).isdisjoint(decoded[1]) and set(decoded[0]+decoded[1])==set(edges)
        atomic_json(out / 'LAST_MODEL.json', {'n':28,'E1':decoded[0],'E2':decoded[1]})
        new = []
        cliques=set()
        for clique in nx.find_cliques(graph):
            if len(clique)<9: continue
            for nine in it.combinations(sorted(clique),9):
                cliques.add(nine)
                if len(cliques)>=(1000 if strengthened else 1): break
            if len(cliques)>=(1000 if strengthened else 1): break
        for clique in sorted(cliques):
            es=list(it.combinations(clique,2)); new.append({'kind':'K9','edges':es,'clause':[-g[e] for e in es]})
        if strengthened:
            es=triangle_free(graph)
            if len(es)>104:
                assert not any(nx.triangles(nx.Graph(es)).values())
                new.append({'kind':'triangle_free','edges':es,'clause':[-g[e] for e in es]})
            if not cliques:
                c=library_cut(graph,g)
                if c: new.append(c)
        for k in range(2):
            layer = nx.Graph(); layer.add_nodes_from(range(28)); layer.add_edges_from(decoded[k])
            planar, cert = nx.check_planarity(layer, counterexample=True)
            if not planar:
                es = sorted(tuple(sorted(e)) for e in cert.edges())
                assert not nx.is_planar(nx.Graph(es))
                new.append({'kind':'Kuratowski','layer':k,'edges':es,'clause':[-ls[k][e] for e in es]})
        if not new:
            from s025_check import check_split
            check_split(28, edges, *decoded)
            result['verdict']='WITNESS_CANDIDATE_STOP'; break
        for c in new:
            f.append(c['clause']); cuts.append(c)
        atomic_json(out/'PROGRESS.json', {'seconds':time.monotonic()-started,'models':len(iterations),'cuts':len(cuts)})
    result.update(seconds=round(time.monotonic()-started,3),iterations=iterations,cuts=len(cuts))
    atomic_json(out/'CUTS.json',cuts)
    dump(out/'final.cnf', f)
    atomic_json(out/'RESULT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='iterations'}),flush=True)


if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['controls','search']); ap.add_argument('--cap',type=int,default=1200)
    ap.add_argument('--strengthened',action='store_true'); ap.add_argument('--out',default='artifacts/tmp/S030')
    args=ap.parse_args(); out=ROOT/args.out; out.mkdir(exist_ok=True,parents=True)
    smoke=json.loads((ROOT/'artifacts/tmp/S030/SMOKE.json').read_text()); assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==271
    controls(out) if args.mode=='controls' else search(out,args.cap,args.strengthened)
