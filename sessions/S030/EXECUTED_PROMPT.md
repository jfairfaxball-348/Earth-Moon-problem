# S030 — OP1(b) at order 28: certified two-sided decision of biplanar graphs on 28 vertices with alpha<=3 (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

The owner's submission of this prompt, its link, or 'run next session' invokes exactly S030 under D047. No second confirmation. Stop before S031. Governing decisions: D062 (docs/D062_LANDSCAPE_THEN_ALPHA3_DIRECTIVE.md) as modified by the frozen S029 audit (D063; research/S029_LANDSCAPE.md, GO-MODIFIED). D042 lower-only headline unchanged; no universal upper-bound work.

## Why this is narrower than the D062 draft (recorded S029 reasons)
1. Lemma F (n<=36) is superseded: n<=30 follows from Szeider's alpha<=2 => n<=18 (CLM-0111, conditional on SRC-0037), and rStation paper 59 claims n<=28 (SRC-0045). Do not re-prove n<=36 (filed as CLM-0110).
2. A biplanar alpha<=3 graph on >=28 vertices exists iff one exists on exactly 28, and each such graph has chi>=10 (CLM-0112). So the whole alpha<=3 counting/witness route is Gethner–Sulanke Open Problem 1(b): is there a biplanar graph on 28 vertices with K4-free complement? It is open (Szeider: feasibility unknown).
3. T3 for 21<=n<=27 is NOT a counting question. It overlaps the rStation order-by-order programme (orders <=20 claimed closed, order 21 in progress, projected ceiling about 22–23). It is PARKED, not attempted in S030.
4. rStation (as of the 2026-10-19 freeze) partly covers order 28: the 11-regular 154-edge case is excluded (paper 59 Thm 12/Cor 13, RUP packet CC0); delta>=11 forces 155 or 156 edges; some 155-edge normal forms are excluded (post 146); fully twinned quotients are 2,543/2,555 decided (post 155); the fixed-point-free Z7 case gives only C7[K4] (post 152, not DRAT-certified). OPEN there: delta<=10 entirely, and delta=11 with m in {155,156}.

## Domain and statement
D28 = simple graphs G on vertex set {0..27} with alpha(G)<=3 that are biplanar (thickness<=2, not geometric thickness). Two-sided target:
* WITNESS: an explicit G in D28 with labelled E1, E2 (edge-disjoint, each planar with an independently checked embedding) is a chi>=10 biplanar graph (chi>=ceil(28/3)). Also verify alpha<=3 by exhaustive independent-4-set check, and give a proper 10-colouring or better as an upper certificate. Then STOP and verify independently before anything else.
* EXCLUSION: certified non-existence over a stated stratum. Bank each finished stratum separately. Only the union of all strata is OP1(b).

## Entry
Read live remote main SHA/tree, PR parents, actual checks/jobs, open PRs/branches before writes. Read AGENTS, STATE, START_HERE, SESSION_PROTOCOL, D062, research/S029_LANDSCAPE.md (FROZEN; append-only), validation/S029/LANDSCAPE_FREEZE.json, catalogue SOURCES/CLAIMS (CLM-0110..0113), and the S026–S028 CLOSEOUTs and their 28-vertex alpha3 tooling. Frozen facts: no chi>=10 biplanar witness; 9<=chi_2<=12; certified obstruction library (C5 sum17 24/26, D036 and descendants); 16/30 seed-270018 profiles closed; old S029 queue PARKED. Run scripts/cloud_setup.sh (or the local pinned toolchain) and the FULL scripts/cloud_smoke.py; a FAIL blocks computation. Record the executor and environment.

