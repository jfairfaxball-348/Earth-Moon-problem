#!/usr/bin/env python3
"""S026 two-branch one-layer K9-minor CEGAR; see the hand proof dossier."""
import itertools as it
import json
from pathlib import Path
import sys
import time

import networkx as nx
from biplanar_cnf import read_edges
from s025_minor_cegar import MinorCegar


class TwoBranch(MinorCegar):
    def __init__(self, edges):
        super().__init__(edges, rmax=5, cmax=5)
        self.two_models, self.pvar = [], {}
        for Q0 in nx.enumerate_all_cliques(self.G):
            if len(Q0) != 7:
                continue
            Q = frozenset(Q0)
            sets = sorted((R for R in self.connected_sets(set(self.G)-Q, 3)
                           if self.dominates(R, Q)), key=lambda R: tuple(sorted(R)))
            for R, S in it.combinations(sets, 2):
                if R & S or not self.joined(R, S):
                    continue
                cr, cs = self.cv(R), self.cv(S)
                for r, s in it.product(sorted(R), sorted(S)):
                    for j in (1, 2):
                        lits = [-cr[j-1], -cs[j-1]]
                        lits += [-self.av(q, R, j) for q in sorted(Q-self.adj[r])]
                        lits += [-self.av(q, S, j) for q in sorted(Q-self.adj[s])]
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
                'two_models': self.two_models, 'flags': ['--lemmaC', '5', '--two-branch', '3']}

    def dump(self, prefix):
        cls = self.clauses()
        Path(str(prefix)+'.cnf').write_text(f'p cnf {self.nv} {len(cls)}\n'+''.join(
            ' '.join(map(str, cl))+' 0\n' for cl in cls))
        Path(str(prefix)+'.lemmas.json').write_text(json.dumps(self.data()))


def main():
    edges, prefix, seconds = read_edges(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    t = time.monotonic()
    c = TwoBranch(edges)
    build = time.monotonic()-t
    verdict, iterations = c.run(seconds)
    if verdict == 'UNSAT':
        c.dump(prefix)
    elif verdict == 'SAT':
        Path(prefix+'.split.json').write_text(json.dumps({'n': c.n, 'E1': c.split[0], 'E2': c.split[1]}))
    result = {'verdict': verdict, 'iterations': iterations, 'build_seconds': build,
              'seconds': time.monotonic()-t, 'two_models': len(c.two_models),
              'kuratowski_lemmas': len(c.lemmas), 'lemmaC_models': len(c.cmodels)}
    Path(prefix+'.result.json').write_text(json.dumps(result, indent=1))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
