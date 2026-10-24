"""Independent brute removed-edge/chord-subset enumeration, stdlib only.

Does not import the patch generator, its polygon recursion, or its scorer.
"""
from collections import Counter, defaultdict
import gzip
import itertools as it
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import rotation, four_sets


def crossing(e, f, order):
    if set(e) & set(f):
        return False
    a, b = sorted(order[v] for v in e)
    return (a < order[f[0]] < b) != (a < order[f[1]] < b)


def enumerate_moves(n, edges, faces, r, forbidden):
    inc = defaultdict(set)
    for i, face in enumerate(faces):
        for a, b in zip(face, face[1:]+face[:1]):
            inc[tuple(sorted((a, b)))].add(i)
    result = {}
    for removed in it.combinations(sorted(edges), r):
        selected = set().union(*(inc[e] for e in removed))
        if len(selected) != r+1:
            continue
        counts = Counter(tuple(sorted((a, b))) for i in selected
                         for a, b in zip(faces[i], faces[i][1:]+faces[i][:1]))
        if {e for e, c in counts.items() if c == 2} != set(removed):
            continue
        rim_edges = [e for e, c in counts.items() if c == 1]
        adj = defaultdict(set)
        for a, b in rim_edges:
            adj[a].add(b); adj[b].add(a)
        if any(len(ns) != 2 for ns in adj.values()):
            continue
        start = min(adj)
        poly, prev, v = [start], start, min(adj[start])
        while v != start and v not in poly:
            poly.append(v)
            following = next(w for w in adj[v] if w != prev)
            prev, v = v, following
        if v != start or len(poly) != len(adj):
            continue
        selected_vertices = {v for i in selected for v in faces[i]}
        q = sum(len(faces[i]) == 4 for i in selected)
        if selected_vertices != set(poly) or q > 1 or len(poly) != r+3+q:
            continue
        outside = edges-set(removed)
        order = {v: i for i, v in enumerate(poly)}
        chords = [e for e in it.combinations(sorted(poly), 2)
                  if e not in counts or counts[e] == 2]
        chords = [e for e in chords if e not in outside | forbidden]
        for ds in it.combinations(chords, r):
            diagonals = set(ds)
            if diagonals == set(removed) or any(crossing(e, f, order) for e, f in it.combinations(ds, 2)):
                continue
            actual_removed, actual_added = tuple(sorted(set(removed)-diagonals)), tuple(sorted(diagonals-set(removed)))
            result[actual_removed, actual_added] = outside | diagonals
    return result


def replay(density):
    start = time.process_time()
    source = 'validation/S037/guided/arm-00.json' if density == 156 else 'validation/S037/pairs/arm-03.json'
    data = json.loads((ROOT/source).read_text())['best']
    checked = next(r for r in json.loads((ROOT/'validation/S037/PAIR_CHECKS.json').read_text())['rows'] if r['path'] == source)
    edges = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
    faces = [rotation(28, data[k], checked['layers'][i]['rotation']) for i, k in enumerate(('E1', 'E2'))]
    expected = json.loads(gzip.decompress((ROOT/f'validation/S038/neighborhood-{density}.json.gz').read_bytes()))
    expected_map = {(row['support_size'], row['layer'], tuple(map(tuple, row['removed'])), tuple(map(tuple, row['added']))): row['score'] for row in expected}
    # Independent construction of Boolean incidence masks, no search imports.
    edge_masks = defaultdict(int)
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            edge_masks[e] += 1 << i
    full = (1 << 20475)-1
    actual = {}
    summary = []
    for r in (1, 2, 3):
        scores = []
        for k in (0, 1):
            moves = enumerate_moves(28, edges[k], faces[k], r, edges[1-k])
            for (removed, added), es in moves.items():
                hit = 0
                for e in es | edges[1-k]:
                    hit |= edge_masks[e]
                value = (full ^ hit).bit_count()
                actual[r, k, removed, added] = value
                scores.append(value)
        summary.append(dict(support_size=r, distinct_neighbors=len(scores), minimum_score=min(scores)))
    assert actual == expected_map, 'Generator and independent chord-subset replay disagree'
    assert four_sets(28, data['E1'], data['E2']) == (91 if density == 156 else 125)
    result = dict(status='PASS', density=density, neighbors_replayed=len(actual),
                  by_support=summary, cpu_seconds=time.process_time()-start)
    print(result, flush=True)
    return result


if __name__ == '__main__':
    rows = [replay(density) for density in (156, 155)]
    (ROOT/'validation/S038/NEIGHBORHOOD_REPLAY.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
