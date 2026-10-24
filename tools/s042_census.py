"""S042 certified apex-leaf census (route R3); see sessions/S042/PLAN.md.

Leaf: (10-a)-critical L and edge e with Lambda = K_a v (L-e), omega(Lambda)<=8,
e(L) <= (6-a)n + 6a-11-a(a-1)/2. Critical graphs are joins K_c v F_1 v ... of
join-irreducible critical factors (Gallai); factor edges obey Kostochka-Yancey,
with equality iff k-Ore and the non-Ore bound of SRC-0020 Theorem 6.
"""
from fractions import Fraction
import hashlib
import itertools as it
import json
from pathlib import Path
import subprocess
import sys
import time

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT/'artifacts/tmp/S042'
OUT = ROOT/'validation/S042'
NMAX = 21


def ky_exact(k, n):
    return Fraction((k+1)*(k-2)*n-k*(k-3), 2*(k-1))


def nonore(k, n):
    y = max(2*k-6, k*k-5*k+2)
    return Fraction((k+1)*(k-2)*n-y, 2*(k-1))


def ceil(x):
    return -(-x.numerator//x.denominator)


def factor_min(k, n):
    """Minimum edges of a join-irreducible k-critical graph on n vertices, or None."""
    if k == 3:
        return n if n % 2 and n >= 5 else None
    if n < 2*k-1:
        return None
    return ceil(ky_exact(k, n))


def budget(a, n):
    return (6-a)*n+6*a-11-a*(a-1)//2


def factor_types():
    return [(k, n) for k in range(3, 10) for n in range(2*k-1, NMAX+1) if factor_min(k, n) is not None]


def multisets(total, start, types):
    if total == 0:
        yield ()
        return
    for i in range(start, len(types)):
        k, n = types[i]
        if k <= total:
            for rest in multisets(total-k, i, types):
                yield ((k, n),)+rest


def survey():
    """Every (a, c, factors) whose minimum edge count fits the leaf budget, with resolution status."""
    types = factor_types()
    rows = []
    for a in (1, 2, 3):
        target = 10-a
        for c in range(0, target+1):
            for facs in multisets(target-c, 0, types):
                n = c+sum(x for _, x in facs)
                if n > NMAX or (not facs and c != target):
                    continue
                if not facs:
                    continue  # L = K_{10-a}: Lambda contains K9 (checked explicitly below anyway)
                mins = [factor_min(k, x) for k, x in facs]
                e_min = c*(c-1)//2+c*sum(x for _, x in facs)+sum(mins)+sum(p*q for (_, p), (_, q) in it.combinations(facs, 2))
                slack = budget(a, n)-e_min
                if slack < 0:
                    continue
                status = []
                for (k, x), m in zip(facs, mins):
                    if k == 3:
                        status.append('ODD_CYCLE')
                    elif x <= 7:
                        status.append('ATLAS_COMPLETE')
                    elif m+slack >= ceil(nonore(k, x)):
                        status.append(f'UNRESOLVED_NONORE_e_{ceil(nonore(k, x))}..{m+slack}')
                    elif ky_exact(k, x).denominator == 1 and ky_exact(k, x) <= m+slack:
                        status.append('ORE_ONLY')
                    else:
                        status.append('EMPTY_NO_ORE_AT_THIS_ORDER')
                rows.append(dict(a=a, c=c, factors=[list(f) for f in facs], n=n, e_min=e_min, budget=budget(a, n),
                                 slack=slack, factor_status=status,
                                 resolved=all(not s.startswith('UNRESOLVED') for s in status)))
    return rows


def canon_key(g):
    return nx.weisfeiler_lehman_graph_hash(g, iterations=4)


def dedup(graphs):
    buckets, out = {}, []
    for g in graphs:
        key = (g.number_of_nodes(), g.number_of_edges(), canon_key(g))
        if any(nx.is_isomorphic(g, h) for h in buckets.get(key, [])):
            continue
        buckets.setdefault(key, []).append(g)
        out.append(g)
    return out


def relabel(g):
    return nx.convert_node_labels_to_integers(g, ordering='sorted')


def complete(g):
    n = g.number_of_nodes()
    return g.number_of_edges() == n*(n-1)//2


def dhgo(g1, g2, reduce=True):
    """DHGO compositions: delete xy from g1, split z of g2 into x,y (Aut(K_k) reduction if reduce)."""
    out = []
    g2r = nx.relabel_nodes(g2, {v: ('b', v) for v in g2})
    g1r = nx.relabel_nodes(g1, {v: ('a', v) for v in g1})
    edges = list(g1r.edges())[:1] if reduce and complete(g1) else list(g1r.edges())
    zs = sorted(g2r.nodes())[:1] if reduce and complete(g2) else sorted(g2r.nodes())
    for x, y in edges:
        for z in zs:
            nb = sorted(g2r[z])
            if reduce and complete(g2):
                masks = [(1 << s)-1 for s in range(1, len(nb))]
            else:
                masks = range(1, 2**len(nb)-1)
            for mask in masks:
                n1 = [w for i, w in enumerate(nb) if mask >> i & 1]
                n2 = [w for i, w in enumerate(nb) if not mask >> i & 1]
                h = nx.Graph()
                h.add_edges_from(e for e in g1r.edges() if set(e) != {x, y})
                h.add_edges_from(e for e in g2r.edges() if z not in e)
                h.add_edges_from((x, w) for w in n1)
                h.add_edges_from((y, w) for w in n2)
                out.append(relabel(h))
    return out


def ore_graphs(k, n, cache={}, reduce=True):
    key = (k, n, reduce)
    if key in cache:
        return cache[key]
    if n == k:
        res = [nx.complete_graph(k)]
    elif (n-1) % (k-1):
        res = []
    else:
        res = []
        for n1 in range(k, n, k-1):
            n2 = n+1-n1
            for g1 in ore_graphs(k, n1, reduce=reduce):
                for g2 in ore_graphs(k, n2, reduce=reduce):
                    res.extend(dhgo(g1, g2, reduce))
        res = dedup(res)
        assert all(r.number_of_edges() == ky_exact(k, n) for r in res)
    cache[key] = res
    return res


def reduction_control():
    out = {}
    for k, n in ((6, 11), (7, 13)):
        full, red = ore_graphs(k, n, reduce=False), ore_graphs(k, n, reduce=True)
        assert len(full) == len(red) and all(any(nx.is_isomorphic(f, r) for r in red) for f in full)
        out[f'{k}-{n}'] = len(red)
    return out


def irreducible(g):
    return nx.is_connected(nx.complement(g))


def chromatic_at_least(g, k):
    from pysat.solvers import Solver
    nodes = sorted(g)
    var = {(v, c): 1+i*(k-1)+c for i, v in enumerate(nodes) for c in range(k-1)}
    with Solver(name='cadical195') as s:
        for v in nodes:
            s.add_clause([var[v, c] for c in range(k-1)])
        for u, v in g.edges():
            for c in range(k-1):
                s.add_clause([-var[u, c], -var[v, c]])
        return not s.solve()


def is_critical(g, k):
    if not chromatic_at_least(g, k):
        return False
    return all(not chromatic_at_least(nx.Graph([f for f in g.edges() if f != e]), k) if g.number_of_edges() > 1 else True
               for e in g.edges())


def atlas_critical(k, n):
    out = []
    for g in nx.graph_atlas_g():
        if g.number_of_nodes() == n and min(dict(g.degree()).values(), default=0) >= k-1 and irreducible(g) and is_critical(g, k):
            out.append(relabel(g))
    return dedup(out)


def factor_graphs(k, n, status):
    if status == 'ODD_CYCLE':
        return [nx.cycle_graph(n)]
    if status == 'ATLAS_COMPLETE':
        return atlas_critical(k, n)
    if status == 'ORE_ONLY' or status.startswith('UNRESOLVED'):
        return [g for g in ore_graphs(k, n) if irreducible(g)]  # for UNRESOLVED: Ore part only (PARTIAL)
    return []


def join_all(c, parts):
    g = nx.complete_graph(c)
    offset = c
    for p in parts:
        p = nx.relabel_nodes(p, {v: offset+i for i, v in enumerate(sorted(p))})
        old = list(g.nodes())
        g.add_nodes_from(p.nodes()); g.add_edges_from(p.edges())
        g.add_edges_from((u, v) for u in old for v in p.nodes())
        offset += p.number_of_nodes()
    return g


def leaf_graphs(rows):
    leaves, considered = [], 0
    for r in rows:
        options = [factor_graphs(k, n, s) for (k, n), s in zip(r['factors'], r['factor_status'])]
        for parts in it.product(*options):
            L = join_all(r['c'], parts)
            a = r['a']
            if L.number_of_edges() > budget(a, L.number_of_nodes()):
                continue
            cliques = [set(q) for q in nx.find_cliques(L)]
            for e in L.edges():
                considered += 1
                if a+max(len(q)-(e[0] in q and e[1] in q) for q in cliques) > 8:
                    continue
                lam = nx.Graph([f for f in L.edges() if f != e]); lam.add_nodes_from(L)
                apex = [L.number_of_nodes()+i for i in range(a)]
                lam.add_edges_from(it.combinations(apex, 2))
                lam.add_edges_from((p, v) for p in apex for v in L)
                lam = relabel(lam)
                n = lam.number_of_nodes()
                if lam.number_of_edges() > 6*n-12:
                    continue
                if max(len(q) for q in nx.find_cliques(lam)) > 8:
                    continue
                leaves.append(dict(a=a, c=r['c'], factors=r['factors'], partial=not r['resolved'], L=sorted(L.edges()), deleted=list(e), graph=lam))
    unique = dedup([x['graph'] for x in leaves])
    groups = []
    for g in unique:
        sources = [dict(a=x['a'], c=x['c'], factors=x['factors'], partial=x['partial'], deleted=x['deleted'], L_edges=len(x['L']))
                   for x in leaves if nx.is_isomorphic(g, x['graph'])]
        groups.append(dict(edges=sorted(tuple(sorted(e)) for e in g.edges()), n=g.number_of_nodes(), m=g.number_of_edges(),
                           slack=6*g.number_of_nodes()-12-g.number_of_edges(),
                           omega=max(len(q) for q in nx.find_cliques(g)), sources=sources[:20], source_count=len(sources),
                           resolved_source=any(not x['partial'] for x in sources)))
    return considered, groups


def run(cmd, cap=None):
    t = time.time()
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=cap)
        return r, time.time()-t
    except subprocess.TimeoutExpired:
        return None, time.time()-t


