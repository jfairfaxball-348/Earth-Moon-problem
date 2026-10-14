#!/usr/bin/env python3
"""CAM-0008 necessary planar-subset/K5 cuts for arbitrary-deficit Cover."""
import itertools
import json
import sys
from pathlib import Path
from pysat.card import CardEnc, EncType
from triangulation_cover import Cover
from biplanar_cnf import read_edges

VERSION = 'S007-subsets-K5-Dle2-v1'


class StrongCover(Cover):
    def __init__(self, edges, lex=False, short_links=False):
        super().__init__(edges, lex, short_links)
        adj = {v: {v} for v in range(self.n)}
        for a, b in edges:
            adj[a].add(b); adj[b].add(a)
        groups = {}
        for v in range(self.n):
            groups.setdefault(tuple(sorted(adj[v])), []).append(v)
        self.groups = list(groups.values())
        # The campaign restricts expensive complete bag-union generation to <=11 bags.
        assert len(self.groups) <= 11
        subsets = {tuple(v for j, bag in enumerate(self.groups) if mask >> j & 1 for v in bag)
                   for mask in range(1, 1 << len(self.groups))}
        subsets |= {tuple(v for v in range(self.n) if v != omitted) for omitted in range(self.n)}
        subsets = sorted({tuple(sorted(s)) for s in subsets if 3 <= len(s) < self.n})
        initial = len(self.base)
        for s in subsets:
            bound = 3 * len(s) - 6
            if len(s) * (len(s)-1)//2 <= bound:
                continue
            for layer in range(2):
                self.base.extend(CardEnc.atmost([self.E(layer, a, b) for a, b in itertools.combinations(s, 2)],
                    bound=bound, vpool=self.pool, encoding=EncType.seqcounter).clauses)
        original = set(edges)
        k5 = 0
        for vs in itertools.combinations(range(self.n), 5):
            es = list(itertools.combinations(vs, 2))
            if all(e in original for e in es):
                k5 += 1
                for layer in range(2):
                    self.base.append([-self.E(layer, *e) for e in es])
        deficit = 6*self.n - 12 - len(edges)
        if deficit <= 2:
            self.base.extend([[-self.F(0, *q), -self.F(1, *q)] for q in self.triples])
        self.static = dict(version=VERSION, groups=self.groups, subset_count=len(subsets),
            input_K5_count=k5, distinct_faces_enabled=deficit <= 2,
            extra_clauses=len(self.base)-initial)

    def save(self, prefix, verdict, iterations, start):
        meta = super().save(prefix, verdict, iterations, start)
        meta['static'] = self.static
        Path(prefix+'.result.json').write_text(json.dumps(meta, indent=1)+'\n', newline='\n')
        Path(prefix+'.cuts.json').write_text(json.dumps(dict(lex=self.lex,
            short_links=self.short_links, cuts=self.cuts, static=self.static), indent=1)+'\n', newline='\n')
        return meta


def main():
    if sys.argv[1] == 'check':
        _, _, ef, prefix = sys.argv
        d = json.loads(Path(prefix+'.cuts.json').read_text())
        c = StrongCover(read_edges(ef), d['lex'], d.get('short_links', False))
        assert c.static == d['static']
        c.cuts = d['cuts']
        c.write_cnf(Path(prefix+'.regenerated.cnf'))
        assert Path(prefix+'.cnf').read_bytes() == Path(prefix+'.regenerated.cnf').read_bytes()
        print('PASS stronger necessary CNF cold regeneration', len(c.cuts), 'lazy cuts')
    else:
        _, ef, prefix, seconds, *flags = sys.argv
        print(json.dumps(StrongCover(read_edges(ef), '--lex' in flags).run(prefix, float(seconds))))


if __name__ == '__main__':
    main()
