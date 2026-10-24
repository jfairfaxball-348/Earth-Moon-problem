"""Independent replay of S040 coordinated neighborhoods.

Components: chord subsets plus direct polygon splitting (S039 replay strategy),
with NO opposite-layer filter, never importing the S038 filling recursion or the
S040 generator. Compatibility: final-layer bitmask intersection over the FULL
cartesian product. Scoring: --delta counts four-sets touched by changed union
pairs (numpy, local); default ORs Python-int four-set masks (stdlib, portable).
"""
from collections import Counter, defaultdict
import hashlib
import itertools as it
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s037_certificates import rotation
from replay_s038_neighborhoods import crossing
from replay_s039_stars import canon, cycle_edges, polygon_cells

N = 28
PAIRS = list(it.combinations(range(N), 2))
BIT = {e: 1 << i for i, e in enumerate(PAIRS)}


def mask(edges):
    m = 0
    for e in edges:
        m |= BIT[e]
    return m


def components(edges, faces, protected=frozenset()):
    """{(removed, added): final layer edge set} for relaxed degree3..6 stars."""
    out = {}
    for v in range(N):
        spokes = {e for e in edges if v in e}
        d = len(spokes)
        if not 3 <= d <= 6 or spokes & protected:
            continue
        selected = [i for i, face in enumerate(faces) if v in face]
        if len(selected) != d:
            continue
        counts = Counter(e for i in selected for e in cycle_edges(faces[i]))
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
        q = sum(len(faces[i]) == 4 for i in selected)
        if w != start or len(rim) != len(adj) or q > 1 or len(rim) != d+q:
            continue
        if set(rim) | {v} != {x for i in selected for x in faces[i]}:
            continue
        outside = edges-spokes
        outside_faces = [f for i, f in enumerate(faces) if i not in selected]
        boundary_edges = cycle_edges(rim)
        chords = [e for e in it.combinations(sorted(rim), 2) if e not in boundary_edges | outside]
        order = {x: i for i, x in enumerate(rim)}
        for ds in it.combinations(chords, d-3):
            if any(crossing(a, b, order) for a, b in it.combinations(ds, 2)):
                continue
            cells = polygon_cells(rim, ds)
            if sum(len(f) == 4 for f in cells) != q or not all(len(f) in (3, 4) for f in cells):
                continue
            base = outside | set(ds)
            for target in outside_faces+list(cells):
                if len(target) != 3:
                    continue
                new = base | {tuple(sorted((v, x))) for x in target}
                if new != edges:
                    out[tuple(sorted(edges-new)), tuple(sorted(new-edges))] = new
    return out


def load(path, pointer=('best',), checks='validation/S039/PAIR_CHECKS.json'):
    data = json.loads((ROOT/path).read_text())
    for key in pointer:
        data = data[key]
    row = next(r for r in json.loads((ROOT/checks).read_text())['rows'] if r['path'] == path and r['pointer'] == list(pointer))
    edges = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
    faces = [sorted(canon(f) for f in rotation(N, data[k], row['layers'][i]['rotation'])) for i, k in enumerate(('E1', 'E2'))]
    return edges, faces, data


def compatible(edges, comps):
    """All (key0, key1, type) with disjoint final layers; full cartesian product."""
    L = [mask(edges[0]), mask(edges[1])]
    rows = [[(key, mask(new), mask(key[1]) & L[1-k]) for key, new in comps[k].items()] for k in (0, 1)]
    out = []
    for key0, f0, c0 in rows[0]:
        for key1, f1, c1 in rows[1]:
            if not f0 & f1:
                out.append((key0, key1, bool(c0)+bool(c1)))
    return out


