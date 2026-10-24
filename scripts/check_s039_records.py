"""Portable independent S039 sphere, star, seed, colouring and trace replay."""
from collections import Counter
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s037_certificates import rotation, four_sets
from check_s038_records import canon, edges_of, patch_replay
from replay_s039_stars import replay, polygon_cells


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def faces_normal(fs):
    return sorted(canon(f) for f in fs)


def star_replay(faces, m):
    v = m['vertex']
    selected = [i for i, f in enumerate(faces) if v in f]
    assert selected == m['selected_faces']
    chosen = [faces[i] for i in selected]
    old = edges_of(faces)
    spokes = {e for e in old if v in e}
    d = len(spokes)
    assert 3 <= d <= 6 and d == m['old_degree'] == len(chosen)
    q = sum(len(f) == 4 for f in chosen)
    assert q in (0, 1) and bool(q) == m['quad_incident']
    rim = m['boundary']
    assert v not in rim and len(set(rim)) == len(rim) == d+q
    assert set().union(*map(set, chosen)) == set(rim) | {v}
    counts = Counter(e for f in chosen for e in edges_of([f]))
    assert {e for e, c in counts.items() if c == 1} == edges_of([rim])
    assert {e for e, c in counts.items() if c == 2} == spokes
    ds = set(map(tuple, m['hole_diagonals']))
    assert len(ds) == d-3
    cells = faces_normal(polygon_cells(rim, sorted(ds)))
    assert cells == faces_normal(m['hole_filling'])
    assert all(len(f) in (3, 4) for f in cells) and sum(len(f) == 4 for f in cells) == q
    outside = [f for i, f in enumerate(faces) if i not in selected]
    assert not ds & edges_of(outside)
    target = canon(m['target'])
    filled = sorted(outside+cells)
    assert len(target) == 3 and target in filled
    assert (target in cells) == m['target_inside_hole']
    new = sorted([f for f in filled if f != target]+[canon((v, a, b)) for a, b in zip(target, target[1:]+target[:1])])
    assert len(new) == len(set(new))
    es = edges_of(new)
    assert len(es) == len(old) and sum(v in e for e in es) == 3
    assert old-es == set(map(tuple, m['removed'])) and es-old == set(map(tuple, m['added']))
    return new


def seed_replay(number, core, protected):
    r = read(f'validation/S039/seeds/{number}.json')
    fs = [faces_normal(rotation(11, core[k], core['rotations'][i])) for i, k in enumerate(('edges_part1', 'edges_part2'))]
    values = sorted(set(core['coloring']))
    colors = {v: values.index(c) for v, c in enumerate(core['coloring'])}
    assert len(r['trace']) == 17
    for v, m in enumerate(r['trace'], 11):
        assert m['vertex'] == v
        targets = list(map(canon, m['faces']))
        assert not set(targets[0]) & set(targets[1])
        neighbors = set().union(*map(set, targets))
        assert sorted(neighbors) == m['new_neighbors'] and len(neighbors) <= 8
        c = m['colour']
        assert c in range(9) and c not in {colors[w] for w in neighbors}
        colors[v] = c
        for k, target in enumerate(targets):
            assert target in fs[k] and len(target) in (3, 4)
            fs[k] = sorted([f for f in fs[k] if f != target]+[canon((v, a, b)) for a, b in zip(target, target[1:]+target[:1])])
        es = list(map(edges_of, fs))
        assert not es[0] & es[1] and all(protected[k] <= es[k] for k in (0, 1))
    assert colors == {int(k): c for k, c in r['colouring'].items()}
    assert all(colors[a] != colors[b] for layer in fs for a, b in edges_of(layer))
    assert fs == list(map(faces_normal, r['faces']))
    assert all(edges_of(fs[k]) == set(map(tuple, r['pair'][key])) for k, key in enumerate(('E1', 'E2')))
    if r['deleted_edge'] is not None:
        e = tuple(r['deleted_edge'])
        assert number % 2 and e not in protected[1]
        selected = [f for f in fs[1] if e in edges_of([f])]
        assert len(selected) == 2 and all(len(f) == 3 for f in selected)
        variant = faces_normal(r['variant_faces'][1])
        assert edges_of(variant) == edges_of(fs[1])-{e}
        assert all(f in variant for f in fs[1] if f not in selected)
        merged = [f for f in variant if f not in fs[1]]
        assert len(merged) == 1 and len(merged[0]) == 4
        assert edges_of(merged) == edges_of(selected)-{e}
        fs[1] = variant
    assert fs == list(map(faces_normal, r['variant_faces']))
    assert all(edges_of(fs[k]) == set(map(tuple, r['variant'][key])) for k, key in enumerate(('E1', 'E2')))
    return fs


