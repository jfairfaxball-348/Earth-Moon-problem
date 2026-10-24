"""Combinatorial vertex-star relocation on genuine triangulated/near layers."""
import itertools as it
import json
from pathlib import Path
import random

from s038_patch import Plane, boundary, canonical, covered, cycle_edges, explicit, fillings
from s037_certificates import rotation

ROOT = Path(__file__).resolve().parents[1]


def load_start(density):
    source = f'validation/S038/arms/{density}-3800-patch.json'
    data = json.loads((ROOT/source).read_text())['best']
    check = next(r for r in json.loads((ROOT/'validation/S038/PAIR_CHECKS.json').read_text())['rows']
                 if r['path'] == source and r['pointer'] == ['best'])
    planes = [Plane(28, rotation(28, data[key], check['layers'][i]['rotation']))
              for i, key in enumerate(('E1', 'E2'))]
    return planes, data, source


def star_candidates(planes, cover, full, degree_cap=6, protected=None):
    protected = protected or (set(), set())
    for k, plane in enumerate(planes):
        other = planes[1-k].edges
        for v in range(plane.n):
            spokes = {e for e in plane.edges if v in e}
            d = len(spokes)
            if not 3 <= d <= degree_cap or spokes & protected[k]:
                continue
            selected = [i for i, face in enumerate(plane.faces) if v in face]
            old_faces = [plane.faces[i] for i in selected]
            if len(selected) != d:
                continue
            rim = boundary(old_faces)
            q = sum(len(f) == 4 for f in old_faces)
            if rim is None or v in rim or q > 1 or len(rim) != d+q:
                continue
            if {v} | set(rim) != set().union(*map(set, old_faces)):
                continue
            outside_faces = [f for i, f in enumerate(plane.faces) if i not in set(selected)]
            outside_edges = plane.edges-spokes
            for ds, fs in fillings(rim, bool(q)):
                if len(ds) != d-3 or ds & (outside_edges | other):
                    continue
                filled = sorted(outside_faces+list(fs))
                base_edges = outside_edges | ds
                base_hits = covered(base_edges | other, cover)
                for target in filled:
                    if len(target) != 3:
                        continue
                    added_spokes = {tuple(sorted((v, w))) for w in target}
                    if added_spokes & other:
                        continue
                    new_edges = base_edges | added_spokes
                    if new_edges == plane.edges:
                        continue
                    new_faces = [f for f in filled if f != target]
                    new_faces += [canonical((v, a, b)) for a, b in zip(target, target[1:]+target[:1])]
                    value = (full & ~(base_hits | covered(added_spokes, cover))).bit_count()
                    move = dict(kind='star', layer=k, vertex=v, old_degree=d,
                                selected_faces=selected, boundary=rim, quad_incident=bool(q),
                                hole_diagonals=sorted(ds), hole_filling=fs, target=target,
                                target_inside_hole=(target in fs),
                                removed=sorted(plane.edges-new_edges), added=sorted(new_edges-plane.edges), score=value)
                    yield value, k, new_faces, move


def core():
    data = json.loads((ROOT/'validation/sulanke.json').read_text())
    n = data['num_vertices']
    assert n == 11
    es = [set(tuple(sorted(e)) for e in data[key]) for key in ('edges_part1', 'edges_part2')]
    assert not es[0] & es[1] and list(map(len, es)) == [26, 24]
    cycle = data['cycle_order']
    assert len(set(cycle)) == 5
    clique = sorted(set(range(n))-set(cycle))
    expected = set(it.combinations(clique, 2)) | {tuple(sorted((a, b))) for a in clique for b in cycle}
    expected |= {tuple(sorted(e)) for e in zip(cycle, cycle[1:]+cycle[:1])}
    assert es[0] | es[1] == expected and len(expected) == 50
    colours = data['coloring']
    values = sorted(set(colours))
    assert len(values) == 9 and all(colours[a] != colours[b] for a, b in expected)
    normalized = {v: values.index(colours[v]) for v in range(n)}
    planes = [Plane(n, rotation(n, sorted(es[i]), data['rotations'][i])) for i in (0, 1)]
    assert [sum(len(f) == 4 for f in p.faces) for p in planes] == [1, 3]
    assert all(len(f) <= 4 for p in planes for f in p.faces)
    return planes, es, normalized, dict(clique=clique, odd_cycle=cycle, edges=50,
                                       planar_layer_edges=[26, 24], proper_colours=9,
                                       lower_bound='K6 join odd C5 requires6+3=9 distinct colours')


def seed(number):
    rng = random.Random(number)
    planes, protected, colours, core_proof = core()
    trace = []
    for v in range(11, 28):
        choices = [(-(len(a)+len(b)), rng.random(), a, b) for a in planes[0].faces for b in planes[1].faces
                   if not set(a) & set(b)]
        if not choices:
            return dict(status='FAILED_FACE_PACKING_UNKNOWN', seed=number, last_vertex=v,
                        trace=trace, partial=explicit(planes, None), core=core_proof)
        _, _, a, b = min(choices)
        old_neighbors = set(a) | set(b)
        assert len(old_neighbors) <= 8
        chosen_colour = next(c for c in range(9) if c not in {colours[w] for w in old_neighbors})
        colours[v] = chosen_colour
        for k, face in enumerate((a, b)):
            new = [f for f in planes[k].faces if f != face]
            new += [canonical((v, x, y)) for x, y in zip(face, face[1:]+face[:1])]
            planes[k] = Plane(v+1, new)
        assert not planes[0].edges & planes[1].edges
        assert all(protected[k] <= planes[k].edges for k in (0, 1))
        trace.append(dict(vertex=v, faces=[a, b], new_neighbors=sorted(old_neighbors), colour=chosen_colour))
    return dict(status='CHECKED_CONSTRUCTION_REQUIRES_INDEPENDENT_REPLAY', seed=number,
                pair=explicit(planes, None), faces=[p.faces for p in planes],
                colouring=colours, trace=trace, core=core_proof)
