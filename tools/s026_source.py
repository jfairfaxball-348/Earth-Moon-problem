#!/usr/bin/env python3
"""Bounded SAT-generated larger quotient source; exact filters, heuristic search.

No independence-four set => alpha<=3 in the clique blow-up (one per bag),
so 28 vertices require at least ten colours. The model order is deterministic,
but there is no claim of source exhaustion when a time/model cap is reached.
"""
import itertools as it
import json
from pathlib import Path
import random
import sys
import time

import networkx as nx
from pysat.solvers import Solver

from blowup_graph import blowup
from s025_transfer import find_map, explicit_check
from s026_campaign import child, py, save, exact, sha

ROOT = Path(__file__).resolve().parents[1]


def containment(g6, w, dest):
    B = nx.from_graph6_bytes(g6.encode())
    H = nx.from_graph6_bytes(b'Dhc')
    entries = json.loads((ROOT / 'validation/S025/C5_CERTIFICATES.json').read_text())
    if isinstance(entries, dict):
        entries = entries.get('certificates', entries.get('results', []))
    records = []
    for e in entries:
        if not e.get('certified'):
            continue
        u = list(map(int, e['tag']))
        a = find_map(H, u, B, w)
        row = {'tag': e['tag'], 'contains': a is not None}
        if a is not None:
            row['vertex_map'] = explicit_check('Dhc', u, g6, w, a)
            records.append(row)
            save(dest, {'avoids_all': False, 'tests': records})
            return
        records.append(row)
    assert len(records) == 18, len(records)
    save(dest, {'avoids_all': True, 'tests': records})


def generate(out):
    d = out / 'source'
    d.mkdir(exist_ok=True)
    summary = {'seed': 260018, 'universe': 'labelled SAT models; no completeness claim',
               'orders': [], 'candidates': []}
    count = 0
    for n, w in [(9, [4] + [3]*8), (10, [3]*8 + [2]*2), (11, [3]*6 + [2]*5)]:
        pairs = list(it.combinations(range(n), 2))
        random.Random(260018+n).shuffle(pairs)
        idx = {e: i+1 for i, e in enumerate(pairs)}
        def var(a, b):
            return idx[tuple(sorted((a, b)))]
        clauses = [[var(a, b) for a, b in it.combinations(S, 2)]
                   for S in it.combinations(range(n), 4)]
        for k in range(2, n+1):
            for S in it.combinations(range(n), k):
                total = sum(w[v] for v in S)
                if total >= 9 and all(total-w[v] < 9 for v in S):
                    clauses.append([-var(a, b) for a, b in it.combinations(S, 2)])
        stats = {'nbase': n, 'weights': w, 'models': 0, 'euler_filtered': 0,
                 'cut_filtered': 0, 'c5_filtered': 0, 'filter_unknown': 0, 'admitted': 0}
        start = time.monotonic()
        with Solver(name='cadical195', bootstrap_with=clauses) as solver:
            for model_no in range(2000):
                if time.monotonic()-start > 900 or count >= 12:
                    stats['stop'] = 'REGISTERED_CAP'
                    break
                if not solver.solve():
                    stats['stop'] = 'GENERATOR_UNSAT_UNCERTIFIED'
                    break
                m = set(x for x in solver.get_model() if x > 0)
                E = sorted(e for e in pairs if idx[e] in m)
                solver.add_clause([-i if i in m else i for i in range(1, len(pairs)+1)])
                stats['models'] += 1
                B = nx.Graph()
                B.add_nodes_from(range(n))
                B.add_edges_from(E)
                g6 = nx.to_graph6_bytes(B, header=False).decode().strip()
                es, _ = blowup(g6, w)
                if len(es) > 6*28-12:
                    stats['euler_filtered'] += 1
                    continue
                maxcut = max(sum(w[a]*w[b] for a, b in E if ((bits>>a) ^ (bits>>b)) & 1)
                             for bits in range(1 << (n-1)))
                if maxcut > 4*28-8:
                    stats['cut_filtered'] += 1
                    continue
                name = f'B{n}-{model_no:04d}'
                trial = d / name
                trial.mkdir(exist_ok=True)
                rec = {'name': name, 'g6': g6, 'w': w, 'maxcut': maxcut}
                save(trial / 'INPUT.json', rec)
                filt = child(py('s026_source.py', 'containment', trial / 'INPUT.json', trial / 'FILTER.json'),
                             30, trial / 'filter.log')
                if filt['returncode'] != 0:
                    stats['filter_unknown'] += 1
                    rec['filter_status'] = 'UNKNOWN'
                else:
                    check = json.loads((trial / 'FILTER.json').read_text())
                    if not check['avoids_all']:
                        stats['c5_filtered'] += 1
                        rec['filter_status'] = 'CONTAINS_CERTIFIED_C5'
                    else:
                        # No K6 clique: rules out retained Sulanke H as subgraph.
                        # Exact weighted clique bound was independently rechecked here.
                        cliques = list(nx.find_cliques(B))
                        omega = max(sum(w[v] for v in C) for C in cliques)
                        assert omega <= 8
                        # S013/S014 closed H-anchored <=18 families cannot contain n28 graphs.
                        # Exclude them as candidate sources by order; no claim of excluding H subgraphs.
                        indep = [list(S) for k in range(n+1) for S in it.combinations(range(n), k)
                                 if all(not B.has_edge(a, b) for a, b in it.combinations(S, 2))]
                        assert max(map(len, indep)) <= 3
                        rec.update(filter_status='ADMITTED', omega=omega, independent_sets=indep,
                                   chromatic_lower=10, num_vertices=28, edges=es)
                        save(trial / 'CANDIDATE.json', rec)
                        edge = trial / 'graph.edges'
                        edge.write_text(''.join(f'{a} {b}\n' for a, b in es))
                        count += 1
                        stats['admitted'] += 1
                        for seed in (1, 2):
                            child(py('s025_cover_anneal.py', edge, seed, 60, trial / f'anneal{seed}.json'),
                                  75, trial / f'anneal{seed}.log')
                        rec['exact'] = exact(edge, trial, 300)
                summary['candidates'].append(rec)
                save(d / 'SUMMARY.json', summary)
            else:
                stats['stop'] = 'MODEL_CAP'
        stats['seconds'] = round(time.monotonic()-start, 2)
        summary['orders'].append(stats)
        save(d / 'SUMMARY.json', summary)
        print(json.dumps(stats), flush=True)


if __name__ == '__main__':
    inp = json.loads(Path(sys.argv[2]).read_text())
    containment(inp['g6'], inp['w'], sys.argv[3])
