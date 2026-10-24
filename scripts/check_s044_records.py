"""Portable S044 audit replay: frozen evidence, fixed scope control, live boundaries."""
import hashlib
import itertools as it
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def scope_control():
    c = read('validation/S044/LEAF_SCOPE_CONTROL.json')
    triangles = [set(it.combinations(vs, 2)) for vs in c['initial_triangles']]
    graph = triangles[0]
    leaf_images = [set(triangles[0])]
    for step, incoming in zip(c['joins'], triangles[1:]):
        e1, e2 = map(tuple, step['delete'])
        assert e1 in graph and e2 in incoming
        x, y = step['identify']
        assert x in e1 and y in e2
        left = {v for e in graph for v in e}
        right = {v for e in incoming for v in e}
        assert not left & right
        remap = lambda edge: tuple(sorted(x if v == y else v for v in edge))
        assert len({x if v == y else v for v in right}) == len(right)
        bridge = tuple(step['add'])
        assert set(bridge) == (set(e1)-{x}) | (set(e2)-{y})
        graph = (graph-{e1}) | {remap(e) for e in incoming-{e2}} | {bridge}
        leaf_images.append({remap(e) for e in incoming})
    assert graph == {tuple(e) for e in c['final_edges']}
    designated = set(c['designated_leaf'])
    retained = {e for e in graph if set(e) <= designated}
    assert retained == {tuple(e) for e in c['designated_edges_retained']} == {(1,2)}
    assert [len(es-graph) for es in leaf_images] == [2,1,1]
    assert sum(len(es-graph) for es in leaf_images) == 2*(len(triangles)-1)
    assert all(sum(v in e for e in graph) == 2 for v in {v for e in graph for v in e})
    # This control checks copy retention only, not global noncontainment.
    assert 'no global mixed-composite counterexample' in c['scope']


def main():
    started = time.process_time()
    base = 'validation/S044/'
    reg = read(base+'REGISTRATION.json')
    assert reg['cpu_cap'] == 600
    for p,h in reg['sha256'].items():
        assert sha(p) == h, p
    verification = read(base+'VERIFICATION.json')
    assert verification['status'] == 'PASS' and len(verification['checks']) == 13
    assert all(r['returncode'] == 0 and not r['capped'] for r in verification['checks'])
    assert verification['cpu_upper_accounted'] < verification['cpu_cap'] == 600
    assert abs(sum(r['cpu_seconds'] for r in verification['checks'])-verification['job_cpu_seconds']) < .001
    smoke = read(base+'SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    evidence = read(base+'EVIDENCE.json')
    assert [r['session'] for r in evidence['rows']] == [f'S{n:03d}' for n in range(37,44)]
    costs = []
    for r in evidence['rows']:
        s = read(r['summary_path'])
        sid = r['session']
        if sid == 'S037':
            value = s['total_discovery_and_certificate_cpu_seconds']
        elif sid == 'S040':
            value = s['total_counted_cpu_seconds']
        elif sid == 'S041':
            value = s['probe_cpu_seconds']['total']
        else:
            value = s['experimental_cpu_seconds']
        assert value == r['reported_cpu_seconds']
        costs.append(value)
    assert sum(costs) == evidence['reported_cpu_sum'] and not evidence['cost_total_is_exact']
    for p,h in evidence['sha256'].items():
        assert sha(p) == h, p
        if p.endswith('/MANIFEST.json'):
            for frozen,digest in read(p)['sha256'].items():
                assert sha(frozen) == digest, frozen
    s043 = read('validation/S043/RESULT.json')
    assert s043['verdict'] == 'UNKNOWN' and not s043['whole_slice_certified']
    assert (s043['models'],s043['cuts'],s043['planar_layers']) == (10000,20000,0)
    s042 = read('validation/S042/SUMMARY.json')
    assert s042['leaf_graphs'] == s042['nonbiplanar_drat_verified'] == 97 and s042['unresolved_types'] == 30
    scope_control()
    corrections = read(base+'CORRECTIONS.json')
    assert not corrections['finite_certificates_changed']
    assert {c['id'] for c in corrections['original_claims']} == {'CLM-0140','CLM-0141','CLM-0143'}
    claims = {c['id']:c for c in read('catalogue/CLAIMS.json')}
    for ident,text in corrections['replacements'].items():
        assert claims[ident]['claim'] == text
    assert claims['CLM-0145']['status'] == 'PROGRAMME_PROVED'
    assert 'EVERY leaf' in claims['CLM-0145']['claim']
    summary = read(base+'SUMMARY.json')
    assert summary['recommendation'] == 'PAUSE' and summary['owner_decision'] == 'PENDING'
    assert summary['new_search_experiments'] == 0 and not summary['fresh_97_proof_drat_replay']
    assert summary['bounds'] == [9,12] and summary['order3'] == summary['S11'] == 'UNKNOWN'
    state = read('authoritative/STATE.json')
    assert state['last_completed_session'] >= 'S044' and state['current_computation'] == 'STOPPED'
    if state['last_completed_session'] == 'S044':
        assert state['recommended_next_session'] == 'S045' and state['next_session_is_future_unexecuted']
        assert state['s044_result'] == summary and state['s045_queued']['status'] == 'FUTURE_UNEXECUTED'
        assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S044/S045_FUTURE_PROMPT.md').read_bytes()
    manifest = ROOT/base/'MANIFEST.json'
    if manifest.exists():
        for p,h in read(base+'MANIFEST.json')['sha256'].items():
            assert sha(p) == h, p
    print(json.dumps(dict(status='PASS', recommendation='PAUSE', owner_decision='PENDING',
                          historical_sessions=7, verification_checks=13, designated_leaf_loses=2,
                          finite_apex_negatives=97, order3='UNKNOWN', cpu_seconds=time.process_time()-started)))


if __name__ == '__main__':
    main()
