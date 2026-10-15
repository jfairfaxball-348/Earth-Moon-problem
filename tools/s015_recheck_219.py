#!/usr/bin/env python3
"""S015 CAM-0017 intensified positive-only biplanar split search. No negative classification."""
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


def build_trial(n, edges, rng, mode=0):
    """Random greedy partial planar partition, not a decision procedure."""
    a, b = nx.Graph(), nx.Graph()
    a.add_nodes_from(range(n))
    b.add_nodes_from(range(n))
    missing = []
    order = list(edges)
    if mode == 0:
        rng.shuffle(order)
    else:
        degrees = [0] * n
        for u, v in edges:
            degrees[u] += 1
            degrees[v] += 1
        multiplier = -1 if mode == 1 else 1
        order.sort(key=lambda e: multiplier * (degrees[e[0]] + degrees[e[1]]) + rng.random() * 8)
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



def double_ejection(a, b, missing, rng, deadline):
    """Kuratowski-based ejection with a second repair edge; positive-only."""
    for e in list(missing):
        if time.monotonic() > deadline:
            break
        found = None
        for target in [0, 1]:
            x, y = (a, b) if target == 0 else (b, a)
            gx = x.copy()
            gx.add_edge(*e)
            is_ok, k = nx.check_planarity(gx, counterexample=True)
            if is_ok:
                found = (gx, y.copy(), target)
                break
            first = [tuple(sorted(edge)) for edge in k.edges() if tuple(sorted(edge)) != e]
            rng.shuffle(first)
            for f in first[:16]:
                if time.monotonic() > deadline:
                    break
                x2, y2 = gx.copy(), y.copy()
                x2.remove_edge(*f)
                if not planar(x2):
                    continue
                y2.add_edge(*f)
                is_ok2, k2 = nx.check_planarity(y2, counterexample=True)
                if is_ok2:
                    found = (x2, y2, target)
                    break
                second = [tuple(sorted(edge)) for edge in k2.edges() if tuple(sorted(edge)) != f]
                rng.shuffle(second)
                for g in second[:10]:
                    x3, y3 = x2.copy(), y2.copy()
                    y3.remove_edge(*g)
                    x3.add_edge(*g)
                    if planar(x3) and planar(y3):
                        found = (x3, y3, target)
                        break
                if found:
                    break
            if found:
                break
        if found:
            x, y, target = found
            a, b = (x, y) if target == 0 else (y, x)
            missing.remove(e)
    return a, b, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=680)
    ap.add_argument("--seed", type=int, default=15015)
    ap.add_argument("--output", default="artifacts/tmp/S015/search_result.json")
    args = ap.parse_args()
    assert args.seconds == 680 and args.seed == 15015, "CAM-0017 preregistered parameters"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    smoke = json.loads(Path("artifacts/tmp/cloud_smoke/RESULT.json").read_text())
    assert smoke["verdict"] == "PASS" and smoke["chromatic_rows_verified"] == 271
    assert smoke["chromatic_cnf_byte_matches"] == 271
    assert smoke["k9"]["verified"] and smoke["solver_roundtrip"]["fresh_proof_verified"]
    env = json.loads(Path("artifacts/tmp/native/ENVIRONMENT.json").read_text())
    sources = ["validation/S003/survivors_alpha_ge3.json", "validation/S010/SUMMARY.json",
               "validation/S004/chi10_results.json", "tools/blowup_graph.py",
               "tools/check_layers.py", "tools/check_rotation.py",
               "tools/s015_recheck_219.py", "campaigns/CAM-0017.md",
               ".github/workflows/s015-recheck.yml"]
    hashes = {p: digest(p) for p in sources}
    corpus = json.loads(Path(sources[0]).read_text())
    summary = json.loads(Path(sources[1]).read_text())
    colours = json.loads(Path(sources[2]).read_text())
    unknown = summary["remaining_unknown_indices"]
    excluded = summary["excluded_indices"]
    assert len(corpus) == len(colours) == 271
    assert len(unknown) == 219 and len(excluded) == 52
    assert sorted(unknown + excluded) == list(range(271))
    assert len(set(unknown)) == 219 and len(set(excluded)) == 52
    inputs = {}
    for i in unknown:
        edges, _ = blowup(corpus[i][0], corpus[i][1])
        n = sum(corpus[i][1])
        assert len(edges) == len(set(edges))
        inputs[i] = (n, edges)
    start = time.monotonic()
    deadline = start + args.seconds
    results = {}
    for i in unknown:
        n, edges = inputs[i]
        body = json.dumps({"n": n, "edges": edges}, separators=(",", ":")).encode()
        results[str(i)] = {"row_index": i, "graph_sha256": hashlib.sha256(body).hexdigest(),
                           "n": n, "m": len(edges), "status": "NOT_RUN",
                           "trials": 0, "seeds": [], "best_missing": len(edges),
                           "seconds": 0}
    log = {"campaign": "CAM-0017", "session": "S015", "scope": "POSITIVE_HEURISTIC_ONLY",
           "seed": args.seed, "cap_seconds": args.seconds,
           "canonical_unknown_indices": unknown, "excluded_indices": excluded,
           "source_sha256": hashes, "environment_native_sha256": env["native_sha256"],
           "smoke": {"verdict": smoke["verdict"], "chromatic_checked": smoke["chromatic_rows_verified"],
                     "k9": smoke["k9"]["verified"], "fresh_k9": smoke["solver_roundtrip"]["fresh_proof_verified"]},
           "python": sys.version, "platform": platform.platform(), "stage": "starting",
           "rows": results}
    output.write_text(json.dumps(log, indent=2))
    ordered = sorted(unknown, key=lambda i: (len(inputs[i][1]) / (6 * inputs[i][0] - 12), i))
    best = {}
    witness = None
    for sweep in range(3):
        for i in ordered:
            if time.monotonic() >= deadline - 135:
                break
            n, edges = inputs[i]
            seed = args.seed + sweep * 100003 + i * 149
            rng = random.Random(seed)
            t0 = time.monotonic()
            a, b, missing = build_trial(n, edges, rng, mode=sweep)
            row = results[str(i)]
            row["trials"] += 1
            row["seeds"].append(seed)
            row["seconds"] += round(time.monotonic() - t0, 3)
            row["status"] = "ATTEMPTED_STILL_UNKNOWN"
            if len(missing) < row["best_missing"]:
                row["best_missing"] = len(missing)
                best[i] = (a, b, list(missing))
            if not missing:
                witness = check_complete(i, n, edges, a, b, colours[i]["ten_colouring"], output)
                break
        log["stage"] = "breadth_sweep_" + str(sweep + 1)
        log["elapsed_seconds"] = round(time.monotonic() - start, 2)
        output.write_text(json.dumps(log, indent=2))
        if witness is not None or time.monotonic() >= deadline - 135:
            break
    log["breadth_rows_attempted"] = sum(x["trials"] > 0 for x in results.values())
    log["breadth_trials"] = sum(x["trials"] for x in results.values())
    focused = [156] if 156 in best else []
    focused += [i for i in sorted(best, key=lambda k: (results[str(k)]["best_missing"], k))
                if i not in focused]
    log["depth_order"] = focused[:20]
    if witness is None:
        for i in focused[:20]:
            if time.monotonic() >= deadline - 3:
                break
            n, edges = inputs[i]
            a, b, missing = best[i]
            t0 = time.monotonic()
            deadline_row = min(deadline - 3, t0 + 6)
            rng = random.Random(700000 + args.seed + i)
            a, b, missing = double_ejection(a, b, list(missing), rng, deadline_row)
            row = results[str(i)]
            row["depth_two_ejection"] = True
            row["seconds"] += round(time.monotonic() - t0, 3)
            row["best_missing"] = min(row["best_missing"], len(missing))
            if len(missing) == 0:
                witness = check_complete(i, n, edges, a, b, colours[i]["ten_colouring"], output)
                break
            output.write_text(json.dumps(log, indent=2))
    log["stage"] = "finished"
    log["elapsed_seconds"] = round(time.monotonic() - start, 2)
    log["rows_attempted"] = sum(x["trials"] > 0 for x in results.values())
    log["rows_not_run"] = sum(x["trials"] == 0 for x in results.values())
    log["total_greedy_trials"] = sum(x["trials"] for x in results.values())
    log["top_partial"] = [{"row": i, "n": inputs[i][0], "m": len(inputs[i][1]),
                           "missing": results[str(i)]["best_missing"]}
                          for i in sorted(unknown, key=lambda j: (results[str(j)]["best_missing"], j))[:25]]
    log["provisional_split_found"] = witness is not None
    log["verdict"] = ("PROVISIONAL_SPLIT_NEEDS_SECOND_COLD_CERTIFICATE" if witness else
                      "NO_SPLIT_FOUND_NO_NEW_EXCLUSIONS")
    output.write_text(json.dumps(log, indent=2))
    print(json.dumps({k: log[k] for k in ("verdict", "rows_attempted", "rows_not_run",
          "total_greedy_trials", "top_partial", "elapsed_seconds")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
