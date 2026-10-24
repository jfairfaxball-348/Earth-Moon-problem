"""Portable stdlib S040 replay: registration, neighborhoods, pair traces, records, diagnostics."""
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s037_certificates import rotation, four_sets
from check_s038_records import edges_of, patch_replay
from check_s039_records import faces_normal, read, star_replay
from replay_s038_neighborhoods import enumerate_moves
from replay_s040_neighborhoods import compatible, components, load, table

FULL = (1 << 20475)-1


def masks():
    m = {e: 0 for e in it.combinations(range(28), 2)}
    for i, vs in enumerate(it.combinations(range(28), 4)):
        for e in it.combinations(vs, 2):
            m[e] |= 1 << i
    return m


def score(es, m):
    hits = 0
    for e in es[0] | es[1]:
        hits |= m[e]
    return (FULL ^ hits).bit_count()


def pair_replay(fs, move, protected=None):
    """Replay both components on the PRE-move layers and check the compatibility certificate."""
    assert move['kind'] == 'pair' and [c['layer'] for c in move['components']] == [0, 1]
    old = [edges_of(f) for f in fs]
    new = [star_replay(fs[k], c) for k, c in enumerate(move['components'])]
    es = [edges_of(f) for f in new]
    removed = [old[k]-es[k] for k in (0, 1)]
    added = [es[k]-old[k] for k in (0, 1)]
    conflicts = [added[k] & old[1-k] for k in (0, 1)]
    for k, c in enumerate(move['components']):
        assert set(map(tuple, c['conflicts'])) == conflicts[k]
        assert removed[k] == set(map(tuple, c['removed'])) and added[k] == set(map(tuple, c['added']))
        if protected:
            assert not removed[k] & protected[k]
    assert move['type'] == bool(conflicts[0])+bool(conflicts[1])
    assert conflicts[0] <= removed[1] and conflicts[1] <= removed[0] and not added[0] & added[1]
    assert not es[0] & es[1]
    return new


def replay_arm(path, m, protected):
    rec = read(path)
    edges, faces, _ = load(rec['source'])
    fs = [list(f) for f in faces]
    density = len(edges[0])+len(edges[1])
    quads = sum(len(f) == 4 for layer in fs for f in layer)
    minimum = value = score(edges, m)
    best_es = [set(map(tuple, rec['best'][k])) for k in ('E1', 'E2')]
    seen = value == rec['best']['independent_four_sets'] and edges == best_es
    best_faces = [list(f) for f in fs] if seen else None
    steps = 0
    relaxed_new_best = []
    for m_ in rec['trace']:
        if m_['kind'] == 'pair':
            fs = pair_replay(fs, m_, protected if rec['protected_core'] else None)
        elif m_['kind'] == 'star':
            fs[m_['layer']] = star_replay(fs[m_['layer']], m_)
        else:
            fs[m_['layer']] = patch_replay(fs[m_['layer']], m_)
        es = [edges_of(f) for f in fs]
        assert not es[0] & es[1] and sum(map(len, es)) == density
        assert sorted(map(len, es)) in ([78, 78], [77, 78]) and sum(len(f) == 4 for layer in fs for f in layer) == quads
        if rec['protected_core']:
            assert all(protected[k] <= es[k] for k in (0, 1))
        value = score(es, m)
        assert value == m_['score']
        if value < minimum:
            minimum = value
            if m_['kind'] == 'pair' and m_['type']:
                relaxed_new_best.append(m_['step'])
        if value == rec['best']['independent_four_sets'] and es == best_es and best_faces is None:
            best_faces = [list(f) for f in fs]
        steps += 1
    assert minimum == rec['best']['independent_four_sets'] and best_faces is not None
    assert [faces_normal(f) for f in rec['best_faces']] == best_faces
    history = [h['step'] for h in rec['best_history'] if h['kind'] == 'pair' and h['type']]
    assert history == relaxed_new_best
    return steps, rec


def classes(edges, faces):
    """Recompute C1..C4 of each useful absent pair with independent stdlib enumerators."""
    union = edges[0] | edges[1]
    H = [q for q in it.combinations(range(28), 4) if not any(e in union for e in it.combinations(q, 2))]
    useful = {e for q in H for e in it.combinations(q, 2)}
    comps = [components(edges[k], faces[k]) for k in (0, 1)]
    legal, relaxed = set(), set()
    for k in (0, 1):
        for (rem, add) in comps[k]:
            relaxed |= set(add)
            if not set(add) & edges[1-k]:
                legal |= set(add)
        for r in (1, 2, 3):
            for (rem, add) in enumerate_moves(28, edges[k], faces[k], r, edges[1-k]):
                legal |= set(add)
    paired = set()
    for key0, key1, kind in compatible(edges, comps):
        if kind:
            paired |= set(key0[1]) | set(key1[1])
    out = {}
    for e in useful:
        out[e] = 'C1' if e in legal else 'C2' if e in paired else 'C3' if e in relaxed else 'C4'
    return H, out


def check_diagnostic(path, edges, faces=None):
    d = read(path)
    union = edges[0] | edges[1]
    H = [tuple(q) for q in d['H']]
    assert H == [q for q in it.combinations(range(28), 4) if not any(e in union for e in it.combinations(q, 2))]
    assert d['independent_four_sets'] == len(H)
    t = d['tau']
    packing, hitting = [tuple(q) for q in t['packing']], {tuple(e) for e in t['hitting_set']}
    assert set(packing) <= set(H) and all(len(set(a) & set(b)) <= 1 for a, b in it.combinations(packing, 2))
    assert not hitting & union and all(any(e in hitting for e in it.combinations(q, 2)) for q in H)
    assert t['lower_packing'] == len(packing) <= len(hitting) == t['upper_hitting'] == t['rc2_hitting_optimum']
    assert t['exact'] == (len(packing) == len(hitting))
    if faces is not None:
        _, cls = classes(edges, faces)
        assert {tuple(r['pair']): r['class'] for r in d['rows']} == cls
    return t['lower_packing'], t['upper_hitting']


