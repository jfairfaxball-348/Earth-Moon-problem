#!/usr/bin/env python3
"""S020: original row148 obstruction-guided planar insertion + global/induced Euler CEGAR.

This is a bounded computation, NOT a decision if it caps. Every emitted SAT must
pass a separate exact-planarity checker; UNSAT requires a complete checked proof.
Checkpointed Kuratowski lemmas are necessary clauses of the original graph,
and may be replayed in a later run. Do not run on different graph IDs.
"""
import gzip
import hashlib
import json
import os
import pathlib
import random
import resource
import subprocess
import sys
import time
import traceback

import networkx as nx
from pysat.solvers import Cadical153

ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup
from biplanar_cegar import Cegar, is_kuratowski_subdivision
from s015_recheck_219 import build_trial, double_ejection, check_complete

O=ROOT/"artifacts/tmp/S020"
O.mkdir(parents=True,exist_ok=True)
SEED=191481
ROW=148
SOURCES=["tools/s020_row148_embedding.py","tools/biplanar_cegar.py",
 "tools/s015_recheck_219.py","tools/check_layers.py",
 "validation/S003/survivors_alpha_ge3.json","validation/S004/chi10_results.json",
 "validation/S010/SUMMARY.json","campaigns/CAM-0022.md",
 ".github/workflows/s020-row148-embedding.yml"]
def digest(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save_json(path,obj):
    tmp=pathlib.Path(str(path)+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True))
    tmp.replace(path)
def memory():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)
def planar(g):
    return nx.check_planarity(g)[0]
def canon(e):
    return tuple(sorted(e))
def pack(a,b,missing):
    return {"E1":sorted(map(list,map(canon,a.edges()))),
            "E2":sorted(map(list,map(canon,b.edges()))),
            "unplaced":sorted(map(list,missing))}
def verify_partial(data,edges,n):
    a={canon(e) for e in data["E1"]}
    b={canon(e) for e in data["E2"]}
    m={canon(e) for e in data["unplaced"]}
    assert not a&b and not a&m and not b&m
    assert a|b|m==set(edges)
    assert planar(nx.Graph(data["E1"])) and planar(nx.Graph(data["E2"]))
    return len(m)
smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
assert smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
pool=json.loads((ROOT/"validation/S010/SUMMARY.json").read_text())
unknown=pool["remaining_unknown_indices"]; excluded=pool["excluded_indices"]
assert ROW in unknown and len(unknown)==219 and len(excluded)==52
assert sorted(unknown+excluded)==list(range(271))
corpus=json.loads((ROOT/"validation/S003/survivors_alpha_ge3.json").read_text())
colours=json.loads((ROOT/"validation/S004/chi10_results.json").read_text())
edges,_=blowup(corpus[ROW][0],corpus[ROW][1])
n=sum(corpus[ROW][1]);m=len(edges)
assert (n,m)==(25,131) and len(set(edges))==m
edgefile=O/"row148.edges"
edgefile.write_text("".join("%d %d\n"%e for e in edges))
assert digest(edgefile)=="4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598"
env=json.loads((ROOT/"artifacts/tmp/native/ENVIRONMENT.json").read_text())
log={
 "session":"S020","campaign":"CAM-0022","active_original_row":ROW,
 "source_sha256":{p:digest(p) for p in SOURCES},
 "edgefile_sha256":digest(edgefile),"n":n,"m":m,
 "native_sha256":env["native_sha256"],
 "same_job_smoke":"PASS_271_271_CNF_DRAT_AND_K9_OLD_FRESH",
 "queue":{str(i):{"session":"NOT_RUN","cumulative":"BIPLANARITY_UNKNOWN"}
          for i in unknown},
 "inherited_52_certified_nonbiplanar":excluded,
 "positive":{"status":"NOT_RUN"}, "exact":{"status":"NOT_RUN"},
 "negative_proof_checked":False,"full_positive_verified":False,
 "stage":"ENTERED","status":"UNKNOWN"}
def save():
    log["peak_rss_mb"]=memory()
    save_json(O/"result.json",log)
save()

