#!/usr/bin/env python3
"""CAM-0003: purely propositional biplanarity encoding (Schnyder orders).

A graph is planar iff it admits three linear orders of its vertices such
that for every edge uv and every vertex w outside uv some order puts w
above both u and v (Schnyder 1989).  The CNF below asks for a partition of
E into layers 1/2 and three such orders per layer, so it is satisfiable iff
the graph is biplanar.  Only symmetry breaking: the first edge is put in
layer 1 (layer swap).  With --layers 1 it encodes plain planarity (used for
cross-validation).

Optional implied constraints (registered CAM-0003 amendment):
  --euler   each layer has at most 3n-6 edges (Euler; sequential counter)
  --symtop  inside each layer the three orders are sorted by the index of
            their top element (sound: permuting suitable orders keeps them
            suitable).
  --twinsort  closed twins (equal closed neighbourhoods) appear in label
            order inside order 1 of layer 1.  Any permutation of a closed-twin
            class is an automorphism, so every solution can be mapped to one
            with this property.  Used ALONE: it disables the first-edge
            layer fix and --symtop, whose group actions would interact.

Usage:
  biplanar_cnf.py encode EDGEFILE OUT.cnf [--layers 1|2] [--euler]
                         [--symtop | --twinsort]
  biplanar_cnf.py decode EDGEFILE MODELFILE OUT.json
EDGEFILE: one "u v" pair per line, or a JSON file with key "edges".
"""
import itertools
import json
import sys


def read_edges(path):
    text = open(path).read()
    if path.endswith(".json"):
        data = json.loads(text)
        edges = data["edges"] if "edges" in data else data["E1"] + data["E2"]
    else:
        edges = [tuple(map(int, line.split()[:2])) for line in text.splitlines()
                 if line.strip() and not line.startswith("#")]
    norm = sorted({(min(u, v), max(u, v)) for u, v in edges})
    assert all(u != v for u, v in norm), "loop"
    assert len(norm) == len(edges), "duplicate edge in input"
    return norm


class Encoder:
    def __init__(self, edges, layers=2):
        self.edges = edges
        self.n = 1 + max(max(e) for e in edges)
        self.layers = layers
        self.nv = 0
        self.clauses = []
        self.x = {}
        if layers == 2:
            for e in edges:
                self.x[e] = self.new()
        self.p = {}
        for L in range(layers):
            for i in range(3):
                for a, b in itertools.combinations(range(self.n), 2):
                    self.p[L, i, a, b] = self.new()

    def new(self):
        self.nv += 1
        return self.nv

    def below(self, L, i, a, b):
        """Literal for 'a strictly below b' in order (L,i)."""
        return self.p[L, i, a, b] if a < b else -self.p[L, i, b, a]

    def in_layer(self, e, L):
        if self.layers == 1:
            return None
        return self.x[e] if L == 0 else -self.x[e]

    def add_symtop(self):
        n = self.n
        for L in range(self.layers):
            top = {}
            for i in range(3):
                for v in range(n):
                    t = top[i, v] = self.new()
                    for u in range(n):
                        if u != v:
                            self.clauses.append([-t, self.below(L, i, u, v)])
                self.clauses.append([top[i, v] for v in range(n)])
            for i in range(2):
                for v in range(n):
                    for u in range(v):
                        self.clauses.append([-top[i, v], -top[i + 1, u]])

    def add_euler(self):
        from pysat.card import CardEnc, EncType
        from pysat.formula import IDPool
        cap = 3 * self.n - 6
        for sign in (1, -1):
            lits = [sign * self.x[e] for e in self.edges]
            if len(lits) <= cap:
                continue
            pool = IDPool(start_from=self.nv + 1)
            enc = CardEnc.atmost(lits, bound=cap, vpool=pool, encoding=EncType.seqcounter)
            self.clauses.extend(enc.clauses)
            self.nv = max(self.nv, pool.top)

    def add_twinsort(self):
        closed = {}
        for v in range(self.n):
            closed.setdefault(frozenset(self.adj[v] | {v}), []).append(v)
        for cls in closed.values():
            for u, v in zip(cls, cls[1:]):
                self.clauses.append([self.below(0, 0, u, v)])

    def build(self, euler=False, symtop=False, twinsort=False):
        n = self.n
        self.adj = {v: set() for v in range(n)}
        for u, v in self.edges:
            self.adj[u].add(v)
            self.adj[v].add(u)
        for L in range(self.layers):
            for i in range(3):
                for a, b, c in itertools.permutations(range(n), 3):
                    self.clauses.append([-self.below(L, i, a, b),
                                         -self.below(L, i, b, c),
                                         self.below(L, i, a, c)])
        for e in self.edges:
            u, v = e
            for L in range(self.layers):
                lit = self.in_layer(e, L)
                for w in range(n):
                    if w in e:
                        continue
                    clause = [] if lit is None else [-lit]
                    for i in range(3):
                        a = self.new()
                        self.clauses.append([-a, self.below(L, i, u, w)])
                        self.clauses.append([-a, self.below(L, i, v, w)])
                        clause.append(a)
                    self.clauses.append(clause)
        if self.layers == 2:
            if not twinsort:
                self.clauses.append([self.x[self.edges[0]]])
            if euler:
                self.add_euler()
        if twinsort:
            assert not symtop, "--twinsort must be used alone"
            self.add_twinsort()
        elif symtop:
            self.add_symtop()
        return self

    def dimacs(self):
        out = [f"p cnf {self.nv} {len(self.clauses)}"]
        out += [" ".join(map(str, c)) + " 0" for c in self.clauses]
        return "\n".join(out) + "\n"


def parse_model(path):
    vals = set()
    for line in open(path):
        if line.startswith("v "):
            vals.update(int(t) for t in line.split()[1:] if t != "0")
    return vals


def main(argv):
    if argv[1] == "encode":
        layers = int(argv[argv.index("--layers") + 1]) if "--layers" in argv else 2
        enc = Encoder(read_edges(argv[2]), layers).build(
            euler="--euler" in argv, symtop="--symtop" in argv,
            twinsort="--twinsort" in argv)
        open(argv[3], "w").write(enc.dimacs())
        print(f"n={enc.n} m={len(enc.edges)} vars={enc.nv} clauses={len(enc.clauses)}")
    elif argv[1] == "decode":
        enc = Encoder(read_edges(argv[2]), 2)
        model = parse_model(argv[3])
        e1 = [list(e) for e in enc.edges if enc.x[e] in model]
        e2 = [list(e) for e in enc.edges if enc.x[e] not in model]
        json.dump({"n": enc.n, "E1": e1, "E2": e2}, open(argv[4], "w"))
        print(f"layers {len(e1)}/{len(e2)}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
