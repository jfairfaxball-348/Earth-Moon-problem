# S045 — 50-vertex solver preparation, benchmark and sustained search

INVOKED / IN PROGRESS — explicit owner override, 24 October 2026.
Existing main, ordinary non-force commit/push, no branch or PR.

The owner selected 50 vertices and authorised installation, solver changes,
testing, benchmarking and then search. This supersedes the proposal-only
restriction of sessions/S044/S045_FUTURE_PROMPT.md. See INPUT.md and PLAN.md.
Execute exactly S045. S036 stays CLEAN_STOPPED; no old control or automation
may be restarted. D042 remains a certified finite biplanar chi>=10 witness;
no universal upper-bound work, publication, outreach or Lean invocation.

Read authoritative/STATE.json and sessions/S045/RUNNING.md first. Inspect
scripts/s045_campaign.py status and exact PID/create-time identities before
any action. Do not duplicate a live controller, start another campaign, or
automatically resume a latched STOP/error. Runtime authority is
artifacts/tmp/S045/campaign/{CAMPAIGN,STATUS,IDENTITY,ERROR,LAUNCH}.json;
STATUS can be stale, so actual identities and controller CPU must agree.

The exact domain is 50 labelled vertices, 1225 optional pairs, two disjoint
planar layers, and no proper nine-colouring. No alpha<=3/5, degree-11,
symmetry or exact edge-count restriction. Native planarity clauses and
colouring-partition clauses are independently checked. Incremental native
SAT retains private learning between candidates; 600-second slices reload
audited semantic journals and discard private CDCL. Counts are activity,
not projected graph coverage or an ETA.

Launch only after validation/S045/SMOKE.json, CONTROLS.json and BENCHMARK.json
PASS and all tested source/binary hashes match. The benchmark pre-registers
three serial 60-second arms and a fresh semantic restart. One generator with
a serial oracle; eight-hour production wall ceiling; 3 GiB aggregate private
memory, 1.5 GiB available-RAM floor and 10 GiB disk reserve. Stop on owner
STOP, resource breach, validation failure, dependency/source change, witness
alert, native UNSAT or the ceiling. No unattended successor session.

Safe stop: .venv/Scripts/python.exe scripts/s045_campaign.py stop
Read-only status: .venv/Scripts/python.exe scripts/s045_campaign.py status
Wait for cooperative exit and preserve append-only journals. New-run watchdog
acts only on its exact children if cooperative shutdown fails; it never acts
on historical processes. Do not call S035/S036 STOP/recover/autopilot.

An UNSAT colouring alert is not a witness until standalone DRAT, independent
planar rotations and chromatic claims are checked. Native generator UNSAT
without a separately checked full refutation remains UNKNOWN. Preserve all
graphs, colouring partitions, geometric cuts, source/environment hashes and
failure provenance. Existing UNKNOWN domains and 9<=chi_2<=12 remain.

When the campaign ends, reconcile and archive its final evidence, update
records and close S045 with identical authoritative and session-local S046
FUTURE/UNEXECUTED handoffs; print the full handoff and verified GitHub links.
Do not execute S046. Fresh cloud_smoke.py is mandatory before new scientific
computation. Alternate Actions runner: docs/CLOUD_ENVIRONMENT.md and
validation/S011/SUMMARY.json, setup and full smoke in the SAME job.
