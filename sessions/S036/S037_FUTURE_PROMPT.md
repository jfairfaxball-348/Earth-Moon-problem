# S037 — Structural reset: nine-region symmetry audit and triangulation-first constructions
FUTURE / UNEXECUTED — installed 24 October 2026

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

**Execution authority (D047):** The owner's subsequent instruction "run next session", pasted S037 prompt or link authorises immediate execution of S037, without further confirmation. Installation here does NOT execute S037. Execute exactly S037, never S038 automatically. Use Codex on the existing repository/main (typically C:\Earth-Moon-problem, Windows laptop), ordinary non-force commits/pushes; no new repository, branch or PR.

## Scientific objective and read-first
Find a more mathematically efficient route to a certified 10-chromatic biplanar graph, potentially raising chi_2 >= 10. The current status is 9 <= chi_2 <= 12, with NO new certified witness. S11 m155/156 remains unresolved; 247/256 encoded regions are DRAT proof-closed and nine IDs UNKNOWN. Do not work on universal upper bounds or full resolution under D042. Do not treat those 247 closures as 247 graph exclusions or as a fraction of computational work.

Read AGENTS.md, authoritative/STATE.json, sessions/S036/CLOSEOUT.md, validation/S036/closeout/{STOP_RECORD,REGIONS_FINAL,CUTS_AUDIT,PRESERVATION_MANIFEST}.json, sessions/S035/NINE_REGION_DIAGNOSTIC.md, sessions/S030/RESEARCH.md, tools/s030_op1b.py, tools/region_partition.py, tools/s031_incremental.py, and the relevant source/claim records. Pin LIVE remote main and verify the S036 closeout commit d972b7832b92c48f2cc920f1f181160e0d2a82e1 is an ancestor. S036 was deliberately terminated; its local artifacts/tmp/S036 is preserved but git-ignored (2.64 GiB at closeout). Do not restart S036, revive its autopilot, wake old processes, overwrite S036 archives, or fabricate unavailable local data. If the original local archive is absent, proceed using committed proofs and source and clearly mark unavailable inputs.

## A — PROVE or refute the symmetry-only explanation of the nine cells (mandatory FIRST task)
The nine unresolved eight-bit region IDs are exactly 0,1,3,7,15,31,63,127,255. The proposed explanation is elementary and must be independently verified rather than assumed:

S030 sorts the neighbours 3..13 of root 0 by nondecreasing type 2*g(1,v)+g(2,v). That implies the g(1,v) bits are nondecreasing. The first eight free graph-presence variables in the S034/S035 partition appear to represent edges (1,3)..(1,10); consequently only the nine zero-then-one patterns 00000000 through 11111111 are compatible, and exactly 247 of 256 prefixes violate the symmetry ordering before any planarity reasoning.

Audit precise variable/edge numbering, graph-unit assignments, split-bit order, registration in the actual frozen formula, sorting-clause truth table and all 256 IDs. Independently prove from the ordered types that forbidden prefixes cannot extend to ANY assignment of the remaining local type bits. Implement a tiny self-contained exact checker (and optional small SAT control containing only sorting constraints) that enumerates all 256 prefixes and reports the nine permitted IDs. Compare the forbidden set with ALL 247 already certified closures. Prove and record which exclusions follow from sorting alone; do not infer that permitted prefixes satisfy the complete S11 formula. Distinguish the tiny combinatorial proof, historical DRAT certificates and full unknown mathematical satisfiability.

If confirmed, explicitly explain why the much-publicised 96.5% regional closure represents predominantly built-in symmetry bookkeeping, not nearing completion. Derive a clean nine-case or symmetry-native alternative to the 256-way search WITHOUT restarting it. If disproved, give the exact failing mapping/assignment and correct the hypothesis. Preserve executable tests and the finite evidence under validation/S037.

## B — CONSTRUCT FROM PLANAR LAYERS (main research effort)
Work with edge-disjoint planar layers by construction instead of adding millions of Kuratowski cuts to initially unconstrained edge variables. At n=28 every planar layer has at most 3n-6=78 edges. Hence a 156-edge biplanar graph must be two edge-disjoint 78-edge triangulations, while a 155-edge one has 78+77. Investigate BOTH density cases and only generalise beyond them on mathematical grounds.