def main():
    smoke = read('validation/S040/SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    reg = read('validation/S040/REGISTRATION.json')
    assert hashlib.sha256((ROOT/'sessions/S040/PLAN.md').read_bytes()).hexdigest() == reg['sha256']['sessions/S040/PLAN.md']
    assert read('validation/S040/CONTROLS.json')['status'] == 'PASS'
    m = masks()
    for density in (156, 155):
        rec = read(f'validation/S040/neighborhood-{density}.json')
        r = table(rec['source'])
        assert r['sha256'] == rec['canonical_table_sha256'] and r['rows'] == rec['table_rows']
        for kind, v in rec['by_kind'].items():
            assert r['counts'].get(kind, 0) == v['count'] and r['minimum'].get(kind) == v['minimum']
        edges, faces, data = load(rec['source'])
        assert data['independent_four_sets'] == rec['baseline'] == score(edges, m)
        for kind, b in rec['bests'].items():
            mv = b['move']
            if mv['kind'] == 'pair':
                fs = pair_replay([list(f) for f in faces], mv)
            else:
                fs = [list(f) for f in faces]
                fs[mv['layer']] = star_replay(fs[mv['layer']], mv)
            es = [edges_of(f) for f in fs]
            assert es == [set(map(tuple, b['pair'][k])) for k in ('E1', 'E2')]
            assert score(es, m) == mv['score'] == b['pair']['independent_four_sets'] == rec['by_kind'][kind]['minimum']
        check_diagnostic(f'validation/S040/diagnostics/input-{density}.json', edges, faces)
    for r in read('validation/S040/NEIGHBORHOOD_REPLAY.json'):
        assert r['status'] == 'PASS' and r['scorer'] == 'delta'
        assert r['sha256'] == read(f"validation/S040/neighborhood-{r['density']}.json")['canonical_table_sha256']
    core = read('validation/sulanke.json')
    protected = [set(map(tuple, core[k])) for k in ('edges_part1', 'edges_part2')]
    steps = 0
    arms = sorted(p for p in (ROOT/'validation/S040/arms').glob('*.json') if p.name != 'SUMMARY.json')
    for p in arms:
        path = str(p.relative_to(ROOT)).replace('\\', '/')
        n, rec = replay_arm(path, m, protected)
        steps += n
        es = [set(map(tuple, rec['best'][k])) for k in ('E1', 'E2')]
        check_diagnostic(f'validation/S040/diagnostics/{p.stem}.json', es)
    checks = read('validation/S040/PAIR_CHECKS.json')
    assert checks['status'] == 'PASS' and checks['records'] == len(checks['rows']) == 8+len(arms)
    for r in checks['rows']:
        assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() == r['sha256']
        data = read(r['path'])
        for key in r['pointer']:
            data = data[key]
        es = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
        assert data['n'] == 28 and data['V'] == list(range(28)) and all(len(es[i]) == len(data[k]) for i, k in enumerate(('E1', 'E2')))
        assert all(0 <= a < b < 28 for layer in es for a, b in layer)
        assert not es[0] & es[1] and sorted(map(len, es)) in ([78, 78], [77, 78])
        for i, key in enumerate(('E1', 'E2')):
            assert sorted(map(len, rotation(28, data[key], r['layers'][i]['rotation']))) == r['layers'][i]['face_sizes']
        assert four_sets(28, data['E1'], data['E2']) == data['independent_four_sets'] == r['independent_four_sets'] > 0
        colors = {int(k): c for k, c in r['proper_coloring'].items()}
        assert set(colors) == set(range(28)) and all(colors[a] != colors[b] for a, b in es[0] | es[1])
        assert max(colors.values())+1 == r['proper_coloring_upper_bound'] <= 9
        if '/protected-' in r['path']:
            assert all(protected[k] <= es[k] for k in (0, 1)) and r['chromatic_exact'] == 9
        if r['alpha_exact'] == 4:
            assert all(any(e in es[0] | es[1] for e in it.combinations(vs, 2)) for vs in it.combinations(range(28), 5))
        else:
            ex = r['independent_five_example']
            assert len(set(ex)) == 5 and not any(e in es[0] | es[1] for e in it.combinations(ex, 2))
    experiment = read('validation/S040/EXPERIMENT.json')
    assert experiment['status'] == 'FINISHED' and experiment['experimental_cpu_seconds'] < 7200
    manifest = ROOT/'validation/S040/MANIFEST.json'
    if manifest.exists():
        for p, h in read('validation/S040/MANIFEST.json')['sha256'].items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
        state = read('authoritative/STATE.json')
        assert state['last_completed_session'] >= 'S040' and state['current_computation'] == 'STOPPED'
        if state['last_completed_session'] == 'S040':
            assert state['recommended_next_session'] == 'S041' and state['next_session_is_future_unexecuted']
            assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S040/S041_FUTURE_PROMPT.md').read_bytes()
    print('S040 PASS: coordinated neighborhoods', [read(f'validation/S040/neighborhood-{d}.json')['table_rows'] for d in (156, 155)],
          'rows replayed;', len(arms), 'arms,', steps, 'transitions,', len(checks['rows']), 'records; no witness')


if __name__ == '__main__':
    main()
