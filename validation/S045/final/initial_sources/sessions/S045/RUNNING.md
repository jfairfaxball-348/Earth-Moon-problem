# S045 memory recovery accepted — 24 October 2026

Read validation/S045/memory_recycle/ACCEPTANCE.json and the current execution
prompt. A 2.5 GiB soft threshold recycles completed, audited native slices
before the unchanged 3 GiB hard cap. All semantic journals are retained and
replayed. Hard stop remains 25 October 07:30 UK/GMT. Two-hour checks ACTIVE.
S036 stopped; no automatic S046. Historical handover follows.

# S045 watchdog repaired and restarted — 24 October 2026

Hard search stop: **Sunday 25 October 2026, 07:30 Europe/London = 07:30 UTC/GMT**.
All former eight-hour ceilings are superseded. Two-hour heartbeat
`earth-moon-s045-two-hour-check-in` is ACTIVE. Read the current execution
prompt and `validation/S045/watchdog_repair/ACCEPTANCE.json`.

The repaired campaign was WMI-launched at 19:03:06 UTC. Exact live identities
are in campaign STATUS/IDENTITY; stored PIDs below are observations, never
authority to signal a process. Keep-awake helper is ACTIVE until the deadline.
Read-only: `.venv/Scripts/python.exe scripts/s045_campaign.py status --brief`.
Safe stop: `.venv/Scripts/python.exe scripts/s045_campaign.py stop`.
No automatic restart after STOP, alert, UNSAT or the deadline. No S036/S046.

Checkpoint preparation and loading are separately visible. Native READY starts
the 600-second solve timer; 900-second loading ceiling remains bounded by
the owner's absolute deadline. STOP_CAUSE.json preserves the first cause.
Whole-run deadline checks use wall UTC and monotonic time. Closed journals
are byte-verified gzip archives; raw active files remain append-only.

All 272374 original candidate records and 900798 geometric rule occurrences
were preserved byte-for-byte. The full restart benchmark checked the entire
checkpoint, loaded natively in 18.156 seconds and finished its requested
60-second solve slice. It added 3587 independently checked colour partitions
and 23525 geometric cuts, now included in production (275961/924323 seed).
Counts are activity, not unique graphs or projected coverage. No witness;
9<=chi_2<=12. Fresh full smoke, native controls and timing/deadline controls PASS.
Original evidence/source bytes remain frozen under initial_sources and
preserved; scripts/s045_replay_initial.py verifies that historical context.

Historical running handover follows; its former eight-hour limits are superseded.

# S045 sustained 50-vertex search — IN PROGRESS

Owner authorises preparation, testing, benchmarking and search. S036 remains
CLEAN_STOPPED. No witness or domain exclusion; 9<=chi_2<=12 unchanged.

Current accepted configuration: partition-positive. Positive edge preferences
are a heuristic, not a restriction. Domain: all 1225 optional pairs on 50
vertices, two disjoint planar layers, direct non-nine-colourability; no alpha,
degree, symmetry or exact-density restriction. Fresh full 271+K9 acceptance,
exhaustive native controls, independent rotations/colourings, DRAT round trip,
cooperative STOP and semantic restart PASS. Repeated final benchmark:

| Arm | Candidates | Seconds | Geometric rules |
|---|---:|---:|---:|
| block | 4872 | 60.109 | 1081 |
| partition | 3847 | 60.360 | 11981 |
| partition-positive | 4239 | 61.828 | 39430 |

Semantic restart added 806 candidates. Counts are activity,
not graph coverage, speedup or an ETA. Certificates: validation/S045/benchmark-streaming.
Original benchmark/source receipts remain under benchmark and before-streaming.

## Runtime authority

Root artifacts/tmp/S045/campaign. CAMPAIGN.json identifies the controller;
STATUS.json the slice; IDENTITY.json the generator; LAUNCH.json WMI dispatch.
ERROR.json / GUARD_STOP.json override stale labels. Match PID, creation time
and executable. Never remove a lock, duplicate a run or automatically resume
a STOP/error. No S035/S036 controls. Read-only status and cooperative STOP:

    .venv/Scripts/python.exe scripts/s045_campaign.py status
    .venv/Scripts/python.exe scripts/s045_campaign.py stop

One generator with serial oracle, 3 GiB solver/controller private-memory cap,
1.5 GiB available-RAM floor and 10 GiB disk reserve. Eight-hour wall ceiling
from original start 16:23:36 UTC on 24 October 2026, including maintenance.
WMI launch avoids the desktop app job. Watchdog latches STOP on resource
breach, changed source/binary or ceiling. POWER.json records a bounded Windows
keep-awake request, released when the exact controller exits or ceiling arrives;
the display is not kept on. No recurring task or unattended successor session.

600-second slices retain all audited semantic rules and discard private CDCL.
Learning persists between candidates inside a slice; no private-state checkpoint.
After owner STOP verify actual exits and retain every journal, log and receipt.

## Preserved work and maintenance

First slice completed 38042 checked nine-colourable candidates and 111073
checked geometric rule occurrences. All data are permanently compressed under
validation/S045/initial-slice. Memory buffering grew; cooperative maintenance
retired the old processes and preserved all rules. Streaming replays exactly
the same CNF from all 38042 rows with about 33 MB replay-process memory.
Wrong vertex count, colour target, feedback mode and partial rows are rejected.
Full native controls and the three-arm benchmark were repeated after the change.

Operator-directed resume-maintenance requires accepted byte hashes, exact old
identities exited, no owner STOP and preserved control files. The SAME campaign
resumes every rule under the original ceiling; this is not automatic recovery.
Maintenance evidence and initial source/benchmark are permanent.

Latest permanent launch observation: 39893 total candidates,
1851 new since restart, controller PID 3616,
generator PID 13388, about 30.1s into that slice.
Controller private memory 36.5 MiB. Exact identity
and increasing native CPU checked. These are historical observations; read
runtime files for current identities. Receipt: validation/S045/LAUNCH_SNAPSHOT.json.

## Reproduction and eventual closeout

Build recipe scripts/build_s045_native.py and validation/S045/BUILD.json pin
source and executable bytes. Existing accepted packages/compiler were reused.
Portable replay: python scripts/check_s045_records.py. Immutable historical
checks use the actual archived entry state; current S045 is checked separately.
Native scientific replay requires fresh full cloud_smoke.py. Alternate Actions
runner: docs/CLOUD_ENVIRONMENT.md and validation/S011/SUMMARY.json, setup and
full smoke in the SAME job.

Bare native UNSAT or a non-nine alert stops with UNKNOWN until full independent
proofs pass. A witness needs labelled V,E1,E2, independently checked planar
rotations, standalone chromatic DRAT, and a proper ten-colouring for chi=10.
After this campaign ends, reconcile/retain final evidence and close S045;
install identical full S046 FUTURE/UNEXECUTED prompts in authoritative/ and
sessions/S045/, print the full prompt and verified GitHub links, then stop
before S046. There is no S045 closeout verdict yet. No publication/Lean authority.


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
