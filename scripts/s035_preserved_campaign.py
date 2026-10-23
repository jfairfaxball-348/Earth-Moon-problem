"""Adopt S035's four paused native processes without waking legacy controllers.

This controller never launches a solver, removes historical STOP, edits the old
ledger/claims/deadlines, or invokes recovery/termination. It operates a separate
identity registry and preserves every resident on STOP, failure, or natural
solver return. Cold regions stay queued; native UNSAT needs a separate fresh
proof and independent checker before it can close an encoded region.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import uuid

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from s035_windows import atomic_json, read_json, journal, locked, inhibit_sleep, directory_bytes
from s035_preserved_lifecycle import (LifecycleError, identity, checked, thread_counts,
                                      pause_identity, resume_identity, ProcessHandle,
                                      sample_identities)
import s035_thread_policy as thread_policy

DEFAULT = ROOT / "artifacts/tmp/S035/campaign"
SOURCES = ("tools/s035_preserved_lifecycle.py", "scripts/s035_preserved_campaign.py",
           "scripts/s035_sat_first_resume.py", "tools/s035_sat_validation.py", "tools/s035_thread_policy.py")


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sources():
    return {name: sha(ROOT / name) for name in SOURCES}


def plan(area):
    """Read only: documentary identities, parked state and unresolved domain."""
    area = Path(area)
    paused = read_json(area / "OWNER_PAUSE.json")
    frozen = paused["contexts"]["contexts"]
    current = read_json(area / "RESIDENT_CONTEXTS.json")["contexts"]
    if set(frozen) != {"0", "7", "127", "255"} or set(current) != set(frozen):
        raise LifecycleError("Unexpected resident membership; manual reconciliation required")
    contexts = []
    policy = thread_policy.load(area)
    for key in sorted(frozen, key=int):
        context = frozen[key]
        if (current[key]["worker"] != context["worker"] or
                current[key]["directory"] != context["directory"]):
            raise LifecycleError("Frozen/current resident identity mismatch")
        checked(context["worker"])
        thread_policy.validate(context['worker'], policy, paused=True)
        contexts.append(dict(cell=context["cell"], worker=context["worker"],
                             directory=context["directory"], original_state=context["state"],
                             original_turns=context.get("turns", 0), turns=0,
                             active_seconds=0.0, state="PAUSED",
                             quarantined_threads=policy['processes'][str(context['worker']['pid'])]['quarantined_threads']))
    if not (area / "STOP").exists():
        raise LifecycleError("Historical STOP must remain latched")
    for record in paused["processes"]:
        thread_policy.validate(record, policy, paused=True)
    ledger = read_json(area / "REGIONS.json")
    unresolved = [row["id"] for row in ledger["cells"] if row["status"] != "UNSAT_DRAT_VERIFIED"]
    if unresolved != [0, 1, 3, 7, 15, 31, 63, 127, 255]:
        raise LifecycleError("Unexpected unresolved domain")
    if any(row.get("pending_proof") for row in ledger["cells"]):
        raise LifecycleError("Unexpected pending proof requires reconciliation")
    return dict(status="PLAN_ONLY", contexts=contexts, original_processes=paused["processes"],
                historical_pause_sha256=sha(area / "OWNER_PAUSE.json"),
                historical_regions_sha256=sha(area / "REGIONS.json"),
                unresolved_ids=unresolved, proof_closed_regions=247, cold_ids=[1, 3, 15, 31, 63],
                legacy_control_policy="PERMANENTLY_SUSPENDED_STOP_LATCHED",
                deadline_policy="FRESH_MONOTONIC_ACTIVE_TURNS_NO_OVERALL_CUTOFF",
                verdict="UNKNOWN", whole_stratum_certified=False)


def watcher(control):
    row = read_json(control / "WATCHER.json")
    if row.get("status") != "WATCHING" or not row.get("ready"):
        raise LifecycleError("Independent SAT supervisor is not ready")
    checked(row)
    if time.time() - row["updated_epoch"] > 3:
        raise LifecycleError("Independent SAT supervisor heartbeat is stale")
    if row.get("source_sha256") != sha(ROOT / "scripts/s035_sat_first_resume.py"):
        raise LifecycleError("Independent SAT supervisor source mismatch")
    return {"pid": row["pid"], "start_ticks": row["start_ticks"]}


def published_acceptance(control):
    row = read_json(control / "ACCEPTANCE.json")
    if row.get("status") != "PASS" or row.get("source_sha256") != sources():
        raise LifecycleError("Published lifecycle/SAT acceptance is absent or stale")
    if row.get('thread_policy_sha256') != sha(control/'THREAD_POLICY.json'):
        raise LifecycleError('Thread quarantine policy differs from published acceptance')
    commit = row["published_commit"]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"],
                                     cwd=ROOT, text=True, timeout=30).split()[0]
    if head != commit or remote != commit:
        raise LifecycleError("Acceptance commit is not verified local and remote main")
    committed_policy = subprocess.check_output(['git','show',f'{commit}:validation/S035/thread-repair/THREAD_POLICY.json'],cwd=ROOT)
    if hashlib.sha256(committed_policy).hexdigest()!=row['thread_policy_sha256']:
        raise LifecycleError('Thread policy was not published with acceptance sources')
    for name, digest in sources().items():
        committed = subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != digest:
            raise LifecycleError("Lifecycle/SAT source differs from published bytes")
    return row


def input_gates(area, contexts):
    cfg = read_json(area / "CONFIG.json")
    if cfg.get("deadline") is not None:
        raise LifecycleError("Unexpected historical overall deadline")
    for name, digest in cfg["source_sha256"].items():
        if sha(ROOT / name) != digest:
            raise LifecycleError("Historical scientific source mismatch: " + name)
    if sha(cfg["native"]) != cfg["native_sha256"]:
        raise LifecycleError("Native executable source gate mismatch")
    for context in contexts:
        directory = Path(context["directory"])
        metadata = read_json(directory / "INPUT.json")
        if sha(directory / "input.inst") != metadata["input_sha256"]:
            raise LifecycleError("Retained native input mismatch")
        context["input_sha256"] = metadata["input_sha256"]
        context["native_sha256"] = cfg["native_sha256"]
    if not cfg.get("disable_congruence") or cfg.get("disable_random_walk"):
        raise LifecycleError("Registered congruence/walk settings changed")
    if cfg.get("resident_max_contexts") != 4 or cfg.get("workers") != 2:
        raise LifecycleError("Resident/slot admission policy mismatch")
    return cfg


def stop_reason(area, control):
    # SAT priority is deliberate, including a STOP/SAT race.
    if (area / "SAT_ALERT.json").exists() or (control / "SAT_ALERT.json").exists():
        return "SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW"
    if (control / "STOP").exists():
        return "OWNER_OR_SUPERVISOR_PAUSE"
    watcher(control)
    if not (area / "STOP").exists():
        return "HISTORICAL_STOP_UNLATCHED_UNSAFE"
    return None


def halt_all(control, adoption, reason):
    """Latch first, then serialise suspension against every controller resume."""
    errors = []
    try:
        (control / "STOP").touch()
    except Exception as exc:
        errors.append(dict(stage="stop_latch", error=repr(exc)))
    try:
        terminal_rows = read_json(control / "TERMINAL.json").get("results", []) if (control / "TERMINAL.json").exists() else []
    except Exception as exc:
        terminal_rows = []
        errors.append(dict(stage="terminal_metadata_read", error=repr(exc)))
    terminal_codes = {row["cell"]: row["returncode"] for row in terminal_rows}
    def pause_registered():
        for context in adoption["contexts"]:
            try:
                context["threads"] = pause_identity(context["worker"])
                context["state"] = "PAUSED"
            except (LifecycleError, psutil.Error) as exc:
                if context["cell"] in terminal_codes:
                    try:
                        checked(context["worker"])
                    except LifecycleError:
                        context.update(state="NATIVE_EXITED", returncode=terminal_codes[context["cell"]])
                        continue
                errors.append(dict(cell=context["cell"], error=repr(exc)))
    try:
        with locked(control / "MUTATION.lock"):
            pause_registered()
    except Exception as exc:
        # A filesystem/lock failure must never skip OS preservation. STOP has
        # already been attempted; emergency suspension is idempotent.
        errors.append(dict(stage="mutation_lock", error=repr(exc)))
        pause_registered()
    adoption.update(status="PAUSED", reason=reason, updated_epoch=time.time(), pause_errors=errors,
                    executing_cells=[])
    atomic_json(control / "ADOPTION.json", adoption)
    log_evidence = []
    for context in adoption["contexts"]:
        path = Path(context["directory"]) / "native.log"
        try:
            log_evidence.append(dict(cell=context["cell"], path=str(path), bytes=path.stat().st_size,
                                     sha256=sha(path), input_sha256=context["input_sha256"],
                                     native_sha256=context["native_sha256"]))
        except Exception as exc:
            log_evidence.append(dict(cell=context["cell"], path=str(path), error=repr(exc)))
    atomic_json(control / f"PAUSE_EVIDENCE-{time.time_ns()}.json", dict(logs=log_evidence,
                updated_epoch=time.time(), status="NATIVE_FILES_PRESERVED_NO_REGION_PROMOTED"))
    # Capture only complete append-only bytes and leave original journals/old
    # checkpoint files untouched. This preserves recovery evidence; the prefix
    # is not an accepted geometric source until the independent audit passes.
    for context in adoption["contexts"]:
        source = Path(context["directory"]) / "new-cuts.lem"
        if not source.exists():
            continue
        h = hashlib.sha256()
        complete_bytes = complete_lines = 0
        with source.open("rb") as stream:
            while line := stream.readline():
                if not line.endswith(b"\n"):
                    break
                h.update(line)
                complete_bytes += len(line)
                complete_lines += 1
        atomic_json(control / "checkpoints" / f"cell-{context['cell']:04d}-{time.time_ns()}.json",
                    dict(source=str(source), complete_bytes=complete_bytes,
                         complete_lines=complete_lines, complete_prefix_sha256=h.hexdigest(),
                         source_bytes=source.stat().st_size, updated_epoch=time.time(),
                         status="UNVERIFIED_GEOMETRIC_PREFIX_PRESERVED", worker=context["worker"]))
    journal(control / "JOURNAL.jsonl", "preservation_pause", reason=reason, errors=errors)
    return errors


def resource_reason(area, contexts, registry, cfg, cache):
    sample = sample_identities(registry)
    if sample["private"] > 6 * 1024**3:
        return "SAFETY_AGGREGATE_PRIVATE_CAP", sample
    if psutil.virtual_memory().available < 2 * 1024**3:
        return "SAFETY_AVAILABLE_RAM_FLOOR", sample
    if sample["private"] > 5 * 1024**3:
        return "SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE", sample
    if psutil.virtual_memory().available < 2560 * 1024**2:
        return "SOFT_AVAILABLE_RAM_TARGET_PRESERVATION_PAUSE", sample
    if shutil.disk_usage(ROOT).free < 10 * 1024**3:
        return "SAFETY_DISK_RESERVE", sample
    for context in contexts:
        p = checked(context["worker"])
        if p.memory_info().private > 2 * 1024**3:
            return "SAFETY_PER_WORKER_PRIVATE_CAP", sample
    now = time.monotonic()
    if now - cache.get("sampled", -100) >= 10:
        cache.update(sampled=now, campaign_bytes=directory_bytes(area),
                     s035_bytes=directory_bytes(ROOT / "artifacts/tmp/S035"))
        # No proof process is launched; retained raw bytes must still respect
        # the attempt budget before any further native work is permitted.
        cache["proof_cap"] = any(path.stat().st_size > 2 * 1024**3
                                  for path in area.glob("attempts/cell-*/*/proof.drat"))
    if cache["campaign_bytes"] > 40 * 1024**3:
        return "SAFETY_CAMPAIGN_DISK_CAP", sample
    if cache["s035_bytes"] > 64 * 1024**3:
        return "SAFETY_S035_DISK_CAP", sample
    if cache["proof_cap"]:
        return "SAFETY_RAW_PROOF_ATTEMPT_CAP", sample
    return None, sample


def terminal(control, contexts, handles):
    rows = []
    poll_errors = []
    for context, handle in zip(contexts, handles):
        try:
            code = handle.poll()
        except Exception as exc:
            poll_errors.append(dict(cell=context["cell"], error=repr(exc)))
            continue
        if code is not None:
            directory = Path(context["directory"])
            rows.append(dict(cell=context["cell"], returncode=code,
                             directory=str(directory), worker=context["worker"],
                             input_sha256=context["input_sha256"],
                             native_sha256=context["native_sha256"]))
    if rows:
        value = dict(status="NATIVE_RETURN_REQUIRES_REVIEW", results=rows,
                     updated_epoch=time.time(), no_region_promoted=True, poll_errors=poll_errors)
        atomic_json(control / "TERMINAL.json", value)
        sat = any(row["returncode"] == 10 for row in rows)
        if sat:
            atomic_json(control / "SAT_ALERT.json", dict(**value,
                        ordinary_UNKNOWN_forbidden=True,
                        review_status="SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW"))
        # Optional evidence hashing is deferred until all peers are suspended.
        return "SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW" if sat else "NATIVE_RETURN_PRESERVED_PENDING_PROOF_OR_FAILURE_REVIEW"
    return "NATIVE_EXIT_POLL_FAILURE_REQUIRES_REVIEW" if poll_errors else None


def run(area, control, pilot_seconds=None):
    if pilot_seconds is not None and not 0 < pilot_seconds <= 120:
        raise LifecycleError("Pilot must be between zero and120 seconds")
    area, control = Path(area).resolve(), Path(control).resolve()
    if control != area / "RESUME_CONTROL":
        raise LifecycleError("Scientific adoption uses the registered RESUME_CONTROL directory")
    published_acceptance(control)
    adoption = plan(area)
    contexts = adoption["contexts"]
    cfg = input_gates(area, contexts)
    supervisor = watcher(control)
    if stop_reason(area, control):
        raise LifecycleError("A preservation stop/SAT alert is latched")
    handles = []
    reason = "CONTROLLER_EXCEPTION"
    active_started = {}
    cache = {}
    controller = identity(os.getpid())
    registry = [*adoption["original_processes"], controller, supervisor]
    adoption.update(status="PREPARING", controller=controller, watcher=supervisor,
                    created_epoch=time.time(), epoch=time.time(), source_sha256=sources(),
                    control_directory=str(control), lease_seconds=5,
                    adoption_mode="SAME_PROCESS_NO_NEW_WORKERS_NO_PROOFS_NO_COLD_ADMISSIONS")
    with locked(control / "CONTROLLER.lock", blocking=False):
        try:
            # Open exit-code handles BEFORE the first resume, then pin every
            # suspended thread's identity and actual nested suspend count.
            for context in contexts:
                handles.append(ProcessHandle(context["worker"]))
                context["threads"] = thread_counts(context["worker"])
            initial_issue, initial_sample = resource_reason(area, contexts, registry, cfg, cache)
            if initial_issue:
                raise LifecycleError(initial_issue)
            adoption.update(status="ARMED", updated_epoch=time.time(), sample=initial_sample)
            atomic_json(control / "ADOPTION.json", adoption)
            started = time.monotonic()
            end = started + pilot_seconds if pilot_seconds else float("inf")
            quantum = min(600, pilot_seconds / 4) if pilot_seconds else 600
            inhibited = False
            def request_pause(signum, frame):
                (control / "STOP").touch()
            previous = {sig: signal.signal(sig, request_pause) for sig in (signal.SIGINT, signal.SIGTERM)}
            try:
                inhibit_sleep(True)
                inhibited = True
                while True:
                    reason = terminal(control, contexts, handles) or stop_reason(area, control)
                    if reason:
                        break
                    # Never wake legacy Python/conhost ancestors. Their wall
                    # deadlines, held claims and finally blocks stay frozen.
                    native_pids = {row["worker"]["pid"] for row in contexts}
                    for record in adoption["original_processes"]:
                        thread_policy.validate(record, thread_policy.load(area),
                                               paused=record['pid'] not in native_pids)
                    now = time.monotonic()
                    for context in contexts:
                        key = context["cell"]
                        if key in active_started and now - active_started[key] >= quantum:
                            with locked(control / "MUTATION.lock"):
                                context["threads"] = pause_identity(context["worker"])
                            context["active_seconds"] += now - active_started.pop(key)
                            context["state"] = "PAUSED"
                            journal(control / "JOURNAL.jsonl", "fair_turn_paused", cell=key,
                                    worker=context["worker"], active_seconds=context["active_seconds"])
                    if now >= end:
                        reason = "BOUNDED_PILOT_COMPLETE_RAM_PRESERVED"
                        break
                    issue, sample = resource_reason(area, contexts, registry, cfg, cache)
                    if issue:
                        reason = issue
                        break
                    # At most two native identities execute. Four residents stay
                    # admitted; no evictions or repeated cold-cache churn.
                    choices = sorted((row for row in contexts if row["cell"] not in active_started),
                                     key=lambda row: (row["active_seconds"], row["turns"], row["cell"]))
                    for context in choices[:max(0, 2 - len(active_started))]:
                        with locked(control / "MUTATION.lock"):
                            if stop_reason(area, control):
                                break
                            resume_identity(context["worker"], context["threads"], context['quarantined_threads'])
                            if stop_reason(area, control):
                                context["threads"] = pause_identity(context["worker"])
                                break
                        active_started[context["cell"]] = time.monotonic()
                        context.update(state="RUNNING", turns=context["turns"] + 1)
                        journal(control / "JOURNAL.jsonl", "same_identity_resumed", cell=context["cell"],
                                worker=context["worker"], turn=context["turns"])
                    adoption.update(status="RUNNING", updated_epoch=time.time(), sample=sample,
                                    resource_cache=cache, executing_cells=sorted(active_started))
                    atomic_json(control / "ADOPTION.json", adoption)
                    atomic_json(control / "CONTROLLER.json", dict(status="RUNNING", **controller,
                                updated_epoch=time.time(), executing_cells=sorted(active_started),
                                lease_seconds=5, historical_stop_latched=True, verdict="UNKNOWN"))
                    time.sleep(.2)
            finally:
                if inhibited:
                    inhibit_sleep(False)
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
        except BaseException as exc:
            reason = "CONTROLLER_EXCEPTION_" + repr(exc)
            raise
        finally:
            try:
                # A return can race a resource sample. Poll again, but no failure
                # in terminal logging/hashing may bypass native preservation.
                detected = terminal(control, contexts, handles)
                if detected:
                    reason = detected
            finally:
                for handle in handles:
                    try:
                        if handle.poll() == 10:
                            reason = "SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW"
                    except Exception:
                        pass
                if (control / "SAT_ALERT.json").exists() or (area / "SAT_ALERT.json").exists():
                    reason = "SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW"
                now = time.monotonic()
                for context in contexts:
                    if context["cell"] in active_started:
                        context["active_seconds"] += now - active_started[context["cell"]]
                try:
                    errors = halt_all(control, adoption, reason)
                    atomic_json(control / "CONTROLLER.json", dict(status="PAUSED", reason=reason,
                                **controller, updated_epoch=time.time(), pause_errors=errors, verdict="UNKNOWN"))
                finally:
                    for handle in handles:
                        handle.close()
    print(json.dumps(dict(status="PAUSED", reason=reason, pause_errors=errors,
                         original_stop_latched=(area / "STOP").exists(), no_region_promoted=True)))


def rearm_pilot(area, control):
    """Archive a successful bounded pilot's separate controls; never resume OS work.

    Historical campaign STOP stays latched. A fresh independent supervisor and
    separately gated run are required after this operation.
    """
    area, control = Path(area).resolve(), Path(control).resolve()
    if control != area / "RESUME_CONTROL":
        raise LifecycleError("Only the registered adoption control can be rearmed")
    published_acceptance(control)
    if (area / "SAT_ALERT.json").exists() or (control / "SAT_ALERT.json").exists():
        raise LifecycleError("SAT discovery requires review; pilot rearm forbidden")
    previous = read_json(control / "ADOPTION.json")
    if (previous.get("status") != "PAUSED" or previous.get("pause_errors") or
            previous.get("reason") != "BOUNDED_PILOT_COMPLETE_RAM_PRESERVED"):
        raise LifecycleError("Only a successfully paused bounded pilot may be rearmed")
    planned = plan(area)  # Includes all original identity/status/domain checks.
    if {row["cell"]: row["worker"] for row in planned["contexts"]} != {
            row["cell"]: row["worker"] for row in previous["contexts"]}:
        raise LifecycleError("Pilot/frozen process identities differ")
    for record in (previous["controller"], previous["watcher"]):
        try:
            checked(record)
        except LifecycleError:
            continue
        raise LifecycleError("Previous adoption controller/supervisor has not exited")
    if not (control / "STOP").exists():
        raise LifecycleError("Successful pilot's separate STOP is missing")
    with locked(control / "CONTROLLER.lock", blocking=False):
        with locked(control / "MUTATION.lock", blocking=False):
            for context in previous["contexts"]:
                actual = thread_policy.validate(context['worker'], thread_policy.load(area), paused=True)
                old_ids = thread_policy.keys(context['threads'])
                retained = [r for r in actual if (r['tid'], r['created_ticks']) in old_ids]
                if sorted(retained,key=lambda r:r['tid']) != sorted(context['threads'],key=lambda r:r['tid']):
                    raise LifecycleError("Pilot suspended thread counts changed")
                extras = [r for r in actual if (r['tid'],r['created_ticks']) not in old_ids]
                approved = thread_policy.load(area)['processes'][str(context['worker']['pid'])]['quarantined_threads']
                if not thread_policy.keys(extras) <= thread_policy.keys(approved):
                    raise LifecycleError('Unclassified later-created thread; no rearm')
            history = control / "history" / (str(time.time_ns()) + "-" + uuid.uuid4().hex[:8])
            if not history.resolve().is_relative_to(control):
                raise LifecycleError("History target escaped adoption control directory")
            history.mkdir(parents=True)
            moved = []
            retained = {"ACCEPTANCE.json", "JOURNAL.jsonl", "CONTROLLER.lock", "MUTATION.lock", "history", "STOP", "THREAD_POLICY.json"}
            for path in list(control.iterdir()):
                if path.name in retained:
                    continue
                target = history / path.name
                if not path.resolve().is_relative_to(control) or not target.resolve().is_relative_to(history):
                    raise LifecycleError("Unexpected rearm path")
                path.rename(target)
                moved.append(path.name)
            # Keep the separate STOP latched until all stale adoption metadata
            # has been safely archived. Original campaign STOP is untouched.
            (control / "STOP").rename(history / "STOP")
            moved.append("STOP")
            atomic_json(history / "REARM.json", dict(status="SUCCESSFUL_PILOT_ARCHIVED_NO_WORK_RESUMED",
                        moved=moved, previous_controller=previous["controller"],
                        previous_watcher=previous["watcher"], original_stop_latched=True))
            journal(control / "JOURNAL.jsonl", "successful_pilot_rearmed", history=str(history),
                    original_stop_latched=True, no_process_resumed=True)
    print(json.dumps(dict(status="REARMED_NO_PROCESS_RESUMED", history=str(history))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run", "pause", "status", "rearm-pilot"))
    parser.add_argument("--directory", type=Path, default=DEFAULT)
    parser.add_argument("--control-directory", type=Path)
    parser.add_argument("--pilot-seconds", type=float)
    args = parser.parse_args()
    area = args.directory.resolve()
    control = (args.control_directory or area / "RESUME_CONTROL").resolve()
    if args.action == "plan":
        print(json.dumps(plan(area), indent=1))
    elif args.action == "status":
        print(json.dumps(read_json(control / "ADOPTION.json"), indent=1))
    elif args.action == "pause":
        (control / "STOP").touch()
        print("Preservation pause requested; native identities will be suspended.")
    elif args.action == "rearm-pilot":
        rearm_pilot(area, control)
    else:
        run(area, control, args.pilot_seconds)


if __name__ == "__main__":
    main()
