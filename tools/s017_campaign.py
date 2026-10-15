#!/usr/bin/env python3
"""CAM-0019 S017 preregistered original 219 subset, finite bounds only."""
import hashlib,json,os,pathlib,random,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup
from s017_density_cegar import projected_truth_table
from s017_rotation_repair import repair
OUT=ROOT/"artifacts/tmp/S017"
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
smoke=json.loads(pathlib.Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
assert smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
env=json.loads(pathlib.Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
pool=json.loads(pathlib.Path("validation/S010/SUMMARY.json").read_text())
unknown=pool["remaining_unknown_indices"]; excluded=pool["excluded_indices"]
assert len(unknown)==219 and len(excluded)==52 and sorted(unknown+excluded)==list(range(271))
corpus=json.loads(pathlib.Path("validation/S003/survivors_alpha_ge3.json").read_text())
colours=json.loads(pathlib.Path("validation/S004/chi10_results.json").read_text())
exact=[(156,80,17156),(3,70,17003),(9,70,17009),(173,70,17173),(148,70,17148)]
positive=[(148,171481,35),(156,171561,25),(3,170031,25),(9,170091,25),(173,171731,25)]
source_paths=["tools/s017_density_cegar.py","tools/s017_rotation_repair.py",
"tools/s017_campaign.py","tools/biplanar_cegar.py","tools/check_layers.py",
"tools/check_rotation.py","validation/S003/survivors_alpha_ge3.json",
"validation/S010/SUMMARY.json","validation/S004/chi10_results.json",
"campaigns/CAM-0019.md",".github/workflows/s017-density-originals.yml"]
log={"session":"S017","campaign":"CAM-0019","status":"STARTED",
"science":"new necessary Euler-cardinality SAT and positive backtracking",
"native_sha256":env["native_sha256"],"sources_sha256":{p:sha(p) for p in source_paths},
"cold_smoke":{"verdict":"PASS","rows":271,"cnf_equal":271,"k9_retained":True,"k9_fresh":True},
"inherited_nonbiplanar":excluded,"canonical_unknown":unknown,
"row_status":{str(i):"NOT_RUN" for i in unknown},"exact":[],"positive":[],
"solver_negative_certificates_accepted":0,"complete_splits_independently_checked":0}
def save():
    (OUT/"result.json").write_text(json.dumps(log,indent=2))
save()
log["truth_table_projected_tests"]=projected_truth_table()
assert log["truth_table_projected_tests"]>0
log["encoding_status"]="PASS_ARITHMETIC_PROJECTION_m1_to_5"
save()
def original(i):
    es,_=blowup(corpus[i][0],corpus[i][1])
    n=sum(corpus[i][1])
    assert len(es)==len(set(es))
    return n,es
witness=False
for row,cap,seed in exact:
    n,es=original(row)
    base=OUT/("row"+str(row))
    edgefile=pathlib.Path(str(base)+".edges")
    edgefile.write_text("".join(f"{u} {v}\n" for u,v in es))
    rec={"row":row,"n":n,"m":len(es),"cap_seconds":cap,
         "seed":seed,"edgefile_sha256":sha(edgefile),"limit":24}
    cmd=[sys.executable,"tools/s017_density_cegar.py",str(edgefile),str(base),
         str(cap),str(seed),"24"]
    started=time.monotonic()
    try:
        run=subprocess.run(cmd,capture_output=True,text=True,timeout=cap+25)
        rec.update({"returncode":run.returncode,"stdout":run.stdout[-2500:],
                    "stderr":run.stderr[-1200:]})
        if run.returncode==0:
            try:rec.update(json.loads(run.stdout.splitlines()[-1]))
            except (ValueError,IndexError):pass
        split=pathlib.Path(str(base)+".split.json")
        if split.exists():
            verified=subprocess.run([sys.executable,"tools/check_layers.py",
                str(edgefile),str(split)],capture_output=True,text=True,timeout=25)
            rec["rotation_check"]={"exit_code":verified.returncode,
                "stdout":verified.stdout[-500:],"stderr":verified.stderr[-500:]}
            if verified.returncode==0:
                rec["status"]="PROVISIONAL_SPLIT_COLD_CHI10_CHECK_REQUIRED"
                witness=True
        if not witness:
            rec["status"]="CAPPED" if rec.get("verdict")=="UNKNOWN" else "ATTEMPTED_STILL_UNKNOWN"
        # UNSAT is NOT a certified negative until a separately checked solver
        # proof plus independent formula soundness audit; never promote here.
    except subprocess.TimeoutExpired:
        rec["status"]="CAPPED";rec["error"]="outer cap reached"
    except Exception as e:
        rec["status"]="ATTEMPTED_STILL_UNKNOWN";rec["error"]=repr(e)
    rec["elapsed_seconds"]=round(time.monotonic()-started,2)
    log["exact"].append(rec)
    log["row_status"][str(row)]=rec["status"]
    log["status"]="EXACT_"+str(row)
    save()
    if witness:break
if not witness:
    for row,seed,seconds in positive:
        n,es=original(row)
        t=time.monotonic()
        try:
            rec=repair(n,es,colours[row]["ten_colouring"],row,seed,
                    t+seconds,OUT/"search.json")
            rec["cap_seconds"]=seconds
            if rec["status"].startswith("PROVISIONAL_SPLIT"):
                witness=True
            else:
                if log["row_status"][str(row)]=="NOT_RUN":
                    log["row_status"][str(row)]="ATTEMPTED_STILL_UNKNOWN"
        except Exception as e:
            rec={"row":row,"status":"ATTEMPTED_STILL_UNKNOWN",
                 "error":repr(e),"traceback":traceback.format_exc()[-2000:]}
            if log["row_status"][str(row)]=="NOT_RUN":
                log["row_status"][str(row)]="ATTEMPTED_STILL_UNKNOWN"
        rec["elapsed_seconds"]=round(time.monotonic()-t,2)
        log["positive"].append(rec)
        log["status"]="POSITIVE_"+str(row);save()
        if witness:break
log["partition"]={k:sorted(int(i) for i,v in log["row_status"].items()
                          if v==k) for k in sorted(set(log["row_status"].values()))}
assert sum(map(len,log["partition"].values()))==219
log["status"]="FINISHED"
log["verdict"]="PROVISIONAL_ONLY_COLD_CHROMATIC_REQUIRED" if witness else "NO_CERTIFIED_NEW_POSITIVE_OR_NEGATIVE"
save()
print(json.dumps({"verdict":log["verdict"],"counts":{k:len(v) for k,v in log["partition"].items()},
"best_positive":[(p.get("row"),p.get("best_missing")) for p in log["positive"]]},indent=2))
