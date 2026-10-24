"""Independent star enumeration using chord subsets and direct polygon splitting."""
from collections import Counter, defaultdict
import gzip
import itertools as it
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s037_certificates import rotation
from replay_s038_neighborhoods import crossing


def canon(xs):
    xs = tuple(xs)
    return min(xs[i:]+xs[:i] for xs in (xs, xs[::-1]) for i in range(len(xs)))


def cycle_edges(face):
    return {tuple(sorted((a, b))) for a, b in zip(face, face[1:]+face[:1])}


def polygon_cells(poly, diagonals):
    cells = [list(poly)]
    for a, b in sorted(diagonals):
        chosen = None
        for i, cell in enumerate(cells):
            if a not in cell or b not in cell:
                continue
            ia, ib = sorted((cell.index(a), cell.index(b)))
            if ib-ia not in (1, len(cell)-1):
                chosen = i, ia, ib
                break
        assert chosen is not None
        i, ia, ib = chosen
        cell = cells.pop(i)
        cells += [cell[ia:ib+1], cell[ib:]+cell[:ia+1]]
    return tuple(sorted(canon(cell) for cell in cells))


def enumerate_independent(edges, faces, masks, full):
    output = {}
    for k in (0, 1):
        for v in range(28):
            spokes = {e for e in edges[k] if v in e}
            d = len(spokes)
            if not 3 <= d <= 6:
                continue
            selected = [i for i, face in enumerate(faces[k]) if v in face]
            if len(selected) != d:
                continue
            counts = Counter(e for i in selected for e in cycle_edges(faces[k][i]))
            if {e for e, c in counts.items() if c == 2} != spokes:
                continue
            adj = defaultdict(set)
            for (a, b), count in counts.items():
                if count == 1:
                    adj[a].add(b); adj[b].add(a)
            if v in adj or any(len(ns) != 2 for ns in adj.values()):
                continue
            start = min(adj)
            rim, prev, w = [start], start, min(adj[start])
            while w != start and w not in rim:
                rim.append(w)
                nxt = next(t for t in adj[w] if t != prev)
                prev, w = w, nxt
            q = sum(len(faces[k][i]) == 4 for i in selected)
            if w != start or len(rim) != len(adj) or q > 1 or len(rim) != d+q:
                continue
            if set(rim) | {v} != {x for i in selected for x in faces[k][i]}:
                continue
            outside = edges[k]-spokes
            outside_faces = [f for i, f in enumerate(faces[k]) if i not in selected]
            boundary_edges = cycle_edges(rim)
            chords = [e for e in it.combinations(sorted(rim), 2) if e not in boundary_edges | outside | edges[1-k]]
            order = {x: i for i, x in enumerate(rim)}
            for ds in it.combinations(chords, d-3):
                if any(crossing(a, b, order) for a, b in it.combinations(ds, 2)):
                    continue
                cells = polygon_cells(rim, ds)
                assert sum(len(f) == 4 for f in cells) == q and all(len(f) in (3, 4) for f in cells)
                base = outside | set(ds)
                for target in outside_faces+list(cells):
                    if len(target) != 3:
                        continue
                    added = {tuple(sorted((v, x))) for x in target}
                    if added & edges[1-k]:
                        continue
                    new = base | added
                    if new == edges[k]:
                        continue
                    hits = 0
                    for e in new | edges[1-k]:
                        hits |= masks[e]
                    key = k, tuple(sorted(edges[k]-new)), tuple(sorted(new-edges[k]))
                    output[key] = (full ^ hits).bit_count()
    return output


def replay(density):
    start = time.process_time()
    source = f'validation/S038/arms/{density}-3800-patch.json'
    data = json.loads((ROOT/source).read_text())['best']
    record = next(r for r in json.loads((ROOT/'validation/S038/PAIR_CHECKS.json').read_text())['rows']
                  if r['path'] == source and r['pointer'] == ['best'])
    es = [set(map(tuple, data[key])) for key in ('E1', 'E2')]
    faces = [[canon(f) for f in rotation(28, data[key], record['layers'][i]['rotation'])] for i, key in enumerate(('E1', 'E2'))]
    masks = {e: 0 for e in it.combinations(range(28), 2)}
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            masks[e] |= 1 << i
    actual = enumerate_independent(es, faces, masks, (1 << 20475)-1)
    rows = json.loads(gzip.decompress((ROOT/f'validation/S039/neighborhood-{density}.json.gz').read_bytes()))
    expected = {(r['layer'], tuple(map(tuple, r['removed'])), tuple(map(tuple, r['added']))): r['score'] for r in rows}
    assert actual == expected
    result = dict(status='PASS', density=density, neighbors=len(actual), minimum_score=min(actual.values()),
                  strict_improvements=sum(v < data['independent_four_sets'] for v in actual.values()), cpu_seconds=time.process_time()-start)
    print(result, flush=True)
    return result


if __name__ == '__main__':
    rows = [replay(d) for d in (156, 155)]
    (ROOT/'validation/S039/NEIGHBORHOOD_REPLAY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
