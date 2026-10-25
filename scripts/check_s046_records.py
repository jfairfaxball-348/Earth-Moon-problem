"""Portable stdlib check of S046 evidence, certificates and the live S047 handoff.

Re-checks every archived pilot/calibration candidate (planar rotations,
colouring, filters actually enforced), every explicit <=8-colouring behind the
E1/E3 conclusions, the K6 v C5 calibration hits, instance regeneration,
registration order and budgets. With --native it also re-runs the pinned
drat-trim on the archived DRAT certificates (local Windows tools only).
"""
import argparse
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s045_verify import check_pair, check_colouring, partition_clause  # stdlib checkers
import s046_encode as enc

V = ROOT / 'validation/S046'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def proper(edges, cols, k):
    assert all(type(c) == int and 0 <= c < k for c in cols)
    assert all(cols[a] != cols[b] for a, b in edges)


def clique_ok(edges, q):
    es = {tuple(sorted(e)) for e in edges}
    assert all(tuple(sorted(p)) in es for p in it.combinations(q, 2))


def lex_rows_ok(n, edges):
    adj = [[0] * n for _ in range(n)]
    for a, b in edges:
        adj[a][b] = adj[b][a] = 1
    for i, j in it.combinations(range(n), 2):
        cols = [c for c in range(n) if c not in (i, j)]
        if [adj[i][c] for c in cols] < [adj[j][c] for c in cols]:
            return False
    return True


