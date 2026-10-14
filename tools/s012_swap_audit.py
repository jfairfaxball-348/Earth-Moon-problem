#!/usr/bin/env python3
"""S012 CAM-0015: all single-edge chromatic-restoring swaps, six frozen edge-critical blowups.
Positive 9-colouring witnesses only; no negative SAT/planarity oracle.
"""
import gzip, hashlib, json, os, sys, time
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
TARGETS=[2,55,59,61,199,200]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def expand(row):
    code,w=row[:2]
    data=[ord(c)-63 for c in code]
    assert data[0]==len(w)
    bits=[(b>>shift)&1 for b in data[1:] for shift in (5,4,3,2,1,0)]
    base=set()
    k=0
    for j in range(1,len(w)):
        for i in range(j):
            if bits[k]: base.add((i,j))
            k+=1
    bags=[i for i,weight in enumerate(w) for _ in range(weight)]
    E={(i,j) for i in range(len(bags)) for j in range(i+1,len(bags))
       if bags[i]==bags[j] or (min(bags[i],bags[j]),max(bags[i],bags[j])) in base}
    return bags, E
def run():
    start=time.monotonic()
    output=Path("artifacts/tmp/S012")
    output.mkdir(parents=True,exist_ok=True)
    smoke=json.loads(Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271 and smoke["chromatic_cnf_byte_matches"]==271
    assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    corpus=json.loads(Path("validation/S003/survivors_alpha_ge3.json").read_text())
    with gzip.open("validation/S011/edge_critical_witnesses.json.gz","rt") as f: archive=json.load(f)
    assert archive["campaign"]=="CAM-0014"
    byid={z["index"]:z for z in archive["rows"]}
    assert sorted(byid)==TARGETS
    env=json.loads(Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
    files=["tools/s012_swap_audit.py","tools/s012_swap_check.py","campaigns/CAM-0015.md",".github/workflows/s012-swap-audit.yml",
      "validation/S011/edge_critical_witnesses.json.gz","validation/S003/survivors_alpha_ge3.json"]
    results=[]
    total=0
    for idx in TARGETS:
        bags,edge_set=expand(corpus[idx])
        n=len(bags)
        edges=sorted(edge_set)
        nonedges=[(u,v) for u in range(n) for v in range(u+1,n) if (u,v) not in edge_set]
        witness={tuple(w["edge"]):w["colors"] for w in byid[idx]["witnesses"]}
        assert len(witness)==len(edges)==byid[idx]["m"]
        stats=Counter()
        for e in edges:
            col=witness[e]
            assert len(col)==n and all(isinstance(c,int) and 0<=c<9 for c in col)
            assert all(col[u]!=col[v] for u,v in edges if (u,v)!=e)
            for f in nonedges:
                stats["all_pairs"]+=1
                colors=col
                if col[f[0]]==col[f[1]]:
                    eligible=[z for z in f if bags[z] not in (bags[e[0]],bags[e[1]])]
                    assert eligible, (idx,e,f)
                    z=eligible[0]
                    alt=next(t for t in range(n) if t!=z and bags[t]==bags[z] and col[t]!=col[z])
                    colors=col.copy()
                    colors[z],colors[alt]=colors[alt],colors[z]
                    stats["recoloured_pairs"]+=1
                else: stats["already_separated"]+=1
                assert colors[f[0]]!=colors[f[1]]
                assert all(colors[u]!=colors[v] for u,v in edges if (u,v)!=e)
        assert stats["all_pairs"]==len(edges)*len(nonedges)
        total+=stats["all_pairs"]
        results.append({"row":idx,"n":n,"m":len(edges),"nonedges":len(nonedges),**stats,
            "status":"ALL_SWAP_PAIRS_POSITIVE_NINE_COLOUR_WITNESS_BY_BAG_PERMUTATION"})
    result={"campaign":"CAM-0015","scope":"six fixed labelled clique blowups only",
       "verdict":"PRODUCER_COMPLETE_PENDING_INDEPENDENT_CHECK","rows":results,"total_swap_pairs":total,
       "input_sha256":{p:sha(p) for p in files},"native_sha256":env["native_sha256"],
       "same_job_smoke":"PASS_271_OF_271_PLUS_K9_PLUS_FRESH_K9","elapsed_seconds":round(time.monotonic()-start,3)}
    (output/"swap_audit.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2),flush=True)
if __name__=="__main__": run()