## Stage 1 — written necessary conditions (before any search)
Prove in sessions/S030/RESEARCH.md, each with full proof and attribution:
(a) K9-free; e(G)<=156 (6n-12); e(G)>=117 (Turán: C(28,2)-t(28,3)=378-261).
(b) delta(G)>=9 via CLM-0111's argument (deg>=n-19). This is CONDITIONAL on SRC-0037; label it so, and keep an unconditional fallback where cheap.
(c) delta(G)<=11, since the average degree is <=312/28<12.
(d) Triangle-free bound: every triangle-free subgraph of a biplanar 28-vertex graph has <=2(2n-4)=104 edges (each planar triangle-free layer has <=2n-4 edges). Attribute it to Trivedi/Szeider [42, Q7.1].
(e) Any further filter (e.g. no three disjoint K8, the paper 59 degree-sum Theorem 2, linking lemmas) may DISCARD candidates only if re-proved in writing here or replayed from a checked certificate. Otherwise it is SOURCE_STATED and may only order or prioritise work (AGENTS rule 7).

## Stage 2 — stratify and preregister
Strata by (delta, m): S11 = delta 11, m in {155,156}; S10 = delta 10; S9 = delta 9. Within each stratum, also preregister the complement view: H = complement is K4-free, Delta(H)<=27-delta, e(H) in [222,261]. Before running anything, preregister in sessions/S030/PLAN.md the ranges, symmetry breaking (SMS-style lex-leader / canonical augmentation, with its soundness argument), encodings, caps, memory (one heavy worker <=12 GiB), stopping criteria and independent validation.

## Stage 3 — feasibility measurement (bounded, at most about 15% of session wall time)
1. Replay paper 59's RUP packet (regular566_rup.json, CC0; record its SHA-256 and the checker's) as an independent check of the 154-edge regular case. Fetching it is read-only; it is not imported as a filter unless replayed. If it cannot be fetched, record UNKNOWN.
2. Positive and negative controls: C7[K4] (alpha 3, not biplanar via the 112>104 triangle-free count) must be rejected; Szeider's alpha<=2 setting at n=17/18 (known biplanar examples at 17) must behave as expected; a heuristic biplanar alpha=3 graph near n=25, if constructible, must be accepted by the biplanarity oracle.
3. Measure the enumerator/decider growth on S11 slices (e.g. by fixed degree sequence or by private-clique profile) and extrapolate. Optionally build bipsat2 (SRC-0055, MIT, pinned commit and SHA-256) as a SECOND oracle; any UNSAT it reports counts only after DRAT replay through our pinned drat-trim.

## Stage 4 — certified search, in order S11, then S10, then S9 (stop when capped)
Encode G (or H) with: alpha<=3 (no independent 4-set), K9 exclusion, degree and edge windows, lazy triangle-free 104-cuts, lazy certified-obstruction cuts from our library (the C5 sum17 classes, D036 family; only certified ones), and an exact biplanarity decision for each survivor (two-layer CEGAR with Kuratowski cuts / face encoding, checked DRAT or LRAT). Every exclusion must be a checked proof of the full stratum formula, not of a sampled subset. Record models, cuts and proof sizes. Any SAT survivor that splits is a WITNESS CANDIDATE: stop and verify independently (layers, embeddings, alpha, colouring).

## Rules
No universal upper-bound or T3-below-28 work. No Lean, registration, publication, or contact/posting on rStation or elsewhere (owner-gated). Attribute every overlap per research/S029_LANDSCAPE.md section 4; never call a result novel. Caps give UNKNOWN; partial strata are reported as such. Keep the PARKED queues untouched. Do not invent certificates, hashes, runs or PRs.

## Closeout
Commit full S030 INPUT/PLAN/RESEARCH/ADVERSARIAL/PRIOR_ART (a dated append-only refresh of the S029 baseline: check paper 59, posts 146/152/155 and arXiv for changes since the freeze)/CLOSEOUT/MANIFEST/OWNER_INVOCATION/EXECUTED_PROMPT, the campaign registry entry, validation/S030 certificates and hashes, paired sources/claims MD+JSON, ledgers and truthful STATE. Write the COMPLETE S031 prompt, byte-identical at authoritative/NEXT_SESSION_PROMPT.md and sessions/S030/S031_FUTURE_PROMPT.md. Make one atomic commit, an ordinary PR and a non-force two-parent merge. Verify main, parents, tree and hosted governance jobs. The final report includes the verified links, the stratum-by-stratum verdicts and the FULL S031 prompt. Do not execute S031.
