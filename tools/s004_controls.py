#!/usr/bin/env python3
"""Preregistered positive controls and malformed-cut rejection for CAM-0005."""
import itertools
import json
import random
import time
from pathlib import Path

from biplanar_cnf import read_edges
from triangulation_cover import Cover


def main():
    rng = random.Random(4004)
    rows = []
    root = Path('artifacts/tmp/S004/controls')
    root.mkdir(parents=True,exist_ok=True)
    start = time.monotonic()
    for idx in range(100):
        n = rng.randrange(4,9)
        probability = rng.random()
        # Include a spanning cycle, then a seeded subset of all pairs.
        edges = {tuple(sorted((v,(v+1)%n))) for v in range(n)}
        edges.update(e for e in itertools.combinations(range(n),2) if rng.random() < probability)
        c = Cover(sorted(edges),lex=True,short_links=idx%10 == 0)
        result = c.run(str(root/f'{idx:03d}'),5)
        assert result['verdict'] == 'SAT_CHECKED', (idx,result)
        rows.append({'index':idx,'n':n,'m':len(edges),'short_links':c.short_links,
                     'verdict':result['verdict']})
    for name in ('sulanke','K9e'):
        edges = read_edges(f'validation/S003/splits/{name}.edges')
        c = Cover(edges,lex=True,short_links=True)
        result = c.run(str(root/name),60)
        assert result['verdict'] == 'SAT_CHECKED', (name,result)
        rows.append({'name':name,**result})
    c = Cover(read_edges('validation/S003/splits/K8.edges'))
    malformed = [
        {'kind':'connected','layer':0,'X':[]},
        {'kind':'connected','layer':0,'X':list(range(8))},
        {'kind':'link','layer':0,'v':0,'cycle':[1,2,2],'w':3},
        {'kind':'link','layer':0,'v':0,'cycle':[1,2,3],'w':2},
        {'kind':'link','layer':0,'v':0,'cycle':[0,2,3],'w':4},
        {'kind':'link','layer':0,'v':0,'cycle':[1,2,3],'w':0},
        {'kind':'link','layer':0,'v':0,'cycle':[1,2,8],'w':4},
    ]
    for cut in malformed:
        try:
            c.cut_clause(cut)
        except AssertionError:
            continue
        raise AssertionError(('malformed cut accepted',cut))
    Path('validation/S004/cover_controls.json').write_text(json.dumps({
        'seed':4004,'positive_controls':rows,'malformed_rejected':len(malformed),
        'seconds':time.monotonic()-start},indent=1))
    print('PASS 100 seeded subgraphs of K8, Sulanke, K9-e; 7 malformed cuts rejected')


if __name__ == '__main__':
    main()
