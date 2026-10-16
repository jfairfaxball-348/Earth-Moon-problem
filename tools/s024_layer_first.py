#!/usr/bin/env python3
"""S024 preregistered planar-layer-first exploratory campaign. Only run AFTER full cloud_smoke.
All scientific outputs are lower-strength exploratory unless independent UNSAT proof checks pass.
"""
import hashlib, itertools, json, random, subprocess, sys, time
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/tmp/S024"
PLAN = {"seeds": [24001, 24002, 24003, 24004, 24005, 24006],
        "orders": [22, 28, 36], "flips_per_trial": 2800,
        "sat_wall_seconds": 30, "single_worker": True, "ram_cap_GiB": 12}
def edge(u, v): return (min(u, v), max(u, v))
def eh(E):
    s = "".join("%d %d\n" % e for e in sorted(E))
    return hashlib.sha256(s.encode("ascii")).hexdigest()
def stacked(n, rng):
    E = {edge(u,v) for u in range(4) for v in range(u+1,4)}
    F = {tuple(sorted(t)) for t in itertools.combinations(range(4), 3)}
    for v in range(4,n):
        tri = rng.choice(sorted(F))
        F.remove(tri)
        for u in tri: E.add(edge(u,v))
        for a,b in itertools.combinations(tri,2): F.add(tuple(sorted((a,b,v))))
    return E,F
def rename(E,F,a,b):
    def mv(v): return b if v==a else (a if v==b else v)
    return {edge(mv(u),mv(v)) for u,v in E}, {tuple(sorted(mv(v) for v in t)) for t in F}
def flip(E,F,rng):
    uv = rng.choice(tuple(sorted(E)))
    fs = [t for t in F if uv[0] in t and uv[1] in t]
    assert len(fs)==2, ("face incidence", uv,fs)
    a = next(v for v in fs[0] if v not in uv)
    b = next(v for v in fs[1] if v not in uv)
    ab = edge(a,b)
    if a==b or ab in E: return None
    return uv,ab,fs, {tuple(sorted((a,b,uv[0]))),tuple(sorted((a,b,uv[1])))}
def hunt(n,seed,steps):
    rng = random.Random(seed*100+n)
    first,_ = stacked(n,rng)
    second,faces = stacked(n,rng)
    perm=list(range(n));rng.shuffle(perm)
    second={edge(perm[u],perm[v]) for u,v in second}
    faces={tuple(sorted(perm[v] for v in f)) for f in faces}
    overlap=len(first & second)
    best=(overlap,second.copy(),faces.copy())
    accepted=0
    for i in range(steps):
        if i%11==0:
            a,b=rng.sample(range(n),2)
            newE,newF=rename(second,faces,a,b)
            newoverlap=len(first & newE)
        else:
            move=flip(second,faces,rng)
            if move is None: continue
            old,new,oldfs,newfs=move
            newoverlap=overlap-int(old in first)+int(new in first)
        if newoverlap<=overlap or rng.random() < (0.03 if newoverlap==overlap+1 else 0.001):
            if i%11==0: second,faces=newE,newF
            else:
                second.remove(old); second.add(new)
                faces.difference_update(oldfs);faces.update(newfs)
            accepted+=1;overlap=newoverlap
            if overlap < best[0]:best=(overlap,second.copy(),faces.copy())
            if overlap==0:break
    return first,best[1],best[0],accepted,i+1
def rotation_test(n,E,rot):
    # Independent combinatorial rotation-system validation, no NetworkX calls.
    assert len(E)==3*n-6 and len(rot)==n
    assert all(len(rot[str(u)])>=3 and len(rot[str(u)])==len(set(rot[str(u)])) for u in range(n))
    darts={(u,v) for u,v in E}|{(v,u) for u,v in E}
    for u in range(n):
        assert set(rot[str(u)])=={v for v in range(n) if edge(u,v) in E}
    seen=set();faces=[]
    for st in sorted(darts):
        if st in seen:continue
        walk=[];u,v=st
        while (u,v) not in seen:
            seen.add((u,v));walk.append((u,v))
            nbr=rot[str(v)]
            w=nbr[(nbr.index(u)-1)%len(nbr)]
            u,v=v,w
        assert (u,v)==st, ("nonfacial walk",st)
        assert len(walk)==3
        faces.append(walk)
    assert seen==darts and len(faces)==2*n-4 and n-len(E)+len(faces)==2
    return len(faces)
def layer(n,E):
    g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(E)
    planar,embedding=nx.check_planarity(g)
    if not planar:raise AssertionError("Nonplanar supposed triangulation")
    rot={str(u):list(embedding.neighbors_cw_order(u)) for u in range(n)}
    f=rotation_test(n,E,rot)
    return {"edges":[list(e) for e in sorted(E)],"rotation":rot,
            "edges_sha256":eh(E),"rotation_faces":f}
