"""S041 probe P3: biplanarity of K5 v pentagonal bipyramid = (K7-e) v C5, with controls."""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import rotation

WORK = ROOT/'artifacts/tmp/S041/p3'
OUT = ROOT/'validation/S041'
SOLVER = os.environ.get('EMP_CADICAL', str(ROOT/'artifacts/tmp/S004/cadical.exe'))
CHECKER = os.environ.get('EMP_DRAT_TRIM', str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'))


def sulanke():
    d = json.loads((ROOT/'validation/sulanke.json').read_text())
    edges = sorted({tuple(sorted(e)) for e in d['edges_part1']+d['edges_part2']})
    clique = sorted(set(range(11))-set(d['cycle_order']))
    return edges, clique, d['cycle_order']


def k5_bipyramid():
    """K5 on 0..4 joined to the pentagonal bipyramid: hubs 5,6 (nonadjacent), rim 7..11."""
    rim = list(range(7, 12))
    pyr = [(h, c) for h in (5, 6) for c in rim]+[tuple(sorted((rim[i], rim[(i+1) % 5]))) for i in range(5)]
    edges = list(it.combinations(range(5), 2))+[(a, b) for a in range(5) for b in range(5, 12)]+pyr
    return sorted(set(edges))


def hajos_apex():
    """K1 v H3, H3 a chain of three Sulanke copies, every Hajos deletion inside a K6."""
    base, clique, _ = sulanke()
    c0, c1, c2, c3 = clique[:4]
    label = {}
    nxt = 0
    for copy in range(3):
        for v in range(11):
            if copy == 1 and v == c0:
                label[copy, v] = label[0, c0]
            elif copy == 2 and v == c0:
                label[copy, v] = label[1, c2]
            else:
                label[copy, v] = nxt; nxt += 1
    edges = set()
    for copy in range(3):
        for a, b in base:
            edges.add(tuple(sorted((label[copy, a], label[copy, b]))))
    for copy, a, b in ((0, c0, c1), (1, c0, c1), (1, c2, c3), (2, c0, c1)):
        edges.remove(tuple(sorted((label[copy, a], label[copy, b]))))
    edges.add(tuple(sorted((label[0, c1], label[1, c1]))))
    edges.add(tuple(sorted((label[1, c3], label[2, c1]))))
    h = nxt
    assert h == 31 and len(edges) == 148
    g = nx.Graph(list(edges))
    omega_h = max(len(c) for c in nx.find_cliques(g))
    apex = h
    edges |= {(v, apex) for v in range(h)}
    return sorted(edges), dict(h=h, h_edges=148, omega_H=omega_h, n=h+1, edges=len(edges))


def decide(name, edges, timeout):
    WORK.mkdir(parents=True, exist_ok=True)
    edgefile = WORK/f'{name}.txt'
    edgefile.write_text(''.join(f'{a} {b}\n' for a, b in edges), newline='\n')
    prefix = WORK/name
    start = time.time()
    run = subprocess.run([sys.executable, 'tools/biplanar_cegar.py', edgefile.as_posix(), prefix.as_posix(), str(timeout), '--seed-small'],
                         capture_output=True, text=True, cwd=ROOT)
    info = json.loads(run.stdout.strip().splitlines()[-1])
    info.update(name=name, vertices=1+max(max(e) for e in edges), edges=len(edges), seconds=time.time()-start,
                edges_sha256=hashlib.sha256(edgefile.read_bytes()).hexdigest())
    if info['verdict'] == 'SAT':
        split = json.loads(Path(str(prefix)+'.split.json').read_text())
        layers = [sorted(tuple(e) for e in split[k]) for k in ('E1', 'E2')]
        assert not set(layers[0]) & set(layers[1]) and set(layers[0]) | set(layers[1]) == set(edges)
        n = info['vertices']
        rots = []
        for layer in layers:
            g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(layer)
            ok, emb = nx.check_planarity(g)
            assert ok
            rot = {v: list(w) for v, w in emb.get_data().items()}
            if nx.is_connected(g):
                rotation(n, layer, rot)
            rots.append(rot)
        info.update(certificate='EXPLICIT_PLANAR_LAYERS', E1=layers[0], E2=layers[1], rotations=rots)
    elif info['verdict'] == 'UNSAT':
        cnf, proof = Path(str(prefix)+'.cnf'), Path(str(prefix)+'.drat')
        s = subprocess.run([SOLVER, '-q', '--no-binary', str(cnf), str(proof)], capture_output=True, text=True)
        c = subprocess.run([CHECKER, str(cnf), str(proof)], capture_output=True, text=True)
        k = subprocess.run([sys.executable, 'tools/check_cegar_certificate.py', edgefile.as_posix(), prefix.as_posix()],
                           capture_output=True, text=True, cwd=ROOT)
        verified = s.returncode == 20 and 's VERIFIED' in c.stdout and k.returncode == 0
        info.update(certificate='DRAT_VERIFIED_NONBIPLANAR' if verified else 'UNSAT_NOT_VERIFIED_UNKNOWN',
                    solver_returncode=s.returncode, drat_verified='s VERIFIED' in c.stdout,
                    structure_check=k.stdout.strip()[-200:], cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),
                    lemmas_file=str(Path(str(prefix)+'.lemmas.json').relative_to(ROOT)).replace('\\', '/'))
    print(name, json.dumps({k: v for k, v in info.items() if k not in ('E1', 'E2', 'rotations')}), flush=True)
    return info


def main():
    start = time.process_time()
    rows = []
    sul, _, _ = sulanke()
    rows.append(decide('control_sulanke', sul, 300))
    rows.append(decide('control_K9', list(it.combinations(range(9), 2)), 300))
    assert rows[0]['verdict'] == 'SAT' and rows[1]['verdict'] == 'UNSAT'
    g1 = k5_bipyramid()
    assert len(g1) == 60
    rows.append(decide('K5_join_bipyramid', g1, 600))
    extra = None
    if rows[-1]['verdict'] == 'SAT':
        edges, extra = hajos_apex()
        rows.append(decide('K1_join_hajos3_sulanke', edges, 600))
    out = dict(status='FINISHED', rows=rows, hajos_apex=extra, cpu_seconds_parent=time.process_time()-start,
               wall_seconds=sum(r['seconds'] for r in rows))
    (OUT/'P3_BIPLANARITY.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')


if __name__ == '__main__':
    main()
