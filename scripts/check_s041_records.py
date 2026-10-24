"""Portable stdlib S041 replay: registration, order-13 classification, counting, certificates."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import rotation, subdivision


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def z13_orbits():
    a = lambda i: 2+i % 13
    b = lambda i: 15+i % 13
    orb = {'NA': {(0, a(i)) for i in range(13)}, 'NB': {(0, b(i)) for i in range(13)},
           'SA': {(1, a(i)) for i in range(13)}, 'SB': {(1, b(i)) for i in range(13)}}
    for d in range(1, 7):
        orb[f'AA{d}'] = {tuple(sorted((a(i), a(i+d)))) for i in range(13)}
        orb[f'BB{d}'] = {tuple(sorted((b(i), b(i+d)))) for i in range(13)}
    for t in range(13):
        orb[f'AB{t}'] = {(a(i), b(i+t)) for i in range(13)}
    allp = set()
    for o in orb.values():
        assert len(o) == 13 and not allp & o
        allp |= o
    assert allp == set(it.combinations(range(28), 2))-{(0, 1)}
    return orb


def check_certificate(edges, cert):
    adj = {v: set() for v in range(28)}
    for x, y in edges:
        adj[x].add(y); adj[y].add(x)
    t = cert['test']
    if t == 'T1':
        assert len(adj[cert['vertex']]) < 3
    elif t == 'T2':
        x, y = cert['edge']
        assert (x, y) in edges and len(adj[x] & adj[y]) < 2
    elif t == 'T3_degree':
        v, u = cert['vertex'], cert['neighbour']
        assert u in adj[v] and len(adj[u] & adj[v]) < 2
    elif t == 'T3_connected':
        v, comp = cert['vertex'], set(cert['component'])
        assert comp < adj[v] and all(not (adj[u] & adj[v]) - comp for u in comp)
    else:
        assert t == 'KURATOWSKI'
        k = {tuple(e) for e in cert['edges']}
        assert k <= set(edges) and subdivision(sorted(k)) == cert['kind']


def four_count(edges):
    nbr = [0]*28
    for x, y in edges:
        nbr[x] |= 1 << y; nbr[y] |= 1 << x
    total = 0
    for v in range(28):
        free_v = ~nbr[v] & ((1 << 28)-1) & ~((1 << (v+1))-1)
        for u in range(v+1, 28):
            if not free_v >> u & 1:
                continue
            free_vu = free_v & ~nbr[u] & ~((1 << (u+1))-1)
            for w in range(u+1, 28):
                if free_vu >> w & 1:
                    total += (free_vu & ~nbr[w] & ~((1 << (w+1))-1)).bit_count()
    return total


def check_p1():
    orb = z13_orbits()
    rec = read('validation/S041/P1_Z13.json')
    layers = json.loads(gzip.decompress((ROOT/'validation/S041/P1_Z13_layers.json.gz').read_bytes()))
    rest = sorted(n for n in orb if n[:2] in ('AA', 'BB', 'AB'))
    expected = {(x, y)+four for x in ('NA', 'NB') for y in ('SA', 'SB') for four in it.combinations(rest, 4)}
    assert len(layers) == len(expected) == 50600 == rec['layer_candidates']
    assert {tuple(x for x in r['orbits'][:2])+tuple(sorted(r['orbits'][2:])) for r in layers} == \
        {k[:2]+tuple(sorted(k[2:])) for k in expected}
    planar, tally = [], {}
    for r in layers:
        edges = set().union(*(orb[n] for n in r['orbits']))
        assert len(edges) == 78
        if r['planar']:
            faces = rotation(28, sorted(edges), r['rotation'])
            assert len(faces) == 52 and all(len(f) == 3 for f in faces)
            planar.append(r['orbits'])
            tally['PLANAR'] = tally.get('PLANAR', 0)+1
        else:
            check_certificate(edges, r['certificate'])
            tally[r['certificate']['test']] = tally.get(r['certificate']['test'], 0)+1
    assert tally == rec['certificate_tally'] and len(planar) == rec['planar_layers'] == 156
    pairs, best = 0, None
    for p, q in it.combinations(planar, 2):
        if p[0] == q[0] or p[1] == q[1] or set(p) & set(q):
            continue
        pairs += 1
        c = four_count(set().union(*(orb[n] for n in p+q)))
        assert c > 0
        best = c if best is None else min(best, c)
    assert pairs == rec['valid_pairs'] == 3510 and best == rec['best_pair']['independent_four_sets'] == 767
    assert not rec['alpha3_pairs']
    return pairs


def check_p2():
    d = read('validation/S041/P2_COUNTING.json')
    assert d['mycielski']['counting_feasible'] == []
    for h in range(9, 400):
        e = -(-(70*h-54)//16)
        assert 3*e+h > 6*(2*h+1)-12
    assert {(t['k1'], t['k2']) for t in d['chi10_join_types']} == {(1, 9), (2, 8), (3, 7), (4, 6), (5, 5)}
    assert {tuple(x) for x in d['chi10_unbounded_types']} == {(1, 1), (2, 2)}


def clique_number(edges):
    adj = {}
    for x, y in edges:
        adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    best = 0

    def grow(r, cand):
        nonlocal best
        best = max(best, r)
        for v in sorted(cand):
            grow(r+1, cand & adj[v])
            cand = cand-{v}
    grow(0, set(adj))
    return best


def regenerate():
    rim = list(range(7, 12))
    g1 = set(it.combinations(range(5), 2)) | {(a, b) for a in range(5) for b in range(5, 12)}
    g1 |= {(h, c) for h in (5, 6) for c in rim} | {tuple(sorted((rim[i], rim[(i+1) % 5]))) for i in range(5)}

    def hajos(k, off):
        one = [off+i for i in range(k)]
        two = [off]+[off+k-1+i for i in range(1, k)]
        es = set(it.combinations(one, 2)) | {tuple(sorted(e)) for e in it.combinations(two, 2)}
        es -= {(one[0], one[1]), tuple(sorted((two[0], two[1])))}
        es.add(tuple(sorted((one[1], two[1]))))
        return es, set(one) | set(two)

    def join(se, sv, be, bv):
        return se | be | {tuple(sorted((x, y))) for x in sv for y in bv}
    hb, vb = hajos(6, 4)
    hc, vc = hajos(7, 3)
    return {'K5_join_bipyramid': g1,
            'leaf_K4e_join_hajosK6K6': join({(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)}, {0, 1, 2, 3}, hb, vb),
            'leaf_K3e_join_hajosK7K7': join({(0, 1), (0, 2)}, {0, 1, 2}, hc, vc)}


def check_certificates():
    index = read('validation/S041/certificates/INDEX.json')
    graphs = regenerate()
    pinned = ('120d2c53bf14a8b70cce78be980824651922d53523228d9f0f026998caea7e48',
              '970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e')
    rows = {r['name']: r for f in ('P3B_LEAVES', 'P4_LEAVES') for r in read(f'validation/S041/{f}.json')}
    assert set(index) == set(graphs) == set(rows)
    for name, g in graphs.items():
        item = index[name]
        text = (ROOT/item['edges']['path']).read_text()
        assert sha(item['edges']['path']) == item['edges']['sha256'] == rows[name]['edges_sha256']
        edges = {tuple(sorted(map(int, l.split()))) for l in text.splitlines() if l.strip()}
        assert edges == g
        n = 1+max(max(e) for e in g)
        assert len(g) == rows[name]['edges'] and rows[name]['budget'] == 6*n-12 >= len(g)
        assert clique_number(g) == rows[name]['clique_number'] == 8
        for key in ('cnf', 'lemmas'):
            raw = gzip.decompress((ROOT/item[key]['path']).read_bytes())
            assert sha(item[key]['path']) == item[key]['sha256'] and hashlib.sha256(raw).hexdigest() == item[key]['source_sha256']
        assert sha(item['drat_gz']['path']) == item['drat_gz']['sha256'] == rows[name]['certify']['drat_gz_sha256']
        assert rows[name]['certify']['cnf_sha256'] == item['cnf']['source_sha256']
        assert (rows[name]['certify']['solver_sha256'], rows[name]['certify']['checker_sha256']) == pinned
        assert rows[name]['certify']['verdict'] == 'UNSAT_DRAT_VERIFIED'
        assert rows[name]['structure']['verdict'] == 'ALL_CLAUSES_JUSTIFIED' and rows[name]['verdict'] == 'NONBIPLANAR_DRAT_VERIFIED'
    p3 = read('validation/S041/P3_BIPLANARITY.json')
    sul = read('validation/sulanke.json')
    s_edges = {tuple(sorted(e)) for e in sul['edges_part1']+sul['edges_part2']}
    control = {r['name']: r for r in p3['rows']}
    c = control['control_sulanke']
    layers = [{tuple(e) for e in c[k]} for k in ('E1', 'E2')]
    assert c['verdict'] == 'SAT' and not layers[0] & layers[1] and layers[0] | layers[1] == s_edges
    for layer, rot in zip(layers, c['rotations']):
        rotation(11, sorted(layer), rot)
    assert control['control_K9']['certificate'] == 'DRAT_VERIFIED_NONBIPLANAR'
    assert control['K5_join_bipyramid']['verdict'] == 'UNKNOWN'
    return len(graphs)


def main():
    smoke = read('validation/S041/SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    reg = read('validation/S041/REGISTRATION.json')
    assert sha('sessions/S041/PLAN.md') == reg['sha256']['sessions/S041/PLAN.md'] == reg['revision']['plan_sha256']
    assert sha('sessions/S041/PLAN_ADDENDUM.md') == reg['addendum_p4']['sha256']
    assert read('validation/S041/PROBES.json')['total_cpu_seconds'] < 1800
    pairs = check_p1()
    check_p2()
    certs = check_certificates()
    manifest = ROOT/'validation/S041/MANIFEST.json'
    if manifest.exists():
        for p, h in read('validation/S041/MANIFEST.json')['sha256'].items():
            assert sha(p) == h, p
        state = read('authoritative/STATE.json')
        assert state['last_completed_session'] >= 'S041' and state['current_computation'] == 'STOPPED'
        if state['last_completed_session'] == 'S041':
            assert state['recommended_next_session'] == 'S042' and state['next_session_is_future_unexecuted']
            assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S041/S042_FUTURE_PROMPT.md').read_bytes()
    print('S041 PASS: 50600 order-13 layer certificates,', pairs, 'pairs (min 767 four-sets), counting tables,',
          certs, 'archived non-biplanarity certificates; no witness')


if __name__ == '__main__':
    main()