def complete(data,origin):
    verify_partial(data,edges,n)
    assert not data["unplaced"]
    split={"n":n,"E1":data["E1"],"E2":data["E2"]}
    save_json(O/"row148.split.json",split)
    check=subprocess.run([sys.executable,"tools/check_layers.py",str(edgefile),
        str(O/"row148.split.json")],capture_output=True,text=True,timeout=100)
    log["layer_independent_check"]={"returncode":check.returncode,
        "output":check.stdout[-800:],"stderr":check.stderr[-800:]}
    if check.returncode!=0:
        raise RuntimeError("independent rotation/planarity check failed")
    # Independently archived S004 colour DRATs just replayed for all 271
    # in this SAME runner; validate positive 10-colouring too.
    witness=check_complete(ROW,n,edges,nx.Graph(data["E1"]),nx.Graph(data["E2"]),
        colours[ROW]["ten_colouring"],O/"positive.json")
    log["positive"]["status"]="CERTIFIED_COMPLETE_ORIGINAL_SPLIT_SAME_JOB_CHROMATIC_SMOKE"
    log["positive"]["witness_origin"]=origin
    log["full_positive_verified"]=True
    log["queue"][str(ROW)]={"session":"CERTIFIED_BIPLANAR_WITNESS",
                            "cumulative":"CERTIFIED_BIPLANAR_WITNESS"}
    log["status"]="POSITIVE_CERTIFIED_SAME_JOB"
    save()
    return True

