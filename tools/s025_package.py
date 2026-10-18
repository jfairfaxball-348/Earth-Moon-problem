#!/usr/bin/env python3
"""S025: assemble compact permanent evidence under validation/S025 from artifacts/tmp/S025.

Writes C5_CLASSIFY.json.gz (all 297 orbits, min defects, every explicit split),
C5_CERTIFICATES.json (per-graph CEGAR/justification/DRAT records), certs/ (edge files,
gzipped lemma JSON from which tools/s025_regen_cnf.py rebuilds the CNF byte-for-byte,
gzipped DRAT proofs), ROW148_ANNEAL.json, DESCENT148.json, SWEEP_271.json,
ENGINE_CONTROLS.json, ARM_A_FRONTIER.json.
"""
import glob
import gzip
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / 'artifacts/tmp/S025'
V = ROOT / 'validation/S025'
V.mkdir(parents=True, exist_ok=True)
(V / 'certs').mkdir(exist_ok=True)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gz_json(obj, path):
    with gzip.open(path, 'wt', compresslevel=9) as f:
        json.dump(obj, f)


def lines(path):
    return [json.loads(l) for l in open(path) if l.startswith('{')]


# C5 classification
cls = json.loads((T / 'c5/classify.json').read_text())
gz_json(cls, V / 'C5_CLASSIFY.json.gz')

# certificates
certs = []
for f in sorted(glob.glob(str(T / 'cert/C5-*.certificate.json'))):
    rec = json.loads(Path(f).read_text())
    tag = rec['tag']
    if not rec.get('certified'):
        certs.append({'tag': tag, 'certified': False})
        continue
    shutil.copy(T / f'c5/C5-{tag}.edges', V / f'certs/C5-{tag}.edges')
    with open(T / f'c5/mC_{tag}.lemmas.json', 'rb') as a, gzip.open(V / f'certs/C5-{tag}.lemmas.json.gz', 'wb', 9) as b:
        shutil.copyfileobj(a, b)
    shutil.copy(T / f'cert/mC_{tag}.drat.gz', V / f'certs/C5-{tag}.drat.gz')
    d = rec['drat']
    certs.append({'tag': tag, 'graph': 'C5[' + ','.join(tag) + ']', 'certified': True,
                  'cegar': rec['cegar'], 'justification': rec['justification'],
                  'edges_sha256': rec['edges_sha256'], 'lemmas_json_sha256': rec['lemmas_sha256'],
                  'cnf_sha256': d['cnf_sha256'], 'solver_sha256': d['solver_sha256'],
                  'solve_seconds': d['solve_seconds'], 'checker_sha256': d['checker_sha256'],
                  'check_seconds': d['check_seconds'], 'drat_sha256': d['drat_sha256'],
                  'drat_bytes': d['drat_bytes'], 'drat_verdict': d['verdict'],
                  'drat_gz_sha256': sha(V / f'certs/C5-{tag}.drat.gz'),
                  'lemmas_gz_sha256': sha(V / f'certs/C5-{tag}.lemmas.json.gz'),
                  'reproduce': f'tools/s025_regen_cnf.py validation/S025/certs/C5-{tag}.edges '
                               f'validation/S025/certs/C5-{tag}.lemmas.json.gz OUT.cnf; gunzip drat; '
                               f'drat-trim OUT.cnf C5-{tag}.drat'})
(V / 'C5_CERTIFICATES.json').write_text(json.dumps(certs, indent=1))

# row148 annealing runs
r148 = []
for f in [T / 'ca_148_s1.json'] + sorted(Path(p) for p in glob.glob(str(T / 'r148/s*.json'))):
    r = json.loads(f.read_text())
    r148.append({k: r[k] for k in ('seed', 'moves', 'seconds', 'best_uncovered')} |
                {'best_faces': r['best_faces']})
(V / 'ROW148_ANNEAL.json').write_text(json.dumps({'input_sha256': '4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598',
                                                  'note': 'heuristic positive search; best_faces are two sphere triangulations covering all but best_uncovered G-edges',
                                                  'runs': r148}))
# descent and sweep
(V / 'DESCENT148.json').write_text((T / 'descent148.json').read_text())
sw = lines(T / 'sweep.log')
(V / 'SWEEP_271.json').write_text(json.dumps({'seconds_per_row': 60, 'seed': 1, 'heuristic_only': True, 'rows': sw}))

# engine controls (triangulation-cover SAT + annealer)
ctrl = {}
for f in glob.glob(str(T / 'cov_*.json')) + glob.glob(str(T / 'ca_*.json')) + glob.glob(str(T / 'chrom_*.json')) + \
        glob.glob(str(T / 'ind*_n*.json')):
    r = json.loads(Path(f).read_text())
    ctrl[Path(f).name] = {k: v for k, v in r.items() if k not in ('layers_faces', 'layers_edges', 'E1', 'E2', 'best_faces')}
(V / 'ENGINE_CONTROLS.json').write_text(json.dumps(ctrl, indent=1))

# Arm A frontier
fr = []
for f in sorted(glob.glob(str(T / 'sa/*.log')) + glob.glob(str(T / 'wsa/*.log'))):
    t = [l for l in open(f).read().splitlines() if l.startswith('{')]
    if t:
        d = json.loads(t[-1])
        fr.append({'file': Path(f).name, 'n': d['n'], 'W': d['alpha'],
                   'anchors_weight2': sum(d.get('weights', [1] * d['n'])) - d['n'],
                   'seed': d['seed'], 'seconds': d['seconds'], 'moves': d['moves'],
                   'best_bad_sets': d['best_indep_sets']})
    else:
        fr.append({'file': Path(f).name, 'status': 'NOT_COMPLETED'})
(V / 'ARM_A_FRONTIER.json').write_text(json.dumps({'objective': 'number of independent sets of weight >= W+1 in the union of two annealed sphere triangulations; 0 certifies chi >= ceil(w(V)/W)',
                                                   'heuristic_only': True, 'runs': fr}, indent=1))
print('certified', sum(c['certified'] for c in certs), 'of', len(certs))
