#!/usr/bin/env python3
"""S019: exact neighbourhood reconfiguration of ORIGINAL row148, then widening.
All learned clauses are checked Kuratowski obstructions on the unmodified graph.
Constrained neighbourhood UNSAT is NOT a negative graph certificate.
"""
import gzip,hashlib,itertools,json,os,pathlib,random,resource,sys,time,traceback
import networkx as nx
from pysat.solvers import Cadical153
from pysat.card import CardEnc,EncType
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup
from biplanar_cegar import is_kuratowski_subdivision
from s015_recheck_219 import check_complete

ROW=148;RNG=random.Random(190148)
O=ROOT/"artifacts/tmp/S019";O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def write(p,v):
    tmp=pathlib.Path(str(p)+".tmp");tmp.write_text(json.dumps(v,indent=2,sort_keys=True));tmp.replace(p)
def norm(e):return tuple(sorted(e))
def planar(ed):return nx.check_planarity(nx.Graph(ed),counterexample=False)[0]
smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271 and smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
row=json.loads((ROOT/"validation/S003/survivors_alpha_ge3.json").read_text())[ROW]
edges,bags=blowup(row[0],row[1]);E=set(edges);n=sum(row[1]);m=len(edges)
assert (n,m)==(25,131) and len(E)==m
edgefile=O/"row148.edges";edgefile.write_text("".join("%d %d\n"%e for e in edges))
assert sha(edgefile)=="4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598"
original=ROOT/"validation/S018/row148_best_partial.json"
data=json.loads(original.read_text())
def validate(d):
    a=set(map(norm,d["E1"]));b=set(map(norm,d["E2"]));u=set(map(norm,d["unplaced"]))
    assert not (a&b or a&u or b&u) and a|b|u==E
    assert planar(a) and planar(b)
    return len(u)
assert validate(data)==6
old=ROOT/"validation/S018/row148_lemmas.json.gz"
with gzip.open(old,"rt") as fh:oldcuts=json.load(fh)
assert len(oldcuts)==19480
cuts=[];keys=set()
def addcut(k):
    t=tuple(sorted(map(norm,k)))
    if t in keys:return False
    assert set(t)<=E and is_kuratowski_subdivision(t)
    keys.add(t);cuts.append(t)
    return True
for z in oldcuts:addcut(z)
assert len(cuts)==19480
started=time.monotonic()
log={"session":"S019","row":ROW,"edge_sha256":sha(edgefile),
"old_partial_sha256":sha(original),"old_cut_archive_sha256":sha(old),
"loaded_checked_cuts":len(cuts),"run_status":"SEARCHING",
"attempts":[],"best_unplaced":6,"full_positive":False,"negative_proof_checked":False,
"smoke":"PASS_271_271_K9","method":"exact-local-reconfiguration-expanding-to-full"}
def persist():
    log["elapsed_s"]=round(time.monotonic()-started,1)
    log["maxrss_mib"]=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)
    write(O/"RESULT.json",log)
def cutsave():
    with gzip.open(O/"row148_all_checked_cuts.json.gz","wt",compresslevel=5) as fh:
        json.dump([[list(e) for e in k] for k in cuts],fh,separators=(",",":"))
persist()
def success(a,b,origin):
    global data
    d={"E1":[list(e) for e in sorted(a)],"E2":[list(e) for e in sorted(b)],"unplaced":[]}
    assert validate(d)==0
    write(O/"row148_verified_split.json",{"n":n,"E1":d["E1"],"E2":d["E2"]})
    colours=json.loads((ROOT/"validation/S004/chi10_results.json").read_text())
    check_complete(ROW,n,edges,nx.Graph(a),nx.Graph(b),colours[ROW]["ten_colouring"],O/"positive.json")
    log["full_positive"]=True;log["run_status"]="POSITIVE_SPLIT_CERTIFIED_WITH_FULL_SAME_JOB_SMOKE"
    log["positive_origin"]=origin;log["best_unplaced"]=0;persist()

# Generate necessary edge-count inequalities on full bag unions. They are
# valid for each planar induced layer (|E_i(U)| <= 3|U|-6).
subsets=[]
for mask in range(1,1<<len(bags)):
    U=set(v for i,bag in enumerate(bags) if mask>>i&1 for v in bag)
    if len(U)<3:continue
    es=[e for e in edges if e[0] in U and e[1] in U]
    cap=3*len(U)-6
    if len(es)>2*cap:
        log["run_status"]="ANALYTIC_NONBIPLANAR_SUBSET";log["subset_vertices"]=sorted(U)
        log["subset_edges"]=len(es);log["subset_cap"]=2*cap;persist()
        print("PROVEN_DENSITY_OBSTRUCTION",log,flush=True);sys.exit(0)
    if len(es)>cap+2:
        subsets.append((2*cap-len(es),len(U),tuple(es),cap,sorted(U)))
subsets.sort()
# Finite constraints, sorted by tightest combined-layer slack.
subsets=subsets[:24]
log["bag_union_density_constraints"]=len(subsets)

