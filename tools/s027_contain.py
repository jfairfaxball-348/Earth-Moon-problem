#!/usr/bin/env python3
"""S027 obstruction-support learning: containment encoder, decoder and support.

An obstruction is a certified non-biplanar clique blow-up H = A[u]. A target is a
clique blow-up B[w] on a base graph B with bag capacities w. X[v,b] puts H vertex v
into target bag b. Exactly one bag per v; at most w[b] vertices per bag; for every
H edge vz and distinct target bags a,b the pair X[v,a],X[z,b] requires base edge ab
(variable y_ab in the in-loop form, a fixed nonedge clause in the audit form).
Consecutive H twins (same H bag) take nondecreasing target bags (safe, true twins).

SUPPORT LEMMA (CLM-0101). If a satisfying assignment f has support
S = {f(v)f(z) : vz in E(H), f(v) != f(z)}, then for EVERY base graph B' on the same
labelled vertices with S a subset of E(B') and the same capacities w, the explicit
labelled map (consecutive labels inside each target bag) is an injective subgraph
embedding of H into B'[w]: same-bag pairs are clique edges, cross-bag pairs use an
edge of S. Hence B'[w] is non-biplanar and the clause OR_{e in S} -y_e is sound for
the profile w. A weight-preserving relabelling pi of base vertices maps B'[w] to an
isomorphic blow-up, so the image clause OR_{e in S} -y_{pi(e)} is also sound.
"""
import itertools as it
import json
from math import comb
from pathlib import Path
import sys

import networkx as nx
from pysat.card import CardEnc, EncType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from blowup_graph import blowup   # noqa: E402

DIRECT_CAP_LIMIT = 20000


def obstruction(name, g6, u):
    """Explicit H edges, twin bag labels and the labelled edge-file text."""
    edges, bags = blowup(g6, list(u))
    hbag = [None] * sum(u)
    for i, b in enumerate(bags):
        for v in b:
            hbag[v] = i
    text = ''.join(f'{a} {b}\n' for a, b in edges)
    return {'name': name, 'g6': g6, 'u': list(u), 'n': sum(u), 'edges': edges,
            'hbag': hbag, 'edge_text': text}


def capacity(nh, cap, lits, top):
    """At most cap of lits: direct subset clauses when small, else seqcounter."""
    if cap >= nh:
        return [], top, 'NONE'
    if comb(nh, cap + 1) <= DIRECT_CAP_LIMIT:
        return [[-l for l in S] for S in it.combinations(lits, cap + 1)], top, 'DIRECT'
    enc = CardEnc.atmost(lits, cap, top_id=top, encoding=EncType.seqcounter)
    return enc.clauses, max(top, enc.nv), 'SEQCOUNTER'


def encode(H, w, pairs=None, B=None):
    """In-loop form (pairs given: y_e = 1+index) or audit form (B given)."""
    nb, nh = len(w), H['n']
    off = len(pairs) if pairs is not None else 0
    yidx = {e: i + 1 for i, e in enumerate(pairs)} if pairs is not None else None
    x = lambda v, b: off + 1 + v * nb + b
    top = off + nh * nb
    cls = []
    for v in range(nh):
        cls.append([x(v, b) for b in range(nb)])
        cls.extend([-x(v, a), -x(v, b)] for a, b in it.combinations(range(nb), 2))
    kinds = []
    for b, cap in enumerate(w):
        c, top, kind = capacity(nh, cap, [x(v, b) for v in range(nh)], top)
        cls.extend(c)
        kinds.append(kind)
    for v, z in H['edges']:
        for a, b in it.permutations(range(nb), 2):
            if yidx is not None:
                cls.append([-x(v, a), -x(z, b), yidx[(min(a, b), max(a, b))]])
            elif not B.has_edge(a, b):
                cls.append([-x(v, a), -x(z, b)])
    for v in range(nh - 1):
        if H['hbag'][v] == H['hbag'][v + 1]:
            cls.extend([-x(v, a), -x(v + 1, b)] for a in range(nb) for b in range(a))
    return cls, top, x, kinds


def decode(H, w, model_true, x):
    nb = len(w)
    f = [next(b for b in range(nb) if x(v, b) in model_true) for v in range(H['n'])]
    return f