def or_scorer(edges):
    masks = {e: 0 for e in PAIRS}
    for i, vs in enumerate(it.combinations(range(N), 4)):
        for e in it.combinations(vs, 2):
            masks[e] |= 1 << i
    total = 20475
    cache = {}

    def layer_cov(new):
        key = frozenset(new)
        if key not in cache:
            m = 0
            for e in new:
                m |= masks[e]
            cache[key] = m
        return cache[key]
    return lambda f0, f1: total-(layer_cov(f0) | layer_cov(f1)).bit_count()


def delta_scorer(edges):
    import numpy as np
    fours = list(it.combinations(range(N), 4))
    by_pair = defaultdict(list)
    for i, vs in enumerate(fours):
        for e in it.combinations(vs, 2):
            by_pair[e].append(i)
    by_pair = {e: np.array(v, dtype=np.int32) for e, v in by_pair.items()}
    union = edges[0] | edges[1]
    count = np.zeros(len(fours), dtype=np.int16)
    for e in union:
        count[by_pair[e]] += 1
    base = int((count == 0).sum())

    def score(f0, f1):
        new = f0 | f1
        gone, came = union-new, new-union
        if not gone and not came:
            return base
        idx = np.concatenate([by_pair[e] for e in gone]+[by_pair[e] for e in came])
        weight = np.concatenate([np.full(len(by_pair[e]), -1, dtype=np.int16) for e in gone]
                                + [np.full(len(by_pair[e]), 1, dtype=np.int16) for e in came])
        cells, inverse = np.unique(idx, return_inverse=True)
        old = count[cells]
        now = old+np.bincount(inverse, weights=weight, minlength=len(cells)).astype(np.int16)
        return base+int(((now == 0) & (old > 0)).sum())-int(((old == 0) & (now > 0)).sum())
    return score


def table(path, delta=False):
    start = time.process_time()
    edges, faces, _ = load(path)
    comps = [components(edges[k], faces[k]) for k in (0, 1)]
    score = (delta_scorer if delta else or_scorer)(edges)
    rows = []
    for k in (0, 1):
        for (rem, add), new in comps[k].items():
            if not set(add) & edges[1-k]:
                f = [new, edges[1]] if k == 0 else [edges[0], new]
                rows.append(json.dumps(['single', k, [list(e) for e in rem], [list(e) for e in add], score(*f)], separators=(',', ':')))
    pairs = compatible(edges, comps)
    for key0, key1, kind in pairs:
        s = score(comps[0][key0], comps[1][key1])
        rows.append(json.dumps(['pair', kind, [list(e) for e in key0[0]], [list(e) for e in key0[1]],
                                [list(e) for e in key1[0]], [list(e) for e in key1[1]], s], separators=(',', ':')))
    rows.sort()
    by = Counter()
    minimum = {}
    for r in rows:
        x = json.loads(r)
        kind = 'single' if x[0] == 'single' else f'type{x[1]}'
        by[kind] += 1
        minimum[kind] = min(minimum.get(kind, 10**9), x[-1])
    return dict(components=[len(c) for c in comps], counts=dict(by), minimum=minimum,
                sha256=hashlib.sha256('\n'.join(rows).encode()).hexdigest(), rows=len(rows),
                cpu_seconds=time.process_time()-start)


def main():
    delta = '--delta' in sys.argv
    out = []
    for density in (156, 155):
        recorded = json.loads((ROOT/f'validation/S040/neighborhood-{density}.json').read_text())
        r = table(recorded['source'], delta)
        assert r['sha256'] == recorded['canonical_table_sha256'] and r['rows'] == recorded['table_rows']
        assert r['components'] == recorded['components']
        for kind, v in recorded['by_kind'].items():
            assert r['counts'].get(kind, 0) == v['count'] and r['minimum'].get(kind) == v['minimum']
        r.update(density=density, scorer='delta' if delta else 'or', status='PASS')
        print(json.dumps(r), flush=True)
        out.append(r)
    if delta:
        (ROOT/'validation/S040/NEIGHBORHOOD_REPLAY.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    return out


if __name__ == '__main__':
    main()
