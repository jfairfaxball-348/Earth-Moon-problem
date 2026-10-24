"""S042 certificate archival policy (no new search).

The census wrote edges, CNF, lemma and DRAT archives into validation/S042/certificates
(261 MB). CNF and lemma files are a deterministic function of the edge list
(tools/s025_minor_cegar.py --lemmaC 5 refuted every leaf in one iteration with no
Kuratowski lemma; byte-identical regeneration checked). They move to the ignored
artifacts/tmp/S042/certificates_local and stay pinned by SHA-256; edges and DRAT stay in the
repository. --verify regenerates every CNF/lemma file from its committed edge list and
re-runs pinned drat-trim on the committed DRAT proof (local, long).
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT/'validation/S042/certificates'
LOCAL = ROOT/'artifacts/tmp/S042/certificates_local'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def relocate():
    LOCAL.mkdir(parents=True, exist_ok=True)
    decisions = json.loads((ROOT/'validation/S042/DECISIONS.json').read_text())['decisions']
    rows = []
    for d in decisions:
        arch = d['archive']
        row = dict(name=d['name'], edges=arch['edges'], drat_gz=arch['drat_gz'], local={})
        for key in ('cnf', 'lemmas'):
            src = ROOT/arch[key]['path']
            if src.exists():
                shutil.move(str(src), LOCAL/src.name)
            row['local'][key] = dict(path=str((LOCAL/src.name).relative_to(ROOT)).replace('\\', '/'),
                                     gz_sha256=arch[key]['sha256'], source_sha256=arch[key]['source_sha256'])
        rows.append(row)
    out = dict(policy='edges and DRAT committed; CNF and lemma files local, deterministic from edges, SHA-256 pinned',
               regeneration='tools/s025_minor_cegar.py EDGES PREFIX 300 --lemmaC 5', rows=rows)
    (ROOT/'validation/S042/ARCHIVE.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print('relocated', 2*len(rows), 'files; committed', sum(1 for _ in CERT.iterdir()), 'files')


def verify():
    solver, checker = os.environ['EMP_CADICAL'], os.environ['EMP_DRAT_TRIM']
    work = ROOT/'artifacts/tmp/S042/verify'
    work.mkdir(parents=True, exist_ok=True)
    arch = json.loads((ROOT/'validation/S042/ARCHIVE.json').read_text())
    ok = 0
    for row in arch['rows']:
        edges = work/f"{row['name']}.txt"
        edges.write_bytes(gzip.decompress((ROOT/row['edges']['path']).read_bytes()))
        prefix = (work/row['name']).as_posix()
        subprocess.run([sys.executable, 'tools/s025_minor_cegar.py', edges.as_posix(), prefix, '300', '--lemmaC', '5'],
                       cwd=ROOT, capture_output=True, text=True, check=True)
        assert sha(prefix+'.cnf') == row['local']['cnf']['source_sha256']
        assert sha(prefix+'.lemmas.json') == row['local']['lemmas']['source_sha256']
        drat = work/f"{row['name']}.drat"
        drat.write_bytes(gzip.decompress((ROOT/row['drat_gz']['path']).read_bytes()))
        r = subprocess.run([checker, prefix+'.cnf', str(drat)], capture_output=True, text=True)
        assert 's VERIFIED' in r.stdout, row['name']
        ok += 1
    out = dict(status='PASS', verified=ok, checker_sha256=sha(checker), solver_sha256=sha(solver),
               method='regenerate CNF/lemmas from committed edges, assert pinned SHA-256, drat-trim on committed DRAT')
    (ROOT/'validation/S042/LOCAL_VERIFY.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print('verified', ok, 'regenerated CNFs against committed DRAT proofs')


if __name__ == '__main__':
    verify() if '--verify' in sys.argv else relocate()
