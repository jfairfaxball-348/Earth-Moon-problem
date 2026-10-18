#!/usr/bin/env python3
"""S025: complete two-sphere-triangulation SAT engine (CAM-0027 / CAM-0028).

Two labelled layers i in {0,1} on the vertex set 0..n-1.  Per layer:
  x[i,ab]  pair ab is an edge of triangulation T_i
  t[i,abc] triple abc is a (facial) triangle of T_i
Eager clauses (every pair of sphere triangulations satisfies them, n>=4):
  F1  t[abc] -> x[ab], x[ac], x[bc]
  F2  at most two selected triangles contain each pair ab
  F3  x[ab] -> at least two selected triangles contain ab
  F4  sum_ab x[ab] = 3n-6   (then F2/F3 give 3F = 2E, so F = 2n-4)
  F5  every vertex lies in a selected triangle
Lazy cuts, each an instance of a lemma valid for every sphere triangulation:
  LINK(i,v,S,a,u)  a in S, u notin S+{v}:
      -x[va] | -x[vu] | OR_{s in S, w notin S+{v}} t[vsw]
      (the link of v is ONE cycle through a and u, so it leaves S)
  CONN(i,S)        0 < |S| < n:  OR_{s in S, w notin S} x[sw]
A model violating no cut is a connected closed simplicial 2-manifold with
V-E+F = n-(3n-6)+(2n-4) = 2, i.e. a sphere triangulation (S025 RESEARCH, CLM-0089).
Modes:
  cover EDGEFILE OUT SECONDS          G has thickness<=2 iff E(G) in T_0 u T_1
  chrom N K OUT SECONDS [--mindeg D]   exists T_0,T_1 with chi(T_0 u T_1) >= K
UNSAT verdicts are provisional until the written CNF is re-solved by the
native solver with a DRAT proof checked by drat-trim (tools/s025_certify.py).
"""
import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