def main():
    smoke = read('validation/S039/SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    assert read('validation/S039/CONTROLS.json')['status'] == 'PASS'
    for d in (156, 155):
        replay(d)
    core = read('validation/sulanke.json')
    protected = [set(map(tuple, core[k])) for k in ('edges_part1', 'edges_part2')]
    cycle = core['cycle_order']
    clique = set(range(11))-set(cycle)
    assert len(clique) == 6 and len(set(cycle)) == 5
    expected = set(it.combinations(sorted(clique), 2)) | {tuple(sorted((a, b))) for a in clique for b in cycle}
    expected |= {tuple(sorted(e)) for e in zip(cycle, cycle[1:]+cycle[:1])}
    assert not protected[0] & protected[1] and protected[0] | protected[1] == expected
    seeds = {n: seed_replay(n, core, protected) for n in range(3910, 3914)}
    checks = read('validation/S039/PAIR_CHECKS.json')
    assert checks['status'] == 'PASS' and checks['records'] == len(checks['rows']) == 22 and not checks['witness_found']
    for r in checks['rows']:
        assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() == r['sha256']
        data = read(r['path'])
        for key in r['pointer']:
            data = data[key]
        assert data['n'] == 28 and data['V'] == list(range(28))
        es = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
        assert all(len(es[i]) == len(data[k]) for i, k in enumerate(('E1', 'E2')))
        assert all(0 <= a < b < 28 for layer in es for a, b in layer)
        assert not es[0] & es[1] and sorted(map(len, es)) in ([78, 78], [77, 78])
        for i, key in enumerate(('E1', 'E2')):
            fs = rotation(28, data[key], r['layers'][i]['rotation'])
            assert sorted(map(len, fs)) == r['layers'][i]['face_sizes']
        assert four_sets(28, data['E1'], data['E2']) == data['independent_four_sets'] == r['independent_four_sets'] > 0
        colors = {int(k): c for k, c in r['proper_coloring'].items()}
        assert set(colors) == set(range(28)) and all(c in range(9) for c in colors.values())
        assert all(colors[a] != colors[b] for a, b in es[0] | es[1])
        assert max(colors.values())+1 == r['proper_coloring_upper_bound']
        if r.get('core_chromatic_lower_bound'):
            assert all(protected[k] <= es[k] for k in (0, 1)) and r['chromatic_exact'] == 9
        example = r['independent_five_example']
        if r['alpha_exact'] == 4:
            assert example is None
            assert all(any(e in es[0] | es[1] for e in it.combinations(vs, 2)) for vs in it.combinations(range(28), 5))
        else:
            assert len(set(example)) == 5 and not any(e in es[0] | es[1] for e in it.combinations(example, 2))
    masks = {e: 0 for e in it.combinations(range(28), 2)}
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            masks[e] |= 1 << i
    steps = 0
    paths = sorted((ROOT/'validation/S039/arms').glob('*-*.json'))+sorted((ROOT/'validation/S039/protected').glob('[0-9]*.json'))
    old = read('validation/S038/PAIR_CHECKS.json')['rows']
    for density in (156, 155):
        r = read(f'validation/S039/neighborhood-{density}.json')
        data = read(r['source'])['best']
        cert = next(c for c in old if c['path'] == r['source'] and c['pointer'] == ['best'])
        fs = [faces_normal(rotation(28, data[key], cert['layers'][i]['rotation'])) for i, key in enumerate(('E1', 'E2'))]
        m = r['best']['move']
        fs[m['layer']] = star_replay(fs[m['layer']], m)
        assert all(edges_of(fs[k]) == set(map(tuple, r['best']['pair'][key])) for k, key in enumerate(('E1', 'E2')))
    for path in paths:
        rec = json.loads(path.read_text())
        if rec['protected_core']:
            fs = [list(f) for f in seeds[rec['seed']]]
        else:
            data = read(rec['source'])['best']
            cert = next(r for r in old if r['path'] == rec['source'] and r['pointer'] == ['best'])
            fs = [faces_normal(rotation(28, data[key], cert['layers'][i]['rotation'])) for i, key in enumerate(('E1', 'E2'))]
        initial_edges = list(map(edges_of, fs))
        density = sum(map(len, initial_edges))
        def score(es):
            hits = 0
            for e in es[0] | es[1]:
                hits |= masks[e]
            return (((1 << 20475)-1) ^ hits).bit_count()
        minimum = score(initial_edges)
        best_seen = (minimum == rec['best']['independent_four_sets'] and all(initial_edges[k] == set(map(tuple, rec['best'][key])) for k, key in enumerate(('E1', 'E2'))))
        for m in rec['trace']:
            k = m['layer']
            fs[k] = star_replay(fs[k], m) if m['kind'] == 'star' else patch_replay(fs[k], m)
            es = list(map(edges_of, fs))
            assert not es[0] & es[1] and sum(map(len, es)) == density
            assert sorted(map(len, es)) in ([78, 78], [77, 78])
            assert sum(len(f) == 4 for layer in fs for f in layer) == 156-density
            if rec['protected_core']:
                assert all(protected[k] <= es[k] for k in (0, 1))
            value = score(es)
            assert value == m['score']
            minimum = min(minimum, value)
            best_seen |= value == rec['best']['independent_four_sets'] and all(es[k] == set(map(tuple, rec['best'][key])) for k, key in enumerate(('E1', 'E2')))
            steps += 1
        assert best_seen and minimum == rec['best']['independent_four_sets']
    summary = ROOT/'validation/S039/SUMMARY.json'
    if summary.exists():
        assert read('validation/S039/SUMMARY.json')['experimental_cpu_seconds'] < 7200
    manifest = ROOT/'validation/S039/MANIFEST.json'
    if manifest.exists():
        for p, h in read('validation/S039/MANIFEST.json')['sha256'].items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
        state = read('authoritative/STATE.json')
        assert state['last_completed_session'] >= 'S039' and state['current_computation'] == 'STOPPED'
        if state['last_completed_session'] == 'S039':
            assert state['recommended_next_session'] == 'S040' and state['next_session_is_future_unexecuted']
            assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S039/S040_FUTURE_PROMPT.md').read_bytes()
    print('S039 PASS: 1811 exact star neighbors; 22 sphere/colour records; four seed reconstructions;', steps, 'trace transitions; no witness')


if __name__ == '__main__':
    main()
