#!/usr/bin/env python3
"""S011 CAM-0013 experimental chromatic-preserving edge pruning then positive split."""
import argparse
import fractions
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blowup_graph import blowup
from s011_positive_search import build_trial, single_transfer_repair, check_complete

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cnf(n, edges):
    """Uncompressed, unambiguous 9-colour vertex CNF; no bag abstraction."""
    x = lambda v, c: 9 * v + c + 1
    clauses = [[x(v, c) for c in range(9)] for v in range(n)]
    for v in range(n):
        for a in range(9):
            for b in range(a + 1, 9):
                clauses.append([-x(v, a), -x(v, b)])
    for u, v in edges:
        for c in range(9):
            clauses.append([-x(u, c), -x(v, c)])
    clauses.append([x(0, 0)])  # sound colour-permutation breaking
    return clauses


def sat_worker(n, edges, q):
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    try:
        from pysat.solvers import Cadical153
        with Cadical153(bootstrap_with=cnf(n, edges)) as s:
            q.put("SAT" if s.solve() else "UNSAT_UNCERTIFIED")
    except BaseException as e:
        q.put("ERROR_" + type(e).__name__)


def bounded_sat(n, edges, seconds=3):
    ctx = mp.get_context("fork")
    q = ctx.Queue()
    p = ctx.Process(target=sat_worker, args=(n, edges, q))
    p.start()
    p.join(seconds)
    if p.is_alive():
        p.terminate()
        p.join(1)
        if p.is_alive():
            p.kill()
            p.join()
        return "TIMEOUT"
    try:
        return q.get(timeout=.3)
    except Exception:
        return "ERROR_EMPTY_RESPONSE"


def write_cnf(path, n, edges):
    clauses = cnf(n, edges)
    with Path(path).open("w") as f:
        f.write(f"p cnf {9*n} {len(clauses)}\n")
        for row in clauses:
            f.write(" ".join(map(str, row)) + " 0\n")


