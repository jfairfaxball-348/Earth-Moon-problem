#!/usr/bin/env python3
"""S017 positive-only embedding-aware Kuratowski conflict backtracking.

Every transition preserves exact edge disjointness and planar placed layers;
remaining edges are explicitly retained, never silently dropped.
"""
import json
import random
import time
import networkx as nx
from s015_recheck_219 import build_trial, check_complete

def canon(e):
    return tuple(sorted(e))

def planar(layer):
    return nx.check_planarity(layer,counterexample=False)[0]

def repair(n, edges, colouring, row, seed, deadline, output):
    rng=random.Random(seed)
    best=None
    moves=0
    def invariant(a,b,missing):
        aa={canon(e) for e in a.edges()}
        bb={canon(e) for e in b.edges()}
        mm=set(missing)
        assert aa.isdisjoint(bb) and aa.isdisjoint(mm) and bb.isdisjoint(mm)
        assert aa|bb|mm==set(edges)
    def visit(a,b,missing,depth,seen):
        nonlocal best,moves
        if time.monotonic()>=deadline:
            return None
        invariant(a,b,missing)
        moves+=1
        if best is None or len(missing)<len(best[2]):
            best=(a.copy(),b.copy(),list(missing))
        if not missing:
            return (a,b)
        key=(frozenset(map(canon,a.edges())),frozenset(map(canon,b.edges())))
        if key in seen:
            return None
        seen.add(key)
        # Try a sample of difficult unplaced edges in both layers.
        choices=list(missing)
        rng.shuffle(choices)
        for e in choices[:min(4,len(choices))]:
            other=[f for f in missing if f!=e]
            for side in rng.sample([0,1],2):
                x,y=(a,b) if side==0 else (b,a)
                gx=x.copy()
                gx.add_edge(*e)
                okay,obstruction=nx.check_planarity(gx,counterexample=True)
                if okay:
                    result=visit(gx if side==0 else y.copy(),
                                 y.copy() if side==0 else gx,
                                 other,depth,seen)
                    if result:
                        return result
                    continue
                if depth<=0:
                    continue
                # Every displayed Kuratowski subdivision containing e must
                # lose one of its edges. Backtrack through actual obstructions.
                conflict=[canon(f) for f in obstruction.edges()
                          if canon(f)!=canon(e) and x.has_edge(*f)]
                rng.shuffle(conflict)
                for f in conflict[:min(8,len(conflict))]:
                    if time.monotonic()>=deadline:
                        return None
                    h=gx.copy()
                    h.remove_edge(*f)
                    if not planar(h):
                        continue
                    nxt=other+[f]
                    result=visit(h if side==0 else y.copy(),
                                 y.copy() if side==0 else h,
                                 nxt,depth-1,seen)
                    if result:
                        return result
        return None
    starts=[]
    for mode in [0,1,2]:
        if time.monotonic()>=deadline:
            break
        a,b,missing=build_trial(n,edges,rng,mode)
        invariant(a,b,missing)
        starts.append({"mode":mode,"unplaced":len(missing)})
        if best is None or len(missing)<len(best[2]):
            best=(a.copy(),b.copy(),list(missing))
        ans=visit(a,b,list(missing),3,set())
        if ans:
            a,b=ans
            check_complete(row,n,edges,a,b,colouring,output)
            return {"row":row,"seed":seed,"starts":starts,"moves":moves,
                    "best_missing":0,"status":"PROVISIONAL_SPLIT_NEEDS_COLD_RECHECK"}
    assert best is not None
    a,b,missing=best
    invariant(a,b,missing)
    return {"row":row,"seed":seed,"starts":starts,"moves":moves,
            "best_missing":len(missing),
            "partial":{"E1":sorted(map(list,a.edges())),
                       "E2":sorted(map(list,b.edges())),
                       "unplaced":sorted(map(list,missing))},
            "status":"ATTEMPTED_STILL_UNKNOWN"}
