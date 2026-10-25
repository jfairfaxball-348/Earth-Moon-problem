"""S046 instance encodings for matched pilots (bipsat2 optional-pair format).

Variables 2i+1 / 2i+2 put pair i (lexicographic combinations order, as in
S045) in layer 1 / layer 2. Arms:
  B  : layer disjointness only (the S045 domain at order n);
  C  : B + union degree >= k at every vertex (k=9: minimum degree of a
       10-critical graph), exact two-sided sequential counter;
  CS : C + union variables, lex-leader row_i >=lex row_j over columns other
       than i,j for all i<j, and "first present union pair lies in layer 1".
Preservation arguments are in sessions/S046/RESEARCH.md; exhaustive small
controls are scripts/s046_controls.py. Colouring-partition clauses (CLM-0146)
are appended only for already audited records.
"""
import itertools as it
from pathlib import Path


class CNF:
    def __init__(self, top):
        self.top, self.clauses = top, []

    def new(self):
        self.top += 1
        return self.top

    def add(self, c):
        self.clauses.append(list(c))


def pairs_of(n):
    return list(it.combinations(range(n), 2))


def at_least(cnf, lits, d):
    """Two-sided counter r[i][j] <-> (#true among lits[:i]) >= j, j<=d; assert r[L][d]."""
    L = len(lits)
    if d <= 0:
        return
    if d > L:
        v = cnf.new()  # infeasible: complementary units (no empty clause)
        cnf.add([v])
        cnf.add([-v])
        return
    r = {}
    for i in range(1, L + 1):
        x = lits[i - 1]
        for j in range(1, min(i, d) + 1):
            v = r[i, j] = cnf.new()
            prev = r.get((i - 1, j))          # None means constant false (j > i-1)
            prev1 = r.get((i - 1, j - 1)) if j > 1 else True
            # backward: r[i][j] -> prev OR (x AND prev1)
            cnf.add([-v] + ([prev] if prev else []) + [x])
            if prev1 is not True:
                cnf.add([-v] + ([prev] if prev else []) + [prev1])
            # forward: prev -> r[i][j];  x AND prev1 -> r[i][j]
            if prev:
                cnf.add([-prev, v])
            cnf.add([-x, v] if prev1 is True else [-x, -prev1, v])
    cnf.add([r[L, d]])


def union_vars(cnf, m):
    u = []
    for i in range(m):
        v = cnf.new()
        a, b = 2 * i + 1, 2 * i + 2
        cnf.add([-a, v])
        cnf.add([-b, v])
        cnf.add([-v, a, b])
        u.append(v)
    return u


def lex_geq(cnf, xs, ys):
    """xs >=lex ys (most significant first)."""
    e = None  # None = constant true "equal so far"
    for t, (a, b) in enumerate(zip(xs, ys)):
        pre = [] if e is None else [-e]
        cnf.add(pre + [a, -b])
        if t < len(xs) - 1:
            nxt = cnf.new()
            cnf.add(pre + [a, b, nxt])
            cnf.add(pre + [-a, -b, nxt])
            e = nxt


def symmetry(cnf, n, pairs, u):
    index = {p: i for i, p in enumerate(pairs)}
    U = lambda a, b: u[index[(min(a, b), max(a, b))]]
    for i, j in it.combinations(range(n), 2):
        cols = [c for c in range(n) if c not in (i, j)]
        lex_geq(cnf, [U(i, c) for c in cols], [U(j, c) for c in cols])
    # First present union pair (in pair order) is in layer 1.
    cnf.add([-2])
    p_prev = None
    for t in range(1, len(pairs)):
        p = cnf.new()
        cnf.add([-(2 * t + 2), p])
        cnf.add([-p, u[t - 1]] + ([p_prev] if p_prev else []))
        p_prev = p


def clauses(n, arm, k=9, partition_colourings=()):
    pairs = pairs_of(n)
    m = len(pairs)
    cnf = CNF(2 * m)
    for i in range(m):
        cnf.add([-(2 * i + 1), -(2 * i + 2)])
    if arm in ('C', 'CS'):
        for v in range(n):
            lits = [2 * i + 1 + layer for i, p in enumerate(pairs) if v in p for layer in (0, 1)]
            at_least(cnf, lits, k)
    if arm == 'CS':
        symmetry(cnf, n, pairs, union_vars(cnf, m))
    elif arm not in ('B', 'C'):
        raise ValueError(arm)
    for cols in partition_colourings:
        assert len(cols) == n
        cnf.add([2 * i + 1 + j for i, (a, b) in enumerate(pairs) if cols[a] == cols[b] for j in (0, 1)])
    return pairs, cnf


def write(path, n, arm, k=9, partition_colourings=()):
    pairs, cnf = clauses(n, arm, k, partition_colourings)
    m = len(pairs)
    with Path(path).open('w', encoding='ascii', newline='\n') as f:
        f.write(f'p bipsat2 {n} {m} {cnf.top - 2 * m} {len(cnf.clauses)}\n')
        f.writelines(f'e {a} {b}\n' for a, b in pairs)
        f.writelines(' '.join(map(str, c)) + ' 0\n' for c in cnf.clauses)
    return dict(pairs=m, extra_vars=cnf.top - 2 * m, clauses=len(cnf.clauses))
