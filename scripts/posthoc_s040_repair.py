"""POST-HOC addendum items2-3: label-fixed alpha<=3 repair and K9 barrier near the S040 inputs.

Adds the registered exact hitting set T to the union, then deletes a maximum set
of original union edges keeping every four-set non-independent. Output graphs
have alpha<=3 (direct check) but NO biplanarity claim of any kind.
"""
import hashlib
import itertools as it
import json
from pathlib import Path
import time

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {156: 'validation/S039/arms/156-3900-star.json', 155: 'validation/S039/arms/155-3901-star.json'}


def clique_number(n, es):
    adj = {v: set() for v in range(n)}
    for a, b in es:
        adj[a].add(b); adj[b].add(a)
    best = 0

    def grow(r, p, x):
        nonlocal best
        if not p and not x:
            best = max(best, len(r))
            return
        pivot = max(p | x, key=lambda u: len(adj[u] & p))
        for v in list(p-adj[pivot]):
            grow(r | {v}, p & adj[v], x & adj[v])
            p = p-{v}; x = x | {v}
    grow(set(), set(range(n)), set())
    return best


def repair(density):
    start = time.process_time()
    data = json.loads((ROOT/INPUTS[density]).read_text())['best']
    union = set(map(tuple, data['E1'])) | set(map(tuple, data['E2']))
    diag = json.loads((ROOT/f'validation/S040/diagnostics/input-{density}.json').read_text())
    T = {tuple(e) for e in diag['tau']['hitting_set']}
    assert diag['tau']['exact'] and not T & union
    plus = union | T
    edges = sorted(union)
    var = {e: i+1 for i, e in enumerate(edges)}
    w = WCNF()
    for q in it.combinations(range(28), 4):
        inside = [e for e in it.combinations(q, 2) if e in plus]
        assert inside
        if not set(inside) & T:
            w.append([-var[e] for e in inside])
    for e in edges:
        w.append([var[e]], weight=1)
    with RC2(w) as solver:
        model = set(solver.compute())
    deleted = [e for e in edges if var[e] in model]
    final = plus-set(deleted)
    independent = sum(not any(e in final for e in it.combinations(q, 2)) for q in it.combinations(range(28), 4))
    assert independent == 0
    need = len(union)+len(T)-156
    degrees = sorted(sum(v in e for e in final) for v in range(28))
    # Keep only as many deletions as needed to reach 156 edges, chosen deterministically.
    chosen = sorted(deleted)[:max(need, 0)] if len(deleted) >= need else None
    graph = sorted(plus-set(chosen)) if chosen is not None else None
    if graph is not None:
        assert len(graph) <= 156
        assert all(any(e in set(graph) for e in it.combinations(q, 2)) for q in it.combinations(range(28), 4))
    omega = clique_number(28, graph) if graph is not None else None
    return dict(source=INPUTS[density], union_edges=len(union), tau=len(T), hitting_set=[list(e) for e in sorted(T)],
                max_safe_deletions=len(deleted), required_deletions=need,
                alpha3_graph_within_budget=graph is not None,
                graph_edges=len(graph) if graph else None, deleted=[list(e) for e in chosen] if chosen else None,
                edit_distance=len(T)+len(chosen) if chosen is not None else None,
                graph=[list(e) for e in graph] if graph else None,
                graph_sha256=hashlib.sha256(json.dumps(graph).encode()).hexdigest() if graph else None,
                clique_number=omega, contains_K9=(omega is not None and omega >= 9),
                degree_sequence=sorted(sum(v in e for e in graph) for v in range(28)) if graph else None,
                chi_lower_bound_by_counting=10 if graph else None,
                biplanarity='NOT_TESTED_NO_CLAIM', cpu_seconds=time.process_time()-start)


