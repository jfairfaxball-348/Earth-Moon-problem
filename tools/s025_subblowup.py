#!/usr/bin/env python3
"""S025: flip-annealing on sub-blowups B[w'] (w' <= w) of a corpus row, to locate small
candidate non-biplanar induced subgraphs (positive results are certified splits;
positive objectives are only heuristic leads for the exact Kuratowski CEGAR).
Usage: s025_subblowup.py ROW SECONDS SEEDS WORKERS OUT.json w'1 w'2 ...   (each w' as 1,5,2,...)
"""
import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from blowup_graph import blowup            # noqa: E402
from s025_cover_anneal import anneal       # noqa: E402
from s025_check import check_split         # noqa: E402


def compact(g6, w):
    """Blow-up with zero-weight bags removed (labels consecutive)."""
    import networkx as nx
    g = nx.from_graph6_bytes(g6.encode())
    keep = [i for i in range(len(w)) if w[i] > 0]
    h = nx.relabel_nodes(g.subgraph(keep), {v: k for k, v in enumerate(keep)})
    return nx.to_graph6_bytes(h, header=False).decode().strip(), [w[i] for i in keep]


def job(a):
    g6, w, seed, secs = a
    cg, cw = compact(g6, w)
    edges, _ = blowup(cg, cw)
    n = sum(cw)
    r = anneal(n, edges, seed, secs)
    out = {'w': w, 'seed': seed, 'n': n, 'm': len(edges), 'best': r['best_uncovered'],
           'moves': r['moves']}
    if r['best_uncovered'] == 0:
        T0 = {e for f in r['best_faces'][0] for e in itertools.combinations(f, 2)}
        E1 = sorted(e for e in edges if e in T0)
        E2 = sorted(e for e in edges if e not in T0)
        check_split(n, edges, E1, E2)
        out.update(E1=E1, E2=E2, split_checked=True)
    return out


if __name__ == '__main__':
    row, secs, seeds, workers, outp = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    corpus = json.loads((ROOT / 'validation/S003/survivors_alpha_ge3.json').read_text())
    g6 = corpus[row][0]
    ws = [[int(t) for t in s.split(',')] for s in sys.argv[6:]]
    jobs = [(g6, w, s, secs) for w in ws for s in range(1, seeds + 1)]
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for r in ex.map(job, jobs):
            res.append(r)
            print(json.dumps({k: v for k, v in r.items() if k not in ('E1', 'E2')}), flush=True)
    Path(outp).write_text(json.dumps({'row': row, 'g6': g6, 'seconds': secs, 'results': res}))
