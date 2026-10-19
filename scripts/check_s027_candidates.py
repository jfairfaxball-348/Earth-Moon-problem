"""Independent S027 recheck of admitted and surplus filter-clean graphs.

From each recorded (graph6, w) it rebuilds the 28-vertex clique blow-up without
the programme's blowup helper, compares the stored edge file (admitted graphs),
and brute-forces: no independent 4-set among the 28 vertices (alpha<=3, so
chi>=ceil(28/3)=10 by counting), no 9-clique, and at most 156 edges.
Usage: python scripts/check_s027_candidates.py SOURCE_DIR OUT.json
"""
import itertools as it
import json
from pathlib import Path
import sys

import networkx as nx


def build(g6, w):
    A = nx.from_graph6_bytes(g6.encode())
    bag = [b for b, x in enumerate(w) for _ in range(x)]
    n = len(bag)
    E = sorted((p, q) for p, q in it.combinations(range(n), 2)
               if bag[p] == bag[q] or A.has_edge(bag[p], bag[q]))
    return n, E


def check(g6, w):
    n, E = build(g6, w)
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(E)
    alpha_le3 = not any(all(not G.has_edge(a, b) for a, b in it.combinations(S, 2))
                        for S in it.combinations(range(n), 4))
    omega = max(len(c) for c in nx.find_cliques(G))
    return n, E, {'n': n, 'm': len(E), 'alpha_le_3': alpha_le3, 'omega': omega,
                  'chi_lower_by_counting': -(-n // 3) if alpha_le3 else None}


def main(src, out):
    src = Path(src)
    s = json.loads((src / 'SUMMARY.json').read_text())
    rows = []
    for kind, recs in (('ADMITTED', s['admitted']), ('SURPLUS', s['surplus_filter_clean'])):
        for r in recs:
            n, E, res = check(r['g6'], r['w'])
            res.update(name=r['name'], kind=kind)
            if kind == 'ADMITTED':
                f = src / 'candidates' / r['name'] / 'graph.edges'
                stored = [tuple(map(int, l.split())) for l in f.read_text().splitlines() if l.strip()]
                res['edge_file_matches'] = stored == E
                assert res['edge_file_matches']
            assert res['n'] == 28 and res['m'] <= 156 and res['alpha_le_3'] and res['omega'] <= 8, res
            rows.append(res)
    Path(out).write_text(json.dumps({'checked': len(rows), 'all_pass': True, 'rows': rows}, indent=1))
    print(len(rows), 'graphs: n=28, m<=156, alpha<=3, omega<=8 all PASS')


if __name__ == '__main__':
    main(*sys.argv[1:3])
