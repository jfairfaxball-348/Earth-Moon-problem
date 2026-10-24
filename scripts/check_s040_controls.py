"""S040 pre-experiment controls: S039 reproduction, exact compatibility, sequential types."""
import gzip
import json
from pathlib import Path
import random
import sys
import time

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s038_patch import Plane, covered, universe
from s039_star import load_start
from s040_coordinated import Table, emask, faces_after, load_pair, single_scores

INPUTS = {156: 'validation/S039/arms/156-3900-star.json', 155: 'validation/S039/arms/155-3901-star.json'}


def sphere(faces, n=28):
    """Closed-surface link condition plus Euler characteristic two, and NetworkX planarity."""
    es = {tuple(sorted((a, b))) for f in faces for a, b in zip(f, f[1:]+f[:1])}
    for v in range(n):
        # Face corners at v form the link multigraph; a closed surface needs one cycle.
        corners = []
        for f in faces:
            if v in f:
                i = f.index(v)
                corners.append((f[i-1], f[(i+1) % len(f)]))
        degree = {}
        for a, b in corners:
            assert a != b
            degree[a] = degree.get(a, 0)+1; degree[b] = degree.get(b, 0)+1
        assert corners and set(degree.values()) == {2} and len(corners) == len(degree)
        reached, todo = set(), [corners[0][0]]
        while todo:
            w = todo.pop()
            if w not in reached:
                reached.add(w)
                todo += [b for a, b in corners if a == w]+[a for a, b in corners if b == w]
        assert reached == set(degree)
    g = nx.Graph(list(es))
    assert nx.is_connected(g) and g.number_of_nodes() == n and nx.check_planarity(g)[0]
    assert n-len(es)+len(faces) == 2
    return es


def reproduce_s039(cover, full):
    out = {}
    for density in (156, 155):
        planes, _, _ = load_start(density)
        frozen = json.loads(gzip.decompress((ROOT/f'validation/S039/neighborhood-{density}.json.gz').read_bytes()))
        expected = {(r['layer'], tuple(map(tuple, r['removed'])), tuple(map(tuple, r['added']))): r['score'] for r in frozen}
        actual = {}
        for k in (0, 1):
            t = Table(planes[k], planes[1-k].edges, cover)
            legal, scores = single_scores(t, covered(planes[1-k].edges, cover))
            for i, s in zip(legal, scores):
                rem, add = t.keys[i]
                actual[k, tuple(sorted(rem)), tuple(sorted(add))] = int(s)
        assert actual == expected, density
        out[density] = len(actual)
    assert out == {156: 766, 155: 1045}
    return out


def compatibility(path):
    planes, _ = load_pair(path)
    cover, _ = universe(28)
    t = [Table(planes[k], planes[1-k].edges, cover) for k in (0, 1)]
    L = [emask(p.edges) for p in planes]
    comp = []
    for k in (0, 1):
        rows = []
        for (rem, add) in t[k].keys:
            r, a = emask(rem), emask(add)
            assert r & L[k] == r and not a & L[k] and not r & a
            rows.append((r, a, a & L[1-k]))
        comp.append(rows)
    counts = [0, 0, 0]
    rejected = dict(unresolved_conflict=0, duplicate_addition=0)
    finals = [(L[1] & ~r1) | a1 for r1, a1, _ in comp[1]]
    for r0, a0, c0 in comp[0]:
        f0 = (L[0] & ~r0) | a0
        for (r1, a1, c1), f1 in zip(comp[1], finals):
            direct = not f0 & f1
            test = not (c0 & ~r1) and not (c1 & ~r0) and not (a0 & a1)
            assert direct == test
            if not direct:
                if a0 & a1:
                    rejected['duplicate_addition'] += 1
                else:
                    rejected['unresolved_conflict'] += 1
                continue
            kind = bool(c0)+bool(c1)
            counts[kind] += 1
            # Sequential decomposition: conflict-free component first, other then S039-legal.
            first_b = not c1 and not (a0 & f1)
            first_a = not c0 and not (a1 & f0)
            if kind == 0:
                assert first_a and first_b
            elif kind == 1:
                assert first_a or first_b
            else:
                assert not first_a and not first_b
    return t, planes, counts, rejected


def sampled_spheres(t, planes, rng, per_type=40):
    """Apply sampled compatible pairs and check both final layers as spheres."""
    checked = [0, 0, 0]
    pool = [[], [], []]
    for i in range(t[0].size):
        ok = ~((t[0].C[i] & ~t[1].R).any(1)) & ~((t[1].C & ~t[0].R[i]).any(1)) & ~((t[0].A[i] & t[1].A).any(1))
        for j in np.nonzero(ok)[0]:
            pool[int(t[0].conflicted[i])+int(t[1].conflicted[j])].append((i, int(j)))
    for kind in (0, 1, 2):
        for i, j in rng.sample(pool[kind], min(per_type, len(pool[kind]))):
            new = [faces_after(planes[0], t[0].effects[i]), faces_after(planes[1], t[1].effects[j])]
            es = [sphere(f) for f in new]
            assert not es[0] & es[1] and list(map(len, es)) == list(map(len, (p.edges for p in planes)))
            assert [sum(len(f) == 4 for f in fs) for fs in new] == [sum(len(f) == 4 for f in p.faces) for p in planes]
            for k, idx in ((0, i), (1, j)):
                rem, add = t[k].keys[idx]
                assert planes[k].edges-es[k] == rem and es[k]-planes[k].edges == add
            Plane(28, new[0]); Plane(28, new[1])
            checked[kind] += 1
    return checked


def protected_filter():
    core = json.loads((ROOT/'validation/sulanke.json').read_text())
    protected = [frozenset(map(tuple, core[k])) for k in ('edges_part1', 'edges_part2')]
    planes, _ = load_pair('validation/S039/protected/3912.json')
    assert all(protected[k] <= planes[k].edges for k in (0, 1))
    cover, _ = universe(28)
    sizes = []
    for k in (0, 1):
        t = Table(planes[k], planes[1-k].edges, cover, protected[k])
        assert all(not set(rem) & protected[k] for rem, _ in t.keys)
        sizes.append(t.size)
    return sizes


def main():
    start = time.process_time()
    cover, full = universe(28)
    rng = random.Random(4040)
    result = dict(status='PASS', s039_singles_reproduced=reproduce_s039(cover, full))
    for density, path in INPUTS.items():
        t, planes, counts, rejected = compatibility(path)
        result[str(density)] = dict(input=path, components=[t[0].size, t[1].size], compatible_by_type=counts,
                                    full_cartesian_pairs=t[0].size*t[1].size, rejected=rejected,
                                    sphere_checked_by_type=sampled_spheres(t, planes, rng))
        print(density, result[str(density)], flush=True)
    result['protected_component_sizes'] = protected_filter()
    result['cpu_seconds'] = time.process_time()-start
    (ROOT/'validation/S040/CONTROLS.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    print('S040 CONTROLS PASS', result['s039_singles_reproduced'], result['cpu_seconds'])


if __name__ == '__main__':
    main()
