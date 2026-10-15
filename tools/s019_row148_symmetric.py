#!/usr/bin/env python3
"""S019 second serial ORIGINAL row148 run: audited twin lex + sound SAT cuts.

All edge source indices ORIGINAL. Exact negative requires same-job native DRAT
and separate proof validation. Bounded UNKNOWN is never called nonbiplanar.
"""
import gzip,hashlib,itertools,json,os,pathlib,random,resource,subprocess,sys,time,traceback
import networkx as nx
from pysat.solvers import Cadical153
from pysat.card import CardEnc,EncType
ROOT=pathlib.Path(__file__).resolve().parents[1];os.chdir(ROOT)
sys.path.insert(0,str(ROOT/"tools"))
from blowup_graph import blowup
from biplanar_cegar import is_kuratowski_subdivision
from s015_recheck_219 import check_complete
O=ROOT/"artifacts/tmp/S019-SYM";O.mkdir(parents=True,exist_ok=True)
rng=random.Random(19148)
def hashfile(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,v):
    t=pathlib.Path(str(p)+".tmp");t.write_text(json.dumps(v,indent=2,sort_keys=True));t.replace(p)
def ecanon(e):return tuple(sorted(e))
def planar(e):return nx.check_planarity(nx.Graph(e),counterexample=False)[0]
smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
assert smoke["chromatic_cnf_byte_matches"]==271
assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
source=json.loads((ROOT/"validation/S003/survivors_alpha_ge3.json").read_text())[148]
edges,bags=blowup(source[0],source[1]);E=set(edges);n=sum(source[1]);m=len(E)
assert (n,m)==(25,131)
edgefile=O/"row148.edges";edgefile.write_text("".join("%d %d\n"%e for e in edges))
assert hashfile(edgefile)=="4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598"
p0=ROOT/"validation/S019-WIP/row148_all_checked_cuts.json.gz"
assert p0.exists()
with gzip.open(p0,"rt") as fh:oldcuts=json.load(fh)
assert len(oldcuts)==53747,len(oldcuts)
start=time.monotonic()
log={"status":"SEARCHING","row":148,"method":"exact-symmetric-automorphism-lex"+
 "+sound-Kuratowski-and-density","graph_sha256":hashfile(edgefile),
 "loaded_archive_sha256":hashfile(p0),"loaded_lemmas":len(oldcuts),
 "new_lemmas":0,"iterations":0,"positive":False,"negative_proof_checked":False}
def persist():
    log["elapsed_s"]=round(time.monotonic()-start,2)
    log["maxrss_mib"]=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)
    save(O/"RESULT.json",log)
def cutarchive():
    with gzip.open(O/"row148_all_checked_cuts.json.gz","wt",compresslevel=5) as fh:
        json.dump([[list(e) for e in k] for k in cuts],fh,separators=(",",":"))
persist()
idx={e:i+1 for i,e in enumerate(edges)}
clauses=[];next_var=m
def clause(lits):
    t=list(lits);clauses.append(t);solver.add_clause(t)
solver=Cadical153()
# Every blow-up bag is a closed-twin clique. Adjacent vertex transpositions
# are independently verified graph automorphisms on ORIGINAL labelled edges.
perms=[]
for bag in bags:
    for a,b in zip(bag,bag[1:]):
        def perm(e):
            x,y=e
            x=(b if x==a else a if x==b else x)
            y=(b if y==a else a if y==b else y)
            return (min(x,y),max(x,y))
        trans={e:perm(e) for e in edges}
        assert set(trans.values())==E and len(set(trans.values()))==m
        perms.append(trans)
log["verified_twin_generators"]=len(perms)
# The lexicographically least point of the orbit under all automorphisms
# AND global layer swap satisfies each generator's lex-leader inequality,
# and has first source edge in layer 2. These constraints are
# existential-preserving for biplanarity; not arbitrary fixed layer bits.
clause([-1])
for trans in perms:
    pref=None
    for e in edges:
        te=trans[e]
        if te==e:continue
        x,y=idx[e],idx[te]
        guard=[] if pref is None else [-pref]
        clause(guard+[-x,y])
        next_var+=1;nxt=next_var
        if pref is not None:clause([-nxt,pref])
        clause([-nxt,-x,y]);clause([-nxt,x,-y])
        clause(guard+[x,y,nxt]);clause(guard+[-x,-y,nxt])
        pref=nxt
