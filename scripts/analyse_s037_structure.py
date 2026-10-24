"""Finite structural diagnostics; no solver and no global exclusion claim."""
import itertools as it
import json
from pathlib import Path
import sys
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_check_pair import check


def quads(n, edges):
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    ok, embedding = nx.check_planarity(g)
    assert ok
    marked = set()
    return [embedding.traverse_face(a, b, marked) for a, b in embedding.edges() if (a, b) not in marked]


def main():
    hitting = json.loads((ROOT/'validation/S037/HITTING.json').read_text())
    lower = hitting[0]
    assert lower['result'] == 'SAT_RELAXATION' and lower['second_edges_required'] == 77
    # The failed 78-edge solve is retained. A direct supergraph settles only
    # this relaxed existence question, and remains nonplanar by heredity.
    e1, e2 = set(map(tuple, lower['E1'])), set(map(tuple, lower['E2']))
    added = next(e for e in it.combinations(range(28), 2) if e not in e1 | e2)
    expanded = e2 | {added}
    assert len(expanded) == 78 and not e1 & expanded
    assert all(any(e in e1 | expanded for e in it.combinations(vs, 2)) for vs in it.combinations(range(28), 4))
    assert not nx.is_planar(nx.Graph(expanded))
    derived = dict(status='SAT_RELAXATION_BY_EXPLICIT_EDGE_ADDITION', n=28, E1=sorted(e1),
                   E2=sorted(expanded), added_edge=added, independent_four_sets=0,
                   independently_checked_four_sets=20475, second_layer_planar=False,
                   witness=False, native_78_solve='UNKNOWN_CONFLICT_CAP')
    (ROOT/'validation/S037/HITTING_78_DERIVED.json').write_text(json.dumps(derived, indent=2)+'\n', newline='\n')

    source = ROOT/'validation/S037/guided/arm-00.json'
    data = json.loads(source.read_text())['best']
    base = check(data, 156)
    layers = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
    faces = [quads(28, sorted(es)) for es in layers]
    neighbors = []
    for k in (0, 1):
        for e in sorted(layers[k]):
            adjacent = [f for f in faces[k] if all(v in f for v in e)]
            assert len(adjacent) == 2 and all(len(f) == 3 for f in adjacent)
            opposite = tuple(sorted(next(v for v in f if v not in e) for f in adjacent))
            if opposite in layers[0] | layers[1]:
                continue
            es = (layers[k]-{e}) | {opposite}
            union = es | layers[1-k]
            assert nx.is_planar(nx.Graph(es))
            value = sum(not any(x in union for x in it.combinations(vs, 2))
                        for vs in it.combinations(range(28), 4))
            neighbors.append(dict(layer=k, removed=e, added=opposite, independent_four_sets=value))
    local = dict(source='validation/S037/guided/arm-00.json', baseline=base['independent_four_sets'],
                 admissible_single_flips=len(neighbors),
                 improving_single_flips=sum(r['independent_four_sets'] < base['independent_four_sets'] for r in neighbors),
                 minimum_neighbor_violations=min(r['independent_four_sets'] for r in neighbors), neighbors=neighbors)
    # Inspect all saved near-triangulations for missing-diagonal restrictions.
    near = []
    for p in sorted((ROOT/'validation/S037/pairs').glob('arm-*.json')):
        d = json.loads(p.read_text())
        if d['density'] != 155 or not d['best']:
            continue
        b = d['best']; s1 = set(map(tuple, b['E1'])); s2 = set(map(tuple, b['E2']))
        face = next(f for f in quads(28, b['E2']) if len(f) == 4)
        diagonals = [tuple(sorted((face[i], face[i+2]))) for i in (0, 1)]
        additions = [e for e in it.combinations(range(28), 2) if e not in s1 | s2]
        completions = [e for e in additions if nx.is_planar(nx.Graph(s2 | {e}))]
        near.append(dict(path=str(p.relative_to(ROOT)).replace('\\', '/'), quadrilateral=face,
                         diagonals=diagonals, forbidden_by_T1=[e in s1 for e in diagonals],
                         already_in_T2=[e in s2 for e in diagonals],
                         all_disjoint_additions_tested=len(additions), planar_disjoint_completions=completions))
    out = dict(status='PASS', local_minimum=local, near_triangulations=near)
    (ROOT/'validation/S037/STRUCTURE.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print({k: v for k, v in local.items() if k != 'neighbors'})
    print('Near-layer diagonals forbidden by T1:', [r['forbidden_by_T1'] for r in near])


if __name__ == '__main__':
    main()
