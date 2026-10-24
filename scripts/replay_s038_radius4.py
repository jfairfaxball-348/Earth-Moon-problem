"""Independent removed-edge/chord-subset replay of the final diagnostic."""
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
    check = next(r for r in json.loads((ROOT/'validation/S037/PAIR_CHECKS.json').read_text())['rows'] if r['path'] == source)
    edges = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
    faces = [rotation(28, data[k], check['layers'][i]['rotation']) for i, k in enumerate(('E1', 'E2'))]
    edge_masks = {e: 0 for e in it.combinations(range(28), 2)}
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            edge_masks[e] |= 1 << i
    full = (1 << 20475)-1
    def hit(es):
        bits = 0
        for e in es:
            bits |= edge_masks[e]
        return bits
    one = {}
    for k in (0, 1):
        for (removed, added), es in enumerate_moves(28, edges[k], faces[k], 4, edges[1-k]).items():
            one[k, removed, added] = (full ^ hit(es | edges[1-k])).bit_count()
    rows = json.loads(gzip.decompress((ROOT/f'validation/S038/radius4/{density}-one.json.gz').read_bytes()))
    expected = {(r['layer'], tuple(map(tuple, r['removed'])), tuple(map(tuple, r['added']))): r['score'] for r in rows}
    assert one == expected
    raw = [enumerate_moves(28, edges[k], faces[k], 2, set()) for k in (0, 1)]
    masks = [{key: hit(es) for key, es in moves.items()} for moves in raw]
    two = {(key0, key1): (full & ~(masks[0][key0] | masks[1][key1])).bit_count()
           for key0, es0 in raw[0].items() for key1, es1 in raw[1].items() if not es0 & es1}
    rows = json.loads(gzip.decompress((ROOT/f'validation/S038/radius4/{density}-two.json.gz').read_bytes()))
    expected = {tuple(tuple(tuple(map(tuple, side)) for side in key) for key in r['moves']): r['score'] for r in rows}
    assert two == expected
    result = dict(status='PASS', density=density, one_neighbors=len(one), one_minimum=min(one.values()),
                  joint_neighbors=len(two), joint_minimum=min(two.values()), cpu_seconds=time.process_time()-start)
    print(result, flush=True)
    return result


if __name__ == '__main__':
    rows = [replay(d) for d in (156, 155)]
    (ROOT/'validation/S038/RADIUS4_REPLAY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