def positive_search(cap=330):
    rng=random.Random(SEED)
    t0=time.monotonic()
    best=None
    baseline=[]
    # Reconstruct registered S016 seed and its 10-missing partial, if reproducible.
    for seed in [1628388,1728391,1828394]:
        rr=random.Random(seed)
        a,b,missing=build_trial(n,edges,rr,mode=[1628388,1728391,1828394].index(seed))
        a,b,missing=double_ejection(a,b,missing,rr,time.monotonic()+1.8)
        data=pack(a,b,missing)
        best_count=verify_partial(data,edges,n)
        baseline.append({"seed":seed,"remaining":best_count})
        if best is None or best_count < len(best["unplaced"]):
            best=data
    # Best partial is kept as data (not solver internals), and always independently rechecked.
    old=ROOT/"validation/S018/row148_best_partial.json"
    if old.exists():
        try:
            prev=json.loads(old.read_text())
            if verify_partial(prev,edges,n)<len(best["unplaced"]):
                best=prev
        except Exception as ex:
            log["previous_checkpoint_rejected"]=repr(ex)
    log["positive"]={"status":"IN_PROGRESS","baseline":baseline,
        "best_missing":len(best["unplaced"]),"tries":0,
        "method":"repro_S016_plus_adaptive_LNS_planar_repacking"}
    save_json(O/"row148_best_partial.json",best)
    save()
    if not best["unplaced"]:
        return complete(best,"S016-replay")
    incumbent=best
    # Adaptive large-neighbourhood search: destroy a subset of *placed*
    # edges, then reinsert ALL removed edges and ALL previous missing edges,
    # without ever silently deleting a source edge.
    for trial in range(100000):
        if time.monotonic()-t0 >= cap: break
        data=incumbent if rng.random()<.75 else best
        a=nx.Graph();a.add_nodes_from(range(n));a.add_edges_from(data["E1"])
        b=nx.Graph();b.add_nodes_from(range(n));b.add_edges_from(data["E2"])
        missing=[canon(e) for e in data["unplaced"]]
        k=rng.choice([3,6,10,16,24,36,48,64,96])
        # Bias removal towards endpoints of currently unplaced source edges.
        hot=set(v for e in missing for v in e)
        allplaced=[(0,canon(e)) for e in a.edges()]+[(1,canon(e)) for e in b.edges()]
        hotplaced=[p for p in allplaced if p[1][0] in hot or p[1][1] in hot]
        chosen=[]
        if hotplaced and rng.random()<.75:
            chosen=rng.sample(hotplaced,min(k//2,len(hotplaced)))
        remaining=[p for p in allplaced if p not in chosen]
        chosen+=rng.sample(remaining,min(k-len(chosen),len(remaining)))
        for side,e in chosen:
            (a if side==0 else b).remove_edge(*e)
            missing.append(e)
        # Randomised candidate priorities; try both planar placements.
        rng.shuffle(missing)
        missing.sort(key=lambda e:-(sum(v in hot for v in e)+rng.random()*5))
        left=[]
        for e in missing:
            layers=[a,b] if rng.randrange(2) else [b,a]
            layers.sort(key=lambda g:g.number_of_edges() +rng.random()*8)
            inserted=False
            for g in layers:
                g.add_edge(*e)
                if planar(g):
                    inserted=True
                    break
                g.remove_edge(*e)
            if not inserted:left.append(e)
        rec=pack(a,b,left)
        rec_miss=verify_partial(rec,edges,n)
        log["positive"]["tries"]=trial+1
        if rec_miss<=len(incumbent["unplaced"]) or rng.random()<.04:
            incumbent=rec
        if rec_miss<len(best["unplaced"]):
            best=rec
            log["positive"]["best_missing"]=rec_miss
            log["positive"]["last_improvement_trial"]=trial+1
            save_json(O/"row148_best_partial.json",best);save()
            print("POSITIVE improvement",trial+1,rec_miss,flush=True)
        if not rec_miss:
            return complete(rec,"adaptive-large-neighbourhood-repack")
        if trial%100==0:
            log["positive"]["elapsed_seconds"]=round(time.monotonic()-t0,2)
            save()
    log["positive"]["status"]="CAPPED_STILL_UNKNOWN"
    log["positive"]["elapsed_seconds"]=round(time.monotonic()-t0,2)
    log["queue"][str(ROW)]["session"]="CAPPED"
    save_json(O/"row148_best_partial.json",best)
    save()
    return False


def guided_switch_search(cap=220, max_switches=7, node_cap=100000):
    """Independent partial-planar-search search tree (different from LNS).
    At a nonplanar insertion e, a displayed Kuratowski subdivision
    necessarily contains e (the pre-insertion layer is planar). To retain
    e, some old edge of the obstruction must leave this layer. Enumerate
    every such deletion; later put displaced edges on either side.
    Finite bounded tree is NOT an exhaustive global biplanarity verdict.
    """
    t=time.monotonic()
    partial=json.loads((ROOT/"validation/S019/row148_best_partial.json").read_text())
    remaining=verify_partial(partial,edges,n)
    assert remaining==6
    startA=nx.Graph();startA.add_nodes_from(range(n));startA.add_edges_from(partial["E1"])
    startB=nx.Graph();startB.add_nodes_from(range(n));startB.add_edges_from(partial["E2"])
    best=partial
    seen=set()
    stats={"status":"IN_PROGRESS","method":"kuratowski_guided_reversible_face_insertion",
        "initial_missing":remaining,"best_missing":remaining,
        "node_cap":node_cap,"cap_seconds":cap,"switch_budget":max_switches,
        "nodes":0,"repeated_states":0,"obstruction_branches":0,
        "nonplanar_insertion_tests":0}
    log["positive"]=stats;save()
    deadline=t+cap
    exhausted=False
    def dfs(a,b,pending,moves):
        nonlocal best,exhausted
        if time.monotonic()>=deadline or stats["nodes"]>=node_cap:
            exhausted=True;return False
        if not pending:
            return complete(pack(a,b,[]),"kuratowski-guided-face-insertion")
        state=(frozenset(map(canon,a.edges())),frozenset(map(canon,b.edges())))
        if state in seen:
            stats["repeated_states"]+=1;return False
        seen.add(state)
        stats["nodes"]+=1
        if len(pending)<len(best["unplaced"]):
            rec=pack(a,b,pending)
            assert verify_partial(rec,edges,n)==len(pending)
            best=rec;stats["best_missing"]=len(pending)
            save_json(O/"row148_best_partial.json",best)
            save()
        if stats["nodes"]%500==0:
            stats["elapsed_seconds"]=round(time.monotonic()-t,2)
            save()
        # Prefer a pending edge that can be embedded immediately.
        p=sorted(pending)
        candidates=[]
        for e in p:
            immediate=sum(planar(nx.Graph(list(g.edges())+[e])) for g in (a,b))
            candidates.append((0 if immediate else 1,immediate,e))
        _,_,e=min(candidates)
        rest=[f for f in p if f!=e]
        for side in sorted((0,1),key=lambda s:(a if s==0 else b).number_of_edges()):
            layer=a if side==0 else b
            trial=layer.copy();trial.add_edge(*e)
            isplanar,cert=nx.check_planarity(trial,counterexample=True)
            if isplanar:
                if side==0:
                    if dfs(trial,b,rest,moves):return True
                else:
                    if dfs(a,trial,rest,moves):return True
                continue
            stats["nonplanar_insertion_tests"]+=1
            if moves>=max_switches:continue
            kur={canon(f) for f in cert.edges()}
            assert e in kur, "a planar old layer cannot contain obstruction without inserted edge"
            # Every valid retention of e must break this known obstruction.
            for f in sorted(kur-{e}):
                if f not in layer.edges(): continue
                lower=layer.copy();lower.remove_edge(*f)
                stats["obstruction_branches"]+=1
                if side==0:
                    if dfs(lower,b,rest+[e,f],moves+1):return True
                else:
                    if dfs(a,lower,rest+[e,f],moves+1):return True
                if exhausted:return False
        return False
    try:
        found=dfs(startA,startB,[canon(e) for e in partial["unplaced"]],0)
    except Exception:
        stats["status"]="ERROR";save();raise
    if not found:
        stats["status"]="CAPPED_STILL_UNKNOWN" if exhausted else "LOCAL_SWITCH_BUDGET_EXHAUSTED_NOT_GLOBAL"
        log["queue"][str(ROW)]["session"]="CAPPED"
        log["positive_best_unplaced"]=len(best["unplaced"])
    stats["elapsed_seconds"]=round(time.monotonic()-t,2)
    save()
    return found

def add_induced_euler_constraints(c):
    """Proven necessary for every vertex-induced layer, NOT a sufficiency test.
    Each U of size>=3 has <=3|U|-6 planar edges. Sequential-counter
    auxiliary variables are disjoint between constraints, so each legal
    original-edge assignment extends to a satisfying auxiliary assignment.
    """
    from pysat.card import CardEnc, EncType
    g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(edges)
    subsets=set()
    rng=random.Random(2020148)
    def add(U):
        q=tuple(sorted(U))
        if 5<=len(q)<=20:subsets.add(q)
    for clique in nx.find_cliques(g):
        add(clique)
        for v in clique:add(set(clique)|{v})
    for v in range(n):
        add(set(g[v])|{v})
        for w in g[v]:add((set(g[v])&set(g[w]))|{v,w})
    # Deterministic dense-graph growth; augment candidates with several
    # different independently computed induced-subset families.
    for rep in range(900):
        x=rng.randrange(n)
        S={x}
        while len(S)<rng.randrange(7,20):
            others=[v for v in range(n) if v not in S]
            mx=max(sum(v in g[u] for u in S) for v in others)
            eligible=[v for v in others if sum(v in g[u] for u in S)>=mx-(rep%3)]
            S.add(rng.choice(eligible))
            if len(S)>=5:add(S)
    scored=[]
    for U in subsets:
        Uset=set(U)
        ids=[c.idx[e] for e in edges if e[0] in Uset and e[1] in Uset]
        bound=3*len(U)-6
        if len(ids)>2*bound:
            cert={"vertices":list(U),"original_edge_ids":ids,
                  "edges":len(ids),"two_layer_bound":2*bound}
            save_json(O/"density_obstruction.json",cert)
            raise RuntimeError("DENSITY_OBSTRUCTION_POTENTIAL_CERTIFICATE_VALIDATE_INDEPENDENTLY")
        if len(ids)>bound:
            scored.append((2*bound-len(ids),-len(ids),U,ids,bound))
    scored.sort()
    chosen=scored[:100]
    before=len(c.base);initial=c.nv
    records=[]
    for slack,negative,U,ids,bound in chosen:
        at1=CardEnc.atmost(lits=ids,bound=bound,top_id=c.nv,encoding=EncType.seqcounter)
        c.base.extend(at1.clauses);c.nv=at1.nv
        at2=CardEnc.atmost(lits=[-i for i in ids],bound=bound,
                           top_id=c.nv,encoding=EncType.seqcounter)
        c.base.extend(at2.clauses);c.nv=at2.nv
        records.append({"U":list(U),"edge_ids":ids,"bound":bound,
                        "original_edges":len(ids),"slack":slack})
    info={"candidate_subsets":len(subsets),"active_dense_subsets":len(scored),
          "encoded":len(records),"new_clauses":len(c.base)-before,
          "new_aux_variables":c.nv-initial,"records":records,
          "negative_encoding_sound":"necessary local Euler + independent existential sequential counters"}
    save_json(O/"LOCAL_EULER.json",info)
    log["local_euler"]={k:v for k,v in info.items() if k!="records"}
    save()

def exact_search(cap=610):
    # No lex, no layer swap, no auxiliary cardinality encoding: soundness
    # of the negative formula depends ONLY on graph edge partition and
    # checked Kuratowski obstruction inequalities.
    t0=time.monotonic()
    c=Cegar(edges,seed=18148)
    # Euler: both planar layers have at most 3*n-6=69 edges.
    # Exact cardinality CNF: x_e chooses layer 1, -x_e chooses layer 2.
    # Each original bipartition with planar layers extends existentially
    # to both auxiliary encodings, hence these clauses are SOUND.
    from pysat.card import CardEnc, EncType
    atmost1=CardEnc.atmost(lits=list(range(1,m+1)),bound=3*n-6,top_id=m,encoding=EncType.seqcounter)
    atmost2=CardEnc.atmost(lits=[-i for i in range(1,m+1)],bound=3*n-6,top_id=atmost1.nv,encoding=EncType.seqcounter)
    c.base=atmost1.clauses+atmost2.clauses
    c.nv=atmost2.nv; c.perms=[]
    add_induced_euler_constraints(c)
    log["exact_cardinality"]={"layer_max":3*n-6,"layer_min":m-(3*n-6),
                              "base_clauses":len(c.base),"cnf_variables":c.nv}
    checkpoint=ROOT/"validation/S019/row148_lemmas.json.gz"
    loaded=0
    log["exact"]={"status":"IN_PROGRESS","mode":"NO_SYMMETRY_GLOBAL_AND_INDUCED_EULER",
        "cap_seconds":cap,"seed":18148,"limit":32,
        "iterations":0,"lemmas":0,"loaded_lemmas":0,
        "checkpoint_source":str(checkpoint) if checkpoint.exists() else "none"}
    save()
    with Cadical153(bootstrap_with=c.base) as sol:
        if checkpoint.exists():
            with gzip.open(checkpoint,"rt") as fh:
                obstructions=json.load(fh)
            for ks in obstructions:
                c.add_lemma([tuple(e) for e in ks],sol)
                loaded+=1
        log["exact"]["loaded_lemmas"]=loaded
        # Preregistered exact iteration and memory cap controls external too.
        iteration=0
        while time.monotonic()-t0 < cap:
            iteration+=1
            is_sat=sol.solve()
            if not is_sat:
                log["exact"]["status"]="UNSAT_UNCERTIFIED"
                # Export exact original graph / sound constraints for native proof.
                clauses=list(c.base)
                for ks in c.lemmas:
                    ids=[c.idx[e] for e in ks]
                    clauses.extend(([-i for i in ids],ids))
                cnf=O/"row148_complete.cnf"
                with cnf.open("w") as fh:
                    fh.write("p cnf %d %d\n"%(c.nv,len(clauses)))
                    for clause in clauses:fh.write(" ".join(map(str,clause))+" 0\n")
                log["exact"]["cnf_sha256"]=digest(cnf)
                log["exact"]["cnf_clauses"]=len(clauses)
                save()
                # Fresh proof must be generated and verified by drat-trim
                # before even considering a nonbiplanarity certificate.
                native=ROOT/"artifacts/tmp/native/bin"
                proof=O/"row148_native.drat"
                try:
                    p=subprocess.run([str(native/"cadical"),"-q",str(cnf),str(proof)],
                          capture_output=True,text=True,timeout=150)
                    log["exact"]["native_returncode"]=p.returncode
                    if p.returncode==20 and proof.exists():
                        q=subprocess.run([str(native/"drat-trim"),str(cnf),str(proof)],
                            capture_output=True,text=True,timeout=150)
                        log["exact"]["proof_check_returncode"]=q.returncode
                        if q.returncode==0:
                            with proof.open("rb") as fi, gzip.open(O/"row148_native.drat.gz","wb") as fo:
                                while True:
                                    blk=fi.read(1048576)
                                    if not blk:break
                                    fo.write(blk)
                            log["exact"]["proof_archive_sha256"]=digest(O/"row148_native.drat.gz")
                            log["negative_proof_checked"]=True
                            log["exact"]["status"]="NATIVE_PROOF_CHECKED_ENCODING_AUDIT_REQUIRED"
                            # No automatically accepted negative: independent
                            # source-encoding audit is a separate obligatory gate.
                except Exception as ex:
                    log["exact"]["native_error"]=repr(ex)
                save()
                break
            true_lits={lit for lit in sol.get_model() if lit>0}
            a=[e for e in edges if c.idx[e] in true_lits]
            b=[e for e in edges if c.idx[e] not in true_lits]
            ok1=planar(nx.Graph(a));ok2=planar(nx.Graph(b))
            if ok1 and ok2:
                complete({"E1":[list(e) for e in a],"E2":[list(e) for e in b],
                          "unplaced":[]},"exact-cegar-no-lex")
                log["exact"]["status"]="COMPLETE_SPLIT"
                break
            before=len(c.lemmas)
            if not ok1: c.lemmas_from(a,sol,24)
            if not ok2: c.lemmas_from(b,sol,24)
            if len(c.lemmas)==before:
                log["exact"]["status"]="STALLED_DUPLICATE_CUTS_NO_FALSE_SAT"
                break
            if iteration%15==0:
                log["exact"].update({"iterations":iteration,
                    "lemmas":len(c.lemmas),"elapsed_seconds":round(time.monotonic()-t0,2)})
                persist_lemmas(c.lemmas)
                save()
                print("EXACT progress",iteration,len(c.lemmas),memory(),flush=True)
        else:
            log["exact"]["status"]="CAPPED_STILL_UNKNOWN"
        log["exact"].update({"iterations":iteration,"lemmas":len(c.lemmas),
            "elapsed_seconds":round(time.monotonic()-t0,2)})
        persist_lemmas(c.lemmas)
        if not log["full_positive_verified"] and not log["negative_proof_checked"]:
            log["queue"][str(ROW)]["session"]="CAPPED"
        save()

def persist_lemmas(lemmas):
    p=O/"row148_lemmas.json.gz"
    with gzip.open(str(p)+".tmp","wt",compresslevel=6) as fh:
        json.dump(lemmas,fh,separators=(",",":"))
    pathlib.Path(str(p)+".tmp").replace(p)

t0=time.monotonic()
try:
    log["stage"]="OBSTRUCTION_GUIDED_INSERTION";save()
    found=guided_switch_search(220)
    if not found:
        log["stage"]="LOCAL_EULER_EXACT";save()
        exact_search(530)
    log["stage"]="FINISHED"
    if not log["full_positive_verified"]:
        log["status"]="UNKNOWN_WITH_CHECKPOINTS"
    save()
except Exception as exc:
    log["stage"]="ERROR";log["error"]=repr(exc)
    log["traceback"]=traceback.format_exc()[-3000:]
    save()
    raise
finally:
    print(json.dumps({"status":log["status"],"positive":log["positive"],
      "exact":log["exact"],"rss_mb":memory(),"elapsed":round(time.monotonic()-t0,2)},
      default=str),flush=True)
