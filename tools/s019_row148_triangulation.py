#!/usr/bin/env python3
"""S019 original row148: NEW seven-defect paired-triangulation flip search.

This is a constructive search only. No time cap is a proof of nonbiplanarity.
Both 25-vertex triangulations ALWAYS have exactly 69 edges, are planar, and
their union is tested against ALL 131 exact original edges.
"""
import hashlib,itertools,json,math,os,pathlib,random,resource,subprocess,sys,time,traceback
import networkx as nx
ROOT=pathlib.Path(__file__).resolve().parents[1];os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup
from s015_recheck_219 import check_complete
O=ROOT/"artifacts/tmp/S019-TRI";O.mkdir(parents=True,exist_ok=True)
SEED=1901483;rng=random.Random(SEED)
def norm(e):return tuple(sorted(e))
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
    temp=pathlib.Path(str(p)+".tmp")
    temp.write_text(json.dumps(v,indent=2,sort_keys=True));temp.replace(p)
def egraph(es):
    G=nx.Graph();G.add_nodes_from(range(25));G.add_edges_from(es);return G
def planar(g):return nx.check_planarity(g)[0]
smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
assert smoke["chromatic_cnf_byte_matches"]==271 and smoke["k9"]["verified"]
assert smoke["solver_roundtrip"]["fresh_proof_verified"]
corpus=json.loads((ROOT/"validation/S003/survivors_alpha_ge3.json").read_text())
edges,bags=blowup(corpus[148][0],corpus[148][1]);E=set(edges)
assert len(E)==131 and sum(corpus[148][1])==25
edgefile=O/"row148.edges";edgefile.write_text("".join(f"{a} {b}\n" for a,b in edges))
assert sha(edgefile)=="4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598"
source=ROOT/"validation/S018/row148_best_partial.json"
orig=json.loads(source.read_text())
A=set(map(norm,orig["E1"]));B=set(map(norm,orig["E2"]))
miss=set(map(norm,orig["unplaced"]))
assert A|B|miss==E and not A&B and len(miss)==6
assert planar(egraph(A)) and planar(egraph(B))
start=time.monotonic()
log={"campaign":"CAM-0023","original_row":148,"status":"SEARCHING","source_sha":sha(edgefile),
 "original_partial_sha":sha(source),"original_edges":131,
 "method":"pair_of_maximal_planar_triangulations_randomized_completion_plus_face_flips",
 "initial_missing":6,"best_missing":131,"flip_trials":0,"accepted_flips":0,
 "completed_triangulation_restarts":0,"full_split_checked":False,
 "negative_proof_checked":False,"seed":SEED}
def persist():
    log["elapsed_seconds"]=round(time.monotonic()-start,1)
    log["maxrss_mib"]=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)
    save(O/"RESULT.json",log)
def edgeset(g):return {norm(e) for e in g.edges()}
def check_pair(a,b):
    sa,sb=edgeset(a),edgeset(b)
    assert len(sa)==len(sb)==69
    assert len(a)==len(b)==25
    assert planar(a) and planar(b)
    return len(E-(sa|sb))
def store_best(a,b,origin):
    k=check_pair(a,b)
    if k>=log["best_missing"]:return False
    log["best_missing"]=k;log["best_origin"]=origin
    aa,bb=edgeset(a),edgeset(b)
    excluded=sorted(E-(aa|bb))
    # Equivalent positive certificate: source edges in first triangulation go
    # to E1; every other covered edge belongs to the second triangulation.
    posA=sorted(E&aa);posB=sorted(E-set(posA)-set(excluded))
    assert set(posA)|set(posB)|set(excluded)==E
    assert not set(posA)&set(posB)
    save(O/"row148_best_triangulations.json",{
         "n":25,"T1":[list(e) for e in sorted(aa)],
         "T2":[list(e) for e in sorted(bb)],
         "E1":[list(e) for e in posA],"E2":[list(e) for e in posB],
         "unplaced":[list(e) for e in excluded],
         "shared_triang_edges":len(aa&bb),
         "extra_triang_union_edges":len((aa|bb)-E)})
    persist()
    print("TRIANGULATION_IMPROVEMENT",json.dumps({"missing":k,"origin":origin,
           "shared":len(aa&bb),"extra":len((aa|bb)-E)}),flush=True)
    if k==0:
        split={"n":25,"E1":[list(e) for e in posA],"E2":[list(e) for e in posB]}
        save(O/"row148_full_original_split.json",split)
        # Independent cold checker of the original labelled complete source.
        p=subprocess.run([sys.executable,"tools/check_layers.py",str(edgefile),
                          str(O/"row148_full_original_split.json")],
                          capture_output=True,text=True,timeout=80)
        log["layer_check_stdout"]=p.stdout[-1000:]
        assert p.returncode==0,(p.stdout,p.stderr)
        colours=json.loads((ROOT/"validation/S004/chi10_results.json").read_text())
        check_complete(148,25,edges,egraph(posA),egraph(posB),
                       colours[148]["ten_colouring"],O/"positive.json")
        log["full_split_checked"]=True
        log["status"]="CERTIFIED_CHI10_BIPLANAR_CONSTRUCTION"
        persist()
    return True

def triangulate(g,r):
    """Independently fill an existing planar source layer up to 69 edges.

    Random maximal completion uses source-fixed planar edge inclusion; optional
    NetworkX embedding triangulation serves as a second independent route.
    """
    H=g.copy()
    if r.random()<.82:
        pool=[(u,v) for u in range(25) for v in range(u+1,25)
              if not H.has_edge(u,v)]
        r.shuffle(pool)
        for u,v in pool:
            if H.number_of_edges()==69:break
            H.add_edge(u,v)
            if not planar(H):H.remove_edge(u,v)
    if H.number_of_edges()!=69:
        ok,p=nx.check_planarity(H)
        assert ok
        em,_=nx.algorithms.planar_drawing.triangulate_embedding(
            p,fully_triangulate=True)
        H=nx.Graph(em)
        H.add_nodes_from(range(25))
    assert H.number_of_edges()==69 and planar(H)
    return H