def decide(idx, leaf, spent):
    import gzip
    name = f'leaf{idx:03d}'
    WORK.mkdir(parents=True, exist_ok=True)
    edgefile = WORK/f'{name}.txt'
    edgefile.write_text(''.join(f'{a} {b}\n' for a, b in leaf['edges']), newline='\n')
    prefix = (WORK/name).as_posix()
    rec = dict(name=name, edges_sha256=hashlib.sha256(edgefile.read_bytes()).hexdigest(), n=leaf['n'], m=leaf['m'],
               slack=leaf['slack'], omega=leaf['omega'])
    r, t = run([sys.executable, 'tools/s025_minor_cegar.py', edgefile.as_posix(), prefix, '300', '--lemmaC', '5'], cap=420)
    spent += t
    info = json.loads(r.stdout.strip().splitlines()[-1]) if r and r.stdout.strip() else {'verdict': 'UNKNOWN_TIMEOUT'}
    rec['minor_cegar'] = info
    if info['verdict'] == 'UNSAT':
        c, t1 = run([sys.executable, 'tools/s025_certify.py', prefix+'.cnf', (WORK/f'{name}-proof').as_posix(), '600', '600'])
        k, t2 = run([sys.executable, 'tools/s025_check_minor_cert.py', edgefile.as_posix(), prefix])
        spent += t1+t2
        cert, chk = json.loads(c.stdout.strip().splitlines()[-1]), json.loads(k.stdout.strip().splitlines()[-1])
        rec.update(certify=cert, structure=chk)
        if cert['verdict'] == 'UNSAT_DRAT_VERIFIED' and chk['verdict'] == 'ALL_CLAUSES_JUSTIFIED':
            rec['verdict'] = 'NONBIPLANAR_DRAT_VERIFIED'
            cdir = OUT/'certificates'
            cdir.mkdir(parents=True, exist_ok=True)
            arch = {}
            for key, src in (('edges', edgefile), ('cnf', Path(prefix+'.cnf')), ('lemmas', Path(prefix+'.lemmas.json'))):
                dst = cdir/(f'{name}.{key}.gz')
                dst.write_bytes(gzip.compress(src.read_bytes(), mtime=0))
                arch[key] = dict(path=str(dst.relative_to(ROOT)).replace('\\', '/'), sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),
                                 source_sha256=hashlib.sha256(src.read_bytes()).hexdigest())
            drat = WORK/f'{name}-proof'/f'{name}.drat.gz'
            (cdir/f'{name}.drat.gz').write_bytes(drat.read_bytes())
            arch['drat_gz'] = dict(path=f'validation/S042/certificates/{name}.drat.gz', sha256=hashlib.sha256(drat.read_bytes()).hexdigest())
            rec['archive'] = arch
            return rec, spent
    if info['verdict'] == 'SAT':
        split = json.loads(Path(prefix+'.split.json').read_text())
        rec.update(verdict='CANDIDATE_SPLIT_REQUIRES_INDEPENDENT_CHECK', E1=split['E1'], E2=split['E2'])
        return rec, spent
    for seed in (4201, 4202):
        out = WORK/f'{name}-anneal-{seed}.json'
        _, t = run([sys.executable, 'tools/s025_cover_anneal.py', edgefile.as_posix(), str(seed), '30', out.as_posix()])
        spent += t
        res = json.loads(out.read_text())
        rec[f'anneal_{seed}_best_uncovered'] = res['best_uncovered']
        if res['best_uncovered'] == 0:
            rec.update(verdict='CANDIDATE_SPLIT_REQUIRES_INDEPENDENT_CHECK', E1=res['E1'], E2=res['E2'])
            return rec, spent
    rec['verdict'] = 'UNKNOWN'
    return rec, spent


