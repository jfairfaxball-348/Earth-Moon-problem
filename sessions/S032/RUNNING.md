# STOPPED by owner —2026-10-21 (D070)

The material below is historical launch provenance. The same controller/native have exited, ACTIVE.lock is gone, monitor PAUSED and sleep inhibition released. See CLOSEOUT.md and validation/S032/stopped. No automatic restart.

# S032 is RUNNING — no fixed wall limit (D069)

Owner directly invoked S032, then said: "Don't limit it to 8 hours.....Just keep going until you stop".
D069 supersedes the original8h ceiling. Continue ONLY S032; no S033 invocation.
Last completed session remains S031. No final authored S032 commit/PR/closeout yet.

Controller actual PID13056, native actual PID12892. Parent venv launcher
PID19808 is not the native worker. Actual start{UTC}:2026-10-20T06:25:56.744128+00:00.
Use current runtime files and actual PID creation times, not these launch values.
Command: .venv/Scripts/python.exe scripts/run_s032_native.py --out campaign --cap0
--resume-from artifacts/tmp/S032/diagnostic/learned.lem (actual argv uses --cap 0).
Native receives --timeout inf; both internal and external search wall limits
are null. Serial proof replay/checker also have no fixed wall limit. Infinite
native deadline keeps its progress callback; positive24 control PASS.

One single-threaded native solver tree<=11GiB aggregate private memory;10GiB
disk reserve. Keep laptop plugged in and Codex open for local scheduled checks.
Controller temporarily inhibits idle system sleep while active and releases it
on exit; no permanent power setting change. Resource and owner stops remain.

Current evidence under artifacts/tmp/S032/campaign:
- CONTROLLER.json: actual controller/native/proof PIDs, phases, source/native/
  runtime/input hashes, limits (null wall limits), provenance.
- WORKER.json: native command/PID/start. PROGRESS.json: native counters, elapsed,
  private memory, disk; JOURNAL.jsonl:30s supervisor history.
- worker.log: partial checks/cuts/model checks every30s; inspect bounded tails.
- learned.lem: append-only, newline-terminated negative single-layer presence
  clauses. Each was independently checked by C++ subdivision suppression BEFORE
  solver use. Flushed each clause, committed every30s; final flush on normal exit.
- CHECKPOINT.json: atomic hash/count of a complete byte prefix of learned.lem,
  plus fixed input hash. Read/hash only that prefix to restore a checkpoint;
  preserve any trailing fragment as failure evidence, do not invent its terminator.
  The raw append-only journal persists full semantic clauses; no private CDCL
  state is saved. Fixed input is artifacts/tmp/S032/S11.inst/base.cnf/INPUTS.json.
- RESULT.json exists only after search exits. Native UNSAT/WITNESS statuses
  require independent review and cannot be promoted from solver text.

Native bipsat2 adapted at pinnedab6e472b7ef4ab7dca1d12c8907b3c74399d3828,
CaDiCaL3.0.1. No twin/face-rule/domain restriction or model enumeration/blocking.
All336030 original S031 clauses retained via a checked bijective renaming.
Diagnostic300s produced162536 new partial-layer clauses, all independently
replayed, no model. The campaign resumes those semantic clauses, explicitly
losing diagnostic private CDCL state. Full fresh271+retained/fresh K9 smoke,
S03146-model/1809-cut replay,2916 extension controls/RUP/positive24 PASS.
Native1024 n5/64 n6/fixed K33/positive24 PASS. Free K9 UNKNOWN at60s/300s;
SCOPED_PASS_WITH_FREE_K9_UNKNOWN is intentionally not a full negative calibration.
Actual17v alpha2 control unavailable. Regular154 hand coverage SOURCE_STATED;
S10/S9/S8 NOT_RUN. No chi>=10 witness;9<=chi2<=12; parked gates unchanged.

Automation earth-moon-s032-monitor ACTIVE, every2h in this chat. S031 automation
remains PAUSED. Healthy/non-actionable checks stay quiet. Never stop at8h merely
because8h passed. On source drift, process failure or resource stop preserve
provenance, inspect and repair/resume only within S032 when justified; verify
NO live heavy worker first. ACTIVE.lock prevents duplicates. Do not remove an
active lock blindly. Writing artifacts/tmp/S032/STOP requests an owner/controller
stop; the supervisor snapshots and kills its child, retaining UNKNOWN.

On native SAT stop: independently parse full v assignment, invert variable map,
check exact base formula, all alpha-four-sets/degree/edge/symmetry constraints,
labelled disjoint layers, independent embedding/rotation, proper colouring and
chi>=10 counting before any witness claim. On UNSAT: controller revalidates all
new clauses, builds the full formula, runs pinned standalone DRAT and checker
serially. Still require independent scope/encoding/domain/proof review. Use
scripts/audit_s032_runtime.py campaign and independent clause checks; no bare
UNSAT/cap claim. A result, owner stop or inability to safely continue triggers
truthful S032 closeout, paired catalogues/ledgers, complete byte-identical S033
FUTURE prompts, one atomic authored commit from entry main
e3145c77a7350ebd2c8aa3197cf97bf5e626099f, ordinary PR, non-force two-parent merge
and actual hosted head/main jobs. WIP snapshots are never merged/inherited.
Disable this monitor after S032 closes and stop. Do not execute S033.

Launch hashes, exact input, controls, diagnostic and native source/runtime
archives are frozen under validation/S032/start and START_MANIFEST.json.
Normal completed-session scaffold invariants intentionally do not hold during
this active campaign; use scripts/check_s032_running.py. Do not manufacture a
closeout to make governance CI green.

Owner-requested read-only analyser (2026-10-21): run
`.venv/Scripts/python.exe scripts/analyse_s032_progress.py --out validation/S032/progress-analysis`
during scheduled checks. This samples query-only process CPU and streams the
existing journal, separating long unobserved gaps from observed running time.
Report rule/check throughput and quiet stretches; these are NOT coverage or ETA.
It never stops, suspends, modifies or launches a solver. See PROGRESS_ANALYSIS.md.
