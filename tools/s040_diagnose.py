"""Registered finite diagnostic of the independent-four-set hypergraph.

Proves only: (i) tau bracket, so every alpha<=3 graph on the same labels adds
at least the packing-bound number of absent pairs; (ii) the C1..C4 class of each
useful absent pair relative to the stated move families at this fixed state.
"""
from collections import Counter
import itertools as it

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

from s038_patch import candidates, covered, universe
from s040_coordinated import FOURS, Table, pair_scores, single_scores


def hypergraph(planes):
    es = planes[0].edges | planes[1].edges
    return es, [q for q in it.combinations(range(28), 4) if not any(e in es for e in it.combinations(q, 2))]


def tau_bracket(H):
    if not H:
        return dict(lower_packing=0, upper_hitting=0, rc2_hitting_optimum=0, exact=True, packing=[], hitting_set=[])
    elements = sorted({e for q in H for e in it.combinations(q, 2)})
    var = {e: i+1 for i, e in enumerate(elements)}
    w = WCNF()
    for q in H:
        w.append([var[e] for e in it.combinations(q, 2)])
    for e in elements:
        w.append([-var[e]], weight=1)
    with RC2(w) as solver:
        model = set(solver.compute())
        cost = solver.cost
    hitting = [e for e in elements if var[e] in model]
    w = WCNF()
    for a, b in it.combinations(range(len(H)), 2):
        if len(set(H[a]) & set(H[b])) >= 2:
            w.append([-(a+1), -(b+1)])
    for a in range(len(H)):
        w.append([a+1], weight=1)
    with RC2(w) as solver:
        model = set(solver.compute())
    packing = [H[a] for a in range(len(H)) if a+1 in model]
    chosen = set(hitting)
    assert all(any(e in chosen for e in it.combinations(q, 2)) for q in H)
    assert all(len(set(x) & set(y)) <= 1 for x, y in it.combinations(packing, 2))
    assert len(hitting) == cost
    return dict(lower_packing=len(packing), upper_hitting=len(hitting), rc2_hitting_optimum=cost,
                exact=len(packing) == len(hitting), packing=packing, hitting_set=hitting)


def classify(planes, protected=(frozenset(), frozenset())):
    cover, full = universe(28)
    es, H = hypergraph(planes)
    incidence = Counter(e for q in H for e in it.combinations(q, 2))
    useful = set(incidence)
    witness, best = {}, {}

    def note(e, cls, value, data):
        old = witness.get(e)
        if old is None or (cls != 'C1', int(value)) < (old['class'] != 'C1', old['score']):
            witness[e] = dict(data, **{'class': cls, 'score': int(value)})

    for value, k, patch, ds, fs in candidates(planes, cover, full, sizes=(1, 2, 3), guided_limit=None):
        if set(patch['removed']) & protected[k]:
            continue
        added = set(ds)-set(patch['removed'])
        for e in added & useful:
            note(e, 'C1', value, dict(kind='patch', layer=k, removed=sorted(set(patch['removed'])-set(ds)), added=sorted(added)))
    t = [Table(planes[k], planes[1-k].edges, cover, protected[k]) for k in (0, 1)]
    relaxed_adds = set()
    for k in (0, 1):
        legal, scores = single_scores(t[k], covered(planes[1-k].edges, cover))
        for i, s in zip(legal, scores):
            rem, add = t[k].keys[i]
            for e in add & useful:
                note(e, 'C1', s, dict(kind='star', layer=k, removed=sorted(rem), added=sorted(add)))
        for rem, add in t[k].keys:
            relaxed_adds |= add & useful
    I, J, T, S = pair_scores(t[0], t[1], (1, 2))
    for i, j, kind, s in zip(I, J, T, S):
        (r0, a0), (r1, a1) = t[0].keys[i], t[1].keys[j]
        for e in (a0 | a1) & useful:
            note(e, 'C2', s, dict(kind='pair', type=int(kind), removed=[sorted(r0), sorted(r1)], added=[sorted(a0), sorted(a1)]))
    classes = {}
    for e in sorted(useful):
        if e in witness:
            classes[e] = witness[e]['class']
        else:
            classes[e] = 'C3' if e in relaxed_adds else 'C4'
    summary = {c: dict(pairs=sum(v == c for v in classes.values()),
                       incidence=sum(incidence[e] for e, v in classes.items() if v == c)) for c in ('C1', 'C2', 'C3', 'C4')}
    locked = [q for q in H if all(classes[e] in ('C3', 'C4') for e in it.combinations(q, 2))]
    only_c2 = [q for q in H if not any(classes[e] == 'C1' for e in it.combinations(q, 2))
               and any(classes[e] == 'C2' for e in it.combinations(q, 2))]
    return dict(useful_pairs=len(useful), summary=summary, locked_four_sets=len(locked),
                four_sets_needing_relaxed_pairs=len(only_c2),
                rows=[{'pair': list(e), 'incidence': incidence[e], 'class': classes[e], 'witness': witness.get(e)} for e in sorted(useful)])


def diagnose(planes, protected=(frozenset(), frozenset())):
    es, H = hypergraph(planes)
    vertex = Counter(v for q in H for v in q)
    union_degree = Counter(v for e in es for v in e)
    layer_degree = [Counter(v for e in p.edges for v in e) for p in planes]
    absent = [e for e in it.combinations(range(28), 2) if e not in es]
    result = dict(independent_four_sets=len(H), checked_four_sets=FOURS, H=[list(q) for q in H],
                  vertex_incidence={v: vertex[v] for v in range(28)},
                  union_degree={v: union_degree[v] for v in range(28)},
                  layer_degree=[{v: d[v] for v in range(28)} for d in layer_degree],
                  min_layer_degree=[min(d[v] for v in range(28)) for d in layer_degree],
                  absent_pairs=len(absent), tau=tau_bracket(H))
    result.update(classify(planes, protected))
    return result
