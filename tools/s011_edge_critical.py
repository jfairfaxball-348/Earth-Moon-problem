#!/usr/bin/env python3
"""CAM-0014 enumerate every edge of six fixed chi10 rows with positive 9-colour witnesses."""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import resource
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blowup_graph import blowup
from s011_sparsify_search import cnf

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
TARGETS = [2, 55, 59, 61, 199, 200]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def solve_worker(n, edges, q):
    resource.setrlimit(resource.RLIMIT_AS, (1<<30,1<<30))
    try:
        from pysat.solvers import Cadical153
        with Cadical153(bootstrap_with=cnf(n, edges)) as solver:
            if not solver.solve():
                q.put({"verdict":"UNSAT_UNCERTIFIED"})
                return
            positives = {x for x in solver.get_model() if x > 0}
            colors = []
            for v in range(n):
                choices = [c for c in range(9) if 9*v+c+1 in positives]
                if len(choices)!=1:
                    q.put({"verdict":"INVALID_MODEL"})
                    return
                colors.append(choices[0])
            q.put({"verdict":"SAT","colors":colors})
    except BaseException as e:
        q.put({"verdict":"ERROR_"+type(e).__name__})


def bounded_solve(n, edges):
    ctx = mp.get_context("fork")
    q = ctx.Queue()
    proc = ctx.Process(target=solve_worker, args=(n, edges, q))
    proc.start()
    proc.join(5)
    if proc.is_alive():
        proc.terminate()
        proc.join(1)
        if proc.is_alive():
            proc.kill()
            proc.join()
        return {"verdict":"TIMEOUT"}
    try:
        return q.get(timeout=.5)
    except BaseException:
        return {"verdict":"ERROR_NO_RESULT"}


def run():
    ap=argparse.ArgumentParser()
    ap.add_argument("--seconds",type=int,default=240)
    ap.add_argument("--output",default="artifacts/tmp/S011/edge_critical.json")
    a=ap.parse_args()
    assert a.seconds==240
    dest=Path(a.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    smoke=json.loads(Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke["verdict"]=="PASS" and smoke["chromatic_rows_verified"]==271
    assert smoke["chromatic_cnf_byte_matches"]==271
    assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    env=json.loads(Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
    source_files=["validation/S003/survivors_alpha_ge3.json",
        "validation/S010/SUMMARY.json","validation/S004/chi10_results.json",
        "tools/blowup_graph.py","tools/s011_sparsify_search.py",
        "tools/s011_edge_critical.py","tools/s011_edgecheck.py",
        "campaigns/CAM-0014.md",".github/workflows/s011-edge-critical.yml"]
    sources={fn:sha(fn) for fn in source_files}
    corpus=json.loads(Path(source_files[0]).read_text())
    summary=json.loads(Path(source_files[1]).read_text())
    colours=json.loads(Path(source_files[2]).read_text())
    assert len(corpus)==271 and all(i in summary["remaining_unknown_indices"] for i in TARGETS)
    start=time.monotonic()
    deadline=start+a.seconds
    report={"campaign":"CAM-0014","registered_fixed_indices":TARGETS,
        "enumeration_scope":"all single-edge deletions of six fixed chi10 rows",
        "cap_seconds":a.seconds,"cold_smoke":smoke["verdict"],
        "native_sha256":env["native_sha256"],"source_sha256":sources,
        "python":sys.version,"platform":platform.platform(),"rows":[],
        "independent_checker_expected_complete":[],"verdict":"RUNNING"}
    dest.write_text(json.dumps(report,indent=2))
    for index in TARGETS:
        n_edges, _=blowup(corpus[index][0],corpus[index][1])
        n=sum(corpus[index][1])
        edges=sorted(n_edges)
        colors10=colours[index]["ten_colouring"]
        assert len(set(edges))==len(edges) and len(colors10)==n
        assert all(colors10[u]!=colors10[v] for u,v in edges)
        row={"index":index,"n":n,"m":len(edges),"witnesses":[],
             "status":"IN_PROGRESS","solver_status_counts":{}}
        report["rows"].append(row)
        for edge in edges:
            if time.monotonic()>=deadline-3:
                row["status"]="UNKNOWN_CAP"
                break
            remaining=[e for e in edges if e!=edge]
            ans=bounded_solve(n,remaining)
            status=ans["verdict"]
            row["solver_status_counts"][status]=row["solver_status_counts"].get(status,0)+1
            if status!="SAT":
                row["status"]="UNKNOWN_"+status
                break
            colors=ans["colors"]
            assert len(colors)==n and all(isinstance(c,int) and 0<=c<9 for c in colors)
            assert all(colors[u]!=colors[v] for u,v in remaining)
            assert colors[edge[0]]==colors[edge[1]]
            row["witnesses"].append({"edge":list(edge),"colors":colors})
        if row["status"]=="IN_PROGRESS":
            assert len(row["witnesses"])==len(edges)
            row["status"]="COMPLETE"
            report["independent_checker_expected_complete"].append(index)
        report["elapsed_seconds"]=round(time.monotonic()-start,2)
        dest.write_text(json.dumps(report,indent=2))
    assert len(report["rows"])==len(TARGETS)
    report["elapsed_seconds"]=round(time.monotonic()-start,2)
    report["verdict"]="WITNESSES_CREATED_PENDING_INDEPENDENT_CHECK"
    dest.write_text(json.dumps(report,indent=2))
    print(json.dumps({"verdict":report["verdict"],
        "elapsed_seconds":report["elapsed_seconds"],
        "per_row":[{"index":z["index"],"n":z["n"],"m":z["m"],
                    "status":z["status"],"witnesses":len(z["witnesses"])}
                   for z in report["rows"]],
        "native_sha256":env["native_sha256"],
        "source_sha256":sources},indent=2),flush=True)


if __name__=="__main__":
    run()
