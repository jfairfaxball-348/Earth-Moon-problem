#!/usr/bin/env python3
"""Exact labelled iterator for the S013 17-vertex H=K6 join C5 boundary.
No exhaustive enumeration has been executed; default CLI returns counts only.
"""
from itertools import combinations, product
from math import comb
import argparse, json
OLD=tuple(range(11)); NEW=tuple(range(11,17))
def old_edges():
    edges=set(combinations(range(6),2))
    edges.update(tuple(sorted((6+i,6+(i+1)%5))) for i in range(5))
    edges.update((i,j) for i in range(6) for j in range(6,11))
    assert len(edges)==50
    return edges
def finite_domains():
    # Explicit labelled internal modification and six cross-neighbour sizes.
    yield ("K6",None,(4,4,4,4,4,4))
    for x in range(6):
        d=[4]*6; d[x]=5
        yield ("K6",None,tuple(d))
    for missing in combinations(NEW,2):
        d=tuple(5 if x in missing else 4 for x in NEW)
        yield ("K6-e",missing,d)
def labelled_candidates():
    H=old_edges()
    for name,missing,degrees in finite_domains():
        inside=set(combinations(NEW,2))
        if missing is not None:inside.remove(missing)
        for rows in product(*(combinations(OLD,d) for d in degrees)):
            cross={(u,v) for v,neighbors in zip(NEW,rows) for u in neighbors}
            E=H|inside|cross
            assert len(E) in (89,90)
            yield dict(vertices=list(range(17)),old_edges=sorted(H),
              new_edges=sorted(inside),cross_edges=sorted(cross),
              edges=sorted(E),kind=name,missing=missing,degree_vector=degrees)
def labelled_count():
    k4,k5=comb(11,4),comb(11,5)
    return {"K6_cross24":k4**6, "K6_cross25":6*k5*k4**5,
            "K6e_cross26":15*k5**2*k4**4}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--first",type=int,default=0,
      help="Print at most this many labelled cases; do not attempt complete iteration.")
    args=ap.parse_args()
    assert 0<=args.first<=10
    print(json.dumps({"not_executed_full_search":True,
      "labelled_family_counts":labelled_count(),
      "old_automorphisms":"S6 x D5",
      "new_automorphisms":"S6 (K6) or S2 x S4 (K6-e stabiliser)",
      "logical_closure":"CLM-0074-0076 symbolic Hall/K9 proof; no enumeration needed"}))
    if args.first:
        for i,g in enumerate(labelled_candidates()):
            if i>=args.first:break
            print(json.dumps(g))
if __name__=="__main__":main()