# Necessary Euler constraints only, all use original edge variables.
def bounds(ll,lo,hi):
    global next_var
    if lo>len(ll) or hi<0:clause([]);return
    if hi<len(ll):
        k=CardEnc.atmost(lits=ll,bound=hi,top_id=next_var,encoding=EncType.seqcounter)
        next_var=max(next_var,k.nv)
        for z in k.clauses:clause(z)
    if lo>0:
        k=CardEnc.atleast(lits=ll,bound=lo,top_id=next_var,encoding=EncType.seqcounter)
        next_var=max(next_var,k.nv)
        for z in k.clauses:clause(z)
bounds(list(idx.values()),62,69)
loc=[]
for mask in range(1,1<<len(bags)):
    u={a for j,B in enumerate(bags) if mask>>j&1 for a in B}
    if len(u)<3:continue
    sub=tuple(e for e in edges if e[0] in u and e[1] in u)
    cap=3*len(u)-6
    assert len(sub)<=2*cap or False,"CERTIFIED_DENSITY_OBSTRUCTION"
    if len(sub)>cap+2:
        loc.append((2*cap-len(sub),len(u),sub,cap))
loc.sort()
for _,_,sub,cap in loc[:24]:
    ll=[idx[e] for e in sub]
    bounds(ll,len(sub)-cap,cap)
log["density_subsets"]=min(len(loc),24)
# Full-source Kuratowski K5 or subdivided K3,3 clauses:
# each forbidden edge-set must contain at least one edge of each layer.
cuts=[];seen=set()
def addcut(k):
    key=tuple(sorted(map(ecanon,k)))
    if key in seen:return False
    assert set(key)<=E and is_kuratowski_subdivision(key)
    seen.add(key);cuts.append(key)
    lits=[idx[e] for e in key]
    clause(lits);clause([-v for v in lits])
    return True
for k in oldcuts:addcut(k)
assert len(cuts)==53747
# Add all explicit K5 subgraphs, independent of earlier long subdivisions.
g=nx.Graph(edges)
smalls=0
for clique in nx.enumerate_all_cliques(g):
    if len(clique)==5:
        k=[ecanon(e) for e in itertools.combinations(clique,2)]
        smalls+=addcut(k)
log["new_direct_K5"]=smalls
# Add a capped, deterministic complete-K3,3 direct family as stronger short cuts.
nodes=sorted(g)
for X in itertools.combinations(nodes,3):
    common=set.intersection(*(set(g[v]) for v in X))-set(X)
    for Y in itertools.combinations(sorted(common),3):
        if min(Y)<min(X):continue
        k=[ecanon((x,y)) for x in X for y in Y]
        smalls+=addcut(k)
        if smalls>=30000:break
    if smalls>=30000:break
log["direct_short_total"]=smalls
log["base_cnf_vars"]=next_var
log["base_cnf_clauses"]=len(clauses)
persist();cutarchive()
print("S019_SYM_SEEDED",json.dumps({k:log[k] for k in
 ("loaded_lemmas","verified_twin_generators","direct_short_total","base_cnf_vars","base_cnf_clauses")}),flush=True)

def positive(a,b):
    assert a|b==E and not a&b
    assert planar(a) and planar(b)
    split={"n":n,"E1":[list(e) for e in sorted(a)],"E2":[list(e) for e in sorted(b)]}
    save(O/"row148_full_split.json",split)
    p=subprocess.run([sys.executable,"tools/check_layers.py",str(edgefile),
                      str(O/"row148_full_split.json")],capture_output=True,text=True,timeout=60)
    assert p.returncode==0,p.stdout+p.stderr
    colours=json.loads((ROOT/"validation/S004/chi10_results.json").read_text())
    check_complete(148,n,edges,nx.Graph(a),nx.Graph(b),
                   colours[148]["ten_colouring"],O/"positive.json")
    log["positive"]=True;log["status"]="CERTIFIED_BIPLANAR_10_CHROMATIC_SAME_JOB"
    persist()

