# S032 research — in progress

S031 diagnosis: full-assignment CEGAR spent205206574 conflicts in28692s finding46 assignments, then excluded their nonplanar layers. Its repeated budget re-entry kept learned clauses but supplied geometry only at full models. Throughput alone supplies no coverage or exhaustion estimate.

Material change: inspect SRC0055 bipsat2 at ab6e472b7ef4ab7dca1d12c8907b3c74399d3828 (MIT), optional-edge native external propagator. Native Boyer–Myrvold checks each partial layer and emits a monotone Kuratowski clause. Use S004 pinned CaDiCaL3.0.1 with Windows LLVM-Mingw toolchain; adapted API reserve->resize. All336030 S031 clauses/17976 variables retained via bijective renaming only, literal original CNF byte match. No external encoder, twin symmetry, enumeration or model blocker is used.

Independent pre-use guard: suppress every degree-two vertex in the returned edge certificate, rejecting loops/duplicates or a suppressed edge already present; accept only K5 (5 vertices all degree4) or connected bipartite cubic graph on6 vertices with3+3 sides, hence K3,3. Suppression reverses subdivisions, so the original support is nonplanar independently of the native planarity algorithm. Mapping verifies certificate support corresponds to the current layer, yielding only the clause disallowing all those presence literals together. Planarity is inherited by subgraphs; no planar layer can violate it. Python independent suppression also audits archived clauses after every diagnostic and at closeout.

Native source emits a full SAT assignment for independent literal/domain validation; no witness promotion from native text alone. A full-formula standalone DRAT replay/check is required for UNSAT, including all validated theory clauses as necessary axioms. Full stratum UNKNOWN until exact scope/encoding/cut/proof review. Native semantic clauses persist; private CDCL state does not survive process loss.

## Checked diagnostic (CLM-0118) and owner duration amendment

300s diagnostic:829538 native planarity checks,162536 independently replayed Kuratowski clauses, no full model, UNKNOWN. Whole336030-clause input renaming independently checked. Campaign resumes valid clauses, losing private diagnostic CDCL state. D069 removes fixed wall limits: --cap0/--timeout inf (positive24 callback control passed); parent and proof/checker loops retain resource/owner stops only. Campaign running; no whole-stratum or witness claim.

# S032 closeout — safely stopped; rules preserved; progress tools rebuilt

Owner stopped the long campaign under D070 on2026-10-21. Registered STOP
produced OWNER_STOP, the native/controller exited, lock cleared and sleep
inhibition released. Monitor PAUSED. No long search has been restarted.

Retained2579937 complete geometric rules (162536 diagnostic seeds plus2417401
campaign additions),189309949 bytes, zero partial tail. Full independent
subdivision audit and exact336030-clause/17976-variable input renaming passed.
Uncompressed SHA2566e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177.
The190MB plain file and lossless archive are verified; compressed bytes, exact
source/runtime/input and controls are permanently archived. Private CDCL state
was lost at stop, as disclosed; semantic geometric knowledge is preserved.

Wall duration88133.828s includes8h34m battery sleep; about15.9 CPU hours were
observed before stop. Last native counters14653878 partial checks, zero complete
models. Peak aggregate private2774176KiB, below11GiB. S11 UNKNOWN; no witness,
stratum proof or lower-bound advance. Regular154 source-stated; S10/S9/S8
NOT_RUN and conditional-delta/parked/publication/formalisation gates unchanged.

Built a separate native successor with periodic/final conflicts, decisions and
propagations telemetry. Rebuilt1024 exhaustive n5/fixed K33/positive24 controls
passed.2s free K9 remained UNKNOWN; neither earlier60s/300s caps nor this stress
test certify K9. New disjoint-region accounting has exact combinatorial weights
and requires standalone checked DRAT to close a region. Tiny controls test SAT
remaining unresolved, damaged-proof rejection and exact weights. Exported real
cell128 payload byte-matches its independently refuted formula.

Real cell128 is checked UNSAT both WITHOUT and WITH retained campaign clauses.
It closes0.9685672240percent of the stated unit-pinned encoded denominator,
already implied by baseline encoder/symmetry constraints. This is NOT a new
nonbiplanar graph exclusion, a measured benefit from new rules, a witness, or
percent-to-solution. Its first augmented15s checker cap remains UNKNOWN;
later60s replay/check succeeded. All proof/cap bytes are archived. Other255
regions unresolved; no exact count of graphs excluded solely by learned layer
rules was computed. That would require projected counting over graph edges with
existential layer/auxiliary assignments, not addition of rule effects.

Read PROGRESS_TOOLS.md for CLI commands and limitations. `report` starts no
solver; `check` explicitly starts bounded standalone proof work only; `export`
writes future region input only. No successor search or S033 was executed.
Historical RUNNING/PLAN/launch snapshots retain original wording/provenance;
D070 supersedes D069 continuation. S033 future prompt requires fresh invocation
and a practical budget, fresh smoke and domain/resource/proof gates.

One atomic authored session commit from entrymain e3145c77a7350ebd2c8aa3197cf97bf5e626099f;
WIP backup history is never inherited. Ordinary PR/non-force two-parent merge
and actual head/main hosted jobs are verified after commit. Job identities are
reported live because a commit cannot pin its own final hash. Scaffold checks
test integrity/governance, not mathematical soundness or search exhaustion.
