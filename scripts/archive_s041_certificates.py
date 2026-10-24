"""Archive S041 P3b/P4 non-biplanarity certificates (no new search).

P3b was first run interactively (disclosed); this collects its anneal results, CEGAR
verdict and DRAT receipt, re-runs only the clause-justification checker, and copies
gzipped CNF/lemma/DRAT files with SHA-256 for P3b and P4 into validation/S041.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT/'artifacts/tmp/S041'
OUT = ROOT/'validation/S041/certificates'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gz(src, dst):
    dst.write_bytes(gzip.compress(Path(src).read_bytes(), mtime=0))
    return dict(path=str(dst.relative_to(ROOT)).replace('\\', '/'), sha256=sha(dst), source_sha256=sha(src))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    edgefile = TMP/'p3/K5_join_bipyramid.txt'
    chk = subprocess.run([sys.executable, 'tools/s025_check_minor_cert.py', edgefile.as_posix(), (TMP/'p3b/minor').as_posix()],
                         cwd=ROOT, capture_output=True, text=True)
    p3b = dict(name='K5_join_bipyramid', edges_sha256=sha(edgefile), vertices=12, edges=60, budget=60, clique_number=8,
               anneal_4101_best_uncovered=json.loads((TMP/'p3b/anneal-4101.json').read_text())['best_uncovered'],
               anneal_4102_best_uncovered=json.loads((TMP/'p3b/anneal-4102.json').read_text())['best_uncovered'],
               minor_cegar=json.loads((TMP/'p3b/minor.result.json').read_text()),
               certify=json.loads((TMP/'p3b/proof/minor.certificate.json').read_text()),
               structure=json.loads(chk.stdout.strip().splitlines()[-1]))
    ok = p3b['certify']['verdict'] == 'UNSAT_DRAT_VERIFIED' and p3b['structure']['verdict'] == 'ALL_CLAUSES_JUSTIFIED'
    p3b['verdict'] = 'NONBIPLANAR_DRAT_VERIFIED' if ok else 'UNKNOWN'
    (ROOT/'validation/S041/P3B_LEAVES.json').write_text(json.dumps([p3b], indent=2)+'\n', newline='\n')
    archive = {}
    items = [('K5_join_bipyramid', TMP/'p3/K5_join_bipyramid.txt', TMP/'p3b/minor', TMP/'p3b/proof/minor.drat.gz')]
    for name in ('leaf_K4e_join_hajosK6K6', 'leaf_K3e_join_hajosK7K7'):
        items.append((name, TMP/f'p4/{name}.txt', TMP/f'p4/{name}', TMP/f'p4/{name}-proof/{name}.drat.gz'))
    for name, edges, prefix, drat in items:
        shutil.copyfile(edges, OUT/f'{name}.edges.txt')
        archive[name] = dict(edges=dict(path=f'validation/S041/certificates/{name}.edges.txt', sha256=sha(OUT/f'{name}.edges.txt')),
                             cnf=gz(f'{prefix}.cnf', OUT/f'{name}.cnf.gz'),
                             lemmas=gz(f'{prefix}.lemmas.json', OUT/f'{name}.lemmas.json.gz'),
                             drat_gz=dict(path=f'validation/S041/certificates/{name}.drat.gz', sha256=sha(drat)))
        shutil.copyfile(drat, OUT/f'{name}.drat.gz')
    (OUT/'INDEX.json').write_text(json.dumps(archive, indent=2)+'\n', newline='\n')
    print('archived', list(archive), 'P3b', p3b['verdict'])


if __name__ == '__main__':
    main()
