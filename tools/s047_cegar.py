"""S047 amendment A1: CEGAR form of the E2 extension question (D079).

Same question as tools/s047_extend.py for k = 9 and exactly t added vertices,
restricted (soundly, sessions/S047/RESEARCH.md L3/L4) to |X|-minimal
solutions and one ordering of X:

  * every added vertex has degree >= 9 (L3: in a solution with minimum |X|);
  * seed-adjacency rows of X are lexicographically non-increasing (L4: all
    constraints are invariant under permuting X).

Colour clauses are added lazily: a candidate graph is 9-coloured by an
independent SAT colouring; the colouring determines a partition P (the
singleton of B) and a placement phi of X, and the clause for (P, phi) -
exactly the clause tools/s047_extend.py would contain - is learned. Learned
clauses are therefore a subset of the full E2 formula; UNSAT of the final
formula (filters + degree + lex + learned) implies UNSAT of the full one.
"""
import itertools as it

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from s047_extend import build, partitions


def lex_geq(rowa, rowb, pool):
    cl, eq = [], None
    for j, (a, b) in enumerate(zip(rowa, rowb)):
        pre = [] if eq is None else [-eq]
        cl.append(pre + [a, -b])
        if j == len(rowa) - 1:
            break
        nxt = pool.id(('lexeq', rowa[0], rowb[0], j))
        cl.append(pre + [-a, -b, nxt])
        cl.append(pre + [a, b, nxt])
        eq = nxt
    return cl


def base(t, filters=True):
    f = build(9, t, filters, colour=False)
    pool = f['pool']
    e = lambda u, v: pool.obj2id[('e', min(u, v), max(u, v))]  # noqa: E731
    n0, X = f['n0'], f['X']
    cl = list(f['clauses'])               # filters only (no colour clauses)
    for x in X:
        lits = [e(v, x) for v in range(n0)] + [e(x, y) for y in X if y != x]
        cl += CardEnc.atleast(lits=lits, bound=9, vpool=pool, encoding=EncType.seqcounter).clauses
    rows = [[e(v, x) for v in range(n0)] for x in X]
    for i in range(t - 1):
        cl += lex_geq(rows[i], rows[i + 1], pool)
    return f, e, cl


def colour_clause(f, e, s, phi):
    A, B, X = f['A'], f['B'], f['X']
    classes = [[v] for v in A] + partitions(B)[s]
    c = {e(v, X[i]) for i in range(len(X)) for v in classes[phi[i]]}
    c |= {e(X[i], X[j]) for i, j in it.combinations(range(len(X)), 2) if phi[i] == phi[j]}
    return sorted(c)


def nine_colour(n, edges):
    var = lambda v, c: v * 9 + c + 1  # noqa: E731
    with Solver(name='g4') as s:
        for v in range(n):
            s.add_clause([var(v, c) for c in range(9)])
        for u, v in edges:
            for c in range(9):
                s.add_clause([-var(u, c), -var(v, c)])
        if not s.solve():
            return None
        m = set(l for l in s.get_model() if l > 0)
        return [next(c for c in range(9) if var(v, c) in m) for v in range(n)]


def placement(f, col):
    """Map a proper 9-colouring of G' to (s, phi) of lemma L1."""
    A, B, X = f['A'], f['B'], f['X']
    bcols = [col[b] for b in B]
    single = next(i for i in range(5) if bcols.count(bcols[i]) == 1)
    s = single
    P = partitions(B)[s]
    cls = {col[a]: i for i, a in enumerate(A)}
    for j, part in enumerate(P):
        cls[col[part[0]]] = len(A) + j
    assert len(cls) == 9
    return s, tuple(cls[col[x]] for x in X)


def run(t, deadline, log=None, filters=True):
    from s047_extend import decode
    f, e, cl = base(t, filters)
    learned = []
    with Solver(name='cd15', bootstrap_with=cl) as s:
        import time
        while True:
            if time.time() > deadline:
                return 'CAPPED', f, cl, learned, None
            if not s.solve():
                return 'UNSAT', f, cl, learned, None
            model = s.get_model()
            edges = decode(f, [l for l in model if 0 < abs(l) <= f['nvars0']])
            n = f['n0'] + t
            col = nine_colour(n, edges)
            if col is None:
                return 'CANDIDATE', f, cl, learned, edges
            sp = placement(f, col)
            c = colour_clause(f, e, *sp)
            assert not any(l in set(model) for l in c)
            learned.append(sp)
            s.add_clause(c)
            if log and len(learned) % 500 == 0:
                log(len(learned))
