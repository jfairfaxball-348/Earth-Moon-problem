#!/usr/bin/env python3
"""Reproduce CAM-0005's finite audit of the pinned SRC-0017 edge-list pool.

Usage: audit_apex_pool.py CORPUS_POOL OUTPUT.json
Vertex labels are the labels present in an edge list, not range(max+1).
No chromatic or criticality statements about the source corpus are assumed.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx
from biplanar_cnf import read_edges


def main(pool, output):
    rows=[]
    for p in sorted(Path(pool).glob('*.edges')):
        if '_layer' in p.stem:
            continue
        e=read_edges(str(p))
        g=nx.Graph(e)
        n,m=len(g),len(e)
        d=5*n-6-m
        thin=sum(not(set(g[u])&set(g[v])) for u,v in g.edges())
        clique=max(nx.find_cliques(g),key=len)
        kind=('EULER' if d<0 else 'CODEGREE' if thin>4*d
              else 'K9' if len(clique)>=8 else 'UNKNOWN')
        rows.append({'file':p.name,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                     'n':n,'m':m,'apex_D':d,'zero_codegree_edges':thin,
                     'base_clique':sorted(clique),'exclusion':kind})
    counts=dict(Counter(r['exclusion'] for r in rows))
    Path(output).write_text(json.dumps({'source_commit':
        '5cb2ca9f7d4d6d195617c09f7348841636b646f6','counts':counts,'graphs':rows},indent=1))
    print(len(rows),counts)


if __name__ == '__main__':
    main(*sys.argv[1:3])
