"""Separate direct checker: does not import the search or its bitset objective."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]


def check(data, expected_density=None):
    n = data['n']
    assert data.get('V', list(range(n))) == list(range(n))
    sets = []
    layers = []
    for key in ('E1', 'E2'):
        raw = data[key]
        assert all(len(e) == 2 and 0 <= e[0] < e[1] < n for e in raw)
        es = set(map(tuple, raw))
        assert len(es) == len(raw)
        graph = nx.Graph()
        graph.add_nodes_from(range(n))
        graph.add_edges_from(raw)
        planar, embedding = nx.check_planarity(graph)
        assert planar, key+' nonplanar'
        embedding.check_structure()
        # Independently traverse the supplied rotation, checking each dart once.
        rotation = embedding.get_data()
        darts = {(a, b) for a in graph for b in graph[a]}
        seen, faces = set(), []
        for first in sorted(darts):
            if first in seen:
                continue
            face, dart = [], first
            while dart not in seen:
                seen.add(dart)
                a, b = dart
                face.append(a)
                around = rotation[b]
                dart = b, around[(around.index(a)-1) % len(around)]
            assert dart == first
            faces.append(face)
        assert seen == darts
        if nx.is_connected(graph):
            assert n-len(es)+len(faces) == 2
        sets.append(es)
        layers.append(dict(edges=len(es), planar=True, degree_sequence=sorted(dict(graph.degree()).values()),
                           rotation=rotation, face_sizes=sorted(map(len, faces))))
    assert sets[0].isdisjoint(sets[1]), 'layers overlap'
    es = sets[0] | sets[1]
    if expected_density is not None:
        assert len(es) == expected_density
        assert sorted(map(len, sets)) == ([3*n-7, 3*n-6] if expected_density == 6*n-13 else [3*n-6]*2)
    independent = []
    examined = 0
    for vs in itertools.combinations(range(n), 4):
        examined += 1
        if all((a, b) not in es for a, b in itertools.combinations(vs, 2)):
            independent.append(vs)
    if 'independent_four_sets' in data:
        assert len(independent) == data['independent_four_sets']
    g = nx.Graph()
    g.add_nodes_from(range(n)); g.add_edges_from(es)
    colour = nx.coloring.greedy_color(g, strategy='saturation_largest_first')
    assert all(colour[a] != colour[b] for a, b in es)
    return dict(n=n, edges=len(es), layers=layers, independent_four_sets=len(independent),
                four_sets_examined=examined, first_independent_four=independent[:10],
                proper_coloring=colour, proper_coloring_upper_bound=1+max(colour.values()),
                alpha_at_most_3=(len(independent) == 0),
                union_degree_sequence=sorted(dict(g.degree()).values()))


def main():
    start = time.process_time()
    rows = []
    paths = [p for folder in ('pairs', 'guided', 'permutation')
             for p in (ROOT/f'validation/S037/{folder}').glob('arm-*.json')]
    for p in sorted(paths):
        data = json.loads(p.read_text())
        if data['best'] is None:
            rows.append(dict(path=str(p.relative_to(ROOT)).replace('\\', '/'), no_feasible_pair=True))
            continue
        r = check(data['best'], data['density'])
        r.update(path=str(p.relative_to(ROOT)).replace('\\', '/'), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        rows.append(r)
    out = dict(status='PASS', cpu_seconds=time.process_time()-start, rows=rows,
               witness_found=any(r.get('alpha_at_most_3') for r in rows))
    (ROOT/'validation/S037/PAIR_CHECKS.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print('PASS', [(r['path'], r.get('independent_four_sets')) for r in rows])


if __name__ == '__main__':
    main()
