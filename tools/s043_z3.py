"""S043 preregistered exact Z3 orbit CEGAR. Caps never establish UNSAT."""
import gzip
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

import networkx as nx
import psutil
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import rotation, subdivision, four_sets

OUT = ROOT/'validation/S043'
TMP = ROOT/'artifacts/tmp/S043'


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=1)+'\n', encoding='utf-8', newline='\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sigma(v):
    return 0 if not v else 1+3*((v-1)//3)+(v % 3)


def edge(a, b):
    return tuple(sorted((a, b)))


def pair_orbits():
    left = set(it.combinations(range(28), 2))
    out = []
    while left:
        a, b = min(left)
        orb = sorted({edge(a, b), edge(sigma(a), sigma(b)), edge(sigma(sigma(a)), sigma(sigma(b)))})
        assert len(orb) == 3
        out.append(orb)
        left.difference_update(orb)
    return out


def four_orbits():
    left = set(it.combinations(range(28), 4))
    out = []
    while left:
        vs = min(left)
        orb = {vs, tuple(sorted(map(sigma, vs))), tuple(sorted(sigma(sigma(v)) for v in vs))}
        out.append((vs, len(orb)))
        left.difference_update(orb)
    return out


def vertex_map(kind, i=None):
    out = list(range(28))
    for v in range(1, 28):
        q, r = divmod(v-1, 3)
        if kind == 'rotate' and q == i:
            r = (r+1) % 3
        elif kind == 'swap' and q in (i, i+1):
            q = 2*i+1-q
        elif kind == 'inverse':
            r = -r % 3
        out[v] = 1+3*q+r
    return out


def generators(orb):
    lookup = {e: j for j, es in enumerate(orb) for e in es}
    out = []
    kinds = [('rotate', i) for i in range(9)]+[('swap', i) for i in range(2, 8)]+[('inverse', None), ('swap', 0)]
    for k, i in kinds:
        perm = vertex_map(k, i)
        flip = k == 'swap' and i == 0
        mp = [lookup[edge(perm[es[0][0]], perm[es[0][1]])] for es in orb]
        out.append(dict(name='layer_swap_orbit01' if flip else f'{k}_{i}', vertices=perm,
                        layer_swap=flip, image=[1+126*(l ^ flip)+mp[j] for l in range(2) for j in range(126)]))
    return out


def lex_clauses(xs, ys, top):
    clauses = []
    top += 1
    p = top
    clauses.append([p])
    for a, b in zip(xs, ys):
        if a == b:
            continue
        clauses.append([-p, -a, b])
        top += 1
        q = top
        clauses.extend([[-q, p], [-q, -a, b], [-q, a, -b], [-p, a, b, q], [-p, -a, -b, q]])
        p = q
    return clauses, top


def encode():
    orb = pair_orbits()
    fours = four_orbits()
    lookup = {e: j for j, es in enumerate(orb) for e in es}
    var = lambda l, j: 1+126*l+j
    clauses = [[-var(0, j), -var(1, j)] for j in range(126)]
    top = 252
    for l in range(2):
        c = CardEnc.equals([var(l, j) for j in range(126)], 26, top_id=top, encoding=EncType.seqcounter)
        clauses.extend(c.clauses)
        top = c.nv
    for vs, _ in fours:
        clauses.append(sorted({var(l, lookup[e]) for e in it.combinations(vs, 2) for l in range(2)}))
    triangles = [lookup[(1+3*i, 2+3*i)] for i in range(9)]
    clauses.extend([[var(0, triangles[0])], [var(1, triangles[1])]])
    gs = generators(orb)
    for g in gs:
        cs, top = lex_clauses(list(range(1, 253)), g['image'], top)
        clauses.extend(cs)
    return orb, fours, gs, triangles, clauses, top


def controls(orb, fours, gs):
    assert len(orb) == 126 and len(fours) == 6831
    assert sum(s == 1 for _, s in fours) == 9
    assert sum(s == 3 for _, s in fours) == 6822
    # Exhaustive existential checks of the actual prefix encoding, all 3-bit pairs.
    for a in it.product((0, 1), repeat=3):
        for b in it.product((0, 1), repeat=3):
            cs, _ = lex_clauses([1, 2, 3], [4, 5, 6], 6)
            with Solver(name='g4', bootstrap_with=cs) as s:
                ok = s.solve(assumptions=[i+1 if v else -i-1 for i, v in enumerate(a+b)])
            assert ok == (a <= b)
    for n in range(2, 7):
        for k in range(n+1):
            c = CardEnc.equals(list(range(1, n+1)), k, encoding=EncType.seqcounter)
            with Solver(name='g4', bootstrap_with=c.clauses) as s:
                for bits in it.product((0, 1), repeat=n):
                    assert s.solve(assumptions=[i+1 if v else -i-1 for i, v in enumerate(bits)]) == (sum(bits) == k)
    # Wheel on 27 boundary vertices, with equivariant outside polygon triangulation.
    remap = lambda t: 1+3*(t % 9)+(t//9)
    es = {edge(0, remap(t)) for t in range(27)} | {edge(remap(t), remap((t+1) % 27)) for t in range(27)}
    for start in (0, 9, 18):
        es.add(edge(remap(start), remap((start+9) % 27)))
        es |= {edge(remap(start), remap((start+t) % 27)) for t in range(2, 9)}
    assert len(es) == 78 and {edge(sigma(a), sigma(b)) for a, b in es} == es
    g = nx.Graph(); g.add_nodes_from(range(28)); g.add_edges_from(es)
    ok, emb = nx.check_planarity(g)
    assert ok and len(rotation(28, sorted(es), emb.get_data())) == 52
    for h in (nx.complete_graph(5), nx.complete_bipartite_graph(3, 3)):
        assert subdivision(sorted(edge(a, b) for a, b in h.edges())) in ('K5', 'K33')
    for g in gs:
        assert sorted(g['image']) == list(range(1, 253))
    record = dict(status='PASS', pair_orbits=126, four_orbits=6831, four_orbit_sizes={'1': 9, '3': 6822},
                  lex_truth_table_cases=64, cardinality_n_max=6, generators=len(gs),
                  planar_layer=dict(edges=sorted(es), rotation=emb.get_data()))
    dump(OUT/'CONTROLS.json', record)


def cnf_bytes(clauses, nv):
    return (f'p cnf {nv} {len(clauses)}\n'+''.join(' '.join(map(str, c))+' 0\n' for c in clauses)).encode()


def native_run(cmd, cpu_cap=300, wall_cap=600):
    start = time.monotonic()
    log = TMP/('native_solver.log' if 'cadical' in cmd[0] else 'native_checker.log')
    with log.open('w') as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
        proc = psutil.Process(p.pid)
        cpu = 0.0
        capped = False
        while p.poll() is None:
            try:
                t = proc.cpu_times(); cpu = t.user+t.system
                if cpu >= cpu_cap or time.monotonic()-start >= wall_cap or proc.memory_info().rss > 4*1024**3:
                    p.terminate(); capped = True; break
            except psutil.NoSuchProcess:
                break
            time.sleep(.1)
        p.wait()
    return dict(returncode=p.returncode, capped=capped, cpu_seconds=cpu,
                wall_seconds=time.monotonic()-start, log=log.read_text(errors='replace')[-2000:])


def main():
    assert not (OUT/'RESULT.json').exists(), 'finished run already exists'
    smoke = json.loads((OUT/'SMOKE.json').read_text())
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == 271
    reg = json.loads((OUT/'REGISTRATION.json').read_text())
    assert sha(ROOT/'sessions/S043/PLAN.md') == reg['sha256']['sessions/S043/PLAN.md']
    start, wall = time.process_time(), time.monotonic()
    orb, fours, gs, triangles, clauses, nv = encode()
    controls(orb, fours, gs)
    dump(OUT/'ENCODING.json', dict(orbits=orb, fours=fours, generators=gs, triangles=triangles,
                                  base_variables=nv, base_clauses=len(clauses)))
    raw = cnf_bytes(clauses, nv)
    (OUT/'BASE.cnf.gz').write_bytes(gzip.compress(raw, mtime=0))
    lookup = {e: j for j, es in enumerate(orb) for e in es}
    cut_count = models = calls = 0
    verdict, reason = 'UNKNOWN', 'CAP'
    planar_layer_count = 0
    last_notice = time.monotonic()
    cuts = []
    proc = psutil.Process()
    with Solver(name='g4', bootstrap_with=clauses) as solver, (OUT/'CUTS.jsonl').open('w', encoding='utf-8', newline='\n') as record:
        while True:
            cpu = time.process_time()-start
            if cpu >= 1800 or time.monotonic()-wall >= 3600 or cut_count >= 20000:
                break
            if proc.memory_info().rss > 4*1024**3 or psutil.virtual_memory().available < 1024**3 or shutil.disk_usage(ROOT).free < 10*1024**3:
                reason = 'RESOURCE_GUARD'; break
            solver.clear_interrupt()
            timer = threading.Timer(min(30, 1800-cpu, 3600-(time.monotonic()-wall)), solver.interrupt)
            timer.start()
            try:
                sat = solver.solve_limited(expect_interrupt=True)
            finally:
                timer.cancel(); timer.join()
            calls += 1
            if sat is False:
                reason = 'INCREMENTAL_UNSAT_REQUIRES_PROOF'; break
            if sat:
                models += 1
                chosen = set(v for v in solver.get_model() if 0 < v <= 252)
                layers = [sorted(e for j, es in enumerate(orb) if 1+126*l+j in chosen for e in es) for l in range(2)]
                assert all(len(es) == 78 for es in layers)
                assert not set(layers[0]) & set(layers[1])
                union = set(layers[0]) | set(layers[1])
                assert not any(not any(e in union for e in it.combinations(vs, 2)) for vs, _ in fours)
                planar = []
                for l, es in enumerate(layers):
                    g = nx.Graph(); g.add_nodes_from(range(28)); g.add_edges_from(es)
                    ok, emb = nx.check_planarity(g)
                    planar.append(ok)
                    if ok:
                        assert len(rotation(28, es, emb.get_data())) == 52
                        planar_layer_count += 1
                    else:
                        _, sub = nx.check_planarity(g, counterexample=True)
                        kes = sorted(edge(a, b) for a, b in sub.edges())
                        kind = subdivision(kes)
                        support = sorted({lookup[e] for e in kes})
                        c = [-1-126*l-j for j in support]
                        assert set(kes) <= set(es)
                        row = dict(model=models, layer=l, edges=kes, kind=kind, support=support, clause=c)
                        record.write(json.dumps(row, separators=(',', ':'))+'\n'); record.flush()
                        cuts.append(c); solver.add_clause(c); cut_count += 1
                if all(planar):
                    assert four_sets(28, *layers) == 0
                    rots = []
                    for es in layers:
                        g = nx.Graph(); g.add_nodes_from(range(28)); g.add_edges_from(es)
                        _, emb = nx.check_planarity(g); rots.append(emb.get_data())
                    dump(OUT/'CANDIDATE.json', dict(layers=layers, rotations=rots, independent_four_sets=0))
                    reason = 'POSITIVE_REQUIRES_FINAL_COLOURING'; verdict = 'CANDIDATE'; break
            if time.monotonic()-last_notice >= 25:
                progress = dict(cpu_seconds=time.process_time()-start, wall_seconds=time.monotonic()-wall,
                                models=models, cuts=cut_count, calls=calls, planar_layers=planar_layer_count,
                                solver_stats=solver.accum_stats())
                dump(TMP/'PROGRESS.json', progress)
                print(json.dumps(progress), flush=True)
                last_notice = time.monotonic()
        stats = solver.accum_stats()
    native = {}
    raw_final = cnf_bytes(clauses+cuts, nv)
    (OUT/'FINAL.cnf.gz').write_bytes(gzip.compress(raw_final, mtime=0))
    if reason == 'INCREMENTAL_UNSAT_REQUIRES_PROOF':
        cnf, proof = TMP/'final.cnf', TMP/'final.drat'
        cnf.write_bytes(raw_final)
        binary = ROOT/'artifacts/tmp/S004/cadical.exe'
        checker = ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'
        assert (sha(binary), sha(checker)) == (smoke['solver_sha256'], smoke['checker_sha256'])
        native['solver'] = native_run([str(binary), '-q', '--no-binary', str(cnf), str(proof)])
        native['solver_sha256'], native['checker_sha256'] = sha(binary), sha(checker)
        if native['solver']['returncode'] == 20 and not native['solver']['capped']:
            native['checker'] = native_run([str(checker), str(cnf), str(proof)])
            if native['checker']['returncode'] == 0 and 's VERIFIED' in native['checker']['log'] and not native['checker']['capped']:
                verdict = 'UNSAT_DRAT_VERIFIED_PENDING_CLAUSE_REPLAY'
            (OUT/'FINAL.drat.gz').write_bytes(gzip.compress(proof.read_bytes(), mtime=0))
    final_cpu = time.process_time()-start+sum(v['cpu_seconds'] for v in native.values() if isinstance(v, dict))
    result = dict(verdict=verdict, reason=reason, models=models, cuts=cut_count, calls=calls,
                  planar_layers=planar_layer_count, cpu_seconds=final_cpu, wall_seconds=time.monotonic()-wall,
                  driver_cpu_seconds=time.process_time()-start, solver_stats=stats, native=native,
                  base_cnf_raw_sha256=hashlib.sha256(raw).hexdigest(), final_cnf_raw_sha256=hashlib.sha256(raw_final).hexdigest(),
                  gate_decision='PIVOT' if verdict != 'CANDIDATE' else 'PENDING',
                  whole_slice_certified=False, bounds=[9, 12], S036_restarted=False)
    dump(OUT/'RESULT.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
