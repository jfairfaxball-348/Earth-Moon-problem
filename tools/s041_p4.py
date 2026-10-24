"""S041 probes P3b/P4: exact biplanarity of apex leaf graphs with the S025 K9-minor CEGAR."""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import rotation

WORK = ROOT/'artifacts/tmp/S041/p4'


def hajos_complete(k, offset):
    """Hajos(K_k, K_k) on 2k-1 labels from offset; unique up to isomorphism."""
    one = [offset+i for i in range(k)]
    two = [offset] + [offset+k-1+i for i in range(1, k)]
    edges = set(it.combinations(one, 2)) | {tuple(sorted(e)) for e in it.combinations(two, 2)}
    edges -= {(one[0], one[1]), tuple(sorted((two[0], two[1])))}
    edges.add(tuple(sorted((one[1], two[1]))))
    return sorted(edges), sorted(set(one) | set(two))


def join(small_edges, small_vertices, big_edges, big_vertices):
    return sorted(set(small_edges) | set(big_edges) | {tuple(sorted((a, b))) for a in small_vertices for b in big_vertices})


def leaf_graphs():
    hb, vb = hajos_complete(6, 4)
    # K4-e on 0..3: apex 0 joined to 1,2,3; 1-2 and 1-3 present; 2-3 missing.
    lb = join([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)], [0, 1, 2, 3], hb, vb)
    hc, vc = hajos_complete(7, 3)
    lc = join([(0, 1), (0, 2)], [0, 1, 2], hc, vc)
    return {'leaf_K4e_join_hajosK6K6': lb, 'leaf_K3e_join_hajosK7K7': lc}


def facts(edges):
    g = nx.Graph(edges)
    n = g.number_of_nodes()
    return dict(vertices=n, edges=len(edges), budget=6*n-12, clique_number=max(len(c) for c in nx.find_cliques(g)))


def decide(name, edges, cap):
    WORK.mkdir(parents=True, exist_ok=True)
    edgefile = WORK/f'{name}.txt'
    edgefile.write_text(''.join(f'{a} {b}\n' for a, b in edges), newline='\n')
    prefix = (WORK/name).as_posix()
    rec = dict(name=name, edges_sha256=hashlib.sha256(edgefile.read_bytes()).hexdigest(), **facts(edges))
    for seed in (4101, 4102):
        out = WORK/f'{name}-anneal-{seed}.json'
        subprocess.run([sys.executable, 'tools/s025_cover_anneal.py', edgefile.as_posix(), str(seed), '45', out.as_posix()],
                       cwd=ROOT, capture_output=True, text=True)
        res = json.loads(out.read_text())
        rec[f'anneal_{seed}_best_uncovered'] = res['best_uncovered']
        if res['best_uncovered'] == 0:
            layers = [sorted(tuple(e) for e in res[k]) for k in ('E1', 'E2')]
            assert not set(layers[0]) & set(layers[1]) and set(layers[0]) | set(layers[1]) == set(edges)
            for layer in layers:
                g = nx.Graph(); g.add_nodes_from(range(rec['vertices'])); g.add_edges_from(layer)
                ok, emb = nx.check_planarity(g)
                assert ok
                if nx.is_connected(g):
                    rotation(rec['vertices'], layer, {v: list(w) for v, w in emb.get_data().items()})
            rec.update(verdict='BIPLANAR_EXPLICIT_SPLIT', E1=layers[0], E2=layers[1])
            return rec
    run = subprocess.run([sys.executable, 'tools/s025_minor_cegar.py', edgefile.as_posix(), prefix, str(cap), '--lemmaC', '5'],
                         cwd=ROOT, capture_output=True, text=True)
    info = json.loads(run.stdout.strip().splitlines()[-1])
    rec['minor_cegar'] = info
    if info['verdict'] == 'UNSAT':
        cert = subprocess.run([sys.executable, 'tools/s025_certify.py', prefix+'.cnf', (WORK/f'{name}-proof').as_posix(), '600', '600'],
                              cwd=ROOT, capture_output=True, text=True)
        chk = subprocess.run([sys.executable, 'tools/s025_check_minor_cert.py', edgefile.as_posix(), prefix],
                             cwd=ROOT, capture_output=True, text=True)
        c, k = json.loads(cert.stdout.strip().splitlines()[-1]), json.loads(chk.stdout.strip().splitlines()[-1])
        ok = c['verdict'] == 'UNSAT_DRAT_VERIFIED' and k['verdict'] == 'ALL_CLAUSES_JUSTIFIED'
        rec.update(verdict='NONBIPLANAR_DRAT_VERIFIED' if ok else 'UNKNOWN', certify=c, structure=k)
    elif info['verdict'] == 'SAT':
        split = json.loads(Path(prefix+'.split.json').read_text())
        rec.update(verdict='BIPLANAR_EXPLICIT_SPLIT_FROM_CEGAR', E1=split['E1'], E2=split['E2'])
    else:
        rec['verdict'] = 'UNKNOWN_CAPPED'
    return rec


def main():
    which = sys.argv[1]
    if which == 'p3b':
        src = ROOT/'artifacts/tmp/S041/p3/K5_join_bipyramid.txt'
        edges = [tuple(map(int, l.split())) for l in src.read_text().splitlines() if l.strip()]
        rows = [decide('K5_join_bipyramid', edges, 420)]
    else:
        rows = [decide(name, edges, 180) for name, edges in leaf_graphs().items()]
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k not in ('E1', 'E2', 'certify', 'structure')}), flush=True)
    (ROOT/f'validation/S041/{which.upper()}_LEAVES.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')


if __name__ == '__main__':
    main()
