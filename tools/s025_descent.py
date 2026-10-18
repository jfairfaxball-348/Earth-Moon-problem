#!/usr/bin/env python3
"""S025: greedy descent to a small candidate obstruction inside a corpus row.

From weights w, evaluate every single-bag decrement by flip-annealing (SEEDS runs,
SECS each); keep the child with the largest minimum defect (ties: fewest edges).
Stops when every child reaches defect 0 (each such child has an independently
checked biplanar split).  Heuristic guidance only; no non-biplanarity claim.
Usage: s025_descent.py ROW SECS SEEDS WORKERS OUT.json [start_w]
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s025_subblowup import job             # noqa: E402

if __name__ == '__main__':
    row, secs, seeds, workers, outp = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    corpus = json.loads((ROOT / 'validation/S003/survivors_alpha_ge3.json').read_text())
    g6 = corpus[row][0]
    w = [int(t) for t in sys.argv[6].split(',')] if len(sys.argv) > 6 else list(corpus[row][1])
    log = []
    with ProcessPoolExecutor(workers) as ex:
        while True:
            kids = []
            for i in range(len(w)):
                if w[i] > 0:
                    c = list(w)
                    c[i] -= 1
                    kids.append(c)
            res = list(ex.map(job, [(g6, c, s, secs) for c in kids for s in range(1, seeds + 1)]))
            table = []
            for c in kids:
                rs = [r for r in res if r['w'] == c]
                table.append({'w': c, 'n': rs[0]['n'], 'm': rs[0]['m'],
                              'min_defect': min(r['best'] for r in rs),
                              'splits_checked': sum(1 for r in rs if r.get('split_checked'))})
            step = {'parent': w, 'children': table}
            log.append(step)
            print(json.dumps(step), flush=True)
            Path(outp).write_text(json.dumps({'row': row, 'g6': g6, 'secs': secs, 'seeds': seeds, 'log': log}))
            live = [t for t in table if t['min_defect'] > 0]
            if not live:
                break
            best = max(live, key=lambda t: (t['min_defect'], -t['m']))
            w = best['w']
    print('CANDIDATE', w)
