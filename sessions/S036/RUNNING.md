# S036 sustained retained-RAM search RUNNING — 23 October 2026 11:58 UTC (12:58 BST)

Actual unbounded search, not a pilot. Acceptance commit 7a1c5b8136a7bfa2c91c9c51bb75caf7f1669483
(hosted run 39949472103: all 23 steps success, including the new S036 records
step; the earlier run 39949226899 for ade0cdd failed only because its control
record hashed CRLF working copies, which the new checker correctly rejected).

Sequence: fresh supervisor WATCHING (clean 4862-file first full scan) -> 40 s
same-process validation on the real retained contexts (each context two 10 s
turns, ~10 CPU s per turn, conflicts +34K..+71K per turn, cell 7 +8502 cuts,
all re-suspended, no pause errors) -> supervisor paused on the latched STOP and
exited -> rearm archived the pilot controls without resuming anything ->
fresh supervisor -> controller without --pilot-seconds.

Live authority (always recheck identities; these PIDs are not authority):
artifacts/tmp/S036/control/ADOPTION.json, CONTROLLER.json, WATCHER.json,
GUARD_PAUSE.json, SAT_ALERT.json, TERMINAL.json, COLD_SLOT.json, METRICS.jsonl.
Controller PID 1612 / create 1792756681.9033551; supervisor PID 12716 / create
1792756677.5093255. Read-only status: `.venv/Scripts/python.exe scripts/s036_status.py --sample 15`.

Four original native contexts 0,7,127,255 keep their S035 RAM CDCL; two execute
in fair 600 s turns with no overall cutoff; only exact original native threads
resume; classified ntdll!TppWorkerThread helpers and all legacy ancestors stay
suspended. First independent sample after launch (15 s): cells 0 and 7 each
+15 CPU s, conflicts +106771 and +91411, cell 0 +17602 geometric cuts; parked
127/255 zero CPU. These are liveness measurements, not progress toward closure,
an ETA or a mathematical advance.

Bounded cold slot (registered validation/S036/COLD_CAPACITY_PLAN.json): runner
acceptance smoke on region 1 (cooperative exit 0, 10258 new geometric cuts
independently subdivision-audited) exposed a double count in the yield gate
(controller sample already includes the cold process); fixed to sample the
registered identities directly. Registered option diagnostics then started
(5 regions x 5 arms x 360 s, validation/S036/DIAGNOSTIC_ARMS.json).

SAT outranks STOP/UNKNOWN; native UNSAT never closes a region without a fresh
standalone DRAT and independent checker. Hard caps 6 GiB aggregate / 2 GiB per
worker / 2 GiB available floor / 10 GiB disk reserve / 2 GiB raw proof /
40 GiB campaign / 64 GiB S035+S036; soft RAM dips throttle; thermal sensors
unavailable. 247 encoded closures, nine UNKNOWN; S11 UNKNOWN; 9<=chi2<=12.
Never wake legacy controls, call legacy STOP/recover, remove the historical
STOP, force-kill, evict, duplicate or auto-restart a paused controller.

## Identity loss at 12:14 UTC and fresh semantic recovery

The owner closed the ChatGPT desktop app. S035 had recorded its executor as
"Codex desktop local Windows"; all twelve S035 identities (the four native
contexts and every suspended legacy ancestor) ended at the same moment as the
ChatGPT/Codex processes, without reboot and with no native final-status, FATAL,
SAT or UNSAT line. The S036 controller stopped on the changed thread set, its
halt found the processes terminating or gone, and the supervisor paused and ran a
fresh complete rescan: no SAT signal, nothing unreadable. Private CDCL for
regions 0, 7, 127 and 255 (about 34-37M conflicts each) is lost and is never
claimed as recovered. Evidence: validation/S036/identity-loss/.

A control then showed the S036 controller/supervisor were themselves inside the
Claude Code job object (CREATE_BREAKAWAY_FROM_JOB does not leave it), so closing
Claude Code would have had the same effect. All S036 processes are now launched
through WMI Win32_Process.Create (scripts/s036_launch.py default), outside any
application job.

Semantic recovery: the unshared tails of the lost contexts' geometric journals
were independently subdivision-audited (region 0: 347101 clauses, region 7:
1017564; regions 127/255 had none) and registered as region blocks. Fresh
residents (scripts/s036_fresh_campaign.py, S036 native at baseline settings) are
started for 0, 7, 127, 255 from exact recipes, admitted one at a time through a
measured memory gate (aggregate + 1.5 GiB <= 5 GiB, available - 1.5 GiB >=
2.75 GiB), then kept resident in two-slot 600 s fair turns. Real controls:
validation/S036/FRESH_CONTROLS.json.

