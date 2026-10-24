"""Independent local replay of the S042 resolved-domain leaf graphs (exact isomorphism mapping).

Separately written from tools/s042_census.py: DHGO compositions (with the registered
Aut(K_k) reduction), joins, deletions and omega computed directly on each leaf graph;
no Weisfeiler-Lehman deduplication. Every raw leaf graph must be isomorphic (VF2) to a
recorded leaf graph, and every recorded leaf graph from a resolved type must arise.
"""
import itertools as it
import json
from pathlib import Path
import sys
import time

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from s042_types_stdlib import table


def compose(g1, g2):
    """Delete an edge of g1, split a vertex of g2; complete operands reduced by symmetry."""
    def full(g):
        n = g.number_of_nodes()
        return g.number_of_edges() == n*(n-1)//2
    n1 = g1.number_of_nodes()
    shift = {v: n1+i for i, v in enumerate(sorted(g2))}
    for x, y in (sorted(g1.edges())[:1] if full(g1) else sorted(g1.edges())):
        for z in (sorted(g2)[:1] if full(g2) else sorted(g2)):
            nb = sorted(g2[z])
            subsets = [nb[:s] for s in range(1, len(nb))] if full(g2) else \
                [list(c) for r in range(1, len(nb)) for c in it.combinations(nb, r)]
            for left in subsets:
                h = nx.Graph()
                h.add_nodes_from(range(n1)); h.add_nodes_from(shift[v] for v in g2 if v != z)
                h.add_edges_from(e for e in g1.edges() if {x, y} != set(e))
                h.add_edges_from((shift[a], shift[b]) for a, b in g2.edges() if z not in (a, b))
                h.add_edges_from((x, shift[w]) for w in left)
                h.add_edges_from((y, shift[w]) for w in nb if w not in left)
                yield nx.convert_node_labels_to_integers(h)


FILTER = nx.could_be_isomorphic if '--strong-filter' in sys.argv else nx.faster_could_be_isomorphic


def ore(k, n):
    if n == k:
        return [nx.complete_graph(k)]
    raw = []
    for n1 in range(k, n, k-1):
        for g1 in ore(k, n1):
            for g2 in ore(k, n+1-n1):
                raw.extend(compose(g1, g2))
    reps = []
    for g in raw:
        if not any(FILTER(g, r) and nx.is_isomorphic(g, r) for r in reps):
            reps.append(g)
    return reps


def factor(k, n, status):
    if status == 'ODD_CYCLE':
        return [nx.cycle_graph(n)]
    if status == 'ORE_ONLY' or status.startswith('UNRESOLVED'):
        return [g for g in ore(k, n) if nx.is_connected(nx.complement(g))] if (n-1) % (k-1) == 0 else []
    return []


def main():
    start = time.process_time()
    rec = json.loads((ROOT/'validation/S042/LEAF_GRAPHS.json').read_text())
    recorded = [nx.Graph([tuple(e) for e in g['edges']]) for g in rec['leaf_graphs']]
    hit = [False]*len(recorded)
    raw_count = 0
    for a, c, fs, n, slack, status in table():
        if any(s == 'ATLAS_COMPLETE' for s in status):
            raise AssertionError('atlas factor type present; extend replay')
        for parts in it.product(*[factor(k, x, s) for (k, x), s in zip(fs, status)]):
            L = nx.complete_graph(c)
            for p in parts:
                base = L.number_of_nodes()
                p = nx.relabel_nodes(p, {v: base+i for i, v in enumerate(sorted(p))})
                L.add_edges_from((u, v) for u in list(L.nodes()) for v in p.nodes())
                L.add_edges_from(p.edges())
            nL = L.number_of_nodes()
            for e in list(L.edges()):
                lam = L.copy(); lam.remove_edge(*e)
                apex = list(range(nL, nL+a))
                lam.add_edges_from(it.combinations(apex, 2))
                lam.add_edges_from((p, v) for p in apex for v in range(nL))
                if lam.number_of_edges() > 6*lam.number_of_nodes()-12:
                    continue
                if max(len(q) for q in nx.find_cliques(lam)) > 8:
                    continue
                raw_count += 1
                match = [i for i, r in enumerate(recorded) if FILTER(lam, r) and nx.is_isomorphic(lam, r)]
                assert len(match) == 1, (a, c, fs, e)
                hit[match[0]] = True
    assert all(hit), [i for i, h in enumerate(hit) if not h]
    out = dict(status='PASS', raw_leaf_graphs=raw_count, recorded_leaf_graphs=len(recorded), all_recorded_hit=True,
               prefilter=FILTER.__name__, cpu_seconds=time.process_time()-start)
    target = 'LEAF_REPLAY_STRONG.json' if '--strong-filter' in sys.argv else 'LEAF_REPLAY.json'
    (ROOT/'validation/S042'/target).write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print(out)


if __name__ == '__main__':
    main()
