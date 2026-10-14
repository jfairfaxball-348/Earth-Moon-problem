#!/usr/bin/env python3
"""CAM-0005: necessary sphere-triangulation cover CNF, inspired by SRC-0009.

Unlike the source exact-union test, completion edges outside the input are
allowed. A SAT relaxation is never declared biplanar without LR and rotation
checks. Every lazy cut has a small syntactic certificate. Usage:
  triangulation_cover.py EDGEFILE PREFIX SECONDS [--lex]
  triangulation_cover.py check EDGEFILE PREFIX
External process wall caps are also required, since solve() can overrun.
"""
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

from biplanar_cegar import Cegar
from biplanar_cnf import read_edges
from check_layers import certify_layer


class Cover:
    def __init__(self, edges, lex=False, short_links=False):
        self.input = list(edges)
        self.n = max(max(e) for e in edges) + 1
        assert self.n >= 4 and len(set(edges)) == len(edges)
        self.pairs = list(itertools.combinations(range(self.n), 2))
        self.triples = list(itertools.combinations(range(self.n), 3))
        pool = self.pool = IDPool()
        self.e = {(i, a, b): pool.id(('e', i, a, b))
                  for i in range(2) for a, b in self.pairs}
        self.f = {(i, a, b, c): pool.id(('f', i, a, b, c))
                  for i in range(2) for a, b, c in self.triples}
        self.base = []
        self.cuts = []
        self.lex = lex
        self.short_links = short_links

        def card(lits, bound, kind, gate=None):
            enc = getattr(CardEnc, kind)(lits=lits, bound=bound,
                                        vpool=pool, encoding=EncType.seqcounter)
            self.base.extend(([-gate] if gate is not None else []) + cl
                             for cl in enc.clauses)

        for i in range(2):
            for a, b, c in self.triples:
                fv = self.F(i, a, b, c)
                self.base.extend([[-fv, self.E(i, u, v)]
                                  for u, v in ((a, b), (a, c), (b, c))])
            for a, b in self.pairs:
                ev = self.E(i, a, b)
                fs = [self.F(i, a, b, c) for c in range(self.n) if c not in (a, b)]
                card(fs, 2, 'atmost')
                card(fs, 2, 'atleast', gate=ev)
            card([self.E(i, a, b) for a, b in self.pairs], 3*self.n-6, 'equals')
            for v in range(self.n):
                card([self.E(i, v, u) for u in range(self.n) if u != v], 3, 'atleast')
        for a, b in edges:
            self.base.append([self.E(0, a, b), self.E(1, a, b)])

        if short_links:
            for i in range(2):
                for v in range(self.n):
                    others = [a for a in range(self.n) if a != v]
                    for cycle in itertools.combinations(others, 3):
                        for w in others:
                            if w not in cycle:
                                self.base.append(self.cut_clause({'kind':'link','layer':i,
                                    'v':v,'cycle':list(cycle),'w':w}))

        # Count the exact excess above one occurrence of each input edge.
        excess = []
        original = set(edges)
        for a, b in self.pairs:
            x, y = self.E(0, a, b), self.E(1, a, b)
            if (a, b) in original:
                z = pool.id(('double', a, b))
                self.base.extend([[-z, x], [-z, y], [-x, -y, z]])
                excess.append(z)
            else:
                excess.extend((x, y))
        deficit = 6*self.n-12-len(edges)
        if deficit < 0:
            self.base.append([])
        else:
            card(excess, deficit, 'equals')

        # One common total order: all layer-0 pairs, then layer-1 pairs.
        primary = [self.E(i, a, b) for i in range(2) for a, b in self.pairs]
        self.add_lex(primary, primary[len(self.pairs):]+primary[:len(self.pairs)])
        if lex:
            permutations = Cegar(edges).perms
            for p in permutations:
                target = [self.E(i, p[a], p[b]) for i in range(2) for a, b in self.pairs]
                self.add_lex(primary, target)

    def E(self, i, a, b):
        a, b = sorted((a, b))
        return self.e[i, a, b]

    def F(self, i, a, b, c):
        a, b, c = sorted((a, b, c))
        return self.f[i, a, b, c]

    def add_lex(self, xs, ys):
        prefix = None
        for x, y in zip(xs, ys):
            if x == y:
                continue
            pre = [] if prefix is None else [-prefix]
            self.base.append(pre+[-x, y])
            nxt = self.pool.id()
            self.base.extend((pre+[x, y, nxt], pre+[-x, -y, nxt]))
            prefix = nxt

    def cut_clause(self, cut):
        i = cut['layer']
        assert i in (0, 1)
        if cut['kind'] == 'connected':
            X = cut['X']
            assert len(X) == len(set(X)) and 0 < len(X) < self.n
            assert all(0 <= v < self.n for v in X)
            S = set(X)
            return [self.E(i, a, b) for a, b in self.pairs if (a in S) != (b in S)]
        assert cut['kind'] == 'link'
        v, cycle, w = cut['v'], cut['cycle'], cut['w']
        assert 0 <= v < self.n and 0 <= w < self.n
        assert len(cycle) >= 3 and len(set(cycle)) == len(cycle)
        assert all(0 <= a < self.n for a in cycle)
        assert v not in cycle and w not in cycle and w != v
        return [-self.F(i, v, a, b) for a, b in zip(cycle, cycle[1:]+cycle[:1])] + [-self.E(i, v, w)]

    def save(self, prefix, verdict, iterations, start):
        p = Path(prefix)
        meta = {'verdict': verdict, 'iterations': iterations,
                'seconds': time.monotonic()-start, 'cuts': len(self.cuts),
                'variables': self.pool.top, 'clauses': len(self.base)+len(self.cuts)}
        p.with_suffix('.result.json').write_text(json.dumps(meta, indent=2))
        p.with_suffix('.cuts.json').write_text(json.dumps({'lex': self.lex,
            'short_links':self.short_links,'cuts': self.cuts}))
        if verdict == 'UNSAT':
            self.write_cnf(p.with_suffix('.cnf'))
        return meta

    def write_cnf(self, p):
        cls = self.base + [self.cut_clause(c) for c in self.cuts]
        p.write_text(f'p cnf {self.pool.top} {len(cls)}\n' +
                     ''.join(' '.join(map(str, c))+' 0\n' for c in cls), newline='\n')

    def run(self, prefix, seconds):
        start = time.monotonic()
        it = 0
        with Cadical153(bootstrap_with=self.base) as solver:
            while time.monotonic()-start < seconds:
                it += 1
                if not solver.solve():
                    return self.save(prefix, 'UNSAT', it, start)
                model = set(v for v in solver.get_model() if v > 0)
                added = []
                layers = []
                for i in range(2):
                    le = [(a, b) for a, b in self.pairs if self.E(i, a, b) in model]
                    layers.append(le)
                    graph = nx.Graph()
                    graph.add_nodes_from(range(self.n))
                    graph.add_edges_from(le)
                    for component in nx.connected_components(graph):
                        if len(component) < self.n:
                            added.append({'kind': 'connected', 'layer': i, 'X': sorted(component)})
                    faces = [q for q in self.triples if self.F(i, *q) in model]
                    for v in range(self.n):
                        link = nx.Graph()
                        link.add_nodes_from(graph[v])
                        link.add_edges_from([tuple(a for a in q if a != v) for q in faces if v in q])
                        assert all(d == 2 for _, d in link.degree())
                        components = list(nx.connected_components(link))
                        if len(components) > 1:
                            for component in components:
                                cycle = [min(component)]
                                prev = None
                                while True:
                                    nxt = min(a for a in link[cycle[-1]] if a != prev)
                                    if nxt == cycle[0]:
                                        break
                                    prev = cycle[-1]
                                    cycle.append(nxt)
                                for w in sorted(set(link)-component):
                                    added.append({'kind': 'link', 'layer': i, 'v': v,
                                                  'cycle': cycle, 'w': w})
                if not added:
                    # The relaxation is accepted only after actual planarity checks.
                    for le in layers:
                        certify_layer(self.n, le)
                    original = set(self.input)
                    e1 = sorted(original & set(layers[0]))
                    e2 = sorted(original-set(e1))
                    Path(prefix+'.split.json').write_text(json.dumps({'n': self.n, 'E1': e1, 'E2': e2}))
                    return self.save(prefix, 'SAT_CHECKED', it, start)
                for cut in added:
                    clause = self.cut_clause(cut)
                    assert all(-v in model if v < 0 else v not in model for v in clause)
                    solver.add_clause(clause)
                self.cuts.extend(added)
                self.save(prefix, 'RUNNING', it, start)
        return self.save(prefix, 'UNKNOWN', it, start)


def main():
    if sys.argv[1] == 'check':
        _, _, edgefile, prefix = sys.argv
        data = json.loads(Path(prefix+'.cuts.json').read_text())
        c = Cover(read_edges(edgefile), data['lex'], data.get('short_links',False))
        c.cuts = data['cuts']
        c.write_cnf(Path(prefix+'.regenerated.cnf'))
        assert Path(prefix+'.cnf').read_bytes() == Path(prefix+'.regenerated.cnf').read_bytes()
        print('cover certificate structure PASS', len(c.cuts), 'cuts')
    else:
        _, edgefile, prefix, seconds, *flags = sys.argv
        print(json.dumps(Cover(read_edges(edgefile), '--lex' in flags,
                               '--short-links' in flags).run(prefix, float(seconds))))


if __name__ == '__main__':
    main()