def explicit_map(H, w, f, base_edges):
    """Independent explicit check on the labelled blow-up of base_edges."""
    start = [sum(w[:b]) for b in range(len(w))]
    used = [0] * len(w)
    vm = {}
    for v, b in enumerate(f):
        vm[v] = start[b] + used[b]
        used[b] += 1
    assert all(used[b] <= w[b] for b in range(len(w)))
    assert len(set(vm.values())) == H['n']
    E = {tuple(sorted(e)) for e in base_edges}
    bag = [b for b in range(len(w)) for _ in range(w[b])]
    for a, c in H['edges']:
        p, q = vm[a], vm[c]
        assert bag[p] == bag[q] or (min(bag[p], bag[q]), max(bag[p], bag[q])) in E, (a, c)
    return vm


def support(H, f):
    return sorted({(min(f[a], f[c]), max(f[a], f[c])) for a, c in H['edges'] if f[a] != f[c]})


def usage(H, f, nb):
    u = [0] * nb
    for b in f:
        u[b] += 1
    return u


def weight_perms(w, count, rng):
    """Random relabellings preserving w (permute within equal-weight classes)."""
    classes = {}
    for v, x in enumerate(w):
        classes.setdefault(x, []).append(v)
    out = []
    for _ in range(count):
        p = list(range(len(w)))
        for members in classes.values():
            img = members[:]
            rng.shuffle(img)
            for a, b in zip(members, img):
                p[a] = b
        if p != list(range(len(w))) and p not in out:
            out.append(p)
    return out


def load_obstructions():
    """All certified obstructions usable as filters, with edge-file checks."""
    import hashlib
    out = []
    certs = json.loads((ROOT / 'validation/S025/C5_CERTIFICATES.json').read_text())
    for e in certs:
        if e.get('certified'):
            H = obstruction('C5-' + e['tag'], 'Dhc', list(map(int, e['tag'])))
            f = ROOT / 'validation/S025/certs' / ('C5-' + e['tag'] + '.edges')
            raw = f.read_bytes()
            # The recorded digest is of the stored edge file; compare content LF-normalised.
            assert hashlib.sha256(raw).hexdigest() == e['edges_sha256'], e['tag']
            assert raw.replace(b'\r\n', b'\n') == H['edge_text'].encode(), e['tag']
            H['certificate'] = 'validation/S025/C5_CERTIFICATES.json'
            out.append(H)
    for tag in ('24335', '23525', '23534'):
        d = ROOT / 'validation/S026/local' / ('C5-' + tag)
        s = json.loads((d / 'SUMMARY.json').read_text())
        assert s['verdict'] == 'NONBIPLANAR_CERTIFIED' and s['proof']['certified']
        H = obstruction('C5-' + tag, 'Dhc', list(map(int, tag)))
        assert (d / 'graph.edges').read_bytes().replace(b'\r\n', b'\n') == H['edge_text'].encode()
        H['certificate'] = str((d / 'SUMMARY.json').relative_to(ROOT)).replace('\\', '/')
        out.append(H)
    d = ROOT / 'validation/S026/filter-recovery/candidate'
    c = json.loads((d / 'CANDIDATE.json').read_text())
    s = json.loads((d / 'SUMMARY.json').read_text())
    assert s['verdict'] == 'NONBIPLANAR_CERTIFIED'
    H = obstruction('P29-B14-0001', c['g6'], c['w'])
    assert (d / 'graph.edges').read_bytes().replace(b'\r\n', b'\n') == H['edge_text'].encode()
    H['certificate'] = 'validation/S026/filter-recovery/candidate/SUMMARY.json'
    out.append(H)
    extra = Path(__import__('os').environ.get('EMP_S027_EXTRA_OBSTRUCTIONS', ''))
    if extra.is_file():
        for r in json.loads(extra.read_text()):
            H = obstruction(r['name'], r['g6'], r['u'])
            assert (ROOT / r['edges']).read_bytes().replace(b'\r\n', b'\n') == H['edge_text'].encode()
            s = json.loads((ROOT / r['certificate']).read_text())
            assert s['verdict'] == 'NONBIPLANAR_CERTIFIED' and s['proof']['certified']
            H['certificate'] = r['certificate']
            out.append(H)
    return out


if __name__ == '__main__':
    obs = load_obstructions()
    print(json.dumps([[H['name'], H['n'], len(H['edges'])] for H in obs]))
