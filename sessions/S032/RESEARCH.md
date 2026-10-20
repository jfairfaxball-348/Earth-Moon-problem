# S032 research — in progress

S031 diagnosis: full-assignment CEGAR spent205206574 conflicts in28692s finding46 assignments, then excluded their nonplanar layers. Its repeated budget re-entry kept learned clauses but supplied geometry only at full models. Throughput alone supplies no coverage or exhaustion estimate.

Material change: inspect SRC0055 bipsat2 at ab6e472b7ef4ab7dca1d12c8907b3c74399d3828 (MIT), optional-edge native external propagator. Native Boyer–Myrvold checks each partial layer and emits a monotone Kuratowski clause. Use S004 pinned CaDiCaL3.0.1 with Windows LLVM-Mingw toolchain; adapted API reserve->resize. All336030 S031 clauses/17976 variables retained via bijective renaming only, literal original CNF byte match. No external encoder, twin symmetry, enumeration or model blocker is used.

Independent pre-use guard: suppress every degree-two vertex in the returned edge certificate, rejecting loops/duplicates or a suppressed edge already present; accept only K5 (5 vertices all degree4) or connected bipartite cubic graph on6 vertices with3+3 sides, hence K3,3. Suppression reverses subdivisions, so the original support is nonplanar independently of the native planarity algorithm. Mapping verifies certificate support corresponds to the current layer, yielding only the clause disallowing all those presence literals together. Planarity is inherited by subgraphs; no planar layer can violate it. Python independent suppression also audits archived clauses after every diagnostic and at closeout.

Native source emits a full SAT assignment for independent literal/domain validation; no witness promotion from native text alone. A full-formula standalone DRAT replay/check is required for UNSAT, including all validated theory clauses as necessary axioms. Full stratum UNKNOWN until exact scope/encoding/cut/proof review. Native semantic clauses persist; private CDCL state does not survive process loss.

## Checked diagnostic (CLM-0118) and owner duration amendment

300s diagnostic:829538 native planarity checks,162536 independently replayed Kuratowski clauses, no full model, UNKNOWN. Whole336030-clause input renaming independently checked. Campaign resumes valid clauses, losing private diagnostic CDCL state. D069 removes fixed wall limits: --cap0/--timeout inf (positive24 callback control passed); parent and proof/checker loops retain resource/owner stops only. Campaign running; no whole-stratum or witness claim.
