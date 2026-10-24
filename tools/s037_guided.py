"""Score all legal flips against the exact four-set objective; bounded tabu walk."""
import json
from pathlib import Path
import random
import sys
import time
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_pairs import Tri, masks, independent, serialise
from s037_check_pair import check


def as_tri(n, edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(n)); graph.add_edges_from(edges)
    ok, embedding = nx.check_planarity(graph)
    assert ok
    if len(edges) == 3*n-7:
        marked = set()
        faces = [embedding.traverse_face(a, b, marked) for a, b in embedding.edges() if (a, b) not in marked]
        q = next(f for f in faces if len(f) == 4)
        diagonal = next(tuple(sorted((q[i], q[i+2]))) for i in (0, 1)
                        if not graph.has_edge(q[i], q[i+2]))
        graph.add_edge(*diagonal)
        ok, embedding = nx.check_planarity(graph)
        assert ok
    marked = set()
    faces = [embedding.traverse_face(a, b, marked) for a, b in embedding.edges() if (a, b) not in marked]
    assert all(len(f) == 3 for f in faces)
    return Tri(n, faces)


def run(data, number):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    rng = random.Random(number)
    n, density = data['n'], data['density']
    _, cover, full = masks(n)
    ts = [as_tri(n, data[k]) for k in ('E1', 'E2')]
    inds = [independent(t, cover, full) for t in ts]
    best, tabu, progress = data, {}, []
    evaluations = last_improve = 0
    stop = 'SWEEP_CAP'
    for sweep in range(2000):
        if time.process_time()-start_cpu >= 30:
            stop = 'CPU_CAP'
            break
        if sweep-last_improve >= 300:
            stop = 'PLATEAU_300_SWEEPS'
            break
        choices = []
        for k in (0, 1):
            for e in sorted(ts[k].inc):
                new = ts[k].flip(e)
                if new is None:
                    continue
                overlap = len(ts[0].inc.keys() & ts[1].inc.keys())
                if overlap <= 156-density:
                    value = (independent(ts[k], cover, full) & inds[1-k]).bit_count()
                    evaluations += 1
                    if tabu.get((k, e), -1) < sweep or value < best['independent_four_sets']:
                        choices.append((value, rng.random(), k, e, new))
                assert ts[k].flip(new) == e
        if not choices:
            stop = 'NO_ADMISSIBLE_FLIP'
            break
        value, _, k, e, new = min(choices)
        assert ts[k].flip(e) == new
        inds[k] = independent(ts[k], cover, full)
        tabu[k, new] = sweep+7
        if value < best['independent_four_sets']:
            candidate = serialise(ts, density, cover, full,
                                  dict(seed=number, mode='all-legal-flip-tabu', sweep=sweep))
            if candidate['independent_four_sets'] < best['independent_four_sets']:
                best, last_improve = candidate, sweep
                progress.append([sweep, best['independent_four_sets'], time.process_time()-start_cpu])
        if best['independent_four_sets'] == 0:
            stop = 'ALPHA3_PAIR_REQUIRES_CHECK'
            break
    result = check(best, density)
    return dict(seed=number, density=density, sweeps=sweep+1, evaluations=evaluations,
                stop=stop, best=best, progress=progress,
                best_checked_violations=result['independent_four_sets'],
                cpu_seconds=time.process_time()-start_cpu, wall_seconds=time.monotonic()-start_wall,
                verdict='HEURISTIC_UNKNOWN')


if __name__ == '__main__':
    assert json.loads((ROOT/'validation/S037/CONTROLS.json').read_text())['status'] == 'PASS'
    out = ROOT/'validation/S037/guided'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, arm in enumerate((0, 3, 2, 11)):
        data = json.loads((ROOT/f'validation/S037/pairs/arm-{arm:02d}.json').read_text())['best']
        r = run(data, 3712+i)
        (out/f'arm-{i:02d}.json').write_text(json.dumps(r, indent=2)+'\n', newline='\n')
        rows.append({k: v for k, v in r.items() if k not in ('best', 'progress')})
        (out/'SUMMARY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
        print(json.dumps(rows[-1]), flush=True)
