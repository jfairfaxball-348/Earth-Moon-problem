#!/usr/bin/env python3
"""S013 CAM-0016: bounded POSITIVE-ONLY constructive experiments, never negative biplanarity decisions."""
import argparse, hashlib, json, os, platform, random, sys, time
from pathlib import Path
import networkx as nx
sys.path.insert(0,str(Path(__file__).resolve().parent))
from s012_swap_audit import expand
from s011_positive_search import build_trial, single_transfer_repair
from check_layers import certify_layer

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
TARGETS=[2,55,59,61,199,200]
def sha(s): return hashlib.sha256(Path(s).read_bytes()).hexdigest()
def check_split(n,E,A,B):
    ea={tuple(sorted(z)) for z in A.edges()}
    eb={tuple(sorted(z)) for z in B.edges()}
    assert not (ea&eb) and ea|eb==E
    assert all(0<=u<v<n for u,v in E)
    result=[certify_layer(n,sorted(ea)),certify_layer(n,sorted(eb))]
    assert nx.check_planarity(A)[0] and nx.check_planarity(B)[0]
    return result
def graph(n,es):
    g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(es);return g
def pair(n,rng):
    # Stacked triangulation has an explicitly maintained triangular face list.
    faces=[(0,1,2)]; E={(0,1),(0,2),(1,2)}
    for v in range(3,n):
        i=rng.randrange(len(faces))
        a,b,c=faces.pop(i)
        for u in (a,b,c): E.add(tuple(sorted((u,v))))
        faces.extend([(a,b,v),(b,c,v),(c,a,v)])
    A=graph(n,E)
    assert len(E)==3*n-6 and nx.check_planarity(A)[0]
    candidates=[(u,v) for u in range(n) for v in range(u+1,n) if (u,v) not in E]
    rng.shuffle(candidates)
    B=graph(n,[])
    for u,v in candidates:
        B.add_edge(u,v)
        if not nx.check_planarity(B)[0]:B.remove_edge(u,v)
    F={tuple(sorted(e)) for e in B.edges()}
    assert not E&F
    check_split(n,E|F,A,B)
    U=graph(n,E|F)
    colors=nx.coloring.greedy_color(U,strategy="saturation_largest_first")
    assert len(colors)==n and all(colors[u]!=colors[v] for u,v in E|F)
    return {"n":n,"m1":len(E),"m2":len(F),"m":len(E|F),"greedy_k":len(set(colors.values())),
            "E1":[list(e) for e in sorted(E)],"E2":[list(e) for e in sorted(F)],
            "verified_proper_coloring":[colors[v] for v in range(n)]}
def multi(corpus,rng,deadline):
    out=[]
    for attempt in range(48):
        if time.monotonic()>=deadline-8: break
        idx=TARGETS[attempt%len(TARGETS)]
        bags,E=expand(corpus[idx]);n=len(bags)
        A,B,miss=build_trial(n,sorted(E),rng)
        placed=list(A.edges())+list(B.edges())
        if len(placed)<2:continue
        drop=rng.sample(placed,2)
        oldnon=[(u,v) for u in range(n) for v in range(u+1,n) if (u,v) not in E]
        add=rng.sample(oldnon,2)
        for u,v in drop:
            if A.has_edge(u,v):A.remove_edge(u,v)
            elif B.has_edge(u,v):B.remove_edge(u,v)
            else:raise AssertionError("lost original placed edge")
        required=(E-{tuple(sorted(e)) for e in drop})|set(add)
        initial={tuple(sorted(e)) for e in A.edges()}|{tuple(sorted(e)) for e in B.edges()}
        todo=sorted(required-initial)
        assert len(required)==len(E) and len(initial)+len(todo)==len(required)
        missing=single_transfer_repair(A,B,todo,deadline,rng,maximum=12)
        have={tuple(sorted(e)) for e in A.edges()}|{tuple(sorted(e)) for e in B.edges()}
        assert not(set(map(tuple,A.edges()))&set(map(tuple,B.edges()))) or not any(A.has_edge(*e) for e in B.edges())
        assert have.isdisjoint({tuple(sorted(e)) for e in missing})
        assert have|{tuple(sorted(e)) for e in missing}==required
        item={"source_row":idx,"n":n,"m":len(required),"old_edges_deleted":[list(e) for e in sorted(map(tuple,drop))],
              "original_nonedges_added":[list(e) for e in sorted(add)],
              "still_unplaced":len(missing),"status":"PARTIAL_LAYERS_NOT_NEGATIVE"}
        if not missing:
            rot=check_split(n,required,A,B)
            C=graph(n,required)
            cols=nx.coloring.greedy_color(C,strategy="saturation_largest_first")
            item.update(status="COMPLETE_PLANAR_SPLIT_PROVISIONAL_CHROMATIC",
                        verified_greedy_k=len(set(cols.values())),
                        E1=[list(e) for e in sorted(A.edges())],
                        E2=[list(e) for e in sorted(B.edges())],
                        coloring=[cols[i] for i in range(n)],layers=rot)
        out.append(item)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--lane",choices=["multi","pair"],required=True)
    ap.add_argument("--seed",type=int,required=True);ap.add_argument("--seconds",type=int,default=250)
    args=ap.parse_args()
    assert args.seconds==250 and args.seed==(13013 if args.lane=="multi" else 13113)
    smoke=json.loads(Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
    assert smoke["chromatic_cnf_byte_matches"]==271 and smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    env=json.loads(Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
    files=["tools/s013_constructive.py","campaigns/CAM-0016.md",".github/workflows/s013-constructive.yml",
           "tools/s012_swap_audit.py","tools/s011_positive_search.py","tools/check_layers.py",
           "tools/check_rotation.py","validation/S003/survivors_alpha_ge3.json"]
    outdir=Path("artifacts/tmp/S013");outdir.mkdir(parents=True,exist_ok=True)
    rng=random.Random(args.seed);start=time.monotonic(); deadline=start+args.seconds
    report={"campaign":"CAM-0016","lane":args.lane,"scope":"POSITIVE_HEURISTICS_NO_EXHAUSTIVE_NEGATIVE",
            "seed":args.seed,"seconds_cap":args.seconds,"sha256":{f:sha(f) for f in files},
            "native_sha256":env["native_sha256"],"smoke":"PASS_SAME_JOB_271_AND_K9_FRESH",
            "python":sys.version,"platform":platform.platform(),"status":"STARTED"}
    target=outdir/(args.lane+".json");target.write_text(json.dumps(report,indent=2))
    if args.lane=="multi":
        corpus=json.loads(Path("validation/S003/survivors_alpha_ge3.json").read_text())
        records=multi(corpus,rng,deadline)
        report.update(attempted=len(records),min_missing=min((z["still_unplaced"] for z in records),default=None),
                      completed=sum(z["still_unplaced"]==0 for z in records),records=records)
    else:
        records=[];best=None
        for i in range(80):
            if time.monotonic()>=deadline-8:break
            z=pair(17,rng)
            records.append({"iteration":i,"m1":z["m1"],"m2":z["m2"],"m":z["m"],"greedy_k":z["greedy_k"]})
            if best is None or (z["greedy_k"],z["m"])>(best["greedy_k"],best["m"]):best=z
        report.update(attempted=len(records),records=records,best=best)
    report["status"]="COMPLETED_POSITIVE_ONLY"
    report["elapsed_seconds"]=round(time.monotonic()-start,3)
    target.write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report.get(k) for k in ("lane","status","attempted","min_missing","completed","elapsed_seconds")}))
if __name__=="__main__":main()
