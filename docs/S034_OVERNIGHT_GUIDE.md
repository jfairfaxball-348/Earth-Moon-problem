# S034 completed safety stop — current status

The campaign stopped00:01:43 UTC on22 October2026 for disk reserve. No restart; the07:00 UK deadline has passed. Read sessions/S034/CLOSEOUT.md and docs/S034_RECOVERY.md. S035 Windows multiple workers is queued, not executed. The original operating guide below is historical.

# S034 overnight campaign

Owner deadline:07:00 Europe/London on22 October2026,06:00 UTC. This is a
running S034 campaign, not a completed session and not S035. It uses one real
guarded bipsat2 worker with exact256 graph-prefix regions, the unchanged
S11 formulation and all2579937 retained geometric clauses.

Read-only status (starts no solver):

```
.venv/bin/python scripts/s034_campaign.py status
```

Explicit safe STOP:

```
.venv/bin/python scripts/s034_campaign.py stop
```

Inspect artifacts/tmp/S034/campaign/GUARDIAN.json, CONTROLLER.json,
REGIONS.json and JOURNAL.jsonl before doing anything else. Do not duplicate a
live guardian/controller/worker. The guardian identifies processes by PID and
kernel start ticks, kills identified orphan groups, independently checkpoints
their complete geometric journals, and restarts a recoverable controller crash.
Three controller crashes in15min stop as unstable. A proof-check error, missing
RSS, sustained low memory, thermal cap or disk reserve breach also stops safely.

One GiB aggregate observed RSS,4GiB disk reserve,384MiB MemAvailable floor.
RSS budget caps checkpoint/requeue the current visit and allow other regions
after recovery; actual low-memory pressure stops the campaign. New clauses are
independently audited before reuse. Whole private CDCL state is not saved.
Per-visit time comes from remaining overnight time and unresolved region count,
with120..1800s bounds to amortise measured startup; UNKNOWN is requeued.
There is no independent short overall wall limit.

The guardian has the absolute UTC deadline and a monotonic-clock backstop.
The new native engine additionally checks EMP_ABSOLUTE_DEADLINE. Solver and
proof groups stop at the deadline. Interrupted proofs/audits remain UNKNOWN.
Only exact standalone CaDiCaL DRAT plus independent drat-trim can proof-close
a region; SAT remains a candidate requiring independent domain/witness review.
Counters/region weights are not a percentage-to-solution or an ETA.

Android can kill the entire Termux/proot environment. Screen locking/Doze and
low-memory kills are outside a user-space guardian's control. Termux wake lock
does not guarantee persistence; no systemd, namespaces or cgroups are assumed.
No readable temperature or memory-PSI sensors were available. Concurrency stays
one; small two-worker controls are not a full-input thermal/RAM benchmark.

If the guardian itself was killed, first inspect its PID/start ticks and all
processes. A fresh invocation within this owner's unchanged S034 deadline can
run `guard` again in the same directory; it recovers UNKNOWN claims and preserves
all journals. It cannot extend the stored deadline. Do not clear STOP or bypass
a safety stop without diagnosing the actual condition.

All S032/S033 immutable evidence and native archives remain preserved. Existing
Windows builds remain available. Roll back phone code with ordinary git revert,
preserving later work and all campaign evidence. Same repo/main, no new branch
or PR, no force. S034 closeout and the complete S035 future prompt follow the
deadline; S035 requires a fresh owner invocation.
