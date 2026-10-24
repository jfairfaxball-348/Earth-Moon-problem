"""Portable stdlib S042 replay: registration, census types, leaf graphs, certificate receipts."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from s042_types_stdlib import table

PINNED = ('120d2c53bf14a8b70cce78be980824651922d53523228d9f0f026998caea7e48',
          '970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e')


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def omega(edges):
    adj = {}
    for x, y in edges:
        adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    best = 0

    def grow(size, cand):
        nonlocal best
        if size+len(cand) <= best:
            return
        best = max(best, size)
        for v in sorted(cand):
            grow(size+1, cand & adj[v])
            cand = cand-{v}
    grow(0, set(adj))
    return best


def invariant(edges):
    adj = {}
    for x, y in edges:
        adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    tri = {v: sum(1 for a, b in it.combinations(sorted(adj[v]), 2) if b in adj[a]) for v in adj}
    return sorted((len(adj[v]), tri[v], tuple(sorted(len(adj[w]) for w in adj[v]))) for v in adj)


def join(*graphs):
    edges, offset, blocks = set(), 0, []
    for n, es in graphs:
        edges |= {(a+offset, b+offset) for a, b in es}
        blocks.append(range(offset, offset+n))
        offset += n
    for p, q in it.combinations(blocks, 2):
        edges |= {(a, b) for a in p for b in q}
    return edges


def small_family_leaves():
    """(K7-e)vC5 and (K4-e)v6-Ore(11) for both splits, built independently."""
    k_minus = lambda m: (m, {(a, b) for a, b in it.combinations(range(m), 2)} - {(0, 1)})
    c5 = (5, {(i, (i+1) % 5) if i < 4 else (0, 4) for i in range(5)})
    out = [join(k_minus(7), c5)]
    for s in (1, 2):
        g1 = {(a, b) for a, b in it.combinations(range(6), 2)} - {(0, 1)}
        g2 = {(a+6, b+6) for a, b in it.combinations(range(5), 2)}
        g = g1 | g2 | {(0, 6+i) for i in range(s)} | {(1, 6+i) for i in range(s, 5)}
        out.append(join(k_minus(4), (11, {tuple(sorted(e)) for e in g})))
    return [{tuple(sorted(e)) for e in g} for g in out]


def main():
    smoke = read('validation/S042/SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    reg = read('validation/S042/REGISTRATION.json')
    assert sha('sessions/S042/PLAN.md') == reg['sha256']['sessions/S042/PLAN.md']
    assert sha('sessions/S042/PLAN_ADDENDUM.md') == reg['addendum']['sha256']
    rows = read('validation/S042/CENSUS_TYPES.json')
    mine = table()
    assert mine == sorted((r['a'], r['c'], tuple(tuple(f) for f in r['factors']), r['n'], r['slack'], tuple(r['factor_status'])) for r in rows)
    leaves = read('validation/S042/LEAF_GRAPHS.json')
    assert leaves['reduction_control'] == {'6-11': 2, '7-13': 3}
    graphs = []
    for g in leaves['leaf_graphs']:
        es = {tuple(e) for e in g['edges']}
        n = len({v for e in es for v in e})
        assert (n, len(es)) == (g['n'], g['m']) and g['slack'] == 6*n-12-len(es) >= 0
        assert omega(es) == g['omega'] <= 8
        graphs.append(es)
    invs = [invariant(g) for g in graphs]
    for g in small_family_leaves():
        assert invariant(g) in invs
    dec = read('validation/S042/DECISIONS.json')['decisions']
    archive = {r['name']: r for r in read('validation/S042/ARCHIVE.json')['rows']}
    local = read('validation/S042/LOCAL_VERIFY.json')
    assert local['status'] == 'PASS' and local['verified'] == len(archive)
    assert len(dec) == len(graphs)
    verdicts = {}
    for d, es, g in zip(dec, graphs, leaves['leaf_graphs']):
        text = ''.join(f'{a} {b}\n' for a, b in sorted(es))
        assert hashlib.sha256(text.encode()).hexdigest() == d['edges_sha256']
        verdicts[d['verdict']] = verdicts.get(d['verdict'], 0)+1
        if d['verdict'] == 'NONBIPLANAR_DRAT_VERIFIED':
            arch = archive[d['name']]
            raw = gzip.decompress((ROOT/arch['edges']['path']).read_bytes())
            assert raw.decode() == text and sha(arch['edges']['path']) == arch['edges']['sha256']
            assert hashlib.sha256(raw).hexdigest() == arch['edges']['source_sha256']
            assert arch['local']['cnf']['source_sha256'] == d['archive']['cnf']['source_sha256']
            assert arch['local']['lemmas']['source_sha256'] == d['archive']['lemmas']['source_sha256']
            assert sha(arch['drat_gz']['path']) == arch['drat_gz']['sha256'] == d['certify']['drat_gz_sha256']
            assert d['certify']['cnf_sha256'] == arch['local']['cnf']['source_sha256']
            assert (d['certify']['solver_sha256'], d['certify']['checker_sha256']) == PINNED
            assert d['certify']['verdict'] == 'UNSAT_DRAT_VERIFIED' and d['structure']['verdict'] == 'ALL_CLAUSES_JUSTIFIED'
    replays = [read(f'validation/S042/{f}') for f in ('LEAF_REPLAY.json', 'LEAF_REPLAY_STRONG.json') if (ROOT/'validation/S042'/f).exists()]
    assert replays and all(r['status'] == 'PASS' and r['recorded_leaf_graphs'] == len(graphs) and r['all_recorded_hit'] for r in replays)
    manifest = ROOT/'validation/S042/MANIFEST.json'
    if manifest.exists():
        for p, h in read('validation/S042/MANIFEST.json')['sha256'].items():
            assert sha(p) == h, p
        state = read('authoritative/STATE.json')
        assert state['last_completed_session'] >= 'S042' and state['current_computation'] == 'STOPPED'
        if state['last_completed_session'] == 'S042':
            assert state['recommended_next_session'] == 'S043' and state['next_session_is_future_unexecuted']
            assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S042/S043_FUTURE_PROMPT.md').read_bytes()
    print('S042 PASS:', len(rows), 'census types re-derived,', len(graphs), 'leaf graphs,', verdicts, '; no witness')


if __name__ == '__main__':
    main()
