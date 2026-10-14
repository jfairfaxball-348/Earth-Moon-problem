#!/usr/bin/env python3
"""CAM-0005 constructive heuristic; only exact checked splits are positive."""
import json
import math
import random
import sys
import time
from pathlib import Path

import networkx as nx
from biplanar_cnf import read_edges
from check_layers import certify_layer


def search(edges, prefix, seconds, seed=4004):
    rng = random.Random(seed)
    n = max(max(e) for e in edges)+1
    all_edges = set(edges)
    best = len(edges)
    moves = 0
    start = time.monotonic()
    while time.monotonic()-start < seconds:
        layers = [nx.empty_graph(n),nx.empty_graph(n)]
        order = list(edges)
        rng.shuffle(order)
        omitted = set()
        for e in order:
            options = [0,1]
            rng.shuffle(options)
            for i in options:
                layers[i].add_edge(*e)
                if nx.check_planarity(layers[i])[0]:
                    break
                layers[i].remove_edge(*e)
            else:
                omitted.add(e)
        for local in range(150):
            if time.monotonic()-start >= seconds:
                break
            best = min(best,len(omitted))
            if not omitted:
                e1 = sorted(tuple(sorted(e)) for e in layers[0].edges())
                e2 = sorted(tuple(sorted(e)) for e in layers[1].edges())
                assert not set(e1)&set(e2) and set(e1)|set(e2) == all_edges
                certify_layer(n,e1)
                certify_layer(n,e2)
                Path(prefix+'.split.json').write_text(json.dumps({'n':n,'E1':e1,'E2':e2}))
                return {'verdict':'SAT_CHECKED','best_omitted':0,'moves':moves,
                        'seconds':time.monotonic()-start,'seed':seed}
            edge = rng.choice(sorted(omitted))
            layer = rng.randrange(2)
            trial = layers[layer].copy()
            trial.add_edge(*edge)
            removed=[]
            while True:
                planar,cert = nx.check_planarity(trial,counterexample=True)
                if planar:
                    break
                choices = [tuple(sorted(e)) for e in cert.edges() if tuple(sorted(e)) != edge]
                drop = rng.choice(choices)
                trial.remove_edge(*drop)
                removed.append(drop)
            new = (omitted-{edge})|set(removed)
            temperature = max(.15, 1.0-local/150)
            if len(new) <= len(omitted) or rng.random() < math.exp((len(omitted)-len(new))/temperature):
                layers[layer] = trial
                omitted = new
            moves += 1
    return {'verdict':'UNKNOWN','best_omitted':best,'moves':moves,
            'seconds':time.monotonic()-start,'seed':seed}


def main():
    if sys.argv[1] == 'C5':
        tags = json.loads(Path('validation/S004/C5_frontier.json').read_text())['run_order']
        rows=[]
        for tag in tags:
            prefix = 'validation/S004/search/packing-'+tag
            edges=read_edges('validation/S004/targets/'+tag+'.edges')
            result=search(edges,prefix,30)
            rows.append({'tag':tag,**result})
            Path('validation/S004/C5_packing_results.json').write_text(json.dumps(rows,indent=1))
            print(tag,result,flush=True)
    else:
        _,edgefile,prefix,seconds=sys.argv
        print(json.dumps(search(read_edges(edgefile),prefix,float(seconds))))


if __name__ == '__main__':
    main()
