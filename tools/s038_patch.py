"""Disk-patch enumeration on actual plane layers, including deficit-one layers.

No global completeness claim. A patch is a tree of <=4 faces with simple
boundary and no interior vertex. All fillings keep the outside embedding fixed.
"""
from collections import Counter, defaultdict
from functools import lru_cache
import itertools as it
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def edge(a, b):
    return (a, b) if a < b else (b, a)


def canonical(cycle):
    xs = tuple(cycle)
    return min(xs[i:]+xs[:i] for xs in (xs, xs[::-1]) for i in range(len(xs)))


def cycle_edges(face):
    return [edge(a, b) for a, b in zip(face, face[1:]+face[:1])]


def boundary(faces):
    counts = Counter(e for f in faces for e in cycle_edges(f))
    if any(c > 2 for c in counts.values()):
        return None
    rim = [e for e, c in counts.items() if c == 1]
    adj = defaultdict(list)
    for a, b in rim:
        adj[a].append(b); adj[b].append(a)
    if not adj or any(len(ns) != 2 for ns in adj.values()):
        return None
    start = min(adj)
    order, prev, v = [start], start, min(adj[start])
    while v != start:
        if v in order:
            return None
        order.append(v)
        nxt = next(x for x in adj[v] if x != prev)
        prev, v = v, nxt
    if len(order) != len(adj):
        return None
    return canonical(order)


class Plane:
    def __init__(self, n, faces):
        self.n = n
        self.faces = tuple(sorted(canonical(f) for f in faces))
        assert len(set(self.faces)) == len(self.faces)
        self.inc = defaultdict(list)
        for i, face in enumerate(self.faces):
            assert len(face) in (3, 4) and len(set(face)) == len(face)
            for e in cycle_edges(face):
                self.inc[e].append(i)
        assert all(len(fs) == 2 for fs in self.inc.values())
        self.edges = frozenset(self.inc)
        self.dual = [set() for _ in self.faces]
        for a, b in self.inc.values():
            self.dual[a].add(b); self.dual[b].add(a)

    def patches(self, max_removed=3):
        groups = {frozenset([i]) for i in range(len(self.faces))}
        output = []
        for r in range(1, max_removed+1):
            groups = {group | {j} for group in groups
                      for j in set().union(*(self.dual[i] for i in group))-group}
            for group in sorted(groups, key=lambda g: tuple(sorted(g))):
                internal = {e for e, fs in self.inc.items() if all(i in group for i in fs)}
                if len(internal) != r:
                    continue
                faces = [self.faces[i] for i in sorted(group)]
                rim = boundary(faces)
                q = sum(len(f) == 4 for f in faces)
                if rim is None or q > 1 or len(rim) != r+3+q:
                    continue
                if set(rim) != set().union(*map(set, faces)):
                    continue
                output.append(dict(r=r, selected=tuple(sorted(group)), removed=frozenset(internal),
                                   boundary=rim, quadrilateral=bool(q)))
        return output

    def replace(self, patch, faces):
        selected = set(patch['selected'])
        return Plane(self.n, [f for i, f in enumerate(self.faces) if i not in selected]+list(faces))


@lru_cache(maxsize=4096)
def triangulations(poly):
    if len(poly) < 3:
        return ((frozenset(), ()),)
    output = []
    for k in range(1, len(poly)-1):
        for left, lf in triangulations(poly[:k+1]):
            for right, rf in triangulations(poly[k:]):
                ds = set(left | right)
                if k > 1:
                    ds.add(edge(poly[0], poly[k]))
                if k < len(poly)-2:
                    ds.add(edge(poly[k], poly[-1]))
                output.append((frozenset(ds), tuple(sorted(lf+rf+(canonical((poly[0], poly[k], poly[-1])),)))))
    return tuple(output)


@lru_cache(maxsize=4096)
def fillings(poly, quadrilateral):
    if not quadrilateral:
        return triangulations(poly)
    result = {}
    for diagonals, faces in triangulations(poly):
        for deleted in diagonals:
            adjacent = [f for f in faces if deleted in cycle_edges(f)]
            assert len(adjacent) == 2
            quad = boundary(adjacent)
            assert quad and len(quad) == 4
            ds = diagonals-{deleted}
            fs = tuple(sorted([f for f in faces if f not in adjacent]+[quad]))
            result[ds] = fs
    return tuple(sorted(result.items(), key=lambda p: tuple(sorted(p[0]))))


def universe(n):
    fours = list(it.combinations(range(n), 4))
    cover = {e: 0 for e in it.combinations(range(n), 2)}
    for i, vs in enumerate(fours):
        for e in it.combinations(vs, 2):
            cover[e] |= 1 << i
    return cover, (1 << len(fours))-1


def covered(edges, cover):
    mask = 0
    for e in edges:
        mask |= cover[e]
    return mask


def candidates(planes, cover, full, sizes=(1, 2, 3), guided_limit=None):
    current_bad = full ^ covered(planes[0].edges | planes[1].edges, cover)
    multi = []
    singles = []
    for k, plane in enumerate(planes):
        other = planes[1-k].edges
        for patch in plane.patches(max(sizes)):
            if patch['r'] not in sizes:
                continue
            outside = plane.edges-patch['removed']
            legal = [(ds, fs) for ds, fs in fillings(patch['boundary'], patch['quadrilateral'])
                     if not ds & (outside | other) and ds != patch['removed']]
            if not legal:
                continue
            potential = (current_bad & covered(set().union(*(ds for ds, _ in legal)), cover)).bit_count()
            item = (-potential, k, patch, legal, outside)
            (singles if patch['r'] == 1 else multi).append(item)
    multi.sort(key=lambda item: (item[0], item[1], item[2]['selected']))
    if guided_limit is not None:
        multi = multi[:guided_limit]
    for _, k, patch, legal, outside in singles+multi:
        uncovered = full ^ covered(outside | planes[1-k].edges, cover)
        for ds, fs in legal:
            value = (uncovered & ~covered(ds, cover)).bit_count()
            yield value, k, patch, ds, fs


def explicit(planes, value):
    return dict(n=planes[0].n, V=list(range(planes[0].n)), E1=sorted(planes[0].edges),
                E2=sorted(planes[1].edges), independent_four_sets=value,
                density=len(planes[0].edges)+len(planes[1].edges))


def load_start(density):
    from s037_certificates import rotation
    checks = json.loads((ROOT/'validation/S037/PAIR_CHECKS.json').read_text())
    source = ('validation/S037/guided/arm-00.json' if density == 156 else 'validation/S037/pairs/arm-03.json')
    record = next(r for r in checks['rows'] if r['path'] == source)
    data = json.loads((ROOT/source).read_text())['best']
    planes = [Plane(28, rotation(28, data[key], record['layers'][k]['rotation']))
              for k, key in enumerate(('E1', 'E2'))]
    return planes, data, source


def move_record(k, patch, diagonals, faces, score):
    return dict(layer=k, support_removed=sorted(patch['removed']),
                boundary=patch['boundary'], selected_faces=patch['selected'],
                quadrilateral=patch['quadrilateral'], diagonals=sorted(diagonals),
                filling=faces, removed=sorted(patch['removed']-diagonals),
                added=sorted(diagonals-patch['removed']), score=score)
