"""Portable exact S037 evidence checks; no NetworkX/PySAT dependency or search."""
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_symmetry import audit
from s037_certificates import four_sets, rotation, subdivision


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def main():
    v = 'validation/S037/'
    assert audit() == read(v+'SYMMETRY.json')
    smoke = read(v+'SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    assert read(v+'CONTROLS.json')['rejected'] == ['overlap', 'nonplanar', 'false_objective', 'duplicate']
    assert read(v+'permutation/CONTROLS.json')['all_permutations_checked'] == 240
    checks = read(v+'PAIR_CHECKS.json')
    assert checks['status'] == 'PASS' and checks['witness_found'] is False
    checked = {}
    for r in checks['rows']:
        p = ROOT/r['path']
        source = json.loads(p.read_text())
        if r.get('no_feasible_pair'):
            assert source['best'] is None
            continue
        assert hashlib.sha256(p.read_bytes()).hexdigest() == r['sha256']
        data = source['best']
        assert data['n'] == 28 and data['V'] == list(range(28))
        es = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
        assert not es[0] & es[1]
        for k, key in enumerate(('E1', 'E2')):
            assert len(es[k]) == len(data[key])
            assert all(0 <= a < b < 28 for a, b in es[k])
            faces = rotation(28, data[key], r['layers'][k]['rotation'])
            assert sorted(map(len, faces)) == r['layers'][k]['face_sizes']
        assert sorted(map(len, es)) in ([78, 78], [77, 78])
        assert four_sets(28, data['E1'], data['E2']) == r['independent_four_sets'] == data['independent_four_sets']
        colours = {int(k): v for k, v in r['proper_coloring'].items()}
        assert set(colours) == set(range(28)) and all(colours[a] != colours[b] for a, b in es[0] | es[1])
        assert 1+max(colours.values()) == r['proper_coloring_upper_bound'] <= 9
        checked[r['path']] = r, data
    assert len(checked) == 19
    structure = read(v+'STRUCTURE.json')['local_minimum']
    record, data = checked[structure['source']]
    es = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
    enumerated = []
    for k in (0, 1):
        faces = rotation(28, data[('E1', 'E2')[k]], record['layers'][k]['rotation'])
        for e in sorted(es[k]):
            fs = [f for f in faces if all(v in f for v in e)]
            assert len(fs) == 2
            opposite = tuple(sorted(next(v for v in f if v not in e) for f in fs))
            if opposite in es[0] | es[1]:
                continue
            candidate = es[k]-{e} | {opposite}
            count = four_sets(28, candidate, es[1-k])
            enumerated.append(dict(layer=k, removed=list(e), added=list(opposite), independent_four_sets=count))
    assert enumerated == structure['neighbors']
    assert len(enumerated) == 43 and min(r['independent_four_sets'] for r in enumerated) == 93
    assert record['independent_four_sets'] == 91

    # Prove the finite global nonextension examples using explicit subdivisions,
    # not an assertion about the unique quadrilateral in one embedding.
    nonextension = read(v+'NONEXTENSION.json')
    assert len(nonextension['examples']) == 2
    for example in nonextension['examples']:
        d = read(example['source'])['best']
        a, b = [set(map(tuple, d[k])) for k in ('E1', 'E2')]
        expected = {e for e in it.combinations(range(28), 2) if e not in a | b}
        assert {tuple(row['added']) for row in example['rows']} == expected
        assert len(example['rows']) == len(expected) == 223
        for row in example['rows']:
            assert set(map(tuple, row['obstruction'])) <= b | {tuple(row['added'])}
            assert subdivision(row['obstruction']) == row['kind']

    h = read(v+'HITTING.json')[0]
    assert h['result'] == 'SAT_RELAXATION' and not h['second_layer_planar']
    assert four_sets(28, h['E1'], h['E2']) == 0
    assert set(map(tuple, h['nonplanar_subgraph'])) <= set(map(tuple, h['E2']))
    subdivision(h['nonplanar_subgraph'])
    derived = read(v+'HITTING_78_DERIVED.json')
    assert len(derived['E2']) == 78 and four_sets(28, derived['E1'], derived['E2']) == 0
    assert set(map(tuple, h['E2'])) <= set(map(tuple, derived['E2']))
    assert not set(map(tuple, derived['E1'])) & set(map(tuple, derived['E2']))

    summary = read(v+'SUMMARY.json')
    cpu = sum(r['cpu_seconds'] for d in ('pairs', 'guided', 'permutation') for r in read(v+d+'/SUMMARY.json'))
    cpu += sum(r['cpu_seconds'] for r in read(v+'HITTING.json'))
    assert cpu == summary['experimental_cpu_seconds'] < 7200
    assert summary['best_violations'] == {'155': 125, '156': 91}
    if (ROOT/(v+'MANIFEST.json')).exists():
        for p, digest in read(v+'MANIFEST.json')['sha256'].items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest, p
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] >= 'S037'
    assert state['current_computation'] == 'STOPPED'
    if state['last_completed_session'] == 'S037':
        prompt = (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()
        assert prompt == (ROOT/'sessions/S037/S038_FUTURE_PROMPT.md').read_bytes()
        assert state['recommended_next_session'] == 'S038' and state['next_session_is_future_unexecuted']
    print('S037 PASS: symmetry, 19 layer records/rotations/four-sets/colourings, 43 flips, 446 nonextension subdivisions; bounds unchanged')


if __name__ == '__main__':
    main()