class TwoTri:
    def __init__(self, n, face_sb=False):
        assert n >= 4
        self.n = n
        self.pairs = list(itertools.combinations(range(n), 2))
        self.triples = list(itertools.combinations(range(n), 3))
        self.pool = pool = IDPool()
        self.x = {(i, p): pool.id(('x', i) + p) for i in range(2) for p in self.pairs}
        self.t = {(i, q): pool.id(('t', i) + q) for i in range(2) for q in self.triples}
        self.clauses = []          # (family, clause)
        self.cuts = []             # json records of lazy cuts, in order of addition
        self.extra = []            # json records of mode-specific clauses (colourings)
        for i in range(2):
            self._layer(i)
        if face_sb:
            # Relabelling: T_0 has a face 012, the other face on edge 01 is 013,
            # and the other face on edge 02 is 023 or 024.
            self.add('SB', [self.T(0, 0, 1, 2)])
            self.add('SB', [self.T(0, 0, 1, 3)])
            self.add('SB', [self.T(0, 0, 2, 3), self.T(0, 0, 2, 4)])

    def add_lex(self, xs, ys, fam='LEX'):
        """Clauses for xs <=_lex ys (positions with identical literals skipped)."""
        prefix = None
        for x, y in zip(xs, ys):
            if x == y:
                continue
            pre = [] if prefix is None else [-prefix]
            self.add(fam, pre + [-x, y])
            nxt = self.pool.id()
            # (prefix and x == y) -> nxt: nxt is forced whenever equality holds so far
            self.add(fam, pre + [x, y, nxt])
            self.add(fam, pre + [-x, -y, nxt])
            prefix = nxt

    def X(self, i, a, b):
        return self.x[i, (a, b) if a < b else (b, a)]

    def T(self, i, a, b, c):
        return self.t[i, tuple(sorted((a, b, c)))]

    def add(self, fam, cl):
        self.clauses.append((fam, list(cl)))

    def card(self, fam, lits, bound, kind, gate=None):
        enc = getattr(CardEnc, kind)(lits=lits, bound=bound, vpool=self.pool,
                                     encoding=EncType.seqcounter if kind != 'equals'
                                     else EncType.kmtotalizer)
        for cl in enc.clauses:
            self.add(fam, ([-gate] if gate is not None else []) + cl)

    def _layer(self, i):
        n = self.n
        for a, b, c in self.triples:
            f = self.T(i, a, b, c)
            for u, v in ((a, b), (a, c), (b, c)):
                self.add('F1', [-f, self.X(i, u, v)])
        for a, b in self.pairs:
            e = self.X(i, a, b)
            fs = [self.T(i, a, b, c) for c in range(n) if c not in (a, b)]
            self.card('F2', fs, 2, 'atmost')
            self.add('F3', [-e] + fs)
            for f in fs:
                self.add('F3', [-e, -f] + [g for g in fs if g != f])
        self.card('F4', [self.X(i, a, b) for a, b in self.pairs], 3 * n - 6, 'equals')
        for v in range(n):
            self.add('F5', [self.T(i, *q) for q in self.triples if v in q])

    # ---- lazy cuts -------------------------------------------------------
    def cut_clause(self, cut):
        i = cut['layer']
        if cut['kind'] == 'CONN':
            S = set(cut['S'])
            assert 0 < len(S) < self.n
            return [self.X(i, a, b) for a, b in self.pairs if (a in S) != (b in S)]
        assert cut['kind'] == 'LINK'
        v, S, a, u = cut['v'], set(cut['S']), cut['a'], cut['u']
        assert v not in S and a in S and u not in S and u != v
        out = [w for w in range(self.n) if w != v and w not in S]
        return ([-self.X(i, v, a), -self.X(i, v, u)] +
                [self.T(i, v, s, w) for s in sorted(S) for w in out])

    def violations(self, model):
        """Cuts violated by a model that already satisfies the eager clauses."""
        found = []
        for i in range(2):
            adj = {v: set() for v in range(self.n)}
            for a, b in self.pairs:
                if model[self.X(i, a, b)]:
                    adj[a].add(b)
                    adj[b].add(a)
            seen, comps = set(), []
            for s in range(self.n):
                if s in seen:
                    continue
                comp, stack = {s}, [s]
                while stack:
                    y = stack.pop()
                    for z in adj[y]:
                        if z not in comp:
                            comp.add(z)
                            stack.append(z)
                seen |= comp
                comps.append(comp)
            if len(comps) > 1:
                for comp in comps:
                    found.append({'kind': 'CONN', 'layer': i, 'S': sorted(comp)})
            link = {v: {} for v in range(self.n)}
            for q in self.triples:
                if model[self.T(i, *q)]:
                    for v in q:
                        a, b = [w for w in q if w != v]
                        link[v].setdefault(a, []).append(b)
                        link[v].setdefault(b, []).append(a)
            for v in range(self.n):
                nb = link[v]
                cycles, left = [], set(nb)
                while left:
                    s = min(left)
                    comp, stack = {s}, [s]
                    while stack:
                        y = stack.pop()
                        for z in nb[y]:
                            if z not in comp:
                                comp.add(z)
                                stack.append(z)
                    left -= comp
                    cycles.append(comp)
                if len(cycles) > 1:
                    for k, comp in enumerate(cycles):
                        other = cycles[(k + 1) % len(cycles)]
                        found.append({'kind': 'LINK', 'layer': i, 'v': v, 'S': sorted(comp),
                                      'a': min(comp), 'u': min(other)})
        return found

    def layers(self, model):
        return [[p for p in self.pairs if model[self.X(i, *p)]] for i in range(2)], \
               [[q for q in self.triples if model[self.T(i, *q)]] for i in range(2)]

    def all_clauses(self):
        return ([c for _, c in self.clauses] + [self.cut_clause(c) for c in self.cuts] +
                [self.extra_clause(r) for r in self.extra])

    def extra_clause(self, rec):
        raise NotImplementedError

    def write_cnf(self, path):
        cls = self.all_clauses()
        text = f'p cnf {self.pool.top} {len(cls)}\n' + ''.join(
            ' '.join(map(str, c)) + ' 0\n' for c in cls)
        Path(path).write_text(text, newline='\n')
        return hashlib.sha256(text.encode()).hexdigest(), len(cls)


