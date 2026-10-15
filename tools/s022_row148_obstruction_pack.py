#!/usr/bin/env python3
"""S022/CAM0025: attempt SMALL individually inspectable obstruction-packing
certificates. Failure to pack is not positive, not negative, and does not undo
CAM0024 exhaustive local search. Only original row148 and target edge(0,1).
"""
import hashlib, json, os, pathlib, random, resource, sys, time
import networkx as nx
ROOT=pathlib.Path(__file__).resolve().parents[1];os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup
O=ROOT/"artifacts/tmp/S022-PACK";O.mkdir(parents=True,exist_ok=True)
def pair(e):return tuple(sorted(e))
def h(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(name,obj):(O/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271 and smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
corpus=json.loads((ROOT/"validation/S003/survivors_alpha_ge3.json").read_text())
e0,_=blowup(corpus[148][0],corpus[148][1]);assert len(e0)==131
source=O/"row148.edges";source.write_text("".join("%d %d\n"%x for x in e0))
assert h(source)=="4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598"
p=json.loads((ROOT/"validation/S021/row148_best_partial.json").read_text())
A=set(map(pair,p["E1"]));B=set(map(pair,p["E2"]));U=set(map(pair,p["unplaced"]))
assert (len(A),len(B),len(U))==(62,63,6) and A|B|U==set(map(pair,e0))
target=(0,1);assert target in U
start=time.monotonic();cap=175
out={"session":"S022","campaign":"CAM-0025","target":list(target),
     "source_edge_sha256":h(source),"status":"IN_PROGRESS","same_job_smoke":"PASS271_K9",
     "sideA":{"best_count":0},"sideB":{"best_count":0},"max_trials":2000,"wall_cap_seconds":cap}
def graph(ee):
 g=nx.Graph();g.add_nodes_from(range(25));g.add_edges_from(ee);return g
def validate(groups,base):
 used=set()
 for grp in groups:
  S=set(map(pair,grp))
  assert target in S and S-{target}<=base
  assert not (used & (S-{target}))
  used|=(S-{target})
  assert not nx.check_planarity(graph(S))[0]   # independent replay
 return True
def flush():
 out["elapsed_seconds"]=round(time.monotonic()-start,2)
 out["rss_mib"]=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)
 dump("result.json",out)
flush()
for side_name,side in (("sideA",A),("sideB",B)):
 for attempt in range(2000):
  if time.monotonic()-start>cap:break
  rng=random.Random(230148+attempt*1993+(0 if side_name=="sideA" else 1))
  shuffled=list(side);rng.shuffle(shuffled)
  g=graph(shuffled);g.add_edge(*target)
  groups=[]
  for k in range(4):
   isplanar,counter=nx.check_planarity(g,counterexample=True)
   if isplanar:break
   ks=set(map(pair,counter.edges()))
   if target not in ks:raise AssertionError("base without target is planar")
   if not ks-{target}:raise AssertionError("nonplanar single-edge graph impossible")
   groups.append(sorted(map(list,ks)))
   g.remove_edges_from(ks-{target})
  validate(groups,side)
  if len(groups)>out[side_name]["best_count"]:
   out[side_name]={"best_count":len(groups),"trial":attempt,
     "kur_subdivision_edge_sets":groups,
     "total_distinct_layer_edges":len(set(pair(e) for grp in groups for e in grp))-1}
   flush()
   print("PACKING",side_name,len(groups),"trial",attempt,flush=True)
  if len(groups)>=4:break
 out[side_name]["trials"]=attempt+1
 flush()
out["status"]="FOUR_INDEPENDENT_OBSTRUCTIONS_PER_SIDE_CERTIFIED" if all(out[x]["best_count"]>=4 for x in ("sideA","sideB")) else "PARTIAL_OBSTRUCTION_PACKING_NO_COMPLETE_FOUR_PER_SIDE"
out["does_not_establish_global_nonbiplanarity"]=True
flush()
print("END",out["status"],out["elapsed_seconds"],out["sideA"]["best_count"],out["sideB"]["best_count"],flush=True)
