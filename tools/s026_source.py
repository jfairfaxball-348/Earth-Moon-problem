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
from pysat.card import CardEnc, EncType

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
    seen_edges = set()
    profiles = []
    rng = random.Random(260018)
    for n in range(9, 15):
        ws = {tuple(sorted([28//n+1]*(28 % n) + [28//n]*(n-28 % n), reverse=True))}
        if n <= 11:
            while len(ws) < 9:
                cuts = sorted(rng.sample(range(1, 28), n-1))
                w = [b-a for a, b in zip([0]+cuts, cuts+[28])]
                if max(w) <= 7:
                    ws.add(tuple(sorted(w, reverse=True)))
        profiles.extend((n, list(w)) for w in sorted(ws))
    for profile_no, (n, w) in enumerate(profiles):
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
        # Fresh Boolean copies, each equivalent to its base-edge variable.
        # Their cardinality sum is exactly the number of cross-bag edges.
        top, units = len(pairs), []
        for (a, b), x in idx.items():
            for _ in range(w[a]*w[b]):
                top += 1
                clauses += [[-x, top], [x, -top]]
                units.append(top)
        card = CardEnc.atmost(units, 156-sum(x*(x-1)//2 for x in w),
                             top_id=top, encoding=EncType.seqcounter)
        clauses += card.clauses
        stats = {'profile': profile_no, 'nbase': n, 'weights': w, 'models': 0, 'euler_filtered': 0,
                 'cut_filtered': 0, 'c5_filtered': 0, 'filter_unknown': 0, 'admitted': 0,
                 'model_records': []}
        summary['orders'].append(stats)
        profile_dir = d / f'profile{profile_no:02d}'
        profile_dir.mkdir(exist_ok=True)
        save(profile_dir / 'DOMAIN.json', {'nbase': n, 'w': w, 'pairs': pairs,
                                          'euler_bound': 156, 'independence_bound': 3})
        start = time.monotonic()
        with Solver(name='cadical195', bootstrap_with=clauses) as solver:
            for model_no in range(100):
                if time.monotonic()-start > 180 or count >= 6:
                    stats['stop'] = 'REGISTERED_CAP'
                    break
                if not solver.solve():
                    stats['stop'] = 'GENERATOR_UNSAT_UNCERTIFIED'
                    if stats['models'] == 0:
                        cnf = profile_dir / 'domain.cnf'
                        cnf.write_text(f'p cnf {card.nv} {len(clauses)}\n'+''.join(
                            ' '.join(map(str, cl))+' 0\n' for cl in clauses))
                        stats['domain_proof_run'] = child(py('s025_certify.py', cnf, profile_dir, 60, 120),
                                                         220, profile_dir / 'proof.log')
                        cp = profile_dir / 'domain.certificate.json'
                        if cp.exists():
                            stats['domain_proof'] = json.loads(cp.read_text())
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
                assert len(es) <= 6*28-12, 'eager density encoding violated'
                mr = {'g6':g6,'edges':len(es)}
                stats['model_records'].append(mr)
                maxcut = max(sum(w[a]*w[b] for a, b in E if ((bits>>a) ^ (bits>>b)) & 1)
                             for bits in range(1 << (n-1)))
                if maxcut > 4*28-8:
                    stats['cut_filtered'] += 1
                    mr['filter']='CUT_DENSITY'
                    save(d/'SUMMARY.json',summary)
                    continue
                name = f'P{profile_no:02d}-B{n}-{model_no:04d}'
                trial = d / name
                trial.mkdir(exist_ok=True)
                rec = {'name': name, 'g6': g6, 'w': w, 'maxcut': maxcut}
                mr['filter']='C5_TEST'
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
                        # Exact weighted clique bound was independently rechecked here.
                        cliques = list(nx.find_cliques(B))
                        omega = max(sum(w[v] for v in C) for C in cliques)
                        assert omega <= 8
                        # S023's closed universal-K6 join source.
                        universal_weight=sum(w[v] for v in B if B.degree(v)==n-1)
                        if universal_weight >= 6:
                            rec['filter_status']='CLOSED_UNIVERSAL_K6_SOURCE'
                            summary['candidates'].append(rec)
                            continue
                        # S013/S014 closed H-anchored <=18 families cannot contain n28 graphs.
                        # Exclude them as candidate sources by order; no claim of excluding H subgraphs.
                        indep = [list(S) for k in range(n+1) for S in it.combinations(range(n), k)
                                 if all(not B.has_edge(a, b) for a, b in it.combinations(S, 2))]
                        assert max(map(len, indep)) <= 3
                        edgekey=tuple(es)
                        if edgekey in seen_edges:
                            rec['filter_status']='DUPLICATE_LABELLED_EDGE_SET'
                            summary['candidates'].append(rec)
                            continue
                        seen_edges.add(edgekey)
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
                            ap=trial/f'anneal{seed}.json'
                            if ap.exists():
                                ar=json.loads(ap.read_text())
                                if ar['best_uncovered']==0:
                                    from s025_check import check_split
                                    check_split(28,es,ar['E1'],ar['E2'])
                                    rec['annealed_split_checked']=True
                        rec['exact'] = exact(edge, trial, 300)
                summary['candidates'].append(rec)
                save(d / 'SUMMARY.json', summary)
            else:
                stats['stop'] = 'MODEL_CAP'
        stats['seconds'] = round(time.monotonic()-start, 2)
        save(d / 'SUMMARY.json', summary)
        print(json.dumps(stats), flush=True)


if __name__ == '__main__':
    inp = json.loads(Path(sys.argv[2]).read_text())
    containment(inp['g6'], inp['w'], sys.argv[3])