def solve_loop(enc, seconds, accept, solver_name='cadical195', log=None, max_iter=None):
    """CEGAR loop: lazy topology cuts, then mode-specific acceptance."""
    start = time.monotonic()
    it = 0
    stats = {'topology_cuts': 0, 'extra': 0}
    with Solver(name=solver_name, bootstrap_with=[c for _, c in enc.clauses]) as s:
        for c in enc.cuts:
            s.add_clause(enc.cut_clause(c))
        for r in enc.extra:
            s.add_clause(enc.extra_clause(r))
        while True:
            if time.monotonic() - start > seconds or (max_iter and it >= max_iter):
                return 'UNKNOWN', None, it, time.monotonic() - start, stats
            it += 1
            if not s.solve():
                return 'UNSAT', None, it, time.monotonic() - start, stats
            m = s.get_model()
            model = [False] * (enc.pool.top + 2)
            for lit in m:
                if lit > 0 and lit < len(model):
                    model[lit] = True
            cuts = enc.violations(model)
            if cuts:
                for c in cuts:
                    enc.cuts.append(c)
                    s.add_clause(enc.cut_clause(c))
                stats['topology_cuts'] += len(cuts)
                continue
            new = accept(model)
            if new is None:
                return 'SAT', model, it, time.monotonic() - start, stats
            for r in new:
                enc.extra.append(r)
                s.add_clause(enc.extra_clause(r))
            stats['extra'] += len(new)
            if log and it % 50 == 0:
                log(f'it={it} t={time.monotonic()-start:.1f} cuts={len(enc.cuts)} extra={len(enc.extra)}')


# ---- cover mode -----------------------------------------------------------
class Cover(TwoTri):
    def __init__(self, n, edges, swap_sb=True):
        super().__init__(n)
        self.input = sorted(tuple(sorted(e)) for e in edges)
        assert len(set(self.input)) == len(self.input)
        for a, b in self.input:
            self.add('COVER', [self.X(0, a, b), self.X(1, a, b)])
        if swap_sb and self.input:
            a, b = self.input[0]
            self.add('SB', [self.X(0, a, b)])   # layers are interchangeable


# ---- chromatic mode -------------------------------------------------------
class Chrom(TwoTri):
    def __init__(self, n, k, mindeg=0, face_sb=True):
        super().__init__(n, face_sb=face_sb)
        self.k = k
        self.y = {}
        for a, b in self.pairs:
            y = self.pool.id(('y', a, b))
            self.y[a, b] = y
            x0, x1 = self.X(0, a, b), self.X(1, a, b)
            self.add('Y', [-y, x0, x1])
            self.add('Y', [y, -x0])
            self.add('Y', [y, -x1])
        if mindeg:
            for v in range(n):
                self.card('DEG', [self.Y(v, u) for u in range(n) if u != v], mindeg, 'atleast')

    def Y(self, a, b):
        return self.y[(a, b) if a < b else (b, a)]

    def extra_clause(self, rec):
        col = rec['colouring']
        return [self.Y(a, b) for a, b in self.pairs if col[a] == col[b]]


def transposition_lex(enc, getvar, verts):
    """Lex-leader for every transposition of `verts` on the vector getvar(pair)."""
    vec = [getvar(a, b) for a, b in enc.pairs]
    for i, j in itertools.combinations(verts, 2):
        def img(v):
            return j if v == i else i if v == j else v
        enc.add_lex(vec, [getvar(img(a), img(b)) for a, b in enc.pairs])


class Indep(Chrom):
    """exists T_0,T_1 on n vertices whose union has independence number <= alpha.

    By monotonicity (adding edges never raises alpha) and heredity (an induced
    subgraph of a biplanar graph is biplanar), this is equivalent to the
    existence of ANY biplanar graph of order n with alpha <= alpha.
    """
    def __init__(self, n, alpha, sb='face', k=None, mindeg=0):
        super().__init__(n, k or 0, mindeg=mindeg, face_sb=(sb == 'face'))
        self.alpha = alpha
        if sb == 'lex':
            transposition_lex(self, self.Y, range(n))
        for Q in itertools.combinations(range(n), alpha + 1):
            self.add('IND', [self.Y(a, b) for a, b in itertools.combinations(Q, 2)])


