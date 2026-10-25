"""S046 candidate diagnostics: structure, validated colourings, checked lower bounds.

Every positive colouring is checked edge by edge here; a non-8-colourability
claim requires a drat-trim VERIFIED proof from the pinned S004 tools.
Timeouts and unchecked UNSAT are UNKNOWN. Nothing here is a coverage count.
"""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import threading
import time

import networkx as nx
import psutil
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
CADICAL = ROOT / 'artifacts/tmp/S004/cadical.exe'
DRAT_TRIM = ROOT / 'artifacts/tmp/S004/drat-trim-mingw.exe'
PINNED = {'cadical': '120d2c53bf14a8b70cce78be980824651922d53523228d9f0f026998caea7e48',
          'drat-trim': '970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned_ok():
    return sha(CADICAL) == PINNED['cadical'] and sha(DRAT_TRIM) == PINNED['drat-trim']


class Ledger:
    """Process-tree CPU and wall meter for one experimental block."""

    def __init__(self, block, path=ROOT / 'artifacts/tmp/S046/BUDGET.jsonl'):
        self.block, self.path = block, Path(path)
        self.me = psutil.Process()
        t = self.me.cpu_times()
        self.cpu0, self.wall0 = t.user + t.system, time.monotonic()
        self.child_cpu = 0.0

    def cpu(self):
        t = self.me.cpu_times()
        return t.user + t.system - self.cpu0 + self.child_cpu

    def wall(self):
        return time.monotonic() - self.wall0

    def close(self, **extra):
        row = dict(block=self.block, cpu_seconds=round(self.cpu(), 3), wall_seconds=round(self.wall(), 3),
                   end_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **extra)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(row) + '\n')
        return row


def spent(path=ROOT / 'artifacts/tmp/S046/BUDGET.jsonl'):
    rows = [json.loads(x) for x in Path(path).read_text().splitlines()] if Path(path).exists() else []
    return sum(r['cpu_seconds'] for r in rows), sum(r['wall_seconds'] for r in rows), rows


def check_colouring(edges, colours, k):
    assert all(type(c) == int and 0 <= c < k for c in colours)
    assert all(colours[a] != colours[b] for a, b in edges)


def check_clique(edges, clique):
    es = {tuple(sorted(e)) for e in edges}
    assert all(tuple(sorted(p)) in es for p in it.combinations(clique, 2))


def max_clique(g, seconds):
    best, until = [], time.monotonic() + seconds
    for i, c in enumerate(nx.find_cliques(g)):
        if len(c) > len(best):
            best = c
        if i % 256 == 0 and time.monotonic() > until:
            return sorted(best), False
    return sorted(best), True


def colour_clauses(n, edges, k, clique=()):
    var = lambda v, c: v * k + c + 1
    cls = []
    for v in range(n):
        cls.append([var(v, c) for c in range(k)])
        cls.extend([-var(v, a), -var(v, b)] for a, b in it.combinations(range(k), 2))
    for a, b in edges:
        cls.extend([-var(a, c), -var(b, c)] for c in range(k))
    # Colour names are interchangeable: a validated clique may take colours 0..|Q|-1.
    for i, v in enumerate(list(clique)[:k]):
        cls.append([var(v, i)])
    return cls


def sat_colour(n, edges, k, seconds, clique=(), name='cadical195'):
    cls = colour_clauses(n, edges, k, clique)
    with Solver(name=name, bootstrap_with=cls) as s:
        done = threading.Event()

        def stop():
            if not done.wait(seconds):
                s.interrupt()
        t = threading.Thread(target=stop, daemon=True)
        t.start()
        try:
            r = s.solve_limited(expect_interrupt=True)
            model = s.get_model() if r is True else None
        finally:
            done.set()
            t.join()
    if r is True:
        pos = set(x for x in model if x > 0)
        cols = [next(c for c in range(k) if v * k + c + 1 in pos) for v in range(n)]
        check_colouring(edges, cols, k)
        return 'SAT', cols
    return ('UNSAT' if r is False else 'TIMEOUT'), None


