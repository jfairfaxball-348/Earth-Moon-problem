"""Small fresh-process lifecycle controls; never touches scientific identities.

The scheduler fixture mocks only scientific/published-source preflight and the
independent watcher heartbeat. Actual Windows handles, thread suspend counts,
native scheduling, per-turn retention, STOP and sleep release are exercised.
Independent real supervisor/race controls are recorded separately.
"""
from pathlib import Path
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import psutil

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
from s035_preserved_lifecycle import (identity, checked, pause_identity, thread_counts,
                                      resume_identity, ProcessHandle, LifecycleError,
                                      sample_identities)
from s035_windows import atomic_json

WORKER = r'''
from pathlib import Path
import sys,time
area=Path(sys.argv[1]); code=int(sys.argv[2]); counter=0
while not (area/'EXIT').exists() and counter<10000:
    counter+=1
    (area/'counter').write_text(str(counter))
    time.sleep(.01)
sys.exit(code)
'''


def wait_until(test, seconds=5):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if test():
            return
        time.sleep(.01)
    raise AssertionError("Fixture did not reach expected condition")


def start(base, code=0):
    base.mkdir()
    p = subprocess.Popen([sys._base_executable, "-c", WORKER, str(base), str(code)],
                         creationflags=subprocess.CREATE_NO_WINDOW)
    row = identity(p.pid)
    wait_until(lambda: (base / "counter").exists())
    return p, row, base


