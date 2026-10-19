#!/usr/bin/env python3
"""Independent audit of S027 learned clauses (does not import s027_source/contain).

For every recorded learned clause of a profile w:
  * PRELOAD/CONTAIN(+_PERM): rebuild the certified obstruction H = A[u] from its
    own definition, expand the recorded bag assignment f to explicit consecutive
    labels, and check injectivity, capacities and that EVERY H edge lies inside a
    target bag or on a SOURCE support edge; then check clause = perm(support) with
    perm preserving w. By the support lemma this justifies the clause.
  * EULER(+_PERM): recount sum C(w_v,2) over T plus sum w_a w_b over the recorded
    edges (all inside T) and require > 6 w(T) - 12.
Regenerate mode rebuilds the profile domain CNF and requires byte identity.
Usage: s027_check_learned.py LEARNED.json.gz [DOMAIN.cnf]
"""
import gzip
import itertools as it
import json
from pathlib import Path
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]


def blow(g6, u):
    A = nx.from_graph6_bytes(g6.encode())
    lab, s = [], 0
    for x in u:
        lab.append(list(range(s, s + x)))
        s += x
    E = set()
    for b in lab:
        E |= {(p, q) for p, q in it.combinations(b, 2)}
    for i, j in A.edges():
        E |= {(min(p, q), max(p, q)) for p in lab[i] for q in lab[j]}
    hb = [i for i, b in enumerate(lab) for _ in b]
    return sorted(E), hb


def definitions():
    defs = {}
    for e in json.loads((ROOT / 'validation/S025/C5_CERTIFICATES.json').read_text()):
        if e.get('certified'):
            defs['C5-' + e['tag']] = ('Dhc', list(map(int, e['tag'])))
    for t in ('24335', '23525', '23534'):
        s = json.loads((ROOT / f'validation/S026/local/C5-{t}/SUMMARY.json').read_text())
        assert s['verdict'] == 'NONBIPLANAR_CERTIFIED'
        defs['C5-' + t] = ('Dhc', list(map(int, t)))
    c = json.loads((ROOT / 'validation/S026/filter-recovery/candidate/CANDIDATE.json').read_text())
    defs['P29-B14-0001'] = (c['g6'], c['w'])
    import os
    extra = os.environ.get('EMP_S027_EXTRA_OBSTRUCTIONS')
    if extra and Path(extra).is_file():
        for r in json.loads(Path(extra).read_text()):
            s = json.loads((ROOT / r['certificate']).read_text())
            assert s['verdict'] == 'NONBIPLANAR_CERTIFIED' and s['proof']['certified']
            defs[r['name']] = (r['g6'], r['u'])
    return defs


def check(path, domain=None):
    d = json.load(gzip.open(path, 'rt'))
    n, w = d['n'], d['w']
    defs = definitions()
    cache = {}
    counts = {}
    for L in d['learned']:
        kind = L['kind'].replace('_PERM', '')
        src = [tuple(e) for e in L['source_edges']]
        p = L['perm']
        if p is not None:
            assert sorted(p) == list(range(n)) and all(w[p[v]] == w[v] for v in range(n))
            img = sorted((min(p[a], p[b]), max(p[a], p[b])) for a, b in src)
        else:
            img = sorted(src)
        assert img == sorted(tuple(e) for e in L['edges'])
        S = set(src)
        assert all(0 <= a < b < n for a, b in S)
        if kind in ('PRELOAD', 'CONTAIN'):
            name = L['obstruction']
            if name not in cache:
                cache[name] = blow(*defs[name])
            HE, hb = cache[name]
            f = L['f']
            assert len(f) == len(hb)
            start = [sum(w[:b]) for b in range(n)]
            used = [0] * n
            lab = []
            for b in f:
                lab.append(start[b] + used[b])
                used[b] += 1
            assert all(used[b] <= w[b] for b in range(n)) and len(set(lab)) == len(lab)
            for a, c in HE:
                ba, bc = f[a], f[c]
                assert ba == bc or (min(ba, bc), max(ba, bc)) in S, (name, a, c)
        elif kind == 'EULER':
            T = set(L['T'])
            assert all(a in T and b in T for a, b in S)
            WT = sum(w[v] for v in T)
            cnt = sum(w[v] * (w[v] - 1) // 2 for v in T) + sum(w[a] * w[b] for a, b in S)
            assert cnt > 6 * WT - 12 and WT >= 3
        else:
            raise AssertionError(kind)
        counts[L['kind']] = counts.get(L['kind'], 0) + 1
    rec = {'profile': d['profile'], 'w': w, 'learned_checked': len(d['learned']), 'by_kind': counts,
           'blocks': len(d['blocks'])}
    if domain:
        rec['domain_byte_identical'] = regen(d) == Path(domain).read_bytes()
        assert rec['domain_byte_identical']
    print(json.dumps(rec))
    return rec


def regen(d):
    """Independent rebuild of the generator base formula plus learned/blocks."""
    from pysat.card import CardEnc, EncType
    n, w = d['n'], d['w']
    pairs = [tuple(e) for e in d['pairs']]
    assert sorted(pairs) == list(it.combinations(range(n), 2))
    idx = {e: i + 1 for i, e in enumerate(pairs)}
    v = lambda a, b: idx[(min(a, b), max(a, b))]
    cls = [[v(a, b) for a, b in it.combinations(S, 2)] for S in it.combinations(range(n), 4)]
    for k in range(2, n + 1):
        for S in it.combinations(range(n), k):
            t = sum(w[x] for x in S)
            if t >= 9 and all(t - w[x] < 9 for x in S):
                cls.append([-v(a, b) for a, b in it.combinations(S, 2)])
    top, units = len(pairs), []
    for e, x in idx.items():
        for _ in range(w[e[0]] * w[e[1]]):
            top += 1
            cls += [[-x, top], [x, -top]]
            units.append(top)
    card = CardEnc.atmost(units, 156 - sum(x * (x - 1) // 2 for x in w), top_id=top,
                          encoding=EncType.seqcounter)
    cls += card.clauses
    cls += [[-idx[tuple(e)] for e in L['edges']] for L in d['learned']]
    for b in d['blocks']:
        B = set(map(tuple, b['edges']))
        cls.append([-idx[e] if e in B else idx[e] for e in pairs])
    nv = max([card.nv] + [abs(l) for c in cls for l in c])
    return (f'p cnf {nv} {len(cls)}\n' + ''.join(' '.join(map(str, c)) + ' 0\n' for c in cls)).encode()


if __name__ == '__main__':
    check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
