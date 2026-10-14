"""CAM-0009 completion K5 and input K3,3 necessary full-layer clauses."""
import itertools
import json
import sys
from pathlib import Path
from s007_cover import StrongCover
from biplanar_cnf import read_edges


def obstructions(n, edges):
    original = set(edges)
    for vs in itertools.combinations(range(n), 5):
        yield 'K5', tuple(itertools.combinations(vs, 2))
    adj={v:set() for v in range(n)}
    for u,v in original:adj[u].add(v);adj[v].add(u)
    for a in itertools.combinations(range(n), 3):
        common=set.intersection(*(adj[v] for v in a))-set(a)
        for b in itertools.combinations(sorted(common),3):
            # Canonical part contains the smallest of the six labels.
            if min(a)<min(b):
                cross=tuple(sorted(tuple(sorted((u,v))) for u in a for v in b))
                yield 'K33',cross


class FullCover(StrongCover):
    def __init__(self, edges, lex=False, short_links=False):
        super().__init__(edges, lex, short_links)
        counts = {'K5': 0, 'K33': 0}
        for kind, es in obstructions(self.n, edges):
            counts[kind] += 1
            for layer in range(2):
                self.base.append([-self.E(layer, *e) for e in es])
        self.static.update(s008_version='completion-K5-input-K33-v1', s008_counts=counts)


def main():
    if sys.argv[1] == 'check':
        _, _, ef, prefix = sys.argv
        d = json.loads(Path(prefix+'.cuts.json').read_text())
        c = FullCover(read_edges(ef), d['lex'], d.get('short_links', False))
        assert c.static == d['static']
        c.cuts = d['cuts']
        c.write_cnf(Path(prefix+'.regenerated.cnf'))
        assert Path(prefix+'.cnf').read_bytes() == Path(prefix+'.regenerated.cnf').read_bytes()
        print('PASS S008 cold necessary CNF/cuts regeneration')
    else:
        _, ef, prefix, seconds, *flags = sys.argv
        c = FullCover(read_edges(ef), '--lex' in flags)
        # Save static metadata before solve(), which may block until external cap.
        import time
        c.save(prefix, 'INITIALISED', 0, time.monotonic())
        c.write_cnf(Path(prefix+'.initial.cnf'))
        print(json.dumps(c.static), flush=True)
        print(json.dumps(c.run(prefix, float(seconds))), flush=True)


if __name__ == '__main__':
    main()
