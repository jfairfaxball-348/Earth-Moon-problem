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
