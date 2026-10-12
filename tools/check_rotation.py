"""Stdlib certificate checker for connected orientable genus-zero rotations.

Independent of NetworkX and embedding generation. A cyclic neighbour order
defines an orientable ribbon surface. Capping each dart orbit gives a connected
closed orientable surface; Euler characteristic 2 certifies a sphere embedding.
This checker deliberately rejects disconnected layers and isolated vertices.
"""
import json
import sys


def check(n, edges, rotation):
    assert type(n) is int and n >= 2
    canonical = [tuple(sorted(e)) for e in edges]
    assert len(set(canonical)) == len(canonical)
    assert all(type(u) is int and type(v) is int and 0 <= u < v < n
               for u, v in canonical)
    adjacency = {v: set() for v in range(n)}
    for u, v in canonical:
        adjacency[u].add(v)
        adjacency[v].add(u)
    assert set(rotation) == {str(v) for v in range(n)}
    predecessor = {}
    for v in range(n):
        row = rotation[str(v)]
        assert row and len(row) == len(set(row))
        assert set(row) == adjacency[v]
        for i, u in enumerate(row):
            predecessor[v, u] = row[i - 1]
    reached, pending = set(), [0]
    while pending:
        v = pending.pop()
        if v not in reached:
            reached.add(v)
            pending.extend(adjacency[v] - reached)
    assert len(reached) == n
    darts = {(u, v) for u in adjacency for v in adjacency[u]}
    seen, faces = set(), []
    for start in sorted(darts):
        if start in seen:
            continue
        cur, face = start, []
        while cur not in seen:
            seen.add(cur)
            face.append(cur[0])
            u, v = cur
            cur = (v, predecessor[v, u])
        assert cur == start
        faces.append(face)
    assert seen == darts
    assert n - len(edges) + len(faces) == 2
    return {"vertices": n, "edges": len(edges), "faces": len(faces),
            "euler_characteristic": 2}


def check_file(path):
    with open(path, encoding='utf8') as handle:
        data = json.load(handle)
    n = data['num_vertices']
    edge_sets = [set(map(tuple, data[key])) for key in ('edges_part1', 'edges_part2')]
    assert not (edge_sets[0] & edge_sets[1])
    results = [check(n, data[key], data['rotations'][i])
               for i, key in enumerate(('edges_part1', 'edges_part2'))]
    colors = data['coloring']
    assert len(colors) == n
    assert all(colors[u] != colors[v] for edges in edge_sets for u, v in edges)
    return {"layers": results, "proper_colouring_uses": len(set(colors)),
            "chromatic_lower_bound_checked_by_this_script": False}


if __name__ == '__main__':
    print(json.dumps(check_file(sys.argv[1]), indent=2))
