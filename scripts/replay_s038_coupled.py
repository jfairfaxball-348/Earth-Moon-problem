"""Independent joint neighborhood replay using brute chord subsets."""
import gzip
import itertools as it
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s037_certificates import rotation
from replay_s038_neighborhoods import enumerate_moves


def replay(density):
    start = time.process_time()
    source = 'validation/S037/guided/arm-00.json' if density == 156 else 'validation/S037/pairs/arm-03.json'
    data = json.loads((ROOT/source).read_text())['best']
    record = next(r for r in json.loads((ROOT/'validation/S037/PAIR_CHECKS.json').read_text())['rows'] if r['path'] == source)
    es = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
    faces = [rotation(28, data[k], record['layers'][i]['rotation']) for i, k in enumerate(('E1', 'E2'))]
    raw = {(k, r): enumerate_moves(28, es[k], faces[k], r, set()) for k in (0, 1) for r in (1, 2)}
    edge_masks = {e: 0 for e in it.combinations(range(28), 2)}
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            edge_masks[e] |= 1 << i
    full = (1 << 20475)-1
    def mask(edges):
        v = 0
        for e in edges:
            v |= edge_masks[e]
        return v
    hits = {(k, r): {key: mask(edges) for key, edges in moves.items()} for (k, r), moves in raw.items()}
    actual = {}
    for split in ((1, 1), (1, 2), (2, 1)):
        for key0, edges0 in raw[0, split[0]].items():
            for key1, edges1 in raw[1, split[1]].items():
                if edges0 & edges1:
                    continue
                actual[split, key0, key1] = (full & ~(hits[0, split[0]][key0] | hits[1, split[1]][key1])).bit_count()
    rows = json.loads(gzip.decompress((ROOT/f'validation/S038/coupled/neighborhood-{density}.json.gz').read_bytes()))
    expected = {(tuple(r['split']), tuple(tuple(map(tuple, side)) for side in r['moves'][0]),
                 tuple(tuple(map(tuple, side)) for side in r['moves'][1])): r['score'] for r in rows}
    assert actual == expected
    result = dict(status='PASS', density=density, joint_neighbors_replayed=len(actual),
                  minimum_score=min(actual.values()), cpu_seconds=time.process_time()-start)
    print(result, flush=True)
    return result


if __name__ == '__main__':
    rows = [replay(d) for d in (156, 155)]
    (ROOT/'validation/S038/COUPLED_REPLAY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
