#!/usr/bin/env python3
"""S028 obstruction-closure helpers: deletion children, isomorphism dedup, refilter.

Deleting one vertex of a clique blow-up B[u] removes it from one bag; all
vertices of a bag are closed twins, so one deletion per bag covers every
one-vertex deletion up to isomorphism. A bag reduced to size 0 removes its base
vertex. Containment tests use the audit-form quotient CNF of tools/s027_contain.py
under a conflict budget; SAT answers are decoded and explicitly checked on the
target, UNSAT answers here are only screening (never certificates).
"""
import itertools as it
from pathlib import Path
import sys

import networkx as nx
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s027_contain import encode, explicit_map, obstruction   # noqa: E402


def child(g6, u, bag):
    """Blow-up with one vertex of `bag` deleted, as (g6, u) with no empty bag."""
    A = nx.from_graph6_bytes(g6.encode())
    u = list(u)
    u[bag] -= 1
    keep = [v for v in range(len(u)) if u[v] > 0]
    B = nx.relabel_nodes(A.subgraph(keep), {v: i for i, v in enumerate(keep)})
    B = nx.convert_node_labels_to_integers(B, ordering='sorted')
    return nx.to_graph6_bytes(B, header=False).decode().strip(), [u[v] for v in keep]


def weighted(g6, u):
    A = nx.from_graph6_bytes(g6.encode())
    for v in A:
        A.nodes[v]['w'] = u[v]
    return A


def same(a, b):
    """Isomorphism of weighted base graphs implies isomorphic blow-ups."""
    A, B = weighted(*a), weighted(*b)
    if sorted(a[1]) != sorted(b[1]) or A.number_of_edges() != B.number_of_edges():
        return False
    return nx.is_isomorphic(A, B, node_match=lambda x, y: x['w'] == y['w'])


def contains(H, g6, w, budget=200000):
    """('CONTAINS', f) explicitly checked, ('AVOIDS_SCREEN', None) or ('UNKNOWN', None)."""
    B = nx.from_graph6_bytes(g6.encode())
    if H['n'] > sum(w) or len(H['edges']) > B.number_of_edges() + sum(x * (x - 1) // 2 for x in w) + \
            sum(w[a] * w[b] for a, b in B.edges()):
        return 'AVOIDS_SCREEN', None
    cls, top, x, _ = encode(H, w, B=B)
    with Solver(name='cadical195', bootstrap_with=cls) as s:
        s.conf_budget(budget)
        r = s.solve_limited()
        if r is True:
            m = set(v for v in s.get_model() if v > 0)
            f = [next(b for b in range(len(w)) if x(v, b) in m) for v in range(H['n'])]
            explicit_map(H, w, f, list(B.edges()))
            return 'CONTAINS', f
    return ('AVOIDS_SCREEN', None) if r is False else ('UNKNOWN', None)


def first_contained(obs, g6, w):
    unknown = False
    for H in sorted(obs, key=lambda H: H['n']):
        v, f = contains(H, g6, w)
        if v == 'CONTAINS':
            return H['name'], f, unknown
        unknown |= v == 'UNKNOWN'
    return None, None, unknown


def as_obstruction(name, g6, u):
    return obstruction(name, g6, u)