## Fresh residents RUNNING — 23 October 2026 12:27 UTC

Fresh-campaign acceptance commit 79304bdf3ac61c9a05fe126dc8ab71490cb9bd86 (hosted run
39953216809, 23/23 steps success). The adoption-stage control state was archived to
artifacts/tmp/S036/control/history/*-adoption-identity-loss without resuming anything.
Supervisor and fresh controller were launched through WMI; their ancestry is
WmiPrvSE -> cmd.exe -> venv launcher -> python (only the venv launcher's own job),
and every solver is outside any job object: closing Claude Code, ChatGPT/Codex or a
terminal cannot end the search. Recorded identities (recheck; not authority):
controller 3556 1792758441.015757; supervisor 11768 1792758430.0021162; residents 0: PID 10804 / 1792758446.0958302; 7: PID 17812 / 1792758571.635335; 127: PID 15944 / 1792759050.8506148; 255: PID 11332 / 1792759176.461158.

Residents were admitted one at a time (120 s stagger, measured memory gate). First
turns: region 0 +2.9M conflicts and 314K geometric cuts, region 7 +1.9M conflicts,
both then parked with RAM retained while 127 and 255 execute; private memory per
resident 0.56-1.14 GB, aggregate about 3.8 GiB. Liveness only.

The cold runner was first admitted before residents 127/255 (memory was then ample),
inverting the registered priority. Its arm was stopped cooperatively, but the runner
counted that operator stop as a completed arm and began the next arm. The runner helper
(a Python scheduler holding no solver learning) was then terminated, and its current
cold solver was ended through its cooperative stop file (exit 0, stop marker logged);
no solver was force-terminated. Fixes: cold admission now waits while any
resident is queued or another cold solver is alive, and an arm counts only when it
ran its full budget to the natural timeout. The two early region-1 baseline attempts
are marked not counted. Registered diagnostics restarted once the resident queue emptied.

Loaded residents' input.inst copies (0.33-0.40 GB each) were released after load;
INPUT.json keeps each exact recipe and input SHA256 (hash-pinned sources retained) for
SAT validation by rematerialisation.

## 12:41 UTC preservation pause, fixes and same-identity resume (12:48 UTC)

The cold slot was admitted one second after resident 255 launched, before it had
loaded; both then grew and aggregate private memory (5.39 GB) crossed the 5 GiB target,
so the controller paused all four residents (RAM retained, no errors). The supervisor
also suspended the registered cold solver before it could see its cooperative stop; it
was later resumed only so that it exited through its stop file (exit 0). Fixes (commit
369bd00, hosted run 39955978643): cold admission waits until all residents have loaded;
a target crossing with a live cold solver triggers the cold solver's cooperative stop
instead of a halt; prepare-resume re-adopts a cleanly paused fresh campaign's SAME
processes (idle thread-pool workers created while suspended are suspended with the rest).

prepare-resume verified all four residents alive and suspended and archived the controls
without resuming anything; a fresh supervisor (13324 / 1792759718.4744055) and controller (16436 / 1792759722.9924011) were
launched through WMI with --resume. Residents 127 and 255 continued their counters
from the paused values (same processes, RAM learning intact). Loaded residents now use
0.6-0.85 GB each; the registered region-1 baseline cold arm was admitted and aggregate
private memory stayed at 3.8-4.2 GiB. Liveness only; nine regions UNKNOWN.

## Cold band amendments and equal-input repair (14:37-14:51 UTC)

The 15:14 BST check-in reported the cold diagnostics abandoned (aggregate crossed the
5 GiB target with four loaded residents). With the owner's delegation the cold slot
may now occupy the band up to 5.75 GiB aggregate (residents alone still bound by
5 GiB; 6 GiB aggregate and 2 GiB per-worker hard caps unchanged), and its per-solver
yield cap and the adoption memory criterion are 1.9 GiB (COLD_CAPACITY_PLAN amendments
2 and 3; registered before any non-baseline arm was counted). The controller switched
over by a preservation pause and same-identity resume (commit c402824, hosted run
39971271327); residents kept their RAM.

Partial (yielded) attempts had been adding their audited cuts to region 1's recipe,
so later arms would not have read the counted baseline's input. Diagnostics now use one
frozen recipe per region (region 1 frozen to the counted baseline input c2e16af3...),
and cuts found during diagnostics join only the later rotation recipes. The region-1
phase0 arm then ran its full budget on the identical input and was counted. Idle cold
runner helpers (no solver child) were ended between attempts to apply these changes;
every cold solver ended by timeout or its cooperative stop file.
