#!/usr/bin/env python3
"""S011 CAM-0012 positive-only biplanar split search. No negative classification."""
import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blowup_graph import blowup
from check_layers import certify_layer

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def planar(g):
    return nx.check_planarity(g, counterexample=False)[0]


def build_trial(n, edges, rng):
    """Random greedy partial planar partition, not a decision procedure."""
    a, b = nx.Graph(), nx.Graph()
    a.add_nodes_from(range(n))
    b.add_nodes_from(range(n))
    missing = []
    order = list(edges)
    rng.shuffle(order)
    for e in order:
        # Favor the currently smaller layer; random tie-breaking.
        if a.number_of_edges() < b.number_of_edges():
            choices = (a, b)
        elif b.number_of_edges() < a.number_of_edges():
            choices = (b, a)
        else:
            choices = (a, b) if rng.randrange(2) else (b, a)
        inserted = False
        for layer in choices:
            layer.add_edge(*e)
            if planar(layer):
                inserted = True
                break
            layer.remove_edge(*e)
        if not inserted:
            missing.append(e)
    return a, b, missing


def single_transfer_repair(a, b, missing, deadline, rng, maximum=16):
    """One-edge ejection attempt. Success only after complete independent recheck."""
    still = []
    for e in missing:
        if time.monotonic() >= deadline or len(still) >= maximum:
            still.append(e)
            continue
        fixed = False
        options = [(a, b), (b, a)]
        rng.shuffle(options)
        for target, other in options:
            target.add_edge(*e)
            ok, kur = nx.check_planarity(target, counterexample=True)
            if ok:
                fixed = True
                break
            target.remove_edge(*e)
            witnesses = list(kur.edges())
            rng.shuffle(witnesses)
            for f in witnesses[:24]:
                if not target.has_edge(*f):
                    continue
                target.remove_edge(*f)
                target.add_edge(*e)
                other.add_edge(*f)
                if planar(target) and planar(other):
                    fixed = True
                    break
                other.remove_edge(*f)
                target.remove_edge(*e)
                target.add_edge(*f)
            if fixed:
                break
        if not fixed:
            still.append(e)
    return still


