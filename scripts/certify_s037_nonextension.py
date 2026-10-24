"""Emit subdivision certificates for every forbidden disjoint addition."""
import itertools as it
import json
from pathlib import Path
import sys
import time
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s037_certificates import subdivision


if __name__ == '__main__':
    start = time.process_time()
    structure = json.loads((ROOT/'validation/S037/STRUCTURE.json').read_text())
    result = []
    for entry in structure['near_triangulations']:
        if entry['planar_disjoint_completions']:
            continue
        data = json.loads((ROOT/entry['path']).read_text())['best']
        es1, es2 = [set(map(tuple, data[k])) for k in ('E1', 'E2')]
        rows = []
        for e in it.combinations(range(28), 2):
            if e in es1 | es2:
                continue
            g = nx.Graph(es2 | {e})
            planar, obstruction = nx.check_planarity(g, counterexample=True)
            assert not planar
            edges = sorted(tuple(sorted(x)) for x in obstruction.edges())
            assert set(edges) <= es2 | {e}
            kind = subdivision(edges)
            rows.append(dict(added=e, obstruction=edges, kind=kind))
        assert len(rows) == 223
        result.append(dict(source=entry['path'], rows=rows, all_additions=223))
        print('certified all 223 additions:', entry['path'], flush=True)
    (ROOT/'validation/S037/NONEXTENSION.json').write_text(json.dumps(dict(
        status='PASS_SUBDIVISION_CERTIFIED', cpu_seconds=time.process_time()-start, examples=result), indent=2)+'\n', newline='\n')
