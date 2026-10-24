"""Controls for complete small polygon fillings and actual plane patches."""
import itertools as it
import json
from pathlib import Path
import random
import sys
import time
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import Plane, boundary, candidates, explicit, fillings, load_start, universe
from s037_check_pair import check


def cross(a, b, n):
    if set(a) & set(b):
        return False
    u, v = sorted(a)
    return (u < b[0] < v) != (u < b[1] < v)


def main():
    start = time.process_time()
    assert json.loads((ROOT/'validation/S038/SMOKE.json').read_text())['verdict'] == 'PASS'
    rows = []
    for n, expected, near in ((4, 2, 1), (5, 5, 5), (6, 14, 21), (7, 42, 84), (8, 132, 330)):
        poly = tuple(range(n))
        boundary_edges = {(i, i+1) for i in range(n-1)} | {(0, n-1)}
        chords = [e for e in it.combinations(range(n), 2) if e not in boundary_edges]
        for deficit, count in ((0, expected), (1, near)):
            independent = {frozenset(es) for es in it.combinations(chords, n-3-deficit)
                           if not any(cross(a, b, n) for a, b in it.combinations(es, 2))}
            produced = fillings(poly, bool(deficit))
            assert len(produced) == count and {ds for ds, _ in produced} == independent
            rows.append(dict(vertices=n, deficit=deficit, exact_fillings=count))
    assert boundary([(0, 1, 2), (3, 4, 5)]) is None
    assert boundary([(0, 1, 2), (0, 1, 3), (0, 1, 4)]) is None
    assert cross((0, 2), (1, 3), 4)
    try:
        Plane(4, [(0, 1, 2), (0, 1, 2)])
    except AssertionError:
        pass
    else:
        raise AssertionError('duplicate faces accepted')
    rng = random.Random(3799)
    cover, full = universe(28)
    moves_checked = 0
    for density in (156, 155):
        planes, data, source = load_start(density)
        assert check(data, density)['independent_four_sets'] == (91 if density == 156 else 125)
        choices = list(candidates(planes, cover, full))
        for value, k, patch, ds, faces in rng.sample(choices, min(40, len(choices))):
            trial = list(planes)
            trial[k] = planes[k].replace(patch, faces)
            assert trial[k].edges == planes[k].edges-patch['removed'] | ds
            checked = check(explicit(trial, value), density)
            assert checked['independent_four_sets'] == value
            assert sum(len(f) == 4 for t in trial for f in t.faces) == 156-density
            moves_checked += 1
        assert not any(ds & planes[1-k].edges for _, k, _, ds, _ in choices)
    record = dict(status='PASS', seed=3799, polygons=rows, independently_checked_patch_moves=moves_checked,
                  invalid_disconnected_boundary_rejected=True, duplicate_faces_rejected=True,
                  direct_four_set_score_checks=True, cpu_seconds=time.process_time()-start)
    (ROOT/'validation/S038/CONTROLS.json').write_text(json.dumps(record, indent=2)+'\n', newline='\n')
    print(record)


if __name__ == '__main__':
    main()
