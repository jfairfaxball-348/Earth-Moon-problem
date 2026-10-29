"""S047 E2: seeded one-step extensions of the seed K_{k-3} v C5 (D079).

Seed S: A = vertices 0..a-1 (a = k-3, a clique), B = a..a+4 (a 5-cycle in
order), A complete to B. Added vertices X = a+5 .. a+4+t. The CNF is
satisfiable iff there is a graph G' on S ∪ X with G'[S] = S, satisfying the
registered necessary biplanarity filters, that has no proper k-colouring.

Lemma (sessions/S047/RESEARCH.md, L1): every proper k-colouring of S gives A
a distinct colours and B the remaining three, partitioning B as {singleton,
pair, pair}, determined by the singleton b_s (five partitions). Hence G' is
k-colourable iff for some partition P and placement phi of X into the k
colour classes of (A singletons) + P, nothing conflicts. Each (P, phi) gives
one clause: the disjunction of the edge literals that would conflict.
"""
import itertools as it
import json
import sys

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def seed(k):
    a = k - 3
    A = list(range(a))
    B = list(range(a, a + 5))
    edges = set(it.combinations(A, 2))
    edges |= {(x, y) for x in A for y in B}
    edges |= {tuple(sorted((B[i], B[(i + 1) % 5]))) for i in range(5)}
    return A, B, edges


def partitions(B):
    out = []
    for s in range(5):
        r = [B[(s + j) % 5] for j in range(5)]
        out.append([[r[0]], [r[1], r[3]], [r[2], r[4]]])
    return out


def build(k, t, filters=True, colour=True):
    A, B, sedges = seed(k)
    n0 = len(A) + 5
    X = list(range(n0, n0 + t))
    pool = IDPool()

    def e(u, v):
        u, v = min(u, v), max(u, v)
        return pool.id(('e', u, v))

    for x in X:                      # fix variable numbering first
        for v in range(n0):
            e(v, x)
    for x, y in it.combinations(X, 2):
        e(x, y)
    nvars0 = pool.top
    clauses = []
    for P in (partitions(B) if colour else []):
        classes = [[v] for v in A] + P
        for phi in it.product(range(k), repeat=t):
            cl = []
            for i, x in enumerate(X):
                cl += [e(x, v) for v in classes[phi[i]]]
            for i, j in it.combinations(range(t), 2):
                if phi[i] == phi[j]:
                    cl.append(e(X[i], X[j]))
            clauses.append(sorted(set(cl)))
    if filters:
        m0 = len(sedges)
        for r in range(1, t + 1):
            for Xs in it.combinations(X, r):
                lits = [e(x, v) for x in Xs for v in range(n0)]
                lits += [e(x, y) for x, y in it.combinations(Xs, 2)]
                bound = 6 * (n0 + r) - 12 - m0
                clauses += card(lits, bound, pool)
                lits = [e(x, v) for x in Xs for v in A]
                lits += [e(x, y) for x, y in it.combinations(Xs, 2)]
                bound = 6 * (len(A) + r) - 12 - len(A) * (len(A) - 1) // 2
                clauses += card(lits, bound, pool)
        # no K9: 9-sets whose seed pairs are all edges (at most 2 B vertices,
        # adjacent); clause forbids all their variable pairs being present
        bpairs = [()] + [(b,) for b in B] + [tuple(sorted((B[i], B[(i + 1) % 5]))) for i in range(5)]
        for bp in bpairs:
            for ra in range(len(A) + 1):
                rx = 9 - ra - len(bp)
                if rx < 1 or rx > t:
                    continue
                for As in it.combinations(A, ra):
                    for Xs in it.combinations(X, rx):
                        S = list(As) + list(bp) + list(Xs)
                        cl = [-e(u, v) for u, v in it.combinations(S, 2) if max(u, v) >= n0]
                        clauses.append(cl)
    return {'k': k, 't': t, 'filters': filters, 'n0': n0, 'A': A, 'B': B,
            'seed_edges': sorted(sedges), 'X': X, 'nvars0': nvars0,
            'nvars': pool.top, 'clauses': clauses, 'pool': pool}


def card(lits, bound, pool):
    if bound >= len(lits):
        return []
    if bound < 0:
        return [[]]
    enc = CardEnc.atmost(lits=lits, bound=bound, vpool=pool, encoding=EncType.seqcounter)
    return enc.clauses


def dimacs(f):
    nv = max([f['nvars']] + [abs(l) for c in f['clauses'] for l in c])
    lines = [f'p cnf {nv} {len(f["clauses"])}']
    lines += [' '.join(map(str, c)) + ' 0' for c in f['clauses']]
    return '\n'.join(lines) + '\n'


def decode(f, model):
    pos = {l for l in model if l > 0}
    edges = set(map(tuple, f['seed_edges']))
    for v in range(f['n0'] + f['t']):
        for u in range(v):
            if u >= f['n0'] or v >= f['n0']:
                if f['pool'].obj2id.get(('e', u, v)) in pos:
                    edges.add((u, v))
    return sorted(edges)


if __name__ == '__main__':
    k, t = int(sys.argv[1]), int(sys.argv[2])
    filt = len(sys.argv) < 4 or sys.argv[3] != 'nofilter'
    f = build(k, t, filt)
    sys.stdout.write(dimacs(f))
    json.dump({'k': k, 't': t, 'nvars0': f['nvars0'], 'clauses': len(f['clauses'])}, sys.stderr)