Build a reproducible triangulation-pair search prototype, testing multiple genuinely different construction moves/representations, such as:
* generate distinct planar triangulation seeds, then valid edge flips and vertex relabellings to explore diverse combinatorial triangulations (stacked insertion alone is NOT all triangulations);
* find or optimise a second planar triangulation/one-edge-short planar layer in the complement of the first, with disjoint edges by design; compare local flips, embedding-aware constructive moves and/or a bounded direct constraint model.

Key structural insight: for fixed T1, every four-vertex set independent in T1 MUST contain at least one edge of T2 if alpha(T1 union T2) <= 3. Enumerate this exact family of four-sets and formulate the second-layer problem as a hitting constraint/violation-separation problem. Use its size and actual violated sets as a constructive objective; avoid arbitrary conflict-count progress. Ensure all proposed edges of T2 are absent from T1 and its embedding remains planar. Record independently checked feasible layer pairs, best alpha or independent-four-set violations, actual CPU time and reproducible random seeds. Failed heuristics are UNKNOWN, not impossibility proofs.

If any 28-vertex two-layer union has no independent four-set, it necessarily requires at least ceil(28/3)=10 colours. Independently verify each layer's planarity, all 28 vertices, 78+78 or 78+77 edges, disjointness, simplicity and all C(28,4)=20475 four-sets with a separate checker. Preserve explicit V,E1,E2, a reproducible validation script and immutable hashes. Never call a relaxation SAT assignment a witness or a numerical estimate of independence an exact result. Independent validation is mandatory before updating any lower-bound claim. Try falsifying candidates and algorithms on small positive/negative controls.

Do not confine all constructive searches to S11's anchored degree class: the point is to explore explicit biplanar constructions, including plausible alternative vertex orders when well motivated. A negative result for the S11 encoding does not exclude other graph classes.

## C — MATHEMATICAL REDUCTIONS + genuinely different solvers
Explore structural restrictions unique to paired dense planar layers: face and degree constraints, disjoint embedding feasibility, forced local patterns and four-set hitting. Seek a short standalone lemma that reduces witness search, and actively search for counterexamples to it. Independently check exact claims and prior art; no novelty claim from a heuristic.

If useful, implement and benchmark ONE genuinely different bounded exact formulation (e.g. direct rotation/embedding constraints, triangulation-complement hitting constraints with planarity separation, or a constructive CP-SAT/ILP), contrasting it with the current CaDiCaL + lazy Kuratowski strategy. Do not merely rerun the same nine region formulas with different solver flags. A bounded experiment may remain UNKNOWN; report it as such.

## Compute policy, priorities and closeout
This is a discovery/prototype session, NOT another indefinite laptop grind. Give meaningful mathematical deliverables precedence over raw computing. Cap heavy experimental compute initially at 2 cumulative CPU-hours (not counting short controls) and do not start unattended autonomous workers or scheduled restarts without new owner authority. Stop individual experiments when evidence no longer improves; preserve partial data and errors. If Codex is executing in a cloud/container without the Windows archive, run only portable appropriately bounded work; do not falsely claim Windows lifecycle or restored local data.

Order of work: (1) establish the nine-pattern theorem with independent exact finite verification; (2) direct triangulation-first prototype and independently checked candidates/obstructions; (3) investigate an alternative formulation and rank the directions by measured mathematical promise. Summarise whether dense planar-pair search is feasible, why searches fail or succeed, and what structural breakthrough is still required. No expectation that S037 must finish all nine regions.

Keep research and test artifacts in sessions/S037 and validation/S037 and avoid unnecessary session bureaucracy. Preserve frozen S036 records and mathematical gates. Close out S037 with concise status/limitations, tested commands, independently validated outputs, verified normal commit/push to existing main and actual hosted results. Recommend a concrete S038 direction supported by S037 evidence. Install an identical full S038 FUTURE/UNEXECUTED prompt in authoritative/NEXT_SESSION_PROMPT.md and an archival copy, and print the full next prompt with verified links in the closeout. Do not execute S038.

**Status now: S037 FUTURE / UNEXECUTED; the old solver stays STOPPED until a new explicitly authorised experiment.**
