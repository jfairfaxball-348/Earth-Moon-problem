#!/usr/bin/env python3
"""S022 deterministic exact Hamming neighbourhood around original row148 split.

A final split differing on at most r of the 125 ALREADY PLACED original edges
appears exactly once as a flip subset; the six UNPLACED edges are enumerated
by exhaustive, non-symmetric binary branching. Planarity is monotone under
edge addition, so rejecting a nonplanar partial is sound. This proves
exhaustion of this explicitly restricted neighbourhood ONLY, never global
nonbiplanarity. The script checks the IMMUTABLE S004 source in the same
runner after full native 271+K9 cloud smoke.
"""
import hashlib, itertools, json, os, pathlib, resource, subprocess, sys, time, traceback
import networkx as nx

ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup

OUT=ROOT/"artifacts/tmp/S022"
OUT.mkdir(parents=True,exist_ok=True)
ROW=148
TIME_CAP=850.0
MAX_FLIPS=3
SOURCE_HASH="4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598"

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def store(name,obj):
    p=OUT/name
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    os.replace(tmp,p)

def edge(e): return tuple(sorted(map(int,e)))
def graph(ee,n=25):
    g=nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(ee)
    return g

def planar(g):
    return nx.check_planarity(g, counterexample=False)[0]

def check_full(g1,g2,original,colours,smoke):
    aa=set(map(edge,g1.edges()));bb=set(map(edge,g2.edges()))
    assert not aa&bb and aa|bb==original
    yes1,emb1=nx.check_planarity(g1)
    yes2,emb2=nx.check_planarity(g2)
    assert yes1 and yes2
    emb1.check_structure();emb2.check_structure()
    assert len(colours)==25 and len(set(colours))==10
    assert all(colours[u]!=colours[v] for u,v in original)
    assert smoke["chromatic_rows_verified"]==271
    assert smoke["chromatic_cnf_byte_matches"]==271
    assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    split={"n":25,"E1":sorted(map(list,aa)),"E2":sorted(map(list,bb))}
    store("row148_full_candidate.json",split)
    t=subprocess.run([sys.executable,"tools/check_layers.py",str(OUT/"row148.edges"),
        str(OUT/"row148_full_candidate.json")], capture_output=True,text=True,timeout=120)
    assert t.returncode==0,(t.stdout[-2000:],t.stderr[-2000:])
    return {"layer1":len(aa),"layer2":len(bb),"independent_layer_checker":t.stdout[-2000:],
            "same_job_chromatic_smoke":True,"embedding1_checked":True,"embedding2_checked":True}

smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
assert smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
pool=json.loads((ROOT/"validation/S010/SUMMARY.json").read_text())
assert len(pool["remaining_unknown_indices"])==219 and ROW in pool["remaining_unknown_indices"]
survivors=json.loads((ROOT/"validation/S003/survivors_alpha_ge3.json").read_text())
colours=json.loads((ROOT/"validation/S004/chi10_results.json").read_text())
orig_edges,_=blowup(survivors[ROW][0],survivors[ROW][1])
n=sum(survivors[ROW][1]);m=len(orig_edges)
assert (n,m)==(25,131)
original=set(map(edge,orig_edges))
assert len(original)==131
sourcefile=OUT/"row148.edges"
sourcefile.write_text("".join("%d %d\n"%tuple(e) for e in orig_edges))
assert sha(sourcefile)==SOURCE_HASH
partial=json.loads((ROOT/"validation/S021/row148_best_partial.json").read_text())
A=set(map(edge,partial["E1"])); B=set(map(edge,partial["E2"]))
missing=tuple(sorted(map(edge,partial["unplaced"])))
assert (len(A),len(B),len(missing))==(62,63,6)
assert not (A&B or A&set(missing) or B&set(missing))
assert A|B|set(missing)==original
assert planar(graph(A)) and planar(graph(B))
fixed=tuple((0,e) for e in sorted(A))+tuple((1,e) for e in sorted(B))
assert len(fixed)==125
native=json.loads((ROOT/"artifacts/tmp/native/ENVIRONMENT.json").read_text())
start=time.monotonic()
log={"session":"S022","active_original":148,"status":"IN_PROGRESS",
     "source_edge_sha256":SOURCE_HASH,"source_131":len(original),
     "source_code_sha256":sha("tools/s022_row148_exact_neighbourhood.py"),
     "source_partial_sha256":sha("validation/S021/row148_best_partial.json"),
     "same_job_smoke":"PASS271_CNF_DRAT_RETAINED_FRESH_K9",
     "native_sha256":native["native_sha256"],"method":"exact_hamming_ball_planarity_BB",
     "radius_max":MAX_FLIPS,"wall_cap_seconds":TIME_CAP,"fixed_edges":len(fixed),
     "missing_edges":len(missing),"radii":{},"complete_positive":False,
     "full_negative_certified":False,"global_original_verdict":"BIPLANARITY_UNKNOWN"}

