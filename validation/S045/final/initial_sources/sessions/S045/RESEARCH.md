# S045 research and benchmark

Owner selected 50 vertices and explicitly authorised prepare/test/benchmark/
launch. No target change: chi>=10, thickness at most two. The new domain has
all 1225 optional pairs, no independence/degree/symmetry/density restriction.
Inherited attributed native partial-planarity code is preserved as source in
tools/s045_native.cpp; tools/s045_main.hpp supplies a new incremental protocol.
Python independently checks both rotation systems and every colouring before
feeding back a necessary partition clause. Private solver learning persists
between candidates; only audited semantic rules survive slice recycling.

For any map c:V->{0,...,8}, every graph without a proper nine-colouring must
have an edge uv with c(u)=c(v). Therefore OR over both layer variables of all
such pairs is a sound necessary clause. If the current graph is properly
coloured by c, it falsifies that clause and is excluded. No assumption about
alpha is involved. Colour names may be permuted freely; splitting a class
preserves properness and can shorten/strengthen the clause.

| Arm | Verified candidates | Elapsed seconds | Checked geometric cuts |
|---|---:|---:|---:|
| block | 4814 | 60.094 | 1081 |
| partition | 3842 | 60.391 | 11962 |
| partition-positive | 3365 | 61.891 | 38322 |

Default partition feedback selected under the registered operational gate.
Exact blocking visited more models; no speedup or greater projected coverage
is claimed. Each partition rule excludes all graphs permitting that same
colouring, while exact blocking excludes just one layer assignment. Candidate
counts and geometric clause counts are diagnostics. The benchmark contains
no non-nine-colourable candidate, no domain refutation and no headline advance.

Fresh semantic restart: 995 additional verified candidates in 16.125s.

## Streaming revision and repeated benchmark

38042 candidates and 111073 geometric rule occurrences from the first slice
are preserved. Exact regenerated CNF bytes from all rows match; replay private
memory about 33 MB. Wrong n/k/mode and partial checkpoint rows rejected.
Fresh native acceptance repeated after the streaming change.

| Arm | Candidates | Seconds | Geometric rules |
|---|---:|---:|---:|
| block | 4872 | 60.109 | 1081 |
| partition | 3847 | 60.360 | 11981 |
| partition-positive | 4239 | 61.828 | 39430 |

Selected partition-positive; fresh restart added 806 candidates
in 17.594s. This operational selection does not
establish a statistical speedup. Original source/receipts and both benchmarks
remain archived. Same campaign resumes all saved rules, original ceiling.


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