def check_complete(rowid, n, edges, a, b, colouring, out):
    target = set(edges)
    first = {tuple(sorted(e)) for e in a.edges()}
    second = {tuple(sorted(e)) for e in b.edges()}
    assert first.isdisjoint(second)
    assert first | second == target
    assert all(0 <= u < v < n for u, v in target)
    assert len(colouring) == n and len(set(colouring)) == 10
    assert all(colouring[u] != colouring[v] for u, v in target)
    faces = [certify_layer(n, sorted(first)), certify_layer(n, sorted(second))]
    record = {
        "source": "S003 candidate row", "index": rowid,
        "num_vertices": n, "chromatic_number": 10,
        "edges_part1": [list(e) for e in sorted(first)],
        "edges_part2": [list(e) for e in sorted(second)],
        "coloring": colouring, "independently_checked_component_faces": faces,
        "chromatic_lower": "S004 DRAT requires separate cold verification",
        "status": "PROVISIONAL_PENDING_FULL_COLD_CERTIFICATE"
    }
    Path(out).with_name("provisional_split.json").write_text(json.dumps(record, indent=2))
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=300)
    ap.add_argument("--seed", type=int, default=11011)
    ap.add_argument("--output", default="artifacts/tmp/S011/heuristic_result.json")
    args = ap.parse_args()
    assert args.seconds == 300 and args.seed == 11011, "CAM-0012 exact caps/seed"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    smoke = json.loads(Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke["verdict"] == "PASS" and smoke["chromatic_rows_verified"] == 271
    assert smoke["chromatic_cnf_byte_matches"] == 271
    assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    env = json.loads(Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
    sources = ["validation/S003/survivors_alpha_ge3.json",
               "validation/S010/SUMMARY.json", "validation/S004/chi10_results.json",
               "tools/blowup_graph.py", "tools/check_layers.py",
               "tools/check_rotation.py", "tools/s011_positive_search.py",
               "campaigns/CAM-0012.md",
               ".github/workflows/s011-research.yml"]
    hashes = {p: digest(p) for p in sources}
    corpus = json.loads(Path(sources[0]).read_text())
    summary = json.loads(Path(sources[1]).read_text())
    colours = json.loads(Path(sources[2]).read_text())
    excluded = set(summary["excluded_indices"])
    assert len(corpus) == 271 and len(excluded) == 52
    inputs = {}
    for i in range(271):
        if i in excluded:
            continue
        edges, _ = blowup(corpus[i][0], corpus[i][1])
        n = sum(corpus[i][1])
        assert len(set(edges)) == len(edges)
        inputs[i] = (n, edges)
    assert len(inputs) == 219
    # Most density slack first, deterministic ties. Never a completeness claim.
    ordered = sorted(inputs, key=lambda i: (len(inputs[i][1]) / (6 * inputs[i][0] - 12), i))
    start = time.monotonic()
    deadline = start + args.seconds
    results = {i: {"status": "NOT_RUN", "trials": 0,
                   "best_missing": len(inputs[i][1])} for i in ordered}
    log = {"campaign": "CAM-0012", "scope": "POSITIVE_HEURISTIC_ONLY",
           "preregistered_seed": args.seed, "cap_seconds": args.seconds,
           "input_rows": len(corpus), "excluded_rows": len(excluded),
           "unknown_rows": len(inputs),
           "source_sha256": hashes, "environment_native_sha256": env["native_sha256"],
           "smoke": {"verdict": smoke["verdict"],
                     "chromatic_checked": smoke["chromatic_rows_verified"],
                     "k9": smoke["k9"]["verified"],
                     "fresh_k9": smoke["solver_roundtrip"]["fresh_proof_verified"]},
           "python": sys.version, "platform": platform.platform(),
           "stage": "starting", "rows": results}
    output.write_text(json.dumps(log, indent=2))
    best_trial = {}
    witness = None
    # Two deterministic full sweeps if time permits, no worker beyond time cap.
    for sweep in range(2):
        for i in ordered:
            if time.monotonic() >= deadline - 5:
                break
            n, edges = inputs[i]
            rng = random.Random(args.seed + 9973 * sweep + i)
            a, b, missing = build_trial(n, edges, rng)
            r = results[i]
            r["trials"] += 1
            r["status"] = "ATTEMPTED_BIPLANARITY_UNKNOWN"
            if len(missing) < r["best_missing"]:
                r["best_missing"] = len(missing)
                best_trial[i] = (a.copy(), b.copy(), list(missing))
            if not missing:
                witness = check_complete(i, n, edges, a, b,
                                         colours[i]["ten_colouring"], output)
                break
        log["stage"] = f"sweep_{sweep + 1}_completed_or_capped"
        log["elapsed_seconds"] = round(time.monotonic() - start, 2)
        output.write_text(json.dumps(log, indent=2))
        if witness is not None or time.monotonic() >= deadline - 5:
            break
    # Intensify only candidates with fewest missing edges.
    repaired = []
    if witness is None:
        ranked = sorted(best_trial, key=lambda i: (results[i]["best_missing"], i))
        for i in ranked[:25]:
            if time.monotonic() >= deadline - 5:
                break
            n, edges = inputs[i]
            a, b, missing = best_trial[i]
            if len(missing) > 24:
                continue
            rng = random.Random(args.seed + i + 550000)
            left = single_transfer_repair(a, b, missing, deadline - 5, rng)
            results[i]["repair_attempted"] = True
            results[i]["best_missing"] = min(results[i]["best_missing"], len(left))
            repaired.append(i)
            if not left:
                witness = check_complete(i, n, edges, a, b,
                                         colours[i]["ten_colouring"], output)
                break
    log["repaired_rows"] = repaired
    log["elapsed_seconds"] = round(time.monotonic() - start, 2)
    log["number_rows_attempted"] = sum(v["trials"] > 0 for v in results.values())
    log["total_greedy_trials"] = sum(v["trials"] for v in results.values())
    log["best_missing_edges"] = min(v["best_missing"] for v in results.values())
    log["top_partial"] = [
        {"row": i, "n": inputs[i][0], "m": len(inputs[i][1]),
         "best_missing": results[i]["best_missing"], "trials": results[i]["trials"]}
        for i in sorted(results, key=lambda j: (results[j]["best_missing"], j))[:20]
    ]
    log["provisional_split_found"] = witness is not None
    log["verdict"] = ("PROVISIONAL_SPLIT_NEEDS_COLD_CERTIFICATE" if witness
                      else "NO_WITNESS_FOUND; ALL_UNRESOLVED_ROWS_REMAIN_UNKNOWN")
    log["stage"] = "finished"
    output.write_text(json.dumps(log, indent=2))
    print(json.dumps({k: log[k] for k in
                      ("verdict", "elapsed_seconds", "number_rows_attempted",
                       "total_greedy_trials", "best_missing_edges", "top_partial")},
                     indent=2), flush=True)


if __name__ == "__main__":
    main()
