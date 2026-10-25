# S045 adversarial and operational review

Fresh full smoke: all 271 chromatic input byte matches/proofs, retained K9
and new native K9 proof PASS. Exhaustive 1024 fixed five-vertex layer cases,
K3,3, padded 50-vertex positive, independent disconnected/isolated rotation
checks, 5184 partition truth-table cases, invalid feedback, truncated geometric
checkpoint, chromatic oracle/DRAT round trip and cooperative stop PASS.

Two preparation failures are retained, not promoted: the imported positive
fixture had reverse-ordered endpoints, exposing a canonicalisation omission;
normalize endpoints before encoding and comparing. A Windows psutil call
needed str(Path), rather than WindowsPath. Failed attempts and full logs stay
under artifacts/tmp/S045/controls*; final successful suite is controls-r3.
No failed run established a mathematical exclusion. Compact failure logs are
permanent under validation/S045/failures/.

Native UNSAT is always UNKNOWN without a separate full proof. A colouring
UNSAT alert stops the run and needs standalone proof verification. Independent
rotation Euler checks operate component by component and include isolates.
No criticality or edge saturation is assumed. Graphs with smaller critical
cores remain admissible. No canonical enumeration/completeness-speed claim.

The portable historical check scripts hard-code a globally stopped runtime.
They remain byte-for-byte frozen. scripts/s045_replay_history.py replays them
against the actual archived entry STATE and original prompt, explicitly as
historical checks. check_s045_records.py separately validates current S045
authority. This separates historical evidence from current process state;
it neither changes a frozen certificate nor weakens its hash check.

Guard controls check the wall ceiling, resource floor and changed-source
stop conditions. WMI launch avoids the application's job object. No blind
PID reuse, duplicate launch or automatic resume; status checks creation time
and executable. A private-state checkpoint is never claimed. Source/binary
change, unsafe resources, owner STOP, native UNSAT, non-nine alert, fault or
eight-hour ceiling stops the new run. S036 remains CLEAN_STOPPED.

The first local CI pass exposed interaction with the legacy D072 checker,
which temporarily writes and restores the active prompt. Exclude it from
the entry-state wrapper, restore the executed S045 prompt, and rerun CI.
Its historical source is unchanged; failed CI log retained. No solver or
scientific state was resumed or stopped by that check.

Streaming revision: final acceptance suite controls-streaming-r2 PASS; original
controls-r3/source/benchmark receipts retained under before-streaming. Initial
slice fully archived. Maintenance stopped cooperatively; exact former process
identities exited. The pre-stop second-slice entry has zero new candidates and
no generator, and is not counted as new scientific execution. Explicit operator
resume checks old identities and owner STOP, preserves controls and all journals,
and retains the original ceiling. This is current owner-authorised preparation
and search, not automatic recovery of an owner stop. Runtime guard/keep-awake
helpers are newly scoped to S045 only. No historical process was touched.


Watchdog repair, owner instruction of 24 October 2026: the old parent timer
started before native checkpoint loading while the solver timer started after
loading. The observed 614.69-second stop is consistent with that mismatch;
the old STOP_FILE overwrite lost the actual first cause, so this remains a
root-cause inference supported by a fresh regression test. Separate READY
and solve clocks fix the mismatch; immutable STOP_CAUSE preserves provenance.
The full cold restart loaded 900798 rules in 18.156 seconds, exceeding the old
15-second allowance, then completed its registered 60-second solve slice.
All original 272374 rows/900798 geometric rules survive in decoded-hash-checked
archives. Benchmark additions 3587 rows/23525 cuts were independently replayed
and transferred using identical n=50 labelled vertices and lexicographic
variables 2i+1/2i+2. These are unconditional colouring/Kuratowski clauses for
the same target. Seed is now 275961 rows/924323 geometric rules. Private CDCL
was lost on the earlier exit. No projected coverage or graph exclusion follows.
The owner replaced all eight-hour roofs with 25 October 07:30 UTC/GMT.
Timing controls cover missing/slow READY, preparation/loading/solving deadline,
clock rollback, first cause, byte-preserving compression and duplicate recovery.
Actual two-hour heartbeat receipt is CHECKIN.json. The live search remains S045;
S036 stays stopped, no S046 invoked, no witness or bound advance.


S045 memory-limit recovery, 24 October 2026: the 20:22 UTC safe stop was
PRIVATE_MEMORY_LIMIT, native rc0; no owner STOP, alert or uncertified UNSAT.
Four completed slices preceded it. All 453656 candidate records and 1570940
geometric rule occurrences were preserved; the pending final 72775-rule
geometric tail was independently checked during recovery. Private CDCL ended
with its process. Fresh full 271+K9 smoke, all 1024 native fixed n5 cases,
protocol/DRAT controls, timing controls and real-child memory regressions PASS.

Resource policy now ends a native slice cooperatively at 2.5 GiB aggregate
private memory; after independent audit the next slice reloads ALL semantic
records. The existing 3 GiB hard cap, 1.5 GiB available floor and 10 GiB disk
reserve remain. A local SLICE_STOP is distinct from durable campaign STOP.
Owner/scientific/hard-resource/deadline stops remain latched. An already-too-large
checkpoint producing zero new candidates stops CHECKPOINT_MEMORY_NO_PROGRESS;
no endless zero-progress restart. No increase to the machine's resource limits.

