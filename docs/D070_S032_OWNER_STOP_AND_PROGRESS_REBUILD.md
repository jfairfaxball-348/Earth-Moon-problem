# D070 — stop the live S032 search; retain rules; rebuild for progress

2026-10-21 owner explicitly requested a safe stop and preservation of accumulated
information, especially geometric rules. Owner requests a rebuilt solver and a
simple separate command-line progress tool. This supersedes D069's continue
until stop instruction: the stop has now been requested. S032 only; no S033.

Registered STOP caused OWNER_STOP; native process exited, controller snapshotted
and exited, ACTIVE.lock removed and sleep inhibition released. Monitor PAUSED.
Final checkpoint:2579937 complete lines/189309949 bytes, zero incomplete tail,
SHA2566e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177.
Immutable compressed copy and runtime evidence:validation/S032/stopped.
Private CDCL state is lost; saved semantic clauses and exact original inputs
are preserved. No witness or impossibility proof; S11 remains UNKNOWN.

Do not restart the long campaign automatically. Build/test the successor
separately, leaving old native bytes and provenance intact. Bounded verification
and small controls for the rebuild are authorised as part of the owner's request.
Any later resumed campaign needs explicit owner instruction after this handoff.

Progress amendment: add CaDiCaL conflicts/decisions/propagations telemetry to the
native build and provide a separate bounded region-accounting CLI. Rules are
layer clauses, so summing their effects does not count excluded union graphs.
Partition graph-presence variables, attach exact combinatorial weights to each
disjoint region, and only close a region with standalone checked UNSAT proof.
SAT of base+retained clauses is only a relaxation survivor, not a planar witness.
Denominator is the explicitly encoded labelled search domain after graph unit
pins, not all unlabelled graphs or a percentage-to-solution. Encoder symmetry
exclusions must not be advertised as nonbiplanarity results. Bare native UNSAT,
timeouts, approximate counting, rule totals and percentages are not certificates.