def flip_moves(g):
    """Every move is a face-diagonal flip between two adjacent triangle faces."""
    ok,p=nx.check_planarity(g)
    assert ok
    moves=[]
    for u,v in g.edges():
        left=p.traverse_face(u,v);right=p.traverse_face(v,u)
        if len(left)!=3 or len(right)!=3:raise AssertionError("bad triangulation face")
        x=next(z for z in left if z!=u and z!=v)
        y=next(z for z in right if z!=u and z!=v)
        if x==y or g.has_edge(x,y):continue
        moves.append((norm((u,v)),norm((x,y))))
    return moves
def delta_move(old,new,own,other):
    # Change in original G edges *not* present in T1 union T2.
    assert old in own and new not in own
    return int(old in E and old not in other)-int(new in E and new not in other)

def anneal(epoch,GA,GB,limit_seconds=105):
    current=check_pair(GA,GB)
    epoch_start=time.monotonic()
    counter=0
    accepted=0
    baseline=current
    while time.monotonic()-epoch_start<limit_seconds:
        if log["full_split_checked"]:break
        side=rng.randrange(2)
        g=GA if side==0 else GB
        other=GB if side==0 else GA
        moves=flip_moves(g)
        if not moves:break
        own=edgeset(g);o=edgeset(other)
        potentials=[delta_move(old,new,own,o) for old,new in moves]
        lo=min(potentials)
        # Strongly favour improvements and equal-score rearrangements while
        # using scheduled uphill exploration to escape local minima.
        if rng.random()<.72:
            choices=[j for j,v in enumerate(potentials) if v==lo]
            j=rng.choice(choices)
        else:j=rng.randrange(len(moves))
        d=potentials[j]
        # Low-to-high-to-low temperature cycles, with most time near cold.
        cycle=counter%10000
        temperature=(0.28 if cycle<4000 else .7 if cycle<6500 else
                     1.4 if cycle<7800 else .45)
        counter+=1;log["flip_trials"]+=1
        if d>0 and rng.random()>=math.exp(-d/temperature):
            continue
        old,new=moves[j]
        g.remove_edge(*old);g.add_edge(*new)
        current+=d;accepted+=1;log["accepted_flips"]+=1
        # Every face diagonal flip of maximal planar graph is planar; check
        # this independently and reconcile energy at bounded intervals.
        if accepted%800==0:
            assert check_pair(GA,GB)==current
        if current<log["best_missing"]:
            store_best(GA,GB,{"epoch":epoch,"step":counter,"temperature":temperature})
            if log["full_split_checked"]:break
        if counter%5000==0:
            log["epoch"]=epoch;log["epoch_tried"]=counter
            log["epoch_current_missing"]=current
            persist()
            print("TRI_FLIP_PROGRESS",json.dumps({"epoch":epoch,"moves":counter,
              "current_missing":current,"best_missing":log["best_missing"],
              "elapsed_s":round(time.monotonic()-start,1)}),flush=True)
    return {"epoch":epoch,"tried":counter,"accepted":accepted,
            "initial_missing":baseline,"last_missing":current,
            "elapsed_s":round(time.monotonic()-epoch_start,1)}

try:
    initialA=egraph(A);initialB=egraph(B)
    # Chance of fast completion via random planar triangulation augmentation.
    bestpair=None;seedpair=None;bestmiss=999
    for j in range(18):
        ta=triangulate(initialA,rng);tb=triangulate(initialB,rng)
        k=check_pair(ta,tb)
        log["completed_triangulation_restarts"]+=1
        if k<bestmiss:
            bestmiss=k;bestpair=(ta.copy(),tb.copy())
        if seedpair is None:seedpair=(ta.copy(),tb.copy())
        store_best(ta,tb,{"random_completion":j})
        if log["full_split_checked"]:break
    rounds=[]
    for epoch in range(26):
        if log["full_split_checked"] or time.monotonic()-start>1220:break
        # Enforce diversity: fresh source-preserving triangulations every
        # fourth epoch, restart from global incumbent on the others.
        if epoch%4==0:
            ta=triangulate(initialA,rng);tb=triangulate(initialB,rng)
        elif epoch%4==1 and bestpair is not None:
            ta,tb=(z.copy() for z in bestpair)
        elif epoch%4==2:
            ta,tb=(z.copy() for z in seedpair)
        else:
            ta=triangulate(initialA,rng);tb=triangulate(initialB,rng)
        result=anneal(epoch,ta,tb,min(65,1270-(time.monotonic()-start)))
        rounds.append(result)
        k=check_pair(ta,tb)
        if k<bestmiss:
            bestmiss=k;bestpair=(ta.copy(),tb.copy())
        log["rounds"]=rounds;persist()
        print("TRI_EPOCH",json.dumps(result),flush=True)
    if not log["full_split_checked"]:
        log["status"]="UNKNOWN_CONSTRUCTIVE_SEARCH_ONLY"
    persist()
except Exception as err:
    log["status"]="ERROR";log["error"]=repr(err)
    log["traceback"]=traceback.format_exc()[-3500:]
    persist();raise
finally:
    print("TRI_FINAL",json.dumps({k:log.get(k) for k in
         ("status","best_missing","flip_trials","accepted_flips",
          "completed_triangulation_restarts","maxrss_mib","elapsed_seconds")}),flush=True)
