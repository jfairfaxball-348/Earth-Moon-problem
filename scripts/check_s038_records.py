"""Portable exact S038 replay, no NetworkX/PySAT/search-module dependency."""
from collections import Counter
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s037_certificates import four_sets, rotation
from replay_s038_neighborhoods import replay as replay_one
from replay_s038_coupled import replay as replay_joint
from replay_s038_radius4 import replay as replay_radius4


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def canon(xs):
    xs = tuple(xs)
    return min(xs[i:]+xs[:i] for xs in (xs, xs[::-1]) for i in range(len(xs)))


def edges_of(faces):
    return {tuple(sorted((a, b))) for face in faces for a, b in zip(face, face[1:]+face[:1])}


def patch_replay(faces, move):
    selected = move['selected_faces']
    assert len(set(selected)) == len(selected)
    chosen = [faces[i] for i in selected]
    counts = Counter(tuple(sorted((a, b))) for f in chosen for a, b in zip(f, f[1:]+f[:1]))
    assert all(c in (1, 2) for c in counts.values())
    support = set(map(tuple, move['support_removed']))
    assert {e for e, c in counts.items() if c == 2} == support
    assert len(chosen) == len(support)+1
    dual = {i: set() for i in range(len(chosen))}
    for a, b in it.combinations(dual, 2):
        if edges_of([chosen[a]]) & edges_of([chosen[b]]):
            dual[a].add(b); dual[b].add(a)
    reached, todo = set(), [0]
    while todo:
        i = todo.pop()
        if i not in reached:
            reached.add(i); todo.extend(dual[i]-reached)
    assert len(reached) == len(chosen)
    rim = move['boundary']
    assert len(rim) == len(set(rim)) and set(rim) == {v for f in chosen for v in f}
    assert edges_of([rim]) == {e for e, c in counts.items() if c == 1}
    filling = [canon(f) for f in move['filling']]
    assert all(len(f) in (3, 4) and len(set(f)) == len(f) and set(f) <= set(rim) for f in filling)
    assert sum(len(f) == 4 for f in filling) == sum(len(f) == 4 for f in chosen)
    new_counts = Counter(tuple(sorted((a, b))) for f in filling for a, b in zip(f, f[1:]+f[:1]))
    assert {e for e, c in new_counts.items() if c == 1} == edges_of([rim])
    assert all(c in (1, 2) for c in new_counts.values())
    diagonals = set(map(tuple, move['diagonals']))
    assert {e for e, c in new_counts.items() if c == 2} == diagonals and len(diagonals) == len(support)
    order = {v: i for i, v in enumerate(rim)}
    for a, b in it.combinations(diagonals, 2):
        if set(a) & set(b):
            continue
        u, v = sorted(order[x] for x in a)
        assert not ((u < order[b[0]] < v) != (u < order[b[1]] < v))
    outside = [f for i, f in enumerate(faces) if i not in set(selected)]
    assert not diagonals & edges_of(outside)
    new_faces = sorted(outside+filling)
    assert len(set(new_faces)) == len(new_faces)
    old_edges, new_edges = edges_of(faces), edges_of(new_faces)
    assert old_edges-new_edges == set(map(tuple, move['removed']))
    assert new_edges-old_edges == set(map(tuple, move['added']))
    return new_faces


def main():
    v = 'validation/S038/'
    smoke = read(v+'SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    assert read(v+'CONTROLS.json')['independently_checked_patch_moves'] == 80
    for density in (156, 155):
        replay_one(density); replay_joint(density); replay_radius4(density)
    checks = read(v+'PAIR_CHECKS.json')
    assert checks['status'] == 'PASS' and checks['records'] == 22 and not checks['witness_found']
    for r in checks['rows']:
        path = ROOT/r['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == r['sha256']
        data = json.loads(path.read_text())
        for key in r['pointer']:
            data = data[key]
        assert data['n'] == 28 and data['V'] == list(range(28))
        es = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
        assert all(len(es[i]) == len(data[k]) for i, k in enumerate(('E1', 'E2')))
        assert all(0 <= a < b < 28 for es1 in es for a, b in es1)
        assert not es[0] & es[1] and sorted(map(len, es)) in ([78, 78], [77, 78])
        for i, k in enumerate(('E1', 'E2')):
            fs = rotation(28, data[k], r['layers'][i]['rotation'])
            assert sorted(map(len, fs)) == r['layers'][i]['face_sizes']
        assert four_sets(28, data['E1'], data['E2']) == data['independent_four_sets'] == r['independent_four_sets']
        colors = {int(k): value for k, value in r['proper_coloring'].items()}
        assert set(colors) == set(range(28)) and all(0 <= c <= 8 for c in colors.values())
        assert all(colors[a] != colors[b] for a, b in es[0] | es[1])
        assert 1+max(colors.values()) == r['proper_coloring_upper_bound']

    # Replay every search transition, including atomic changes to both layers.
    edge_masks = {e: 0 for e in it.combinations(range(28), 2)}
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            edge_masks[e] |= 1 << i
    trace_steps = 0
    all_paths = sorted((ROOT/(v+'arms')).glob('*-single.json'))+sorted((ROOT/(v+'arms')).glob('*-patch.json'))
    all_paths += sorted((ROOT/(v+'coupled')).glob('arm-*.json'))
    old_checks = read('validation/S037/PAIR_CHECKS.json')['rows']
    for path in all_paths:
        rec = json.loads(path.read_text())
        initial = read(rec['source'])['best']
        old = next(r for r in old_checks if r['path'] == rec['source'])
        faces = [sorted(canon(f) for f in rotation(28, initial[k], old['layers'][i]['rotation'])) for i, k in enumerate(('E1', 'E2'))]
        minimum = initial['independent_four_sets']
        for row in rec['trace']:
            moves = row['layers'] if 'layers' in row else [row.get('single_layer', row)]
            for move in moves:
                k = move['layer']
                faces[k] = patch_replay(faces[k], move)
            es = list(map(edges_of, faces))
            assert not es[0] & es[1] and len(es[0])+len(es[1]) == rec['density']
            hits = 0
            for e in es[0] | es[1]:
                hits |= edge_masks[e]
            value = (((1 << 20475)-1) ^ hits).bit_count()
            expected = row['single_layer']['score'] if 'single_layer' in row else row['score']
            assert value == expected
            minimum = min(minimum, value)
            trace_steps += 1
        assert minimum == rec['best']['independent_four_sets']
    summary = read(v+'SUMMARY.json')
    assert summary['experimental_cpu_seconds'] < 7200 and summary['best_violations'] == {'155': 123, '156': 91}
    manifest = ROOT/(v+'MANIFEST.json')
    if manifest.exists():
        for path, digest in read(v+'MANIFEST.json')['sha256'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] >= 'S038' and state['current_computation'] == 'STOPPED'
    if state['last_completed_session'] == 'S038':
        assert state['recommended_next_session'] == 'S039' and state['next_session_is_future_unexecuted']
        assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S038/S039_FUTURE_PROMPT.md').read_bytes()
    print('S038 PASS: exact neighborhoods, 22 sphere/colour/four-set records and', trace_steps, 'independently replayed planar patch transitions; no witness')


if __name__ == '__main__':
    main()
