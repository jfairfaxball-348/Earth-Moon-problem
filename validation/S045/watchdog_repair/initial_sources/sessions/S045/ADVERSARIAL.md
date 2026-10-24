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
