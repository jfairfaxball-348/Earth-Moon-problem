#!/usr/bin/env python3
"""S025: re-solve a CNF with the pinned native CaDiCaL writing a DRAT proof, check it
with the pinned drat-trim, and archive the gzipped proof with SHA-256 records.

A solver's UNSAT exit alone is never accepted: only 's VERIFIED' from drat-trim.
Usage: s025_certify.py CNF OUTDIR [SOLVER_SECONDS] [CHECK_SECONDS]
Environment: EMP_CADICAL, EMP_DRAT_TRIM (absolute paths).
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def certify(cnf, outdir, solve_cap=36000, check_cap=36000):
    solver = os.environ['EMP_CADICAL']
    checker = os.environ['EMP_DRAT_TRIM']
    cnf = Path(cnf)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    proof = outdir / (cnf.stem + '.drat')
    t = time.time()
    run = subprocess.run([solver, '-q', '--no-binary', str(cnf), str(proof)],
                         capture_output=True, text=True, timeout=solve_cap)
    solve_s = time.time() - t
    rec = {'cnf': str(cnf), 'cnf_sha256': sha(cnf), 'solver': solver, 'solver_sha256': sha(solver),
           'solver_returncode': run.returncode, 'solve_seconds': round(solve_s, 2)}
    if run.returncode != 20:
        rec['verdict'] = 'NOT_UNSAT'
        rec['solver_tail'] = run.stdout[-2000:]
        return rec
    t = time.time()
    chk = subprocess.run([checker, str(cnf), str(proof), '-t', str(check_cap)],
                         capture_output=True, text=True, timeout=check_cap + 120)
    rec.update(checker=checker, checker_sha256=sha(checker), check_seconds=round(time.time() - t, 2),
               drat_sha256=sha(proof), drat_bytes=proof.stat().st_size,
               checker_tail=chk.stdout[-1500:])
    rec['verdict'] = 'UNSAT_DRAT_VERIFIED' if 's VERIFIED' in chk.stdout else 'CHECK_FAILED'
    gz = proof.with_suffix('.drat.gz')
    with open(proof, 'rb') as f, gzip.open(gz, 'wb', compresslevel=9) as g:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            g.write(chunk)
    rec['drat_gz'] = str(gz)
    rec['drat_gz_sha256'] = sha(gz)
    proof.unlink()
    return rec


if __name__ == '__main__':
    cnf, outdir = sys.argv[1], sys.argv[2]
    a = float(sys.argv[3]) if len(sys.argv) > 3 else 36000
    b = float(sys.argv[4]) if len(sys.argv) > 4 else 36000
    rec = certify(cnf, outdir, a, b)
    Path(outdir, Path(cnf).stem + '.certificate.json').write_text(json.dumps(rec, indent=1))
    print(json.dumps({k: v for k, v in rec.items() if 'tail' not in k}))
