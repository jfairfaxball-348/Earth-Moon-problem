"""Independent, stdlib-only S043 encoding/certificate replay; never starts search."""
import gzip
import hashlib
import itertools as it
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'validation/S043'


def read(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def permutation(power):
    return [0]+[1+3*i+(r+power) % 3 for i in range(9) for r in range(3)]


def orbit_partition(k):
    perms = [permutation(p) for p in range(3)]
    groups = {}
    for subset in it.combinations(range(28), k):
        images = {tuple(sorted(p[v] for v in subset)) for p in perms}
        groups[min(images)] = sorted(images)
    return [groups[key] for key in sorted(groups)]


def cardinality(literals, maximum, top):
    """Recognise the triangular unary-counter clauses by explicit grid semantics.

    Cell(r,j) means >=r+1 true among literals[0:j+r+1]. Horizontal
    monotonicity and adding the next true literal force each threshold;
    the last-row overflow clauses forbid a (maximum+1)th true literal.
    Conversely assigning each cell its threshold meaning satisfies them.
    """
    assert 1 < maximum < len(literals)-1
    cells = {}
    clauses = []

    def cell(r, j):
        nonlocal top
        if (r, j) not in cells:
            top += 1
            cells[r, j] = top
        return cells[r, j]

    columns = len(literals)-maximum
    for j in range(columns):
        clauses.append([-literals[j], cell(0, j)])
        for r in range(maximum):
            if j+1 < columns:
                clauses.append([-cell(r, j), cell(r, j+1)])
            if r+1 < maximum:
                clauses.append([-literals[j+r+1], -cell(r, j), cell(r+1, j)])
            else:
                clauses.append([-literals[j+maximum], -cell(r, j)])
    return clauses, top


def expected_generators(orbits):
    lookup = {e: i for i, es in enumerate(orbits) for e in es}
    descriptions = [('rotate', i) for i in range(9)]+[('swap', i) for i in range(2, 8)]+[('inverse', None), ('swap', 0)]
    rows = []
    for op, i in descriptions:
        perm = [0]
        for q, r in it.product(range(9), range(3)):
            qq = i+1 if op == 'swap' and q == i else i if op == 'swap' and q == i+1 else q
            rr = (r+1) % 3 if op == 'rotate' and q == i else (-r) % 3 if op == 'inverse' else r
            perm.append(1+3*qq+rr)
        swap = op == 'swap' and i == 0
        image = []
        for l in range(2):
            for es in orbits:
                e = tuple(sorted(perm[v] for v in es[0]))
                image.append(1+126*(1-l if swap else l)+lookup[e])
        rows.append(dict(name='layer_swap_orbit01' if swap else f'{op}_{i}', vertices=perm,
                         layer_swap=swap, image=image))
    return rows


def expected_base(enc):
    pairs = orbit_partition(2)
    fours = orbit_partition(4)
    assert enc['orbits'] == [[list(e) for e in es] for es in pairs]
    assert enc['fours'] == [[list(es[0]), len(es)] for es in fours]
    assert len(pairs) == 126 and len(fours) == 6831
    assert sum(len(es) == 1 for es in fours) == 9 and sum(map(len, fours)) == 20475
    lookup = {e: i for i, es in enumerate(pairs) for e in es}
    cs = [[-1-j, -127-j] for j in range(126)]
    top = 252
    for layer in range(2):
        xs = list(range(1+126*layer, 127+126*layer))
        for ls, k in (([-x for x in xs], 100), (xs, 26)):
            new, top = cardinality(ls, k, top)
            cs += new
    for group in fours:
        vs = group[0]
        c = sorted({1+126*l+lookup[e] for e in it.combinations(vs, 2) for l in range(2)})
        # Check all members, including every one of the20475 four-sets.
        for member in group:
            assert c == sorted({1+126*l+lookup[e] for e in it.combinations(member, 2) for l in range(2)})
        cs.append(c)
    triangles = [lookup[(1+3*i, 2+3*i)] for i in range(9)]
    assert triangles == enc['triangles']
    pins = {1+triangles[0], 127+triangles[1]}
    cs.extend([[1+triangles[0]], [127+triangles[1]]])
    gs = expected_generators(pairs)
    assert gs == enc['generators']
    for g in gs:
        assert sorted(g['image']) == list(range(1, 253))
        assert {g['image'][v-1] for v in pins} == pins
        # Commutation with sigma, or conjugation to its inverse.
        for v in range(28):
            p = g['vertices']
            assert p[permutation(1)[v]] == permutation(2 if g['name'].startswith('inverse') else 1)[p[v]]
        top += 1
        prefix = top
        cs.append([prefix])
        for a, b in enumerate(g['image'], 1):
            if a == b:
                continue
            cs.append([-prefix, -a, b])
            top += 1
            q = top
            # q <=> (prefix AND (a == b)); local truth table checked below.
            block = [[-q, prefix], [-q, -a, b], [-q, a, -b], [-prefix, a, b, q], [-prefix, -a, -b, q]]
            for pp, aa, bb, qq in it.product((False, True), repeat=4):
                assignment = {prefix: pp, a: aa, b: bb, q: qq}
                truth = all(any(assignment[abs(x)] == (x > 0) for x in c) for c in block)
                assert truth == (qq == (pp and aa == bb))
            cs.extend(block)
            prefix = q
    assert top == enc['base_variables'] and len(cs) == enc['base_clauses']
    return cs, top, lookup


def check_subdivision(edges):
    """Trace branch-to-branch paths, independent of search's vertex suppression."""
    es = {tuple(e) for e in edges}
    assert len(es) == len(edges) and all(0 <= a < b < 28 for a, b in es)
    adj = {}
    for a, b in es:
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    branches = {v for v in adj if len(adj[v]) != 2}
    assert len(branches) in (5, 6)
    used, skeleton = set(), set()
    for v in sorted(branches):
        for w in sorted(adj[v]):
            first = tuple(sorted((v, w)))
            if first in used:
                continue
            used.add(first)
            prev, cur = v, w
            while cur not in branches:
                nxt, = adj[cur]-{prev}
                e = tuple(sorted((cur, nxt)))
                assert e not in used
                used.add(e)
                prev, cur = cur, nxt
            assert cur != v
            s = tuple(sorted((v, cur)))
            assert s not in skeleton
            skeleton.add(s)
    assert used == es
    if len(branches) == 5:
        assert skeleton == set(it.combinations(sorted(branches), 2))
        return 'K5'
    assert len(skeleton) == 9 and all(sum(v in e for e in skeleton) == 3 for v in branches)
    for a in it.combinations(sorted(branches), 3):
        b = branches-set(a)
        if skeleton == {tuple(sorted((x, y))) for x in a for y in b}:
            return 'K33'
    raise AssertionError('not K3,3')


def check_rotation(edges, rot):
    adj = {v: set() for v in range(28)}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    rot = {int(k): v for k, v in rot.items()}
    assert all(len(rot[v]) == len(adj[v]) and set(rot[v]) == adj[v] for v in adj)
    darts = {(a, b) for a, ns in adj.items() for b in ns}
    cycles = []
    while darts:
        first = cur = min(darts)
        cycle = []
        while cur in darts:
            darts.remove(cur)
            a, b = cur; cycle.append(a)
            ns = rot[b]
            cur = b, ns[(ns.index(a)-1) % len(ns)]
        assert cur == first and len(cycle) == 3
        cycles.append(cycle)
    assert len(edges) == 78 and len(cycles) == 52
    seen, todo = {0}, [0]
    while todo:
        v = todo.pop()
        for w in adj[v]-seen:
            seen.add(w); todo.append(w)
    assert len(seen) == 28


def raw_cnf(cs, nv):
    return (f'p cnf {nv} {len(cs)}\n'+''.join(' '.join(str(x) for x in c)+' 0\n' for c in cs)).encode()


def main():
    start = __import__('time').process_time()
    smoke = read('SMOKE.json')
    assert smoke['verdict'] == 'PASS' and smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    reg = read('REGISTRATION.json')
    for p, h in reg['sha256'].items():
        assert sha(ROOT/p) == h, p
    enc = read('ENCODING.json')
    cs, nv, lookup = expected_base(enc)
    base = raw_cnf(cs, nv)
    assert gzip.decompress((OUT/'BASE.cnf.gz').read_bytes()) == base
    ctrl = read('CONTROLS.json')
    assert ctrl['status'] == 'PASS'
    check_rotation(ctrl['planar_layer']['edges'], ctrl['planar_layer']['rotation'])
    edges = {tuple(e) for e in ctrl['planar_layer']['edges']}
    assert {tuple(sorted(permutation(1)[v] for v in e)) for e in edges} == edges
    cuts = []
    path = OUT/'CUTS.jsonl.gz'
    text = gzip.decompress(path.read_bytes()).decode() if path.exists() else (OUT/'CUTS.jsonl').read_text()
    kinds = {}
    models = set()
    for line in text.splitlines():
        row = json.loads(line)
        kind = check_subdivision(row['edges'])
        assert row['kind'] == kind
        assert row['layer'] in (0, 1)
        support = sorted({lookup[tuple(e)] for e in row['edges']})
        assert support == row['support']
        clause = [-1-126*row['layer']-j for j in support]
        assert clause == row['clause']
        cuts.append(clause); models.add(row['model'])
        kinds[kind] = kinds.get(kind, 0)+1
    result = read('RESULT.json')
    assert len(cuts) == result['cuts'] and len(models) <= result['models']
    final = raw_cnf(cs+cuts, nv)
    assert gzip.decompress((OUT/'FINAL.cnf.gz').read_bytes()) == final
    assert hashlib.sha256(base).hexdigest() == result['base_cnf_raw_sha256']
    assert hashlib.sha256(final).hexdigest() == result['final_cnf_raw_sha256']
    assert result['cpu_seconds'] <= 2401 and result['bounds'] == [9, 12] and not result['S036_restarted']
    if result['verdict'] == 'UNKNOWN':
        assert not result['whole_slice_certified'] and result['gate_decision'] == 'PIVOT'
    elif result['verdict'].startswith('UNSAT_DRAT_VERIFIED'):
        native = result['native']
        assert native['solver']['returncode'] == 20 and not native['solver']['capped']
        assert native['checker']['returncode'] == 0 and not native['checker']['capped']
        assert 's VERIFIED' in native['checker']['log']
        assert (native['solver_sha256'], native['checker_sha256']) == (smoke['solver_sha256'], smoke['checker_sha256'])
        assert (OUT/'FINAL.drat.gz').exists()
    else:
        raise AssertionError('positive result needs full witness checker')
    manifest = OUT/'MANIFEST.json'
    if manifest.exists():
        for p, h in read('MANIFEST.json')['sha256'].items():
            assert sha(ROOT/p) == h, p
        state = json.loads((ROOT/'authoritative/STATE.json').read_text())
        assert state['last_completed_session'] >= 'S043' and state['current_computation'] == 'STOPPED'
        if state['last_completed_session'] == 'S043':
            assert state['recommended_next_session'] == 'S044' and state['next_session_is_future_unexecuted']
            assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == (ROOT/'sessions/S043/S044_FUTURE_PROMPT.md').read_bytes()
    summary = dict(status='PASS', base_clauses=len(cs), base_variables=nv, cuts=len(cuts), kinds=kinds,
                   all_clauses_rejustified=True, verdict=result['verdict'], cpu_seconds=__import__('time').process_time()-start,
                   scope='encoding and subdivision replay; UNKNOWN does not exclude any whole class')
    print(json.dumps(summary))
    return summary


if __name__ == '__main__':
    main()
