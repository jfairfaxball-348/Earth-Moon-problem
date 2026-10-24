"""Stdlib certificate checks, independent of NetworkX and search bitsets."""
import itertools as it


def subdivision(edges):
    es = [tuple(sorted(e)) for e in edges]
    assert len(set(es)) == len(es)
    adj = {}
    for a, b in es:
        assert a != b
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen, todo = set(), [next(iter(adj))]
    while todo:
        v = todo.pop()
        if v not in seen:
            seen.add(v); todo.extend(adj[v]-seen)
    assert seen == set(adj)
    for v in list(adj):
        if v in adj and len(adj[v]) == 2:
            a, b = adj[v]
            assert b not in adj[a]
            adj[a].remove(v); adj[b].remove(v); del adj[v]
            adj[a].add(b); adj[b].add(a)
    if len(adj) == 5:
        assert all(len(ns) == 4 for ns in adj.values())
        return 'K5'
    assert len(adj) == 6 and all(len(ns) == 3 for ns in adj.values())
    colour = {next(iter(adj)): 0}
    todo = list(colour)
    while todo:
        v = todo.pop()
        for w in adj[v]:
            if w not in colour:
                colour[w] = 1-colour[v]; todo.append(w)
            else:
                assert colour[w] != colour[v]
    assert len(colour) == 6
    return 'K33'


def rotation(n, edges, data):
    es = set(map(tuple, edges))
    neighbors = {v: set() for v in range(n)}
    for a, b in es:
        neighbors[a].add(b); neighbors[b].add(a)
    rot = {int(k): vs for k, vs in data.items()}
    assert set(rot) == set(range(n))
    assert all(set(rot[v]) == neighbors[v] and len(rot[v]) == len(neighbors[v]) for v in range(n))
    # Connected orientable map + Euler characteristic two certifies the sphere.
    reached, todo = set(), [0]
    while todo:
        v = todo.pop()
        if v not in reached:
            reached.add(v); todo.extend(neighbors[v]-reached)
    assert len(reached) == n
    darts = {(a, b) for a in rot for b in rot[a]}
    seen, faces = set(), []
    for first in sorted(darts):
        if first in seen:
            continue
        dart, face = first, []
        while dart not in seen:
            seen.add(dart)
            a, b = dart
            face.append(a)
            around = rot[b]
            dart = b, around[(around.index(a)-1) % len(around)]
        assert dart == first
        faces.append(face)
    assert seen == darts and n-len(es)+len(faces) == 2
    return faces


def four_sets(n, e1, e2):
    es = set(map(tuple, e1)) | set(map(tuple, e2))
    return sum(not any(e in es for e in it.combinations(vs, 2)) for vs in it.combinations(range(n), 4))