def flush():
    log["elapsed_seconds"]=round(time.monotonic()-start,2)
    log["peak_rss_mib"]=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)
    store("result.json",log)

flush()
deadline=start+TIME_CAP
col=colours[ROW]["ten_colouring"]
found=False
try:
    for radius in range(MAX_FLIPS+1):
        total=0
        base_nonplanar=0
        base_planar=0
        subcalls=0
        prunes=0
        leaves=0
        completed=True
        first=tuple(range(125))
        combos_count=__import__("math").comb(125,radius)
        log["radii"][str(radius)]={"status":"IN_PROGRESS",
            "possible_flip_subsets":combos_count,"enumerated_flip_subsets":0}
        flush()
        for flips in itertools.combinations(first,radius):
            if time.monotonic()>=deadline:
                completed=False
                break
            total+=1
            AA=set(A);BB=set(B)
            for j in flips:
                oldside,e=fixed[j]
                if oldside==0: AA.remove(e);BB.add(e)
                else:BB.remove(e);AA.add(e)
            ga=graph(AA);gb=graph(BB)
            if not planar(ga) or not planar(gb):
                base_nonplanar+=1
                continue
            base_planar+=1
            # Exhaustive two-way branching in the FIXED sorted order of six
            # unplaced source edges. No symmetry, repeated-state or budget pruning.
            def assign(i):
                global subcalls,prunes,leaves,found
                subcalls+=1
                if i==len(missing):
                    leaves+=1
                    proof=check_full(ga,gb,original,col,smoke)
                    store("positive.json",{"flipped_placed_edges":[list(fixed[j][1]) for j in flips],
                       "radius":radius,"six_original_missing":list(map(list,missing)),
                       "verification":proof})
                    log["complete_positive"]=True
                    log["global_original_verdict"]="CERTIFIED_POSITIVE_PENDING_INDEPENDENT_OWNER_RECHECK"
                    found=True
                    flush()
                    return True
                e=missing[i]
                ga.add_edge(*e)
                if planar(ga) and assign(i+1):return True
                if not planar(ga):prunes+=1
                ga.remove_edge(*e)
                gb.add_edge(*e)
                if planar(gb) and assign(i+1):return True
                if not planar(gb):prunes+=1
                gb.remove_edge(*e)
                return False
            if assign(0):
                break
            if total%500==0:
                log["radii"][str(radius)].update({"enumerated_flip_subsets":total,
                   "base_planar":base_planar,"base_nonplanar":base_nonplanar,
                   "insertion_nodes":subcalls,"nonplanar_prunes":prunes,
                   "complete_assignments":leaves})
                flush()
        log["radii"][str(radius)]={"status":("FOUND_POSITIVE" if found else
            "EXHAUSTED_LOCAL_RADIUS" if completed else "CAPPED_INCOMPLETE_RADIUS"),
            "possible_flip_subsets":combos_count,"enumerated_flip_subsets":total,
            "base_planar":base_planar,"base_nonplanar":base_nonplanar,
            "insertion_nodes":subcalls,"nonplanar_prunes":prunes,
            "complete_assignments":leaves,
            "mathematical_scope": "exactly this many original placed edges reassigned; all 6 missing assigned"}
        flush()
        print("RADIUS",radius,json.dumps(log["radii"][str(radius)]),flush=True)
        if found or not completed:break
    log["status"]="POSITIVE_CANDIDATE_INDEPENDENTLY_CHECKED" if found else "CAPPED_GLOBAL_UNKNOWN" if time.monotonic()>=deadline else "LOCAL_NEIGHBOURHOODS_EXHAUSTED_GLOBAL_UNKNOWN"
    flush()
except BaseException as exc:
    log["status"]="ERROR_NO_CERTIFIED_SCIENCE"
    log["error"]=repr(exc)
    log["traceback"]=traceback.format_exc()[-6000:]
    flush()
    raise
print("END",log["status"],"elapsed",log["elapsed_seconds"],"rss",log["peak_rss_mib"],flush=True)