Current acceptance: validation/S045/memory_recycle/ACCEPTANCE.json; seed
459411 candidate records / 1590816 geometric
rule occurrences includes the independently checked restart benchmark additions.
The native binary and mathematical checks are unchanged; source pins include
the recycling driver. Original watchdog evidence stays frozen and is replayed
with scripts/s045_replay_watchdog.py against its exact 673d4a6 context.

Two-hour check-ins remain ACTIVE. Hard stop remains 25 October 2026 07:30
Europe/London = UTC/GMT. S045 continues, S036 stays stopped, no S046 invocation.
Counts are activity, not projected coverage; no witness; 9<=chi_2<=12.


Final UNSAT-priority amendment: while the resumed controller was still in
checkpoint replay (no native generator), review found that concurrent memory
recycle and native exit 20 needed an unconditional stop latch. Replay was
cooperatively paused; final native/protocol, timing and memory regressions PASS,
including forced concurrent recycle/UNSAT remaining STOPPED. The prior full
checkpoint benchmark returned 0 and retains its ORIGINAL source hashes. An
exact byte comparison proves the only driver delta is the added exit-20 latch;
the normal exit-zero path is unchanged. It was not labelled a rerun of that
full benchmark. See memory_recycle/UNSAT_GATE_AMENDMENT.json for this explicit
compatibility gate and final tested hashes. No mathematical claim follows.


S045 CLOSED_OWNER_DEADLINE_UNKNOWN, 25 October 2026. Search stopped at
07:30 UTC/GMT as requested; first-cause latch was 0.002776 seconds
after the absolute deadline. Final controller, native generator and power
helper identities have exited; keep-awake released; no restart or S046 execution.

Saved candidate/colour records: 642381. All archive bytes
were verified. The previously independently checked 453656-record
prefix was reused by exact archive hashes; 188725 additional records
received fresh layer/rotation, proper-nine-colouring, bit-map and partition
checks. All 2376754 geometric clause occurrences were freshly
checked as Kuratowski subdivisions on the registered variable map. These
counts are activity and retained evidence, not unique unlabelled graphs,
projected coverage, a percentage toward a witness or a finite exclusion.

All retained native traces were scanned (642382 candidate occurrences).
1 previously unjournalled distinct layer assignments were decoded,
independently checked planar and nine-coloured; certificates are ORPHANS.jsonl.gz.
No retained native UNSAT signal or pending scientific alert was found. No
certified chi>=10 witness; 9<=chi_2<=12 unchanged. Nine sorted S11 prefixes,
order-3 domain and historical unresolved construction windows remain UNKNOWN.

The main operational result is a reproducible bottleneck: as the checkpoint
grew, the 2.5 GiB soft recycle threshold was reached almost immediately after
loading, and all-rule replay plus audit dominated roughly twelve-minute cycles.
From 04:49 through 06:15 UTC the last eight observed slices added only
21,12,1,1,1,1,95,60 records. Later growth remained small. More total records
and more CPU do not constitute a lower-bound advance. S046 must change this
mechanism before any longer run; its bounded acceptance gate is operational.

Private CDCL state was discarded at process exit and is not durable. All
semantic journals, geometric clauses, retained native traces, original/fixed
source contexts, stop provenance and check-in records are archived by
validation/S045/final/ARCHIVE_INDEX.json. Existing S045 acceptance and repair
receipts stay immutable; historical checkers run against exact frozen context.

Fresh Windows full 271+K9 smoke PASS. Final audit command:
.venv/Scripts/python.exe scripts/audit_s045_final.py
Portable complete closeout replay:
python scripts/check_s045_final.py
Source/environment, raw-versus-compressed hashes and prior checks are in
validation/S045/final. All replay data are permanent repository files, not
expiring hosted ZIPs. Hosted scaffold replay is distinct from local native
acceptance and mathematical scope.

Integration: existing main; ordinary non-force publication; no branch/PR.
Entry main307399a7ce471f722181098a93c8378d5b2f5824,
tree27e46b9ff7ec7fc81a1a12e3534877a071b5b276, parent673d4a6b38cecf2533f3fc21ae66f09c7908685e.
Actual final commit/parent/tree and hosted run/job are independently verified
after publication, reported to the owner and recorded locally in
artifacts/tmp/S045/FINAL_INTEGRATION.json. No zero-context CI claim.

Next: S046 memory-bounded redesign and bounded acceptance, FUTURE/UNEXECUTED.
The full prompt is byte-identical in authoritative/NEXT_SESSION_PROMPT.md and
sessions/S045/S046_FUTURE_PROMPT.md. Only the owner's provision invokes it.
Actions fallback remains docs/CLOUD_ENVIRONMENT.md and
validation/S011/SUMMARY.json, with pinned setup plus full smoke in the SAME job.
No S046, Lean, publication, outreach or S035/S036 resumption is performed here.