def main():
    reg = json.loads((OUT/'REGISTRATION.json').read_text())
    assert hashlib.sha256((ROOT/'sessions/S042/PLAN.md').read_bytes()).hexdigest() == reg['sha256']['sessions/S042/PLAN.md']
    assert hashlib.sha256((ROOT/'sessions/S042/PLAN_ADDENDUM.md').read_bytes()).hexdigest() == reg['addendum']['sha256']
    start = time.process_time()
    rows = survey()
    assert rows == json.loads((OUT/'CENSUS_TYPES.json').read_text())
    control = reduction_control()
    print('reduction control', control, flush=True)
    considered, groups = leaf_graphs(rows)
    ore_counts = {f'{k}-{n}': len(v) for (k, n, red), v in ore_graphs.__defaults__[0].items() if red}
    gen = time.process_time()-start
    out = dict(reduction_control=control, considered_leaf_pairs=considered, leaf_graphs=groups, ore_counts=ore_counts,
               generation_cpu_seconds=gen)
    (OUT/'LEAF_GRAPHS.json').write_text(json.dumps(out, indent=2)+'\n', newline='\n')
    print('considered', considered, 'unique leaf graphs', len(groups), 'ore', ore_counts, 'cpu', round(gen, 2), flush=True)
    for g in groups:
        print('  leaf n', g['n'], 'm', g['m'], 'slack', g['slack'], 'omega', g['omega'], 'resolved_source', g['resolved_source'],
              'from', g['sources'][0], flush=True)
    spent = reg['addendum']['stopped_run_cpu_seconds_counted']+gen
    decisions = []
    for i, g in enumerate(groups):
        if spent > 3300:
            decisions.append(dict(name=f'leaf{i:03d}', verdict='NOT_RUN_CPU_CAP'))
            continue
        rec, spent = decide(i, g, spent)
        decisions.append(rec)
        print('DECISION', rec['name'], rec['n'], rec['m'], rec['verdict'], round(spent, 1), flush=True)
        (OUT/'DECISIONS.json').write_text(json.dumps(dict(decisions=decisions, cpu_seconds_total=spent), indent=2)+'\n', newline='\n')
    (OUT/'DECISIONS.json').write_text(json.dumps(dict(decisions=decisions, cpu_seconds_total=spent), indent=2)+'\n', newline='\n')
    print('CENSUS FINISHED', len(decisions), 'cpu', round(spent, 1), flush=True)


if __name__ == '__main__':
    main()