def colour(n, edges, k, solver_name='cadical195', seconds=None):
    """Proper k-colouring of the graph or None (no claim of optimality)."""
    var = lambda v, c: v * k + c + 1
    cls = [[var(v, c) for c in range(k)] for v in range(n)]
    for a, b in edges:
        for c in range(k):
            cls.append([-var(a, c), -var(b, c)])
    with Solver(name=solver_name, bootstrap_with=cls) as s:
        if not s.solve():
            return None
        m = set(l for l in s.get_model() if l > 0)
    out = []
    for v in range(n):
        out.append(next(c for c in range(k) if var(v, c) in m))
    return out


def read_edges(path):
    es = []
    for line in Path(path).read_text().split('\n'):
        p = line.split()
        if len(p) >= 2:
            es.append((int(p[0]), int(p[1])))
    return es


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    c = sub.add_parser('cover')
    c.add_argument('edges')
    c.add_argument('out')
    c.add_argument('seconds', type=float)
    c.add_argument('--solver', default='cadical195')
    h = sub.add_parser('chrom')
    h.add_argument('n', type=int)
    h.add_argument('k', type=int)
    h.add_argument('out')
    h.add_argument('seconds', type=float)
    h.add_argument('--mindeg', type=int, default=0)
    h.add_argument('--solver', default='cadical195')
    d = sub.add_parser('indep')
    d.add_argument('n', type=int)
    d.add_argument('alpha', type=int)
    d.add_argument('out')
    d.add_argument('seconds', type=float)
    d.add_argument('--k', type=int, default=0, help='also require chi>=k by colouring CEGAR')
    d.add_argument('--sb', default='face', choices=['face', 'lex', 'none'])
    d.add_argument('--solver', default='cadical195')
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    log = lambda s: print(s, flush=True)
    t0 = time.monotonic()
    if args.mode == 'cover':
        edges = read_edges(args.edges)
        n = max(max(e) for e in edges) + 1
        enc = Cover(n, edges)
        accept = lambda model: None
        meta = {'mode': 'cover', 'input': str(args.edges), 'n': n, 'm': len(edges),
                'input_sha256': hashlib.sha256(Path(args.edges).read_bytes()).hexdigest()}
    elif args.mode == 'indep':
        n, k = args.n, args.k
        enc = Indep(n, args.alpha, sb=args.sb, k=k)

        def accept(model):
            if not k:
                return None
            g = [p for p in enc.pairs if model[enc.Y(*p)]]
            col = colour(n, g, k - 1)
            return None if col is None else [{'colouring': col}]
        meta = {'mode': 'indep', 'n': n, 'alpha': args.alpha, 'k': k, 'sb': args.sb}
    else:
        n, k = args.n, args.k
        enc = Chrom(n, k, mindeg=args.mindeg)

        def accept(model):
            g = [p for p in enc.pairs if model[enc.Y(*p)]]
            col = colour(n, g, k - 1)
            if col is None:
                return None
            return [{'colouring': col}]
        meta = {'mode': 'chrom', 'n': n, 'k': k, 'mindeg': args.mindeg}
    meta['build_seconds'] = round(time.monotonic() - t0, 3)
    verdict, model, it, secs, stats = solve_loop(enc, args.seconds, accept, args.solver, log)
    meta.update(verdict=verdict, iterations=it, seconds=round(secs, 3), stats=stats,
                variables=enc.pool.top, eager_clauses=len(enc.clauses),
                topology_cuts=len(enc.cuts), extra_clauses=len(enc.extra), solver=args.solver)
    if model is not None:
        es, fs = enc.layers(model)
        meta['layers_edges'] = es
        meta['layers_faces'] = fs
        if args.mode == 'cover':
            inp = set(enc.input)
            e0 = sorted(inp & set(es[0]))
            meta['E1'] = e0
            meta['E2'] = sorted(inp - set(e0))
    out.with_suffix('.cuts.json').write_text(json.dumps({'cuts': enc.cuts, 'extra': enc.extra}))
    if verdict == 'UNSAT':
        h, ncl = enc.write_cnf(out.with_suffix('.cnf'))
        meta['cnf_sha256'] = h
        meta['cnf_clauses'] = ncl
    out.with_suffix('.json').write_text(json.dumps(meta))
    print(json.dumps({k2: v for k2, v in meta.items() if k2 not in ('layers_edges', 'layers_faces', 'E1', 'E2')}))


if __name__ == '__main__':
    main()
