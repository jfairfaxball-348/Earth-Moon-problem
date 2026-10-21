"""Independent adjacency-set subdivision audit, cross-checked against NetworkX."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"tools")]
import check_s032_native as native
from replay_s030_search import subdivision as reference

def subdivision(edges):
    adj={}
    for a,b in edges:
        assert a!=b
        adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
    assert adj
    seen=set();todo=[next(iter(adj))]
    while todo:
        v=todo.pop()
        if v in seen:continue
        seen.add(v);todo.extend(adj[v]-seen)
    assert seen==set(adj)
    queue=[v for v,ns in adj.items() if len(ns)==2]
    while queue:
        v=queue.pop()
        if v not in adj or len(adj[v])!=2:continue
        a,b=adj[v];assert a!=b and b not in adj[a]
        adj[a].remove(v);adj[b].remove(v);del adj[v]
        adj[a].add(b);adj[b].add(a)
        # Suppression preserves endpoint degree; queue remains complete.
    if len(adj)==5 and all(len(ns)==4 for ns in adj.values()):return "K5"
    assert len(adj)==6 and all(len(ns)==3 for ns in adj.values())
    colours={}
    for start in adj:
        if start in colours:continue
        colours[start]=0;todo=[start]
        while todo:
            v=todo.pop()
            for w in adj[v]:
                if w not in colours:colours[w]=1-colours[v];todo.append(w)
                else:assert colours[w]!=colours[v]
    return "K33"

def verdict(fn,es):
    try:return fn(es)
    except AssertionError:return "REJECT"

def main():
    start=time.monotonic();rng=random.Random(3301);tests=0
    for n in (5,6):
        pairs=list(itertools.combinations(range(n),2))
        masks=range(1<<len(pairs)) if n==5 else [rng.randrange(1<<len(pairs)) for _ in range(2048)]
        for mask in masks:
            es=[e for i,e in enumerate(pairs) if mask>>i&1]
            # Empty NetworkX graph raises its explicit pointless-concept error.
            if not es:assert verdict(subdivision,es)=="REJECT";continue
            assert verdict(subdivision,es)==verdict(reference,es);tests+=1
    for kind in ("K5","K33"):
        for seed in range(256):
            es=list(itertools.combinations(range(5),2)) if kind=="K5" else list(itertools.product(range(3),range(3,6)))
            nextv=5 if kind=="K5" else 6
            for _ in range(seed%23):
                a,b=es.pop(rng.randrange(len(es)));es.extend([(a,nextv),(nextv,b)]);nextv+=1
            assert subdivision(es)==reference(es)==kind;tests+=1
    area=ROOT/"artifacts/tmp/S032"
    inputs=json.loads((area/"INPUTS.json").read_text())
    for name,h in inputs["sha256"].items():assert hashlib.sha256((area/name).read_bytes()).hexdigest()==h
    rename={int(k):v for k,v in inputs["original_to_native"].items()}
    assert sorted(rename)==sorted(rename.values())==list(range(1,17977))
    with (area/"original.cnf").open() as old,(area/"base.cnf").open() as new:
        assert next(old)==next(new)
        count=0
        for a,b in zip(old,new,strict=True):
            xs=list(map(int,a.split()));ys=list(map(int,b.split()))
            assert xs[-1]==ys[-1]==0
            assert [rename[abs(x)]*(1 if x>0 else -1) for x in xs[:-1]]==ys[:-1];count+=1
        assert count==inputs["base_clauses"]==336030
    rules=area/"campaign/learned.lem"
    h=hashlib.sha256(rules.read_bytes()).hexdigest()
    assert h=="6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177"
    native.subdivision=subdivision
    checked=native.lemmas(rules,28,[tuple(e) for e in inputs["pairs"]]);assert checked==2579937
    record={"status":"PASS","base_clauses":count,"variables":17976,"bijective_renaming_checked":True,"independently_checked_native_clauses":checked,"lemma_sha256":h,"verdict":"UNKNOWN","validator":"independent Python adjacency-set suppression; every clause checked","networkx_comparison_controls":tests,"seconds":time.monotonic()-start}
    for p in (area/"CAMPAIGN_AUDIT.json",ROOT/"validation/S033/INPUT_AUDIT.json"):
        p.write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps(record,indent=2))
if __name__=="__main__":main()
