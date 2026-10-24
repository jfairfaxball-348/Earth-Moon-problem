# S037 preregistration

Exactly S037; S038 is not executed. Frozen S036 files and runtime stay untouched.

1. Before constructive experiments, independently inspect committed S032 mapping,
   original S031 frozen formula, S034 partition, S035 final closure receipts.
   Enumerate all 16 consecutive type assignments and all 256 prefixes; compare
   dynamic extension, exhaustive missing bits, and the monotone-bit proof.
   Verify every sorting clause is present in the frozen formula and its native
   renaming. Optional SAT is only a control, never a full S11 verdict.
2. Generate n=28 triangulations by stacked insertion AND a bipyramid seed,
   diversify by embedding-preserving flips, optimise relabellings for packing,
   then search disjoint layer pairs with independent-four-set objective.
   Compare flips and relabelling kicks; test both 78+78 and 78+77 cases.
   Record seeds, actual process CPU and wall seconds, moves, exact violation
   counts and explicit best layers. Failure is UNKNOWN. Preserve partial results.
3. Test a different finite exact formulation: fixed T1, permitted T2 edges in
   its complement, independent-four-set hitting, degree/edge bounds and small
   planar-subset cuts. Bound solving by conflicts and CPU time; distinguish a
   necessary relaxation from a verified planar pair. No bare UNSAT promotion.
4. Independently validate layers using rotation face traversal, Euler, NetworkX
   planarity, disjointness and direct enumeration of all 20475 four-sets.
   Controls include known planar/nonplanar graphs and deliberate corruptions.
   Prove a useful fixed-layer obstruction and seek explicit counterexamples to
   tempting stronger claims. Inspect primary prior art; claim no novelty.

Resource registration: one experimental process at a time; total heavy compute
<=7200 cumulative process CPU seconds, short smoke/controls separately logged.
Initial local-search allocation <=600 CPU seconds across seeds 3700..3711;
stop each arm at <=50 CPU seconds or 15000 proposals, and stop on zero violations.
Exact formulation <=120 CPU seconds total, <=20000 conflicts per arm, <=6 arms.
These are ceilings, not targets. No autonomous, scheduled or unattended jobs.
Expected small working set (<1 GiB); incremental checkpoints per completed arm;
no large DRAT from discovery prototypes. Later changes require recorded rationale
within the installed two CPU-hour maximum. No new formalisation/publication.

Measured refinement: initial random moves used 13.3125 CPU seconds, produced 11
checked pairs, best 125/180 violations at 155/156 edges. Add four guided all-legal
flip descent arms from states 0,3,2,11 (seeds 3712..3715): <=30 CPU seconds each,
<=2000 sweeps, stop at 300 sweeps without improvement. Register before execution.
The alternative exact model uses fixed planar templates and vertex-bijection SAT:
<=20 CPU seconds and 20000 conflicts per arm, four arms. No exclusion claim.

Final diagnostic, registered before running: two fixed-T1 complement hitting
relaxations (77 and 78 edges), <=20000 native conflicts each, within the original
six-arm/120 CPU-second exact allocation. Second-layer planarity is omitted only
in these labelled relaxations. Independently check all four-sets and test
nonplanarity. This tests whether covering alone is a bottleneck, not a witness.