def final_native_certificate(out, i, n, edges, a, b, colouring, env):
    """Any found split remains provisional until complete proof and independent cold layers."""
    outdir = Path(out).parent
    record = check_complete(i, n, edges, a, b, colouring, out)
    cnfpath = outdir / "found_non9.cnf"
    drat = outdir / "found_non9.drat"
    write_cnf(cnfpath, n, edges)
    cadical = Path("artifacts/tmp/native/bin/cadical")
    trim = Path("artifacts/tmp/native/bin/drat-trim")
    assert sha(cadical) == env["native_sha256"]["cadical"]
    assert sha(trim) == env["native_sha256"]["drat-trim"]
    result = {"candidate_row": i, "cnf_sha256": sha(cnfpath)}
    try:
        solve = subprocess.run([str(cadical), "-q", "--no-binary",
                                str(cnfpath), str(drat)],
                               capture_output=True, text=True, timeout=90)
        result["native_cadical_exit"] = solve.returncode
        if solve.returncode == 20:
            result["drat_sha256"] = sha(drat)
            checked = subprocess.run([str(trim), str(cnfpath), str(drat), "-t", "90"],
                                     capture_output=True, text=True, timeout=90)
            result["drat_checker_exit"] = checked.returncode
            result["drat_verified"] = (checked.returncode == 0 and
                                        "s VERIFIED" in checked.stdout)
            result["drat_checker_tail"] = checked.stdout[-500:]
        else:
            result["drat_verified"] = False
    except subprocess.TimeoutExpired:
        result["drat_verified"] = False
        result["native_timeout"] = True
    edgefile, splitfile = outdir / "found.edges", outdir / "found.split.json"
    edgefile.write_text("".join(f"{u} {v}\n" for u, v in sorted(edges)))
    splitfile.write_text(json.dumps({
        "n": n, "E1": sorted(tuple(sorted(e)) for e in a.edges()),
        "E2": sorted(tuple(sorted(e)) for e in b.edges())}))
    layer = subprocess.run([sys.executable, "tools/check_layers.py",
                            str(edgefile), str(splitfile)],
                           capture_output=True, text=True, timeout=30)
    result["independent_layer_check_exit"] = layer.returncode
    result["independent_layer_check_stdout"] = layer.stdout.strip()
    result["accepted"] = bool(result.get("drat_verified") and layer.returncode == 0)
    if result["accepted"]:
        record["status"] = "CERTIFIED_CHI10_BIPLANAR_CHECK_FRESH_REVIEW"
        record["no_9_coloring_D​RAT_sha256"] = sha(drat)
        record["CNF_sha256"] = sha(cnfpath)
        Path(out).with_name("certified_split.json").write_text(json.dumps(record, indent=2))
        with gzip.open(outdir / "found_non9.drat.gz", "wb") as handle:
            handle.write(drat.read_bytes())
    (outdir / "certification_status.json").write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=280)
    parser.add_argument("--seed", type=int, default=13113)
    parser.add_argument("--output", default="artifacts/tmp/S011/sparsify_result.json")
    args = parser.parse_args()
    assert (args.seconds, args.seed) == (280, 13113)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    smoke = json.loads(Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke["verdict"] == "PASS" and smoke["chromatic_rows_verified"] == 271
    assert smoke["chromatic_cnf_byte_matches"] == 271
    assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    env = json.loads(Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
    files = ["validation/S003/survivors_alpha_ge3.json",
             "validation/S010/SUMMARY.json", "validation/S004/chi10_results.json",
             "tools/blowup_graph.py", "tools/check_layers.py", "tools/check_rotation.py",
             "tools/s011_positive_search.py", "tools/s011_sparsify_search.py",
             "campaigns/CAM-0013.md", ".github/workflows/s011-sparsify.yml"]
    inputs = {p: sha(p) for p in files}
    corpus = json.loads(Path(files[0]).read_text())
    summary = json.loads(Path(files[1]).read_text())
    colour = json.loads(Path(files[2]).read_text())
    excluded = set(summary["excluded_indices"])
    choices = []
    for i in range(len(corpus)):
        if i in excluded:
            continue
        edges, _ = blowup(*corpus[i][:2])
        n = sum(corpus[i][1])
        choices.append((fractions.Fraction(len(edges), 6 * n - 12), i, n, edges))
    assert len(choices) == 219
    chosen = sorted(choices)[:6]
    report = {
        "campaign": "CAM-0013", "positive_heuristic_only": True,
        "time_cap_seconds": args.seconds, "seed": args.seed,
        "source_sha256": inputs, "native_sha256": env["native_sha256"],
        "cold_smoke": smoke["verdict"], "chosen_rows": [x[1] for x in chosen],
        "rows": [], "verdict": "IN_PROGRESS"}
    out.write_text(json.dumps(report, indent=2))
    start = time.monotonic()
    deadline = start + args.seconds
    witness = None
    for _, i, n, original in chosen:
        if time.monotonic() >= deadline - 10:
            report["rows"].append({"index": i, "status": "NOT_RUN"})
            continue
        rnd = random.Random(args.seed + 59 * i)
        order = list(original)
        rnd.shuffle(order)
        remaining = set(original)
        timeouts = 0
        removed = 0
        sat_results = {"SAT": 0, "UNSAT_UNCERTIFIED": 0, "TIMEOUT": 0, "ERROR": 0}
        for e in order[:40]:
            if time.monotonic() >= deadline - 10 or timeouts >= 2:
                break
            subset = sorted(remaining - {e})
            verdict = bounded_sat(n, subset, 3)
            if verdict == "UNSAT_UNCERTIFIED":
                remaining.remove(e)
                removed += 1
                timeouts = 0
                sat_results["UNSAT_UNCERTIFIED"] += 1
            elif verdict == "SAT":
                timeouts = 0
                sat_results["SAT"] += 1
            else:
                timeouts += 1
                sat_results["TIMEOUT" if verdict == "TIMEOUT" else "ERROR"] += 1
        pruned = sorted(remaining)
        best = len(pruned)
        record = {"index": i, "n": n, "original_edges": len(original),
                  "remaining_edges": len(pruned), "tentatively_removed": removed,
                  "edge_attempts": sum(sat_results.values()),
                  "trial_counts": sat_results,
                  "chromatic_status": "UNSAT_EXPLORATORY_NOT_PROOF",
                  "best_unplaced": best, "greedy_trials": 0,
                  "status": "BIPLANARITY_UNKNOWN"}
        for trial in range(4):
            if time.monotonic() >= deadline - 10:
                break
            seed = args.seed + i + 747 * trial
            a, b, missing = build_trial(n, pruned, random.Random(seed))
            record["greedy_trials"] += 1
            if len(missing) < record["best_unplaced"]:
                record["best_unplaced"] = len(missing)
            if 0 < len(missing) <= 24 and trial == 3:
                missing = single_transfer_repair(a, b, missing, deadline-10,
                                                 random.Random(seed + 1))
                record["best_unplaced"] = min(record["best_unplaced"], len(missing))
            if not missing:
                witness = final_native_certificate(out, i, n, pruned, a, b,
                                                  colour[i]["ten_colouring"], env)
                record["certification"] = witness
                record["status"] = "ACCEPTED" if witness["accepted"] else "PROVISIONAL"
                break
        report["rows"].append(record)
        report["elapsed_seconds"] = round(time.monotonic() - start, 2)
        out.write_text(json.dumps(report, indent=2))
        if witness is not None:
            break
    for _, i, _, _ in chosen:
        if not any(x["index"] == i for x in report["rows"]):
            report["rows"].append({"index": i, "status": "NOT_RUN"})
    report["elapsed_seconds"] = round(time.monotonic() - start, 2)
    report["verdict"] = ("FULL_CERTIFICATE_WITNESS_FOUND" if witness and witness["accepted"]
                         else "NO_CERTIFIED_WITNESS_FOUND; ALL_TARGETS_REMAIN_UNRESOLVED")
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps({
        "verdict": report["verdict"], "rows": report["rows"],
        "elapsed_seconds": report["elapsed_seconds"], "source_sha256": inputs,
        "native_sha256": env["native_sha256"]
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