def authority():
    state = load(ROOT / 'authoritative/STATE.json')
    assert state['last_completed_session'] == 'S046' and state['recommended_next_session'] == 'S047'
    assert state['next_session_is_future_unexecuted'] and not state.get('active_session')
    r = state['s046_result']
    assert r['status'] == 'CLOSED_PIVOT_INCONCLUSIVE' and not r['witness'] and not r['domain_excluded']
    assert r['selected_domain'] is None and not r['long_run_started'] and not r['s047_executed']
    assert state['s047_queued']['status'] == 'FUTURE_UNEXECUTED'
    prompt = (ROOT / 'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()
    assert prompt == (ROOT / 'sessions/S046/S047_FUTURE_PROMPT.md').read_bytes()
    assert prompt.startswith(b'# S047') and b'FUTURE / UNEXECUTED' in prompt
    assert sha(ROOT / 'sessions/S045/S046_FUTURE_PROMPT.md') == 'f4c202cd0cb6f9c336aa4eeb18b5f883bd005c218ac13c897bc09a38445e8452'
    for name in ('INPUT', 'PLAN', 'RESEARCH', 'ADVERSARIAL', 'PRIOR_ART', 'CLOSEOUT'):
        assert (ROOT / f'sessions/S046/{name}.md').is_file()
    ctx = load(V / 'ENTRY_CONTEXT.json')
    assert ctx['entry_commit'] == '5f56fdf14b88eef9b77f549679c35a1e59a5b106'
    for path, item in ctx['files'].items():
        assert sha(ROOT / item['archive']) == item['sha256'], path
    man = load(V / 'MANIFEST.json')
    for path, digest in man['sha256'].items():
        assert sha(ROOT / path) == digest, path
    return len(man['sha256'])


def registration():
    reg = load(V / 'REGISTRATION.json')
    am = load(V / 'AMENDMENT_A1.json')
    budget = load(V / 'BUDGET.json')
    rng = random.Random(reg['e1']['seed'])
    for name, lo, hi in reg['e1']['strata']:
        assert sorted(rng.sample(range(lo, hi), reg['e1']['per_stratum'])) == reg['e1']['sample_indices'][name]
    rows = budget['ledger_rows']
    first = min(r['end_utc'] for r in rows)
    assert reg['registered_utc'] < first
    e3_end = next(r['end_utc'] for r in rows if r['block'] == 'E3')
    a1_first = min(r['end_utc'] for r in rows if r['block'].startswith('A1'))
    assert e3_end <= am['registered_utc'] < a1_first and am['changes_decision'] is False
    t = budget['totals']
    assert t['cpu_raw'] <= 1800 and t['wall_raw'] <= 3600 and budget['within_ceiling_even_counting_audits']
    assert load(ROOT / 'validation/S046/SMOKE.json')['verdict'] == 'PASS'
    assert load(V / 'CONTROLS.json')['status'] == 'PASS'


def journals():
    runtime = load(V / 'RUNTIME_MANIFEST.json')['runs']
    reg = load(V / 'REGISTRATION.json')
    checked = 0
    for key, files in runtime.items():
        group, name = key.split('/')
        status = load(V / group / 'runs' / name / 'STATUS.json')
        n, k, arm = status['n'], status['k'], status['arm']
        assert (group == 'pilots' and k == 9 and n in reg['e2']['orders']) or (group == 'calibration' and k == 8)
        assert status['reason'] in ('NATIVE_TIMEOUT', 'NONCOLOUR_ALERT_UNVERIFIED'), key
        pairs = list(it.combinations(range(n), 2))
        count = 0
        if 'CANDIDATES.jsonl' in files:
            raw = gzip.decompress((V / group / 'runs' / name / 'CANDIDATES.jsonl.gz').read_bytes())
            assert hashlib.sha256(raw).hexdigest() == files['CANDIDATES.jsonl']['raw_sha256']
            for line in raw.decode('utf-8').splitlines():
                r = json.loads(line)
                assert (r['n'], r['k'], r['arm'], r['mode']) == (n, k, arm, 'partition')
                check_pair(n, r['layers'], r['rotations'])
                check_colouring(n, r['layers'], r['colours'], k)
                assert partition_clause(n, r['colours'])
                bits = r['bits']
                assert [[list(p) for i, p in enumerate(pairs) if bits[2 * i + j] == '1'] for j in (0, 1)] == r['layers']
                edges = [tuple(e) for ls in r['layers'] for e in ls]
                if arm in ('C', 'CS'):
                    deg = [0] * n
                    for a, b in edges:
                        deg[a] += 1
                        deg[b] += 1
                    assert min(deg) >= k, key
                if arm == 'CS':
                    first = next(i for i in range(len(pairs)) if bits[2 * i] == '1' or bits[2 * i + 1] == '1')
                    assert bits[2 * first] == '1' and lex_rows_ok(n, edges), key
                count += 1
        assert count == status['candidates'], key
        checked += count
        # The encoded instance regenerates byte-identically from the encoder.
        with tempfile.TemporaryDirectory() as tmp:
            enc.write(Path(tmp) / 'BASE.inst', n, arm, k)
            assert sha(Path(tmp) / 'BASE.inst') == status['instance']['sha256'] == files['BASE.inst']['raw_sha256'], key
    return checked


def k6c5(edges, n):
    adj = {v: set() for v in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    hubs = [v for v in range(n) if len(adj[v]) == n - 1]
    rest = [v for v in range(n) if v not in hubs]
    assert len(hubs) == 6 and len(rest) == 5 and all(len(adj[v] & set(rest)) == 2 for v in rest)
    v, prev, seen = rest[0], None, [rest[0]]
    while True:  # the five non-hubs form a single 5-cycle
        nxt = [u for u in adj[v] & set(rest) if u != prev]
        u = nxt[0]
        if u == rest[0]:
            break
        prev, v = v, u
        seen.append(v)
    assert len(seen) == 5 and len(edges) == 50


def calibration():
    a1 = load(V / 'calibration/A1.json')
    hits = [r for r in a1['runs'] if r.get('hit')]
    assert sorted((r['arm'], r['n']) for r in hits) == [('B', 11), ('C', 11)]
    for r in a1['runs']:
        assert r['hit'] or r['reason'] == 'NATIVE_TIMEOUT'
    for r in hits:
        alert = load(V / 'calibration/runs' / f"k8-n{r['n']}-{r['arm']}" / 'ALERT.json')
        check_pair(11, alert['layers'], alert['rotations'])
        edges = sorted({tuple(e) for ls in alert['layers'] for e in ls})
        k6c5(edges, 11)
        f = r['found']
        assert f['non8'] == 'VERIFIED_NON_K_COLOURABLE' and f['chi'] == 9
        proper(edges, f['nine_colouring'], 9)
    return len(hits)


def certificates():
    e1 = load(V / 'diagnostics/E1.json')
    reg = load(V / 'REGISTRATION.json')
    certs = json.loads(gzip.decompress((V / 'diagnostics/E1_CERTS.json.gz').read_bytes()))
    want = sorted(i for idx in reg['e1']['sample_indices'].values() for i in idx)
    assert [c['index'] for c in certs] == want == sorted(r['index'] for r in e1['sample'])
    by = {}
    for c in certs:
        proper(c['edges'], c['colours'], 8)
        clique_ok(c['edges'], c['clique'])
        by.setdefault(c['archive'], {})[c['local_index']] = c
    for archive, rows in by.items():  # edges are exactly the archived S045 unions
        last = max(rows)
        with gzip.open(ROOT / archive, 'rt', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i in rows:
                    r = json.loads(line)
                    assert sorted({tuple(e) for ls in r['layers'] for e in ls}) == [tuple(e) for e in rows[i]['edges']]
                if i >= last:
                    break
    assert e1['census']['records'] == 642381 and e1['census']['empty_core9'] == 640299
    assert e1['census']['labelled_duplicate_unions'] == 0 and e1['census']['min_degree']['max'] == 8
    e3 = load(V / 'pilots/E3.json')
    assert e3['targeting_passed'] is False and e3['selected'] is None
    c3 = json.loads(gzip.decompress((V / 'pilots/E3_CERTS.json.gz').read_bytes()))
    analysed = {(a['n'], a['arm']): {d['candidate'] for d in a.get('detail', [])} for a in e3['arms']}
    seen = {}
    cache = {}
    for c in c3:
        key = (c['n'], c['arm'])
        if key not in cache:
            raw = gzip.decompress((V / 'pilots/runs' / f'n{key[0]}-{key[1]}' / 'CANDIDATES.jsonl.gz').read_bytes())
            cache = {key: raw.decode('utf-8').splitlines()}
        r = json.loads(cache[key][c['candidate']])
        edges = sorted({tuple(e) for ls in r['layers'] for e in ls})
        proper(edges, c['colours'], 8)
        clique_ok(edges, c['clique'])
        seen.setdefault(key, set()).add(c['candidate'])
    assert seen == {k: v for k, v in analysed.items() if v}
    assert sum(len(v) for v in seen.values()) == 300
    for a in e3['arms']:
        assert a['certified_non8'] == 0 and a['T'] is False
    return len(certs), len(c3)


def native():
    tool = ROOT / 'artifacts/tmp/S004/drat-trim-mingw.exe'
    assert sha(tool) == '970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e'
    count = 0
    for cnf in sorted((V / 'certificates').rglob('*.cnf')):
        proof = cnf.with_suffix('.drat')
        run = subprocess.run([str(tool), str(cnf), str(proof)], capture_output=True, text=True, timeout=600)
        assert run.returncode == 0 and 's VERIFIED' in run.stdout, cnf
        count += 1
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--native', action='store_true')
    a = ap.parse_args()
    files = authority()
    registration()
    records = journals()
    hits = calibration()
    e1c, e3c = certificates()
    extra = f'; {native()} DRAT certificates re-verified' if a.native else ''
    print(f'S046 PASS: {files} manifest files; {records} archived candidate records rechecked; '
          f'{e1c} E1 and {e3c} E3 explicit <=8-colourings; {hits} K6 v C5 calibration hits{extra}; '
          'decision PIVOT/INCONCLUSIVE; S047 FUTURE/UNEXECUTED')


if __name__ == '__main__':
    main()
