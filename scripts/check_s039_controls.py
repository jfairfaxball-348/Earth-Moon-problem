"""Controls for vertex bookkeeping, both deficit cases and protected core."""
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s039_star import core, load_start, star_candidates
from s038_patch import Plane, universe, explicit
from s037_check_pair import check


if __name__ == '__main__':
    start = time.process_time()
    assert json.loads((ROOT/'validation/S039/SMOKE.json').read_text())['verdict'] == 'PASS'
    planes, protected, colours, proof = core()
    for k, p in enumerate(planes):
        assert len(p.edges) == [26, 24][k]
    cover, full = universe(28)
    rng = random.Random(3899)
    counts = dict(ordinary=0, quad_incident=0, inside_hole=0, elsewhere=0)
    sampled = 0
    for density in (156, 155):
        planes, data, source = load_start(density)
        moves = list(star_candidates(planes, cover, full))
        assert moves
        selected = rng.sample(moves, min(50, len(moves)))
        quad_moves = [m for m in moves if m[3]['quad_incident']]
        if quad_moves:
            selected += rng.sample(quad_moves, min(10, len(quad_moves)))
        for value, k, fs, move in selected:
            trial = list(planes); trial[k] = Plane(28, fs)
            assert len(trial[k].edges) == len(planes[k].edges)
            assert len([e for e in trial[k].edges if move['vertex'] in e]) == 3
            assert not trial[0].edges & trial[1].edges
            check(explicit(trial, value), density)
            assert sum(len(f) == 4 for p in trial for f in p.faces) == 156-density
            counts['quad_incident' if move['quad_incident'] else 'ordinary'] += 1
            counts['inside_hole' if move['target_inside_hole'] else 'elsewhere'] += 1
            sampled += 1
    assert counts['ordinary'] and counts['quad_incident'] and counts['elsewhere']
    result = dict(status='PASS', seed=3899, checked_moves=sampled, cases=counts, core=proof,
                  omitted='degree2, degree>6, nonsimple links; all recorded as unsearched',
                  cpu_seconds=time.process_time()-start)
    (ROOT/'validation/S039/CONTROLS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    print(result)
