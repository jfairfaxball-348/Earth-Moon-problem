#!/usr/bin/env python3
"""Certify the fixed CAM-0005 survivor list with standalone proof tools."""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from blowup_chi_cnf import bag_cnf, vertex_cnf
from blowup_graph import blowup
from blowup_census_check import tri_free_ok
import networkx as nx


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_cnf(p, nv, cls):
    p.write_text(f'p cnf {nv} {len(cls)}\n'+
                 ''.join(' '.join(map(str, c))+' 0\n' for c in cls), newline='\n')


def refute(cnf, proof, solver, checker):
    result = subprocess.run([solver, '-q', '--no-binary', str(cnf), str(proof)],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 20, result.stdout+result.stderr
    checked = subprocess.run([checker, str(cnf), str(proof), '-t', '600'],
                             capture_output=True, text=True, timeout=620)
    assert 's VERIFIED' in checked.stdout, checked.stdout+checked.stderr
    proof.with_suffix('.check.log').write_text(checked.stdout+checked.stderr)
    return {'cnf_sha256': digest(cnf), 'drat_sha256': digest(proof),
            'drat_bytes': proof.stat().st_size, 'checker': 'VERIFIED'}


def main(solver, checker):
    source = json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    out = Path('validation/S004/chi10')
    out.mkdir(parents=True, exist_ok=True)
    scratch = Path('artifacts/tmp/S004/chi10')
    scratch.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, (g6, w, _) in enumerate(source):
        g = nx.from_graph6_bytes(g6.encode())
        assert max(sum(w[i] for i in c) for c in nx.find_cliques(g)) <= 8
        for mask in range(1, 1 << len(w)):
            nodes = [i for i in range(len(w)) if mask >> i & 1]
            n = sum(w[i] for i in nodes)
            m = sum(w[i]*(w[i]-1)//2 for i in nodes)
            m += sum(w[a]*w[b] for a, b in g.subgraph(nodes).edges())
            assert n < 3 or m <= 6*n-12
        assert tri_free_ok(g, w)
        row = {'index': idx, 'g6': g6, 'w': w, 'N': sum(w), 'F1_F2_F3': 'PASS'}
        for mode, fn in [('bag', bag_cnf), ('vertex', vertex_cnf)]:
            nv, cls = fn(g6, w, 9)
            cnf = scratch / f'{idx:03d}-{mode}.cnf'
            proof = scratch / f'{idx:03d}-{mode}.drat'
            write_cnf(cnf, nv, cls)
            row[mode] = refute(cnf, proof, solver, checker)
            if mode == 'bag':
                gz = out / f'{idx:03d}-bag.drat.gz'
                with gzip.GzipFile(filename=str(gz), mode='wb', mtime=0) as f:
                    f.write(proof.read_bytes())
                row[mode]['archive'] = str(gz).replace('\\', '/')
            # Vertex proofs and CNFs remain in scratch, with hashes and
            # deterministic regeneration; bag proofs are retained in Git.
        nv, cls = vertex_cnf(g6, w, 10)
        cnf = scratch / f'{idx:03d}-vertex10.cnf'
        write_cnf(cnf, nv, cls)
        result = subprocess.run([solver, '-q', str(cnf)], capture_output=True,
                                text=True, timeout=60)
        assert result.returncode == 10
        positive = {int(t) for line in result.stdout.splitlines() if line.startswith('v ')
                    for t in line.split()[1:] if int(t) > 0}
        colour = [next(c for c in range(10) if v*10+c+1 in positive) for v in range(sum(w))]
        edges, bags = blowup(g6, w)
        assert all(colour[u] != colour[v] for u, v in edges)
        assert all(len({colour[v] for v in b}) == len(b) for b in bags)
        row['ten_colouring'] = colour
        rows.append(row)
        Path('validation/S004/chi10_results.json').write_text(json.dumps(rows, indent=1))
        print(idx, g6, w, 'bag/vertex DRAT VERIFIED, 10-colouring checked', flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:3])