def k9_barrier(path):
    """Item3: K9-completion status of each useful absent pair and the K9-safe hitting number."""
    import networkx as nx
    start = time.process_time()
    data = json.loads((ROOT/path).read_text())['best']
    union = set(map(tuple, data['E1'])) | set(map(tuple, data['E2']))
    adj = {v: set() for v in range(28)}
    for a, b in union:
        adj[a].add(b); adj[b].add(a)
    g = nx.Graph(list(union))
    assert clique_number(28, union) == max(len(c) for c in nx.find_cliques(g)) <= 8
    H = [q for q in it.combinations(range(28), 4) if not any(e in union for e in it.combinations(q, 2))]
    incidence = {}
    for q in H:
        for e in it.combinations(q, 2):
            incidence[e] = incidence.get(e, 0)+1
    completes = {}
    for (a, b) in incidence:
        common = sorted(adj[a] & adj[b])
        sub = [e for e in union if e[0] in common and e[1] in common]
        k = clique_number(28, sub) if sub else (1 if common else 0)
        nk = max((len(c) for c in nx.find_cliques(g.subgraph(common))), default=0)
        assert k == nk
        completes[a, b] = k >= 7
    safe = sorted(e for e in incidence if not completes[e])
    locked = [q for q in H if all(completes[e] for e in it.combinations(q, 2))]
    result = dict(source=path, independent_four_sets=len(H), useful_pairs=len(incidence),
                  k9_completing_pairs=sum(completes.values()), safe_pairs=len(safe),
                  incidence_total=sum(incidence.values()),
                  incidence_on_k9_completing=sum(c for e, c in incidence.items() if completes[e]),
                  k9_locked_four_sets=len(locked), k9_locked_examples=[list(q) for q in locked[:10]],
                  top_pairs=[dict(pair=list(e), incidence=c, completes_K9=completes[e])
                             for e, c in sorted(incidence.items(), key=lambda x: (-x[1], x[0]))[:12]])
    if not locked:
        var = {e: i+1 for i, e in enumerate(safe)}
        w = WCNF()
        for q in H:
            w.append([var[e] for e in it.combinations(q, 2) if e in var])
        for e in safe:
            w.append([-var[e]], weight=1)
        with RC2(w) as solver:
            model = set(solver.compute())
        hitting = [e for e in safe if var[e] in model]
        assert all(any(e in set(hitting) for e in it.combinations(q, 2)) for q in H)
        w = WCNF()
        for x, y in it.combinations(range(len(H)), 2):
            if set(it.combinations(H[x], 2)) & set(it.combinations(H[y], 2)) & set(safe):
                w.append([-(x+1), -(y+1)])
        for x in range(len(H)):
            w.append([x+1], weight=1)
        with RC2(w) as solver:
            model = set(solver.compute())
        packing = [H[x] for x in range(len(H)) if x+1 in model]
        assert all(not (set(it.combinations(p, 2)) & set(it.combinations(q, 2)) & set(safe)) for p, q in it.combinations(packing, 2))
        joint = union | set(hitting)
        result.update(tau_safe_upper=len(hitting), tau_safe_lower_packing=len(packing), tau_safe_exact=len(packing) == len(hitting),
                      safe_hitting_set=[list(e) for e in hitting], union_plus_safe_clique_number=clique_number(28, joint))
    result['cpu_seconds'] = time.process_time()-start
    return result


def main():
    rows = []
    for density in (156, 155):
        r = repair(density)
        rows.append(r)
        print(json.dumps({k: v for k, v in r.items() if k not in ('graph',)}), flush=True)
    barrier = []
    for path in list(INPUTS.values())+['validation/S040/arms/protected-4010-coord.json']:
        b = k9_barrier(path)
        barrier.append(b)
        print(json.dumps({k: v for k, v in b.items() if k != 'top_pairs'}), flush=True)
    out = dict(status='POSTHOC_ADDENDUM_NO_BIPLANARITY_CLAIM', rows=rows, k9_barrier=barrier,
               cpu_seconds=sum(r['cpu_seconds'] for r in rows+barrier))
    (ROOT/'validation/S040/POSTHOC_REPAIR.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')


if __name__ == '__main__':
    main()
