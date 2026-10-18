#!/usr/bin/env python3
"""S026 two-branch one-layer K9-minor CEGAR; see the hand proof dossier."""
import itertools as it
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import networkx as nx
from pysat.solvers import Solver
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

    def checkpoint(self,prefix,iterations):
        path=Path(str(prefix)+'.checkpoint.json.gz')
        temp=path.with_name(path.name+'.tmp')
        with gzip.open(temp,'wt',compresslevel=1) as f:
            json.dump({'version':1,'iterations':iterations,'data':self.data()},f)
        os.replace(temp,path)
        print(json.dumps({'kind':'checkpoint','iterations':iterations,
                          'kuratowski_lemmas':len(self.lemmas),'path':str(path)}),flush=True)

    def run_resumable(self,seconds,prefix):
        ck=Path(str(prefix)+'.checkpoint.json.gz')
        resumed=0
        if ck.exists():
            old=json.load(gzip.open(ck,'rt'))
            current=json.loads(json.dumps(self.data()))
            assert all(current[k]==old['data'][k] for k in current if k!='lemmas'), 'checkpoint source/input mismatch'
            self.lemmas=[[tuple(e) for e in K] for K in old['data']['lemmas']]
            self.lemma_keys={frozenset(K) for K in self.lemmas}
            resumed=len(self.lemmas)
        start=time.monotonic(); last=start
        with Solver(name='cadical195',bootstrap_with=self.clauses()) as solver:
            for iteration in it.count(1):
                if time.monotonic()-start>=seconds:
                    self.checkpoint(prefix,iteration)
                    return 'UNKNOWN',iteration,resumed
                solver.conf_budget(10000)
                answer=solver.solve_limited()
                if answer is False:
                    return 'UNSAT',iteration,resumed
                if answer is True:
                    model=set(x for x in solver.get_model() if x>0)
                    left=[e for e in self.edges if self.idx[e] in model]
                    right=[e for e in self.edges if self.idx[e] not in model]
                    added=self.lemmas_from(left,solver,12)+self.lemmas_from(right,solver,12)
                    if added==0:
                        self.split=(left,right)
                        return 'SAT',iteration,resumed
                if time.monotonic()-last>=60:
                    self.checkpoint(prefix,iteration); last=time.monotonic()


def main():
    edges, prefix, seconds = read_edges(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    t = time.monotonic()
    c = TwoBranch(edges)
    build = time.monotonic()-t
    verdict, iterations, resumed = c.run_resumable(seconds,prefix)
    if verdict == 'UNSAT':
        c.dump(prefix)
    elif verdict == 'SAT':
        Path(prefix+'.split.json').write_text(json.dumps({'n': c.n, 'E1': c.split[0], 'E2': c.split[1]}))
    result = {'verdict': verdict, 'iterations': iterations, 'build_seconds': build,
              'seconds': time.monotonic()-t, 'two_models': len(c.two_models),
              'kuratowski_lemmas': len(c.lemmas), 'lemmaC_models': len(c.cmodels),
              'resumed_kuratowski_lemmas':resumed}
    Path(prefix+'.result.json').write_text(json.dumps(result, indent=1))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
