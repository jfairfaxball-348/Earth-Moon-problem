#!/usr/bin/env python3
"""S027 admitted-candidate audit against every certified obstruction.

cnf mode: for each obstruction write the audit-form quotient CNF (fixed nonedge
clauses, no y variables) and solve it with the pinned native CaDiCaL; UNSAT is
accepted only with drat-trim 's VERIFIED'. SAT is decoded and explicitly checked.
backtrack mode: the separate S025 count-vector backtracking (find_map), recorded
per obstruction until an external cap; a missing result is UNKNOWN.
Usage: s027_audit.py cnf|backtrack CANDIDATE_DIR
"""
import json
from pathlib import Path
import subprocess
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s027_contain import encode, explicit_map, load_obstructions   # noqa: E402
from s025_certify import certify                                    # noqa: E402
from s026_supervision import atomic_json                            # noqa: E402


def cnf_mode(d):
    c = json.loads((d / 'CANDIDATE.json').read_text())
    B = nx.from_graph6_bytes(c['g6'].encode())
    w = c['w']
    out = []
    for H in load_obstructions():
        sub = d / 'audit' / H['name']
        sub.mkdir(parents=True, exist_ok=True)
        cls, top, x, kinds = encode(H, w, B=B)
        cnf = sub / 'contain.cnf'
        cnf.write_text(f'p cnf {top} {len(cls)}\n' + ''.join(' '.join(map(str, k)) + ' 0\n' for k in cls),
                       newline='\n')
        proof = certify(cnf, sub, 120, 240)
        row = {'obstruction': H['name'], 'capacity_encodings': sorted(set(kinds)),
               'clauses': len(cls), 'proof': proof}
        if proof.get('verdict') == 'UNSAT_DRAT_VERIFIED':
            row['verdict'] = 'AVOIDS_DRAT_VERIFIED'
            import gzip
            import shutil
            with open(cnf, 'rb') as f, gzip.open(str(cnf) + '.gz', 'wb', 9) as g:
                shutil.copyfileobj(f, g)
            cnf.unlink()
        elif proof.get('solver_returncode') == 10:
            # Re-solve in-process to obtain a model, then check explicitly.
            from pysat.solvers import Solver
            with Solver(name='cadical195', bootstrap_with=cls) as s:
                assert s.solve()
                m = set(v for v in s.get_model() if v > 0)
            f = [next(b for b in range(len(w)) if x(v, b) in m) for v in range(H['n'])]
            row['vertex_map'] = explicit_map(H, w, f, list(B.edges()))
            row['f'] = f
            row['verdict'] = 'CONTAINS_EXPLICIT_CHECKED'
        else:
            row['verdict'] = 'UNKNOWN'
        out.append(row)
        atomic_json(d / 'AUDIT_CNF.json', out)
        print(H['name'], row['verdict'], flush=True)


def backtrack_mode(d):
    from s025_transfer import find_map
    c = json.loads((d / 'CANDIDATE.json').read_text())
    B = nx.from_graph6_bytes(c['g6'].encode())
    out = []
    for H in load_obstructions():
        A = nx.from_graph6_bytes(H['g6'].encode())
        a = find_map({i: set(A[i]) for i in A}, H['u'], B, c['w'])
        out.append({'obstruction': H['name'], 'contains': a is not None,
                    'bag_map': {str(k): v for k, v in a.items()} if a else None})
        atomic_json(d / 'AUDIT_BACKTRACK.json', out)
        print(H['name'], a is not None, flush=True)


if __name__ == '__main__':
    (cnf_mode if sys.argv[1] == 'cnf' else backtrack_mode)(Path(sys.argv[2]))
