#!/usr/bin/env python3
"""Portable checker for S047 (D079 contradiction-route feasibility).

Standard library only by default (hosted scaffold):
  * registration precedes every experimental row; budget within ceiling;
  * obstruction O2/O3 integer inequalities, exhaustively for the stated
    ranges, and the closed-form polynomial identity behind O3;
  * the K6 v C5 seed receipt: layers disjoint, union exactly K6 v C5,
    rotation systems satisfy Euler, explicit 9-colouring proper;
  * the E2 colour clauses regenerated independently of PySAT and checked to
    be exactly the colour part of each archived CNF; K9 clauses likewise;
    archived CNF/proof hashes;
  * authority: S048 prompt identical in both locations, STATE fields.
With --native (local): regenerate every CNF with tools/s047_extend.py (needs
PySAT) byte for byte and re-run drat-trim on every archived proof.
"""
import gzip
import hashlib
import itertools as it
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / 'validation/S047'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def ky(k, n):
    """Kostochka-Yancey lower bound on edges of a k-critical n-vertex graph."""
    num = (k + 1) * (k - 2) * n - k * (k - 3)
    den = 2 * (k - 1)
    return -(-num // den)


def obstructions():
    # O2: 10-critical biplanar window
    for n in range(11, 5001):
        lo, hi = ky(10, n), 6 * n - 12
        assert lo <= hi and 18 * lo >= 88 * n - 70
    # O3: M_r(H) for 9-critical H on h vertices: (2r+1)e + h edges on (r+1)h+1 vertices
    for h in range(9, 2001):
        e = ky(9, h)
        for r in range(1, 41):
            assert (2 * r + 1) * e + h > 6 * ((r + 1) * h + 1) - 12, (h, r)
    # closed form: 16*[(2r+1)(70h-54)/16 + h - 6(r+1)h + 6] = 44rh - 10h - 108r + 42
    for r in range(0, 30):
        for h in range(0, 30):
            assert (2 * r + 1) * (70 * h - 54) + 16 * h - 96 * (r + 1) * h + 96 == 44 * r * h - 10 * h - 108 * r + 42
    # O3 with K6 v C5 itself (n=11, m=50): Mycielskian has 161 edges, 23 vertices
    assert 3 * 50 + 11 == 161 and 6 * 23 - 12 == 126
    # heuristic H1 (only when a 10-critical subgraph keeps all 50 seed edges):
    # e(X) >= 3t - 4 is impossible inside C(t,2) for 2 <= t <= 5
    assert [t for t in range(1, 7) if 3 * t - 4 > t * (t - 1) // 2] == [2, 3, 4, 5]
    # O4: 10-chromatic Schrijver graphs SG(2k+8, k): k=1 is K10 (contains K9), k=2,3 exceed 6n-12
    for k, (nv, ne) in ((1, (10, 45)), (2, (54, 999)), (3, (210, 10353))):
        n = 2 * k + 8
        Vs = [set(S) for S in it.combinations(range(n), k)
              if all(S[i + 1] - S[i] > 1 for i in range(k - 1)) and not (S[0] == 0 and S[-1] == n - 1)]
        m = sum(1 for a, b in it.combinations(range(len(Vs)), 2) if not Vs[a] & Vs[b])
        assert (len(Vs), m) == (nv, ne) and (k == 1 or m > 6 * len(Vs) - 12)
    return 'O2 n<=5000, O3 h<=2000 r<=40, closed form, O4 Schrijver k<=3, H1 arithmetic'


def seed_receipt():
    rec = load(V / 'E1_SEED.json')
    assert rec['status'] == 'PASS'
    alert = load(ROOT / rec['source'])
    assert sha((ROOT / rec['source']).read_bytes()) == rec['source_sha256']
    L = [[tuple(e) for e in layer] for layer in alert['layers']]
    s0, s1 = ({tuple(sorted(e)) for e in l} for l in L)
    assert not (s0 & s1)
    union = s0 | s1
    deg = {v: sum(v in e for e in union) for v in range(11)}
    A = [v for v in range(11) if deg[v] == 10]
    B = [v for v in range(11) if deg[v] == 8]
    assert len(A) == 6 and len(B) == 5 and len(union) == 50
    assert all(tuple(sorted(p)) in union for p in it.combinations(A, 2))
    assert all(tuple(sorted((a, b))) in union for a in A for b in B)
    bedges = [e for e in union if e[0] in B and e[1] in B]
    assert len(bedges) == 5 and all(sum(v in e for e in bedges) == 2 for v in B)
    adj = {v: {u for e in bedges for u in e if v in e and u != v} for v in B}
    seen, cur, prev = [B[0]], B[0], None
    while True:
        nxt = [u for u in adj[cur] if u != prev][0]
        if nxt == B[0]:
            break
        seen.append(nxt)
        prev, cur = cur, nxt
    assert len(seen) == 5  # B induces a 5-cycle
    for i in range(2):
        edges, rot = L[i], {int(k): v for k, v in alert['rotations'][i].items()}
        darts = {(u, v) for u, v in edges} | {(v, u) for u, v in edges}
        for u, nb in rot.items():
            assert sorted(nb) == sorted(v for (a, v) in darts if a == u)
        done, F = set(), 0
        for d in sorted(darts):
            if d in done:
                continue
            F += 1
            c = d
            while c not in done:
                done.add(c)
                u, v = c
                c = (v, rot[v][(rot[v].index(u) + 1) % len(rot[v])])
        verts = {v for e in edges for v in e}
        comp = {v: v for v in verts}

        def find(x):
            while comp[x] != x:
                x = comp[x]
            return x
        for u, v in edges:
            comp[find(u)] = find(v)
        C = len({find(v) for v in verts})
        assert len(verts) - len(edges) + F == 1 + C, i
    col = rec['explicit_9_colouring']
    assert max(col) < 9 and all(col[u] != col[v] for u, v in union)
    assert sha(gzip.decompress((V / 'e1_k8.drat.gz').read_bytes())) == rec['non_8_colourable']['proof_sha256']
    return 'seed K6 v C5 layers/union/rotations/colouring'


def colour_clauses(k, t):
    """Independent regeneration of the E2 colour clauses (literal ids as in
    tools/s047_extend.py: x-seed variables first, x by x, then X pairs)."""
    a = k - 3
    n0 = a + 5
    X = list(range(n0, n0 + t))
    var, nxt = {}, 1
    for x in X:
        for v in range(n0):
            var[(v, x)] = nxt
            nxt += 1
    for x, y in it.combinations(X, 2):
        var[(x, y)] = nxt
        nxt += 1
    B = list(range(a, a + 5))
    out = []
    for s in range(5):
        r = [B[(s + j) % 5] for j in range(5)]
        classes = [[v] for v in range(a)] + [[r[0]], [r[1], r[3]], [r[2], r[4]]]
        for phi in it.product(range(k), repeat=t):
            cl = {var[(v, X[i])] for i in range(t) for v in classes[phi[i]]}
            cl |= {var[(X[i], X[j])] for i, j in it.combinations(range(t), 2) if phi[i] == phi[j]}
            out.append(sorted(cl))
    return out, var, n0, X


def k9_clauses(t, var, n0, X):
    A, B = list(range(6)), list(range(6, 11))
    bpairs = [()] + [(b,) for b in B] + [tuple(sorted((B[i], B[(i + 1) % 5]))) for i in range(5)]
    out = []
    for bp in bpairs:
        for ra in range(7):
            rx = 9 - ra - len(bp)
            if rx < 1 or rx > t:
                continue
            for As in it.combinations(A, ra):
                for Xs in it.combinations(X, rx):
                    S = list(As) + list(bp) + list(Xs)
                    out.append([-var[(min(u, v), max(u, v))] for u, v in it.combinations(S, 2) if max(u, v) >= n0])
    return out


def e2(native):
    lad = load(V / 'E2_LADDER.json')
    reg = load(V / 'REGISTRATION.json')
    rows = lad['rows']
    assert all(reg['registered_utc'] < r['start_utc'] for r in rows)
    assert lad['totals']['experimental_cpu_s'] <= reg['budget']['e2_cpu_s']
    checked = []
    for r in rows:
        t = r['t']
        p = V / f'e2_t{t}.cnf.gz'
        if not p.exists():
            continue
        cnf = gzip.decompress(p.read_bytes())
        assert sha(cnf) == r['cnf_sha256'], t
        lines = cnf.decode().splitlines()
        body = [sorted(map(int, l.split()[:-1])) for l in lines[1:]]
        cc, var, n0, X = colour_clauses(9, t)
        assert body[:len(cc)] == cc, t
        kc = k9_clauses(t, var, n0, X)
        tail = body[len(cc):]
        tailset = {tuple(c) for c in tail}
        assert all(tuple(sorted(c)) in tailset for c in kc), t
        if r['verdict'] == 'UNSAT_VERIFIED' and r.get('proof_archive'):
            proof = gzip.decompress((ROOT / r['proof_archive']).read_bytes())
            assert sha(proof) == r['proof_sha256'], t
            if native:
                sys.path.insert(0, str(ROOT / 'tools'))
                from s047_extend import build, dimacs
                assert sha(dimacs(build(9, t, True)).encode()) == r['cnf_sha256'], t
                assert drat_native(cnf, proof), t
        checked.append((t, r['verdict']))
    return checked


def drat_native(cnf, proof):
    tmp = ROOT / 'artifacts/tmp/S047/check'
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / 'f.cnf').write_bytes(cnf)
    (tmp / 'f.drat').write_bytes(proof)
    out = subprocess.run([str(ROOT / 'artifacts/tmp/native/bin/drat-trim'), str(tmp / 'f.cnf'),
                          str(tmp / 'f.drat'), '-t', '20000'], capture_output=True, text=True).stdout
    return 's VERIFIED' in out


def a1(native):
    am = load(V / 'AMENDMENT_A1.json')
    lad = load(V / 'A1_LADDER.json')
    ctl = load(V / 'A1_CONTROLS.json')
    e2rows = load(V / 'E2_LADDER.json')['rows']
    assert max(r['end_utc'] for r in e2rows) <= am['registered_utc'] < ctl['started_utc']
    assert all(am['registered_utc'] < r['start_utc'] for r in lad['rows'])
    assert ctl['status'] == 'PASS' and am['changes_decision_rule'] is False
    assert lad['totals']['experimental_cpu_s'] <= am['budget']['cpu_s']
    rows = [(f'a1_t{r["t"]}', r) for r in lad['rows']] + [(f'a1c_t{r["t"]}', r) for r in ctl['rows'][:3]]
    checked = []
    for tag, r in rows:
        if r.get('verdict') != 'UNSAT_VERIFIED':
            continue
        t = r['t']
        cnf = gzip.decompress((V / f'{tag}.cnf.gz').read_bytes())
        assert sha(cnf) == r['final_cnf_sha256'], tag
        body = [sorted(map(int, l.split()[:-1])) for l in cnf.decode().splitlines()[1:]]
        learned = load(V / f'{tag}.learned.json')
        assert len(learned) == r['learned']
        cc, var, n0, X = colour_clauses(9, t)
        a = 6
        B = list(range(a, a + 5))
        for (s, phi), got in zip(learned, body):
            rr = [B[(s + j) % 5] for j in range(5)]
            classes = [[v] for v in range(a)] + [[rr[0]], [rr[1], rr[3]], [rr[2], rr[4]]]
            want = {var[(v, X[i])] for i in range(t) for v in classes[phi[i]]}
            want |= {var[(X[i], X[j])] for i, j in it.combinations(range(t), 2) if phi[i] == phi[j]}
            assert sorted(want) == got, tag
        tailset = {tuple(c) for c in body[len(learned):]}
        assert all(tuple(sorted(c)) in tailset for c in k9_clauses(t, var, n0, X)), tag
        proof = gzip.decompress((V / f'{tag}.drat.gz').read_bytes())
        assert sha(proof) == r['proof_sha256'], tag
        if native:
            assert drat_native(cnf, proof), tag
        checked.append(tag)
    return checked


def authority():
    state = load(ROOT / 'authoritative/STATE.json')
    assert state['last_completed_session'] == 'S047' and state['recommended_next_session'] == 'S048'
    r = state['s047_result']
    assert not r['witness'] and r['bounds'] == [9, 12] and not r['s048_executed']
    prompt = (ROOT / 'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()
    assert prompt == (ROOT / 'sessions/S047/S048_FUTURE_PROMPT.md').read_bytes()
    assert prompt.startswith(b'# S048') and b'FUTURE / UNEXECUTED' in prompt
    for name in ('INPUT', 'PLAN', 'RESEARCH', 'ADVERSARIAL', 'PRIOR_ART', 'CLOSEOUT'):
        assert (ROOT / f'sessions/S047/{name}.md').is_file()
    assert load(V / 'SMOKE.json')['verdict'] == 'PASS'
    assert load(V / 'CONTROLS.json')['status'] == 'PASS'
    man = load(V / 'MANIFEST.json')
    for path, digest in man['sha256'].items():
        assert sha((ROOT / path).read_bytes()) == digest, path
    return len(man['sha256'])


def main():
    native = '--native' in sys.argv
    print('obstructions:', obstructions())
    print('seed:', seed_receipt())
    print('E2 rows:', e2(native))
    print('A1 rows:', a1(native))
    if native:
        rec = load(V / 'E1_SEED.json')
        nv = 88
        edges = rec['union_edges']
        x = lambda v, c: v * 8 + c + 1  # noqa: E731
        lines = [[x(v, c) for c in range(8)] for v in range(11)]
        lines += [[-x(u, c), -x(v, c)] for u, v in edges for c in range(8)]
        cnf = (f'p cnf {nv} {len(lines)}\n' + ''.join(' '.join(map(str, c)) + ' 0\n' for c in lines)).encode()
        assert sha(cnf) == rec['non_8_colourable']['cnf_sha256']
        assert drat_native(cnf, gzip.decompress((V / 'e1_k8.drat.gz').read_bytes()))
        print('seed non-8-colourability: drat-trim VERIFIED')
    if '--no-authority' not in sys.argv:
        print('manifest files:', authority())
    print('S047 records PASS' + (' (native)' if native else ''))


if __name__ == '__main__':
    main()
