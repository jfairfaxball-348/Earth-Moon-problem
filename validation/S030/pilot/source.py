"""Labelled, unrestricted order-28 two-layer CEGAR. Caps are UNKNOWN.

No imported s008_tree/CardEnc monkey patch. No sampled-model blocking.
"""
import argparse
import gzip
import hashlib
import itertools as it
import json
import os
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


def encode(n, degree, low, high):
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


def search(out, cap):
    f, g, ls = encode(28, 11, 155, 156)
    started = time.monotonic(); cuts = []; iterations = []
    atomic_json(out / 'VARIABLES.json', {'g': [[*e,x] for e,x in g.items()],
                'layers':[[[*e,x] for e,x in d.items()] for d in ls]})
    result = {'stratum':'S11_m155_156','verdict':'UNKNOWN','coverage':'all labelled graphs, vertex0 degree11',
              'S10':'NOT_RUN','S9':'NOT_RUN','regular154':'SOURCE_STATED_NOT_IMPORTED'}
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
        clique = next((c[:9] for c in nx.find_cliques(graph) if len(c)>=9), None)
        if clique:
            es=list(it.combinations(sorted(clique),2)); new.append({'kind':'K9','edges':es,'clause':[-g[e] for e in es]})
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
    args=ap.parse_args(); out=ROOT/'artifacts/tmp/S030'; out.mkdir(exist_ok=True,parents=True)
    smoke=json.loads((out/'SMOKE.json').read_text()); assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==271
    controls(out) if args.mode=='controls' else search(out,args.cap)