def color_cnf(n,E,k):
    clauses=[]
    for v in range(n):
        clauses.append([v*k+c+1 for c in range(k)])
        for a in range(k):
            for b in range(a+1,k):
                clauses.append([-(v*k+a+1),-(v*k+b+1)])
    for u,v in sorted(E):
        for c in range(k):
            clauses.append([-(u*k+c+1),-(v*k+c+1)])
    return "p cnf %d %d\n" % (n*k,len(clauses))+"".join(" ".join(map(str,x))+" 0\n" for x in clauses)
def colouring(n,E,k,tag):
    inp=OUT/(tag+"-k%d.cnf"%k);proof=OUT/(tag+"-k%d.drat"%k)
    inp.write_text(color_cnf(n,E,k))
    native=ROOT/"artifacts/tmp/native/bin/cadical"
    try: rr=subprocess.run([str(native),str(inp),str(proof)],
            text=True,capture_output=True,timeout=PLAN["sat_wall_seconds"])
    except subprocess.TimeoutExpired:
        return {"status":"TIMEOUT_UNKNOWN","cnf_sha256":hashlib.sha256(inp.read_bytes()).hexdigest()}
    rec={"solver_rc":rr.returncode, "cnf_sha256":hashlib.sha256(inp.read_bytes()).hexdigest()}
    if rr.returncode==10:
        ints=[]
        for line in rr.stdout.splitlines():
            if line.startswith("v "):
                ints.extend(int(x) for x in line[2:].split() if x!="0")
        positives=set(x for x in ints if x>0)
        col=[]
        for v in range(n):
            cs=[c for c in range(k) if v*k+c+1 in positives]
            if len(cs)!=1:return {**rec,"status":"SAT_MODEL_MISSING_OR_INVALID"}
            col.append(cs[0])
        assert all(col[u]!=col[v] for u,v in E)
        return {**rec,"status":"SAT_COLOURING_INDEPENDENTLY_CHECKED","colours":col,"num_used":len(set(col))}
    if rr.returncode==20 and proof.exists():
        checker=ROOT/"artifacts/tmp/native/bin/drat-trim"
        try: ck=subprocess.run([str(checker),str(inp),str(proof),"-t","90"],
                    text=True,capture_output=True,timeout=100)
        except subprocess.TimeoutExpired:return {**rec,"status":"UNSAT_CHECK_TIMEOUT_UNKNOWN"}
        rec.update({"checker_rc":ck.returncode,"proof_sha256":hashlib.sha256(proof.read_bytes()).hexdigest()})
        if ck.returncode==0 and "s VERIFIED" in ck.stdout:
            rec["status"]="UNSAT_DRAT_CHECKED"
            return rec
        return {**rec,"status":"UNSAT_UNVERIFIED"}
    return {**rec,"status":"SOLVER_UNKNOWN_OR_INVALID"}
def triple(n,E):
    for a,b,c in itertools.combinations(range(n),3):
        if all(edge(u,v) not in E for u,v in [(a,b),(a,c),(b,c)]):
            return [a,b,c]
    return None
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert (ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").exists(), "cold smoke missing"
    smoke=json.loads((ROOT/"artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke.get("verdict")=="PASS" and smoke.get("chromatic_rows_verified")==271, "full cold smoke not PASS"
    rows=[]
    for n in PLAN["orders"]:
        for seed in PLAN["seeds"]:
            t=time.monotonic()
            E1,E2,overlap,accepted,steps=hunt(n,seed,PLAN["flips_per_trial"])
            row={"n":n,"seed":seed,"overlap":overlap,"accepted":accepted,"steps":steps,
                "edge_hash_first":eh(E1),"edge_hash_second":eh(E2),
                "seconds":round(time.monotonic()-t,2)}
            if not overlap:
                L1=layer(n,E1);L2=layer(n,E2)
                union=E1|E2
                row["edge_count"]=len(union);row["alpha_at_least_three_witness"]=triple(n,union)
                row["rotation_test"]="PASS_TWO_INDEPENDENT_COMBINATORIAL_REPLAYS"
                tag=f"n{n}-seed{seed}"
                row["sat9"]=colouring(n,union,9,tag)
                if row["sat9"]["status"]=="UNSAT_DRAT_CHECKED":
                    row["sat10"]=colouring(n,union,10,tag)
                (OUT/(tag+".json")).write_text(json.dumps({"n":n,"layer1":L1,"layer2":L2,"result":row},indent=2))
            rows.append(row)
            (OUT/"SUMMARY.json").write_text(json.dumps({"preregistration":PLAN,
                 "trials":rows, "scope":"S024 exploratory; every unknown remains unknown"},indent=2))
            print(json.dumps(row),flush=True)
    print("S024 completed",len(rows),"trials",flush=True)
if __name__=="__main__":main()
