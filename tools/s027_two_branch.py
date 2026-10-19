#!/usr/bin/env python3
"""S027 changed-strength C5 strategy: same S026 two-branch lemma, branch sets <=4.

Identical clause family to tools/s026_two_branch.py (research/S026_TWO_BRANCH_LEMMA.md)
except connected R,S of sizes 2..SIZE (registered SIZE=4). The search is seeded
with the Kuratowski cuts saved in the S026 checkpoint; each seeded cut is
re-verified here as a K5/K3,3 subdivision inside E(G) (cuts are valid for G
whatever other clauses are present) and is re-checked by the independent
certificate checker. Internal SAT learned state is NOT resumed.
Usage: s027_two_branch.py EDGEFILE PREFIX SECONDS SIZE [SEED_CHECKPOINT.json.gz]
       s027_two_branch.py regen EDGEFILE PREFIX OUT.cnf
"""
import gzip
import itertools as it
import json
import os
from pathlib import Path
import sys
import time

import networkx as nx
from pysat.solvers import Solver

sys.path.insert(0, str(Path(__file__).resolve().parent))
from biplanar_cegar import is_kuratowski_subdivision   # noqa: E402
from biplanar_cnf import read_edges                     # noqa: E402
from s025_minor_cegar import MinorCegar                 # noqa: E402


class TwoBranchK(MinorCegar):
    def __init__(self, edges, size):
        super().__init__(edges, rmax=5, cmax=5)
        self.size = size
        self.two_models, self.pvar = [], {}
        for Q0 in nx.enumerate_all_cliques(self.G):
            if len(Q0) != 7:
                continue
            Q = frozenset(Q0)
            sets = sorted((R for R in self.connected_sets(set(self.G) - Q, size)
                           if self.dominates(R, Q)), key=lambda R: (len(R), tuple(sorted(R))))
            for R, S in it.combinations(sets, 2):
                if R & S or not self.joined(R, S):
                    continue
                cr, cs = self.cv(R), self.cv(S)
                for r, s in it.product(sorted(R), sorted(S)):
                    for j in (1, 2):
                        lits = [-cr[j - 1], -cs[j - 1]]
                        lits += [-self.av(q, R, j) for q in sorted(Q - self.adj[r])]
                        lits += [-self.av(q, S, j) for q in sorted(Q - self.adj[s])]
                        if s not in self.adj[r]:
                            key = (R, S, j)
                            if key not in self.pvar:
                                self.nv += 1
                                self.pvar[key] = self.nv
                                for a in sorted(R):
                                    for b in sorted(self.adj[a] & S):
                                        x = self.idx[self.edge(a, b)]
                                        self.minor_clauses.append([-x if j == 1 else x, self.nv])
                            lits.append(-self.pvar[key])
                        self.minor_clauses.append(lits)
                        self.two_models.append([sorted(Q), sorted(R), sorted(S), r, s, j])

    def data(self):
        return {'edges': self.edges, 'lemmas': self.lemmas, 'perms': self.perms,
                'branch_sets': [[sorted(R), list(self.cvar[R]), self.trees[R]] for R in self.cvar],
                'models': self.models, 'cmodels': self.cmodels,
                'adjacency_vars': [[q, sorted(R), j, v] for (q, R, j), v in self.avar.items()],
                'pair_vars': [[sorted(R), sorted(S), j, v] for (R, S, j), v in self.pvar.items()],
                'two_models': self.two_models, 'flags': ['--lemmaC', '5', '--two-branch', str(self.size)]}

    def dump(self, prefix):
        cls = self.clauses()
        Path(str(prefix) + '.cnf').write_text(f'p cnf {self.nv} {len(cls)}\n' + ''.join(
            ' '.join(map(str, cl)) + ' 0\n' for cl in cls), newline='\n')
        Path(str(prefix) + '.lemmas.json').write_text(json.dumps(self.data()))

    def seed(self, checkpoint):
        old = json.load(gzip.open(checkpoint, 'rt'))
        assert [tuple(e) for e in old['data']['edges']] == self.edges, 'seed graph mismatch'
        E = set(self.edges)
        for K in old['data']['lemmas']:
            K = sorted(tuple(e) for e in K)
            key = frozenset(K)
            if key in self.lemma_keys:
                continue
            assert set(K) <= E and is_kuratowski_subdivision(K)
            self.lemma_keys.add(key)
            self.lemmas.append(K)
        return len(self.lemmas)

    def checkpoint(self, prefix, iterations):
        path = Path(str(prefix) + '.checkpoint.json.gz')
        temp = path.with_name(path.name + '.tmp')
        with gzip.open(temp, 'wt', compresslevel=1) as f:
            json.dump({'version': 1, 'iterations': iterations, 'data': self.data()}, f)
        os.replace(temp, path)
        print(json.dumps({'kind': 'checkpoint', 'iterations': iterations,
                          'kuratowski_lemmas': len(self.lemmas)}), flush=True)

    def search(self, seconds, prefix):
        start = time.monotonic()
        last = start
        with Solver(name='cadical195', bootstrap_with=self.clauses()) as solver:
            for iteration in it.count(1):
                if time.monotonic() - start >= seconds:
                    self.checkpoint(prefix, iteration)
                    return 'UNKNOWN', iteration
                solver.conf_budget(10000)
                answer = solver.solve_limited()
                if answer is False:
                    return 'UNSAT', iteration
                if answer is True:
                    model = set(x for x in solver.get_model() if x > 0)
                    left = [e for e in self.edges if self.idx[e] in model]
                    right = [e for e in self.edges if self.idx[e] not in model]
                    if self.lemmas_from(left, solver, 12) + self.lemmas_from(right, solver, 12) == 0:
                        self.split = (left, right)
                        return 'SAT', iteration
                if time.monotonic() - last >= 60:
                    self.checkpoint(prefix, iteration)
                    last = time.monotonic()