def drat_certify(n, edges, k, clique, work, solve_seconds, check_seconds):
    """Return (verdict, seconds) with verdict VERIFIED_NON_K_COLOURABLE or a failure label."""
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    cls = colour_clauses(n, edges, k, clique)
    cnf, proof = work / 'col.cnf', work / 'col.drat'
    with cnf.open('w', encoding='ascii', newline='\n') as f:
        f.write(f'p cnf {n * k} {len(cls)}\n')
        f.writelines(' '.join(map(str, c)) + ' 0\n' for c in cls)
    t0 = time.monotonic()
    try:
        run = subprocess.run([str(CADICAL), '-q', '--no-binary', str(cnf), str(proof)],
                             capture_output=True, text=True, timeout=solve_seconds)
    except subprocess.TimeoutExpired:
        return 'DRAT_SOLVE_TIMEOUT', time.monotonic() - t0
    if run.returncode == 10:
        return 'CADICAL_SAT_CONTRADICTS', time.monotonic() - t0
    if run.returncode != 20:
        return f'CADICAL_RC_{run.returncode}', time.monotonic() - t0
    try:
        chk = subprocess.run([str(DRAT_TRIM), str(cnf), str(proof), '-t', str(check_seconds)],
                             capture_output=True, text=True, timeout=check_seconds + 30)
    except subprocess.TimeoutExpired:
        return 'DRAT_CHECK_TIMEOUT', time.monotonic() - t0
    ok = chk.returncode == 0 and 's VERIFIED' in chk.stdout
    return ('VERIFIED_NON_K_COLOURABLE' if ok else 'DRAT_NOT_VERIFIED'), time.monotonic() - t0


def structure(n, edges, clique_seconds=2.0):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    deg = [d for _, d in g.degree()]
    core = nx.core_number(g)
    comps = [c for c in nx.connected_components(g) if len(c) > 1]
    big = g.subgraph(max(comps, key=len)) if comps else None
    order = list(reversed(list(_smallest_last(g))))
    greedy = nx.greedy_color(g, strategy=lambda G, c: order)
    sl = [greedy[v] for v in range(n)]
    check_colouring(edges, sl, max(sl) + 1 if sl else 1)
    ds = nx.greedy_color(g, strategy='DSATUR')
    dsc = [ds[v] for v in range(n)]
    check_colouring(edges, dsc, max(dsc) + 1 if dsc else 1)
    clique, complete = max_clique(g, clique_seconds)
    check_clique(edges, clique)
    return dict(m=len(edges), min_degree=min(deg), max_degree=max(deg),
                isolated=sum(d == 0 for d in deg), nontrivial_components=len(comps),
                largest_component=len(big) if big else 0,
                cut_vertices=len(list(nx.articulation_points(big))) if big else 0,
                degeneracy=max(core.values()), core9_order=sum(c >= 9 for c in core.values()),
                greedy_colours=max(sl) + 1, dsatur_colours=max(dsc) + 1,
                best_colours=min(max(sl), max(dsc)) + 1,
                best_colouring=sl if max(sl) <= max(dsc) else dsc,
                clique=clique, omega=len(clique), omega_exact=complete)


def _smallest_last(g):
    h = {v: set(g[v]) for v in g}
    while h:
        v = min(h, key=lambda x: (len(h[x]), x))
        yield v
        for u in h[v]:
            h[u].discard(v)
        del h[v]


def iso_classes(graphs):
    """Exact isomorphism classes: WL hash screen, VF2 with checked mapping."""
    buckets = {}
    for i, (n, edges) in enumerate(graphs):
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        buckets.setdefault((n, len(edges), nx.weisfeiler_lehman_graph_hash(g, iterations=3)), []).append((i, g))
    classes = []
    for items in buckets.values():
        reps = []
        for i, g in items:
            for rep in reps:
                gm = nx.algorithms.isomorphism.GraphMatcher(rep[0][1], g)
                if gm.is_isomorphic():
                    f = gm.mapping
                    a = {frozenset((f[x], f[y])) for x, y in rep[0][1].edges()}
                    assert a == {frozenset(e) for e in g.edges()}, 'unchecked isomorphism'
                    rep.append((i, g))
                    break
            else:
                reps.append([(i, g)])
        classes.extend([[i for i, _ in rep] for rep in reps])
    return sorted(classes, key=len, reverse=True)


def wilson(successes, total, z=1.959963984540054):
    if total == 0:
        return (0.0, 1.0)
    p = successes / total
    d = 1 + z * z / total
    c = (p + z * z / (2 * total)) / d
    h = z * ((p * (1 - p) / total + z * z / (4 * total * total)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))
