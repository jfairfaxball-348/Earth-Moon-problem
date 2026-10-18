#!/usr/bin/env python3
"""S025 CAM-0028 sweep: flip-annealing cover search on the original 271 corpus rows.

Each row is the exact chi=10 clique blow-up of validation/S003/survivors_alpha_ge3.json
(labels as tools/blowup_graph.py).  The 219 BIPLANARITY_UNKNOWN rows are the targets;
the 52 certified NONBIPLANAR rows are negative controls (a zero there would expose a bug).
Usage: s025_sweep.py OUTDIR SECONDS WORKERS SEED [rows...]
"""
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from blowup_graph import blowup            # noqa: E402
from s025_cover_anneal import anneal       # noqa: E402


def job(args):
    row, seconds, seed, outdir = args
    corpus = json.loads((ROOT / 'validation/S003/survivors_alpha_ge3.json').read_text())
    g6, w = corpus[row][0], corpus[row][1]
    edges, _ = blowup(g6, w)
    n = sum(w)
    text = ''.join(f'{u} {v}\n' for u, v in edges)
    res = anneal(n, edges, seed, seconds)
    res.update(row=row, g6=g6, weights=w, n=n, m=len(edges),
               edges_sha256=hashlib.sha256(text.encode()).hexdigest())
    if res['best_uncovered'] == 0:
        import itertools
        T0 = {e for f in res['best_faces'][0] for e in itertools.combinations(f, 2)}
        res['E1'] = sorted(e for e in edges if e in T0)
        res['E2'] = sorted(e for e in edges if e not in T0)
        res['layers_faces'] = res['best_faces']
    Path(outdir, f'row{row:03d}_s{seed}.json').write_text(json.dumps(res))
    return {k: res[k] for k in ('row', 'n', 'm', 'best_uncovered', 'moves')}


def main():
    outdir, seconds, workers, seed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    Path(outdir).mkdir(parents=True, exist_ok=True)
    summary = json.loads((ROOT / 'validation/S018/SUMMARY.json').read_text())
    unknown = summary['canonical_original_unknown']
    rows = [int(r) for r in sys.argv[5:]] or list(range(271))
    t = time.time()
    out = []
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(job, [(row, seconds, seed, outdir) for row in rows]):
            r['status'] = 'UNKNOWN' if r['row'] in unknown else 'NONBIPLANAR_CERTIFIED'
            out.append(r)
            print(json.dumps(r), flush=True)
    Path(outdir, f'SWEEP_s{seed}.json').write_text(json.dumps(
        {'seconds_per_row': seconds, 'seed': seed, 'workers': workers,
         'wall': round(time.time() - t, 1), 'rows': out}))


if __name__ == '__main__':
    main()