def verify_native_negative():
    cnf=O/"row148_necessary_constraints.cnf"
    with cnf.open("w") as f:
        f.write(f"p cnf {next_var} {len(clauses)}\n")
        for c in clauses:f.write(" ".join(map(str,c))+" 0\n")
    log["cnf_sha256"]=hashfile(cnf)
    log["cnf_clauses"]=len(clauses);log["cnf_vars"]=next_var
    persist()
    nat=ROOT/"artifacts/tmp/native/bin"
    proof=O/"row148_unsat_native.drat"
    p=subprocess.run([str(nat/"cadical"),"-q",str(cnf),str(proof)],
        capture_output=True,text=True,timeout=220)
    log["native_solver_exit"]=p.returncode
    if p.returncode!=20 or not proof.exists():
        log["status"]="UNKNOWN_NATIVE_NEGATIVE_NOT_VERIFIED";return
    q=subprocess.run([str(nat/"drat-trim"),str(cnf),str(proof)],
        capture_output=True,text=True,timeout=220)
    log["native_drat_exit"]=q.returncode
    if q.returncode==0:
        with proof.open("rb") as a,gzip.open(O/"row148_unsat_native.drat.gz","wb") as b:
            while z:=a.read(1<<20):b.write(z)
        log["native_drat_gzip_sha256"]=hashfile(O/"row148_unsat_native.drat.gz")
        log["negative_proof_checked"]=True
        log["status"]="NEGATIVE_CHECKED_NATIVE_AND_ENCODING_AUDIT_PENDING"
    else:log["status"]="UNKNOWN_DRA_TRIM_FAILED"
    persist()

try:
    it=0
    while time.monotonic()-start<1090:
        it+=1
        solver.conf_budget(250000)
        sat=solver.solve_limited(expect_interrupt=True)
        if sat is None:
            log["status"]="UNKNOWN_CONFLICT_BUDGET";break
        if sat is False:
            log["status"]="UNSAT_NEEDS_INDEPENDENT_NATIVE_PROOF";persist()
            verify_native_negative();break
        ml={i for i in solver.get_model() if i>0}
        a={e for e in edges if idx[e] in ml}
        b=E-a
        pa=planar(a);pb=planar(b)
        if pa and pb:
            positive(a,b);break
        added=0
        for layer,okay in [(a,pa),(b,pb)]:
            if okay:continue
            H=nx.Graph(layer)
            for _ in range(5):
                ok,c=nx.check_planarity(H,counterexample=True)
                if ok:break
                k=tuple(sorted(map(ecanon,c.edges())))
                if addcut(k):added+=1
                # Image lemmas under graph automorphisms remain sound.
                for perm in rng.sample(perms,min(6,len(perms))):
                    if addcut([perm[e] for e in k]):added+=1
                H.remove_edge(*rng.choice(k))
        if not added:
            log["status"]="UNKNOWN_DUPLICATE_CUT_STALL";break
        log["new_lemmas"]+=added;log["iterations"]=it
        if it%40==0:
            persist();cutarchive()
            print("S019_SYM_PROGRESS",json.dumps({"iterations":it,
                "cuts":len(cuts),"elapsed":round(time.monotonic()-start,1),
                "rss":log["maxrss_mib"]}),flush=True)
    else:log["status"]="UNKNOWN_TIME_CAP"
    persist();cutarchive()
except Exception as err:
    log["status"]="ERROR";log["error"]=repr(err)
    log["traceback"]=traceback.format_exc()[-3500:]
    persist();cutarchive();raise
finally:
    print("S019_SYM_FINAL",json.dumps({k:log.get(k) for k in
      ("status","iterations","loaded_lemmas","new_direct_K5",
      "new_lemmas","positive","negative_proof_checked","elapsed_s","maxrss_mib")}),flush=True)
    solver.delete()