def finish(fixture):
    p, row, directory = fixture
    (directory / "EXIT").touch()
    if p.poll() is None:
        try:
            if checked(row).status() == psutil.STATUS_STOPPED:
                resume_identity(row, thread_counts(row))
        except LifecycleError:
            pass
    p.wait(timeout=5)


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="s035-preserved-controls-") as temp:
        temp = Path(temp)
        fixture = start(temp / "nested")
        p, row, area = fixture
        try:
            handle = ProcessHandle(row)
            psutil.Process(p.pid).suspend()
            psutil.Process(p.pid).suspend()
            counts = thread_counts(row)
            assert all(x["suspend_count"] == 2 for x in counts)
            before = (area / "counter").read_text()
            cpu = sum(psutil.Process(p.pid).cpu_times()[:2])
            time.sleep(.15)
            assert before == (area / "counter").read_text()
            assert sum(psutil.Process(p.pid).cpu_times()[:2]) == cpu
            assert pause_identity(row) == counts  # idempotence: no third count
            damaged = copy.deepcopy(counts)
            damaged[0]["suspend_count"] += 1
            try:
                resume_identity(row, damaged)
                raise AssertionError("Corrupted count was accepted")
            except LifecycleError:
                pass
            assert thread_counts(row) == counts
            for turn in range(3):
                resume_identity(row, counts)
                wait_until(lambda: (area / "counter").read_text() != before)
                try:
                    resume_identity(row, counts)
                    raise AssertionError("Duplicate resume was accepted")
                except LifecycleError:
                    pass
                counts = pause_identity(row)
                before = (area / "counter").read_text()
                assert all(x["suspend_count"] == 1 for x in counts)
            assert sample_identities([row, row])["processes"] == 1
            wrong = dict(row, start_ticks="0")
            try:
                pause_identity(wrong)
                raise AssertionError("Recycled PID identity was accepted")
            except LifecycleError:
                pass
            assert thread_counts(row) == counts
            results.append(dict(control="nested_counts_identity_retention_duplicate_rejection",
                                status="PASS", worker=row, turns=3, paused_cpu_delta=0))
            (area / "EXIT").touch()
            resume_identity(row, counts)
            wait_until(lambda: handle.poll() is not None)
            assert handle.poll() == 0
            handle.close()
            p.wait(timeout=5)
            results.append(dict(control="cooperative_fixture_exit_without_termination", status="PASS", code=0))
        finally:
            finish(fixture)
        for code in (10, 20):
            fixture = start(temp / f"natural-{code}", code)
            p, row, directory = fixture
            try:
                handle = ProcessHandle(row)
                counts = pause_identity(row)
                (directory / "EXIT").touch()
                resume_identity(row, counts)
                wait_until(lambda: handle.poll() is not None)
                assert handle.poll() == code
                p.wait(timeout=5)
                assert handle.poll() == code  # retained after normal parent reaping
                handle.close()
                results.append(dict(control="retained_handle_natural_exit", status="PASS", code=code))
            finally:
                finish(fixture)

        spec = importlib.util.spec_from_file_location("s035_preserved_campaign", ROOT / "scripts/s035_preserved_campaign.py")
        campaign = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(campaign)
        area = temp / "scheduler"
        control = area / "RESUME_CONTROL"
        control.mkdir(parents=True)
        (area / "STOP").touch()
        fixtures = [start(temp / f"scheduler-worker-{i}") for i in range(4)]
        contexts = []
        for i, (p, row, directory) in enumerate(fixtures):
            counts = pause_identity(row)
            if i < 2:
                psutil.Process(p.pid).suspend()  # nested owner+old parked count
            (directory / "native.log").write_text("c fresh fixture\n")
            contexts.append(dict(cell=i, worker=row, directory=str(directory), original_state="PARKED",
                                 turns=0, active_seconds=0.0, state="PAUSED", input_sha256="fixture",
                                 native_sha256="fixture"))
        planned = dict(status="PLAN_ONLY", contexts=contexts,
                       original_processes=[row for p, row, directory in fixtures])
        try:
            with patch.object(campaign, "published_acceptance", lambda control: {}), \
                    patch.object(campaign, "plan", lambda area: copy.deepcopy(planned)), \
                    patch.object(campaign, "input_gates", lambda area, contexts: {}), \
                    patch.object(campaign, "watcher", lambda control: identity(os.getpid())), \
                    patch.object(campaign, "resource_reason", lambda *args: (None, {})):
                campaign.run(area, control, pilot_seconds=3.2)
            adopted = json.loads((control / "ADOPTION.json").read_text())
            assert adopted["status"] == "PAUSED" and not adopted["pause_errors"]
            assert all(row["turns"] >= 2 for row in adopted["contexts"])
            assert all(checked(row["worker"]).status() == psutil.STATUS_STOPPED for row in contexts)
            assert (area / "STOP").exists() and (control / "STOP").exists()
            journal = [json.loads(line) for line in (control / "JOURNAL.jsonl").read_text().splitlines()]
            active = set()
            peak = 0
            for event in journal:
                if event["kind"] == "same_identity_resumed":
                    active.add(event["cell"])
                    peak = max(peak, len(active))
                elif event["kind"] == "fair_turn_paused":
                    active.discard(event["cell"])
            assert peak == 2
            results.append(dict(control="fresh_four_context_scheduler_fixture", status="PASS", peak_executing=peak,
                                all_four_resumed_twice=True, originals_unmodified=True,
                                scientific_preflight_and_watcher_mocked=True))
            # The prior controller/watcher were in-process test doubles. Mark
            # their fixture records absent to exercise the conservative archive
            # path; the live identity rejection is tested separately below.
            with patch.object(campaign, "plan", lambda area: copy.deepcopy(planned)):
                try:
                    campaign.rearm_pilot(area, control)
                    raise AssertionError("Rearm accepted a still-live controller")
                except LifecycleError:
                    pass
                adopted["controller"] = adopted["watcher"] = dict(pid=0, start_ticks="0")
                atomic_json(control / "ADOPTION.json", adopted)
                campaign.rearm_pilot(area, control)
            assert (area / "STOP").exists() and not (control / "STOP").exists()
            assert list((control / "history").glob("*/STOP"))
            assert list((control / "history").glob("*/ADOPTION.json"))
            results.append(dict(control="bounded_pilot_rearm_archives_only_new_controls", status="PASS",
                                live_controller_rejected=True, historical_stop_retained=True))

            calls = []
            def terminal_failure(*args):
                calls.append(1)
                if len(calls) == 1:
                    return None
                raise OSError("injected terminal evidence failure while workers run")
            try:
                with patch.object(campaign, "published_acceptance", lambda control: {}), \
                        patch.object(campaign, "plan", lambda area: copy.deepcopy(planned)), \
                        patch.object(campaign, "input_gates", lambda area, contexts: {}), \
                        patch.object(campaign, "watcher", lambda control: identity(os.getpid())), \
                        patch.object(campaign, "resource_reason", lambda *args: (None, {})), \
                        patch.object(campaign, "terminal", terminal_failure):
                    campaign.run(area, control, pilot_seconds=1.2)
                raise AssertionError("Injected terminal failure did not propagate")
            except OSError:
                pass
            assert len(calls) >= 3
            assert all(checked(row["worker"]).status() == psutil.STATUS_STOPPED for row in contexts)
            assert (control / "STOP").exists()
            failed = json.loads((control / "ADOPTION.json").read_text())
            assert not failed["pause_errors"]
            results.append(dict(control="terminal_logging_failure_cannot_bypass_preservation", status="PASS",
                                all_four_suspended=True, exception_propagated=True))
        finally:
            for fixture in fixtures:
                finish(fixture)

    value = dict(status="PASS", controls=results, original_scientific_processes_touched=False,
                 native_cooperative_exit_hook="NOT_PRESENT_IN_OLD_BINARY_PAUSE_PRESERVES_RAM",
                 no_scientific_claim=True)
    atomic_json(Path(__file__).with_name("RESULTS.json"), value)
    print(json.dumps(value, indent=1))


if __name__ == "__main__":
    main()
