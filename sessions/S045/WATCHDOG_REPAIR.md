# S045 owner-authorised watchdog repair and overnight continuation

24 October 2026. The owner instructed: fix the stop, install two-hourly
check-ins, restart after testing, and replace the eight-hour roof with a hard
stop at 07:30 tomorrow. This is continuation of S045 only, not S046.

**Controlling deadline: 25 October 2026, 07:30 Europe/London = 07:30 UTC.**
Windows GMT Standard Time conversion independently confirms the post-clock-change
offset. Runtime policy: artifacts/tmp/S045/campaign/DEADLINE.json, pinned to
validation/S045/watchdog_repair/OWNER_DIRECTIVE.json. This supersedes every
earlier eight-hour/original-start-plus-eight-hour ceiling, including maintenance.
All resource safeguards and mathematical certification requirements remain.

Two-hourly heartbeat installed in THIS thread:
earth-moon-s045-two-hour-check-in, ACTIVE. Old S031/S032 monitors remain paused.
The check-in inspects actual controller/generator identities, CPU, checkpoint
phase, resources, alerts and first-cause records, and reports status each time.
After the deadline it verifies exit, preserves/audits results, closes S045 and
pauses itself. It never starts S046. The local watchdog enforces the deadline
independently of heartbeat delivery.

## Failure provenance and repair

The stopped run retained 272374 candidate/colour records and 900798 independently
checked geometric clause occurrences. No witness alert or native UNSAT. The
STOP appeared 614.691s after generator creation, matching the parent’s 600+15s
timer. Native loading time was included by the parent but excluded by the
solver. Repeated polling then overwrote the cause as STOP_FILE. All original
control bytes and source are retained in watchdog_repair/stop_snapshot and
initial_sources, with the exact original source commit 5d910fb.

Native READY now separates checkpoint loading from the solve clock. Startup
has its own bounded 900-second ceiling; normal solve slices remain 600 seconds,
plus a 15-second response grace. The owner deadline bounds EVERY stage:
Python checkpoint replay/encoding, native loading, solving and the oracle.
Stop causes are first-writer, durable records and are never replaced by the
generic STOP filename. Unexpected stops remain stopped for operator investigation.

Closed candidate/native-log files are compressed, decoded and independently
hash-compared before raw retirement. Candidate segments have unique names;
cold replay picks one verified copy if a crash leaves raw and compressed forms.
No rule is discarded or counted as coverage. Private CDCL was not saved from
the stopped processes; restart uses audited semantic rules only.

## Registration and acceptance before restart

Fresh full 271+K9 cloud_smoke.py, fresh native build in a NEW directory, all
1024 fixed five-vertex cases, K3,3, padded-positive50, malformed feedback and
checkpoint controls, chromatic DRAT round trip and cooperative stop are required.
Timing regressions cover slow/missing READY, first-cause retention, expired
deadline, deadline during loading/solving, clock rollback and archive recovery.

Then one bounded 60-second partition-positive semantic-restart benchmark from
the preserved 272374 rows/900798 geometric clauses, independently checking
every replayed rule and returned model. Native startup and solve times must
be reported separately. No requirement to repeat the earlier configuration
comparison: this is an operational timing fix in the same selected domain.
Counts remain activity; caps and bare UNSAT remain UNKNOWN.

Resume only after all acceptance/source/binary/deadline gates pass and exact
old identities have exited, with no owner STOP, scientific alert or native
UNSAT. Explicit current owner authority permits this repaired restart; it
does not grant automatic recovery after a future owner stop. S036 stays stopped.
Read RUNNING.md and actual runtime records before future action. Publication,
outreach, Lean, S046 and improved-bound claims remain gated.
