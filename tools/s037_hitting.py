"""Fixed-T1 four-set hitting diagnostic, explicitly a nonplanar relaxation."""
import itertools as it
import json
from pathlib import Path
import time
import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]


def run(data, size):
    start_cpu, start_wall = time.process_time(), time.monotonic()
    n = data['n']
    e1 = set(map(tuple, data['E1']))
    permitted = [e for e in it.combinations(range(n), 2) if e not in e1]
    x = {e: i+1 for i, e in enumerate(permitted)}
    family = [vs for vs in it.combinations(range(n), 4)
              if not any(e in e1 for e in it.combinations(vs, 2))]
    clauses = [[x[e] for e in it.combinations(vs, 2)] for vs in family]
    clauses += CardEnc.equals(list(x.values()), bound=size, encoding=EncType.seqcounter).clauses
    base = len(clauses)
    with Solver(name='cadical195', bootstrap_with=clauses) as s:
        s.conf_budget(20000)
        sat = s.solve_limited()
        stats = s.accum_stats()
        positive = set(s.get_model()) if sat else set()
        es = sorted(e for e, v in x.items() if v in positive) if sat else None
    record = dict(n=n, fixed_T1_edges=len(e1), second_edges_required=size,
                  family_size=len(family), complement_edge_variables=len(x), clauses=base,
                  result='SAT_RELAXATION' if sat is True else 'UNKNOWN', stats=stats,
                  cpu_seconds=time.process_time()-start_cpu, wall_seconds=time.monotonic()-start_wall,
                  planarity_required_in_formula=False, witness=False)
    if es is not None:
        e2 = set(es)
        assert len(es) == size and not e1 & e2
        assert all(any(e in e2 for e in it.combinations(vs, 2)) for vs in family)
        assert all(any(e in e1 or e in e2 for e in it.combinations(vs, 2))
                   for vs in it.combinations(range(n), 4))
        g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(es)
        planar, obstruction = nx.check_planarity(g, counterexample=True)
        record.update(E1=sorted(e1), E2=es, independently_checked_four_sets=20475,
                      second_layer_planar=planar, independent_four_sets=0,
                      nonplanar_subgraph=sorted(tuple(sorted(e)) for e in obstruction.edges()) if not planar else None)
        assert not planar, 'Unexpected planar relaxation: independently validate immediately'
        assert not nx.is_planar(nx.Graph(record['nonplanar_subgraph']))
    # Include decoding and independent validation in actual CPU accounting.
    record.update(cpu_seconds=time.process_time()-start_cpu, wall_seconds=time.monotonic()-start_wall)
    return record


if __name__ == '__main__':
    assert json.loads((ROOT/'validation/S037/CONTROLS.json').read_text())['status'] == 'PASS'
    data = json.loads((ROOT/'validation/S037/guided/arm-00.json').read_text())['best']
    rows = [run(data, size) for size in (77, 78)]
    (ROOT/'validation/S037/HITTING.json').write_text(json.dumps(rows, indent=2)+'\n', newline='\n')
    for r in rows:
        print({k: v for k, v in r.items() if k not in ('E1', 'E2', 'nonplanar_subgraph')}, flush=True)
