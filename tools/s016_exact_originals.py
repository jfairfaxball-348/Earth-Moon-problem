#!/usr/bin/env python3
"""S016 CAM-0018 bounded original-graph searches; no negative proof without accepted DRAT."""
import hashlib, json, os, pathlib, random, subprocess, sys, time, traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT/"tools"))
from blowup_graph import blowup
from s015_recheck_219 import build_trial, double_ejection, check_complete
TOP=[156,3,9,173,148,167,222,223,61,234,238]
EXACT=[(156,125,16156),(3,85,16003),(9,85,16009),(173,85,16173)]
SEARCH_TIME_PER_ROW=6
OUT=ROOT/"artifacts/tmp/S016"
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
smoke=json.loads(pathlib.Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271 and smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
env=json.loads(pathlib.Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
corpus=json.loads(pathlib.Path("validation/S003/survivors_alpha_ge3.json").read_text())
summary=json.loads(pathlib.Path("validation/S010/SUMMARY.json").read_text())
colours=json.loads(pathlib.Path("validation/S004/chi10_results.json").read_text())
unk=summary["remaining_unknown_indices"]
excluded=summary["excluded_indices"]
assert len(unk)==219 and len(excluded)==52 and sorted(unk+excluded)==list(range(271))
assert len(corpus)==len(colours)==271 and set(TOP)<=set(unk)
sources=["validation/S003/survivors_alpha_ge3.json","validation/S010/SUMMARY.json","validation/S004/chi10_results.json","tools/blowup_graph.py","tools/biplanar_cegar.py","tools/check_layers.py","tools/check_rotation.py","tools/s016_exact_originals.py","campaigns/CAM-0018.md",".github/workflows/s016-exact.yml"]
log={"campaign":"CAM-0018","session":"S016","scope":"ORIGINAL_219_ONLY_POSITIVE_OR_FULL_CERTIFIED_NEGATIVE","source_sha256":{p:sha(p) for p in sources},"native_sha256":env["native_sha256"],"smoke":smoke,"inherited_52":excluded,"canonical_219":unk,"row_status":{str(i):{"status":"NOT_RUN"} for i in unk},"exact":[],"positive":[],"stage":"setup_pass","start_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
def save():
    (OUT/"result.json").write_text(json.dumps(log,indent=2))
save()
def original(i):
    edges,_=blowup(corpus[i][0],corpus[i][1])
    n=sum(corpus[i][1])
    assert len(edges)==len(set(edges)) and all(0<=u<v<n for u,v in edges)
    return n,edges
for i,cap,seed in EXACT:
    n,edges=original(i)
    name=OUT/("row"+str(i))
    edgefile=pathlib.Path(str(name)+".edges")
    edgefile.write_text("".join(f"{u} {v}\n" for u,v in edges))
    cmd=[sys.executable,"tools/biplanar_cegar.py",str(edgefile),str(name),str(cap),"--seed",str(seed),"--limit","24"]
    rec={"row":i,"n":n,"m":len(edges),"seed":seed,"cap_seconds":cap,"limit":24,"edgefile_sha256":sha(edgefile),"cmd":cmd}
    t=time.monotonic()
    try:
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=cap+15)
        rec.update({"returncode":proc.returncode,"stdout":proc.stdout[-1500:],"stderr":proc.stderr[-1500:]})
        if proc.returncode==0:
            for line in reversed(proc.stdout.splitlines()):
                try:
                    data=json.loads(line)
                    if isinstance(data,dict) and "verdict" in data:
                        rec.update(data);break
                except json.JSONDecodeError:pass
        if pathlib.Path(str(name)+".split.json").exists():
            proof=subprocess.run([sys.executable,"tools/check_layers.py",str(edgefile),str(name)+".split.json"],capture_output=True,text=True,timeout=30)
            rec["independent_split_verification"]={"exit_code":proof.returncode,"stdout":proof.stdout[-1000:],"stderr":proof.stderr[-1000:]}
            if proof.returncode==0:
                rec["status"]="PROVISIONAL_BIPLANAR_NEEDS_CHROMATIC_RECHECK"
                log["row_status"][str(i)]={"status":rec["status"],"exact":rec}
                log["exact"].append(rec);save()
                break
        # Even an UNSAT output is not a negative certificate absent independently checked proof.
        rec["status"]="CAPPED" if rec.get("verdict")=="UNKNOWN" or rec.get("returncode")==-15 else "ATTEMPTED_STILL_UNKNOWN"
    except subprocess.TimeoutExpired as e:
        rec["status"]="CAPPED";rec["exception"]="outer time cap"
    except Exception as e:
        rec["status"]="ATTEMPTED_STILL_UNKNOWN";rec["exception"]=repr(e)
    rec["elapsed_seconds"]=round(time.monotonic()-t,2)
    # CNF+lemmas are diagnostic ONLY; do not copy huge files.
    log["row_status"][str(i)]={"status":rec["status"],"exact":rec}
    log["exact"].append(rec)
    log["stage"]="exact_"+str(i);save()
if not any(x["status"]=="PROVISIONAL_BIPLANAR_NEEDS_CHROMATIC_RECHECK" for x in log["row_status"].values()):
    for i in TOP:
        n,edges=original(i)
        t=time.monotonic()
        best=len(edges);best_seed=None
        record={"row":i,"n":n,"m":len(edges),"new_seeds":[],"baseline_seeds":[],"search_seconds_cap":SEARCH_TIME_PER_ROW}
        for mode in range(3):
            seed=1601600+i*181+mode*100003
            rng=random.Random(seed)
            a,b,missing=build_trial(n,edges,rng,mode)
            record["new_seeds"].append(seed)
            a,b,missing=double_ejection(a,b,missing,rng,min(time.monotonic()+SEARCH_TIME_PER_ROW/3,t+SEARCH_TIME_PER_ROW))
            if len(missing)<best:
                best=len(missing);best_seed=seed
            if not missing:
                check_complete(i,n,edges,a,b,colours[i]["ten_colouring"],OUT/"search.json")
                record["provisional_split"]=True
                break
            if time.monotonic()>t+SEARCH_TIME_PER_ROW:break
        record["best_missing"]=best
        record["best_seed"]=best_seed
        record["seconds"]=round(time.monotonic()-t,2)
        record["status"]="PROVISIONAL_BIPLANAR_NEEDS_CHROMATIC_RECHECK" if record.get("provisional_split") else "ATTEMPTED_STILL_UNKNOWN"
        if log["row_status"][str(i)]["status"]=="NOT_RUN":
            log["row_status"][str(i)]={"status":record["status"]}
        elif record.get("provisional_split"):
            log["row_status"][str(i)]={"status":record["status"]}
        log["positive"].append(record)
        log["stage"]="positive_"+str(i);save()
log["stage"]="finished"
log["verdict"]="PROVISIONAL_SPLIT_REQUIRES_FRESH_INDEPENDENT_CERTIFICATE" if any(x["status"]=="PROVISIONAL_BIPLANAR_NEEDS_CHROMATIC_RECHECK" for x in log["row_status"].values()) else "NO_CHECKED_NEW_POSITIVE_OR_NEGATIVE"
log["partition"]={k:sorted(int(i) for i,v in log["row_status"].items() if v["status"]==k) for k in sorted(set(v["status"] for v in log["row_status"].values()))}
assert sum(map(len,log["partition"].values()))==219
save()
print(json.dumps({"verdict":log["verdict"],"partition_counts":{k:len(v) for k,v in log["partition"].items()},"best_positive":sorted([(r["best_missing"],r["row"]) for r in log["positive"]])[:11]},indent=2),flush=True)