def neighbourhood(scope,seed,max_seconds):
    global data
    r=random.Random(seed)
    A=set(map(norm,data["E1"]));B=set(map(norm,data["E2"]));M=set(map(norm,data["unplaced"]))
    hot=set(v for e in M for v in e)
    chosen=list(M)
    placed=list(A|B)
    hotplaced=[e for e in placed if e[0] in hot or e[1] in hot]
    r.shuffle(hotplaced)
    chosen+=hotplaced[:min(len(hotplaced),(scope-len(M))*2//3)]
    remaining=list((A|B)-set(chosen));r.shuffle(remaining)
    chosen+=remaining[:max(0,scope-len(chosen))]
    F=sorted(set(chosen));FS=set(F)
    fA=A-FS;fB=B-FS
    assert len(fA)+len(fB)+len(F)==m and len(F)<=scope
    vars={e:i+1 for i,e in enumerate(F)}
    solver=Cadical153();nv=len(F)
    def countbound(ll,lo,hi):
        nonlocal nv
        if hi<0 or lo>len(ll):
            solver.add_clause([]);return
        if hi<len(ll):
            z=CardEnc.atmost(lits=ll,bound=hi,top_id=nv,encoding=EncType.seqcounter)
            nv=max(nv,z.nv);solver.append_formula(z.clauses)
        if lo>0:
            z=CardEnc.atleast(lits=ll,bound=lo,top_id=nv,encoding=EncType.seqcounter)
            nv=max(nv,z.nv);solver.append_formula(z.clauses)
    countbound(list(vars.values()),62-len(fA),69-len(fA))
    for _,_,es,cap,_ in subsets:
        ll=[vars[e] for e in es if e in FS]
        f1=sum(e in fA for e in es)
        countbound(ll,len(es)-f1-cap,cap-f1)
    loaded=0
    def insert(k):
        nonlocal loaded
        # For each planar layer a Kuratowski edge set cannot be monochromatic.
        # Existing fixed opposite-layer edge makes a clause redundant.
        # A layer with no free member causes an exact LOCAL contradiction.
        if not any(e in fB for e in k):
            solver.add_clause([-vars[e] for e in k if e in FS])
        if not any(e in fA for e in k):
            solver.add_clause([vars[e] for e in k if e in FS])
        loaded+=1
    for k in cuts:insert(k)
    state={"scope":scope,"free":len(F),"seed":seed,"initial_lemmas":len(cuts),
           "status":"RUNNING","iterations":0,"new_obstructions":0}
    local_start=time.monotonic()
    try:
        while time.monotonic()-local_start<max_seconds:
            state["iterations"]+=1
            solver.conf_budget(60000)
            feasible=solver.solve_limited(expect_interrupt=True)
            if feasible is None:
                state["status"]="CONFLICT_BUDGET_EXCEEDED";break
            if feasible is False:
                state["status"]="LOCAL_UNSAT_NOT_GRAPH_NEGATIVE"
                if len(F)==m:
                    # All edges were free. All constraints are original-source
                    # necessary constraints; save formula for independent
                    # native UNSAT proof and source-to-encoding audit.
                    log["full_scope_unsat_observed"]=True
                    # Output exact SAT clauses tracked below in future run.
                break
            model={x for x in solver.get_model() if x>0}
            a=fA|{e for e in F if vars[e] in model}
            b=fB|{e for e in F if vars[e] not in model}
            assert a|b==E and not a&b
            pA=planar(a);pB=planar(b)
            if pA and pB:
                success(a,b,"exact-local-SAT-"+str(scope))
                state["status"]="POSITIVE_WITNESS";break
            progress=0
            for target,ed in [(0,a),(1,b)]:
                if (pA if target==0 else pB):continue
                G=nx.Graph(ed)
                # Multiple distinct Kuratowski subgraphs from this assignment.
                for j in range(8):
                    ok,sub=nx.check_planarity(G,counterexample=True)
                    if ok:break
                    k=tuple(sorted(map(norm,sub.edges())))
                    if addcut(k):
                        insert(k);state["new_obstructions"]+=1;progress+=1
                    G.remove_edge(*r.choice(k))
            if progress==0:
                state["status"]="STALLED_NO_NEW_SOUND_CUTS";break
            if state["iterations"]%25==0:
                state["elapsed_s"]=round(time.monotonic()-local_start,1)
                log["current"]=state;persist();cutsave()
                print("S019_PROGRESS",json.dumps(state),flush=True)
        else:state["status"]="TIME_CAPPED"
    finally:
        state["elapsed_s"]=round(time.monotonic()-local_start,1)
        solver.delete()
    return state

try:
    # Several restricted exact repairs before releasing all original edges.
    # This is strictly sequential: only original row148, one solver process.
    budgets=[(24,75),(36,100),(48,130),(64,140),(90,180),(110,200),(131,430)]
    for i,(scope,cap) in enumerate(budgets):
        if log["full_positive"]:break
        if time.monotonic()-started>1380:break
        s=neighbourhood(scope,190148+i*97,cap)
        log["attempts"].append(s);persist();cutsave()
        print("S019_ATTEMPT",json.dumps(s),flush=True)
    if not log["full_positive"]:
        log["run_status"]="UNKNOWN_FULL_CERTIFICATE_NOT_OBTAINED"
    persist();cutsave()
except Exception as e:
    log["run_status"]="ERROR";log["error"]=repr(e);log["traceback"]=traceback.format_exc()[-5000:]
    persist();cutsave();raise
finally:
    print("S019_FINAL",json.dumps({"status":log["run_status"],"attempts":log["attempts"],
          "all_sound_cuts":len(cuts),"maxrss_mib":log.get("maxrss_mib")}),flush=True)
