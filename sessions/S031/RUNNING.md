# HISTORICAL RUNNING HANDOFF — S031 worker has finished

Final capped result and independent audit are in CLOSEOUT.md and validation/S031.
Do not execute the historical resume command without a fresh authorized session.
The original running handoff follows as provenance.

# S031 is RUNNING — multi-hour campaign, not a closeout

Owner D066 limits execution to S031 ONLY. Continue its running eight-hour
campaign, scheduled checks, independent validation and required closeout, then
stop. D065 is historical launch provenance. S032 requires a fresh invocation.

Current campaign started2026-10-19 at18:44:38 UTC (19:44 London). It has an8h
external cap, one heavy worker,11GiB aggregate private-memory limit and10GiB
disk reserve. Controller temporarily requests the system remain awake; it
releases that request on exit. Keep laptop powered and Codex open for scheduled
local follow-ups. Native proof replay/checking, if triggered, can each take4h
more and run serially. No publication, outreach, Lean or parked-queue work.

Read the actual runtime files, not this launch snapshot, for progress:

- artifacts/tmp/S031/CONTROLLER.json: phase, actual controller PID, source hashes.
- artifacts/tmp/S031/search/WORKER.json: actual worker PID and solver instance.
- artifacts/tmp/S031/search/PROGRESS.json: models/cuts/conflicts/decisions/time.
- artifacts/tmp/S031/LONG_JOURNAL.jsonl: external wall/private-memory heartbeat.
- artifacts/tmp/S031/search/CHECKPOINT.json: authoritative atomic semantic checkpoint;
  its `cuts` list reconstitutes the formula even if a separate CNF export is stale.
- artifacts/tmp/S031/search/CUTS.json, final.cnf, models/*.json.gz: replay evidence.
- artifacts/tmp/S031/search/RESULT.json: only current final result, once it exists.
- artifacts/tmp/S031/controller.stderr.log, worker.log: errors and model progress.

Start profile is under startup-v1:82s diagnostic with2000-conflict slices stopped
gracefully because solver re-entry was too frequent. Its exact source/progress
and receipts were preserved. The current run resumed only the validated1114
semantic cuts, explicitly losing diagnostic private CDCL state. Current budgets
are100000 conflicts/1000000 decisions per slice on the SAME persistent solver.
No further restarts are planned. Zero models alone is not a stall if CPU and
conflict counters advance. Review growth after hours, not every few minutes.

Automation `earth-moon-long-run-continuation` is ACTIVE, checking every2h in this
chat. Monitor only S031. After its closeout disable this heartbeat and stop. Stay quiet when unchanged; report
meaningful progress, completion, failure or required user action.

Fresh S031 full271+retained/fresh K9 smoke PASS. Controls:44 S030 models replayed,
all seed cuts checked,2916 cadical300 assignments, incremental clause addition,
positive24 and both RUP checks PASS. Actual17-vertex alpha2 control unavailable;
no source theorem or whole stratum promoted. Source package/native hashes and
start receipts are in validation/S031/start and START_MANIFEST.json.

Before any restart: verify no existing heavy process; inspect actual PID/source
hashes, error cause and latest checkpoint. Repair only with source/provenance
recorded; use a fresh full gate for a new execution environment or numbered
session. Resume command is `.venv/Scripts/python.exe scripts/run_s031_long.py
--resume`, launched hidden via Start-Process with stdout/stderr logs and a launch
receipt. The controller refuses no duplicate itself, so YOU must check liveness.
The worker should have no stale STOP marker. Do not remove a STOP created by
the owner or launch a replacement after authorization is revoked.

On completion: independently audit every new model and cut, regenerate/check
the full formula, and independently review any native DRAT proof. Only then
make claims. Complete S031 records, paired catalogues/ledgers and full S032
prompt; one authored commit on codex/S031-persistent-op1b with sole parent entry
main, ordinary PR, non-force two-parent merge and actual head/main hosted jobs.
Unmerged wip/S031-long-run is backup only: do not merge or inherit its commit
history into the final session commit. D066 requires stopping after S031 closeout. Leave S032 FUTURE/UNEXECUTED
and disable the heartbeat; a new owner invocation is required for S032.

During this active campaign STATE.last_completed_session stays S030 and
next_session_is_future_unexecuted is false for active S031. The normal closeout
scaffold expects a completed session/future prompt, so it is intentionally not
the validator for this RUNNING snapshot. Do not fabricate a closeout to make it
pass. Restore completed-session invariants only at genuine S031 closeout.