def main():
    if sys.argv[1] == 'regen':
        edgefile, prefix, out = sys.argv[2:5]
        d = json.loads(Path(prefix + '.lemmas.json').read_text())
        size = int(d['flags'][d['flags'].index('--two-branch') + 1])
        c = TwoBranchK(read_edges(edgefile), size)
        gen = json.loads(json.dumps(c.data()))
        for k in gen:
            if k != 'lemmas':
                assert gen[k] == d[k], k
        c.lemmas = [[tuple(e) for e in K] for K in d['lemmas']]
        cls = c.clauses()
        Path(out).write_text(f'p cnf {c.nv} {len(cls)}\n' + ''.join(
            ' '.join(map(str, cl)) + ' 0\n' for cl in cls), newline='\n')
        assert Path(out).read_bytes() == Path(prefix + '.cnf').read_bytes()
        print('BYTE_IDENTICAL')
        return
    edgefile, prefix, seconds, size = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
    t = time.monotonic()
    c = TwoBranchK(read_edges(edgefile), size)
    seeded = c.seed(sys.argv[5]) if len(sys.argv) > 5 else 0
    build = time.monotonic() - t
    verdict, iterations = c.search(seconds, prefix)
    if verdict == 'UNSAT':
        c.dump(prefix)
    elif verdict == 'SAT':
        Path(prefix + '.split.json').write_text(json.dumps({'n': c.n, 'E1': c.split[0], 'E2': c.split[1]}))
    result = {'verdict': verdict, 'iterations': iterations, 'build_and_seed_seconds': round(build, 2),
              'seconds': round(time.monotonic() - t, 2), 'two_models': len(c.two_models),
              'branch_size': size, 'seeded_kuratowski_lemmas': seeded,
              'kuratowski_lemmas': len(c.lemmas), 'lemmaC_models': len(c.cmodels)}
    Path(prefix + '.result.json').write_text(json.dumps(result, indent=1))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
