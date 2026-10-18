#!/usr/bin/env python3
"""S025: classify small C5 clique blow-ups C5[w] by flip-annealing (positives are
independently checked splits; positive defects are heuristic leads only).

Filters (each a proved necessary condition for biplanarity, used only to skip):
 K9: w_i + w_{i+1} <= 8 (else K9 subgraph, programme-certified non-biplanar);
 Euler: m <= 6n-12;  triangle-free cross edges: sum w_i w_{i+1} <= 2(2n-4) since
 the edges between consecutive bags form a triangle-free graph (C5 has no triangle)
 and a planar triangle-free graph on n>=3 vertices has <= 2n-4 edges.
Usage: s025_c5_classify.py NMAX SECS SEEDS WORKERS OUT.json
"""
import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s025_subblowup import job   # noqa: E402

C5 = 'Dhc'


def canon(w):
    rots = [tuple(w[i:] + w[:i]) for i in range(5)]
    rots += [tuple(reversed(r)) for r in rots]
    return min(rots)


def stats(w):
    n = sum(w)
    m = sum(x * (x - 1) // 2 for x in w) + sum(w[i] * w[(i + 1) % 5] for i in range(5))
    cross = sum(w[i] * w[(i + 1) % 5] for i in range(5))
    return n, m, cross


def candidates(nmax):
    out = set()
    for w in itertools.product(range(1, 9), repeat=5):
        if sum(w) > nmax:
            continue
        w = list(w)
        if any(w[i] + w[(i + 1) % 5] > 8 for i in range(5)):
            continue
        n, m, cross = stats(w)
        if m > 6 * n - 12 or cross > 4 * n - 8:
            continue
        out.add(canon(w))
    return sorted(out, key=lambda w: (sum(w), w))


if __name__ == '__main__':
    nmax, secs, seeds, workers, outp = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    ws = candidates(nmax)
    print(len(ws), 'candidates', flush=True)
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(job, [(C5, list(w), s, secs) for w in ws for s in range(1, seeds + 1)]):
            res.append(r)
            print(json.dumps({k: v for k, v in r.items() if k not in ('E1', 'E2')}), flush=True)
            Path(outp).write_text(json.dumps({'graph6': C5, 'secs': secs, 'results': res}))
