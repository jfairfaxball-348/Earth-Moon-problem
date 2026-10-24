# S036 closeout — CLOSED, OWNER-DIRECTED CLEAN STOP (24 October 2026)

The owner stopped the S036 solver campaign as a deliberate research-strategy pause
(not an abandonment). Computation is STOPPED. No next session is queued:
authoritative/NEXT_SESSION_PROMPT.md is a non-executable holding notice, and S037
was neither installed nor executed.

## Shutdown (validation/S036/closeout/STOP_RECORD.json — CLEAN_STOPPED)
Final SAT-first scan first: 5111 scientific files, no SAT/candidate/exit 10, no native
UNSAT output, nothing unreadable (SAT_FINAL_AUDIT.json). Then the registered owner
pause (`s036_fresh_campaign.py pause`, OWNER_PAUSE.json, so the autopilot classified it
BLOCKED); the controller suspended all residents without errors and the supervisor
exited. The suspended cold solver (region 15) was resumed only to honour its stop file
and exited 0. Each resident was resumed briefly with its stop file set and exited 0
with the cooperative-stop marker and `s UNKNOWN`; its final geometric tail was audited.
Idle helpers (cold runner, autopilot) were ended with no solver child. No solver was
force-terminated. No S036 process remains; the scheduled check-in task is disabled and
the in-chat relay deleted.

## Final nine-region status (all UNKNOWN; REGIONS_FINAL.json)
| Region | S036 work | Audited clause occurrences |
|---:|---|---:|
| 0 | resident; gen 0 recycled at 80.4M conflicts, gen 1 stopped at 12.9M | 4207668 |
| 7 | resident; gen 0 recycled at 70.5M, gen 1 stopped at 25.8M | 3930844 |
| 127 | resident gen 0 stopped at 97.0M | 167 |
| 255 | resident gen 0 stopped at 91.1M | 408054 |
| 1 | 5 diagnostic arms; rotation 3.4 h stint + yielded retries (56.9M) | 4311368 |
| 3 | 5 arms; one 70 min stint (25.4M) | 36798 |
| 15 | 5 arms; two stints, 54 min total (19.9M) | 1228903 |
| 31 | 5 arms only | 29169 |
| 63 | 5 arms only | 12240 |

Conflict and cut counts are effort measures, not progress toward closure; per-region
occurrences overlap and are not unique clauses. Inherited baseline unchanged:
247/256 encoded regions proof-closed (S034/S035 certificates) — not a whole-stratum
proof and not graph exclusions.

## Mathematical status (unchanged)
9 <= chi_2 <= 12. Nine encoded S11 regions UNKNOWN; S11 m155/156 UNKNOWN; regular154
SOURCE_STATED; S10/S9/S8 NOT_RUN. No certified 10-chromatic biplanar witness. No
native UNSAT occurred, so no proof is pending. CLM-0122 records the finite closeout audit.

## Preserved and lost
Preserved (durable, local, git-ignored, pinned by PRESERVATION_MANIFEST.json under
artifacts/tmp/S036): every geometric clause each process wrote, as immutable audited
blocks registered in artifacts/tmp/S036/cold/LEDGER.json and re-audited at closeout
(CUTS_AUDIT.json: 60 blocks, 14165211 clause occurrences, all PASS; runtime manifest 4056 files, 2.64 GiB); exact input recipes and SHA256 (INPUT.json in every run
directory; the frozen cold DIAG_RECIPE.json files); native logs, metrics, journals,
diagnostic summaries, adoption and rotation records; the S036 native build and source
hashes. S035 durable archives are unchanged (sessions/S035/RECOVERY_HANDOVER.md).
Committed evidence: validation/S036/ and validation/S036/closeout/.
Lost (unavoidable, never claimed): private CDCL (learned clauses, phases, scores) of
the S035 retained contexts (app closure, 23 Oct 12:14 UTC) and of every S036 process at
recycle or closeout. Loaded input copies were released after load; each is exactly
reproducible from its recipe (base CNF, S032 seed, S035 ledger cuts, S036 blocks).

## What S036 accomplished
Repaired and accepted the S035 watcher failure (sharing-tolerant fail-closed SAT
scanner, explicit stop reasons); recovered after the S035 identity loss with audited
semantic state; WMI launches outside application job objects; measured machine limits,
four concurrent residents and automatic recycling; stall-proof controller (heavy steps
in separate processes) and an autopilot that recovered a real overnight pause; registered
equal-input cold diagnostics (baseline kept in all five cold regions) and a fair cold
rotation with fixed-size inputs.

## Lessons and bottlenecks
- Processes launched from an app shell die with the app; launch long runs via WMI.
- Fresh residents grow with learning; recycling trades private CDCL for continuity.
- Cut journals grow fast (regions 0/7: millions per generation), inflating restarts.
- Algorithmic bottleneck: the nine monotone regions are essentially the whole stratum;
  one-solver-per-region CDCL with planarity cuts showed no measurable route to closure,
  and a closure would still need a standalone DRAT within the 2 GiB per-attempt cap.

## Handover
The existing solver has been deliberately stopped pending a new research strategy.
To recover data in a future session: read this file, validation/S036/closeout/*.json
and sessions/S036/RUNNING.md; runtime evidence is in artifacts/tmp/S036 (verify against
PRESERVATION_MANIFEST.json). Do not restart the campaign or treat any earlier prompt as
queued; wait for the owner's next session.
