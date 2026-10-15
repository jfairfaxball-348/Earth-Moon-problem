# Earth–Moon Problem — Long-Form Research Programme

**Next queued research session (D056, 15 October 2026):** S023 is now a full theoretical **upper-vs-lower bound feasibility audit**, comparing a checked 10-chromatic biplanar construction (improving the 9 lower bound) against a universal 11-colouring theorem (improving the 12 upper bound). This is a specific owner-authorised research exception to the previous lower-only policy, not a completed bound change or a permanent pivot. All 219 original unknown graphs and graph148 evidence remain preserved. [Full executable S023 prompt](authoritative/NEXT_SESSION_PROMPT.md) | [Owner directive](docs/S023_BOUND_COMPARISON_DIRECTIVE.md).


**Headline (re-scoped 2026-10-14, decision D042):** raise the lower bound of the Earth–Moon problem (EMP) from χ₂ > 8 to **χ₂ > 9**, i.e. construct and fully certify a finite simple biplanar graph with chromatic number at least 10. Solving EMP outright and improving the upper bound 12 are out of scope. **Status (2026-10-14): no χ ≥ 10 biplanar graph known; 52/271 candidate rows excluded, 219 UNKNOWN. Bounds 9..12 unchanged.**

## Exact target

A finite simple graph G=(V,E) is biplanar when E partitions as two edge-disjoint sets E1 and E2 for which (V,E1) and (V,E2) are both planar. Define χ₂ = max {χ(G): thickness(G)≤2}. Classical bounds are **9 ≤ χ₂ ≤ 12**.

**Programme target:** exhibit one explicit biplanar graph G with **χ(G) ≥ 10**, certified by explicit labelled layers E1, E2, an independent planarity check of each layer, and a rigorous checked proof that G has no proper 9-colouring. That proves χ₂ > 9. An 11- or 12-chromatic example would also meet the target. A feasible colouring is never evidence for the target; only the non-9-colourability proof is.

**Out of scope (owner decision D042):** universal upper-bound theorems (χ₂ ≤ 11, 10 or 9), discharging/reducibility work and full resolution of EMP. A certified lower bound of 10 does **not** settle EMP and must never be described as doing so.

## Founding baseline — not this programme's result

- Ringel posed the problem in 1959. The classical 12 upper bound follows from the planar edge bound and an 11-degeneracy argument.
- The known 9 lower bound is exemplified by K₆ joined to C₅: the join has χ=6+3=9. A two-planar-layer embedding is attributed in the literature to Sulanke; **independently reconstructed and checked in validation/sulanke.json**.
- Boutin–Gethner–Sulanke (2008) and Gethner–Sulanke (2009) constructed many nine-critical thickness-two graphs. S002 inspected Patil's primary 2026 deposit and Szeider's September 2026 alpha<=2 exclusion; external machine certificates were not replayed.
- This is not a claim that a complete 2026 literature search has been conducted.

## Research architecture

**Constructive track:** explore genuinely 10/11/12-chromatic graphs, preserve both explicit planar layer witnesses and independently checkable chromatic lower-bound certificates.

**Structural filters (construction support only):** proved forbidden subgraphs (K₉, K₆,₉ and other Euler-violating complete bipartite graphs, a K₇ with five common outside neighbours) are used to discard candidates cheaply. The former universal upper-bound track is retired; its results remain as history in S002–S010.

**Infrastructure track:** rebuild published 9-chromatic witnesses, validate independent planarity and colouring checks, pre-register finite search domains, validate SAT unsatisfiability proof traces and eventually formalise in Lean.

## Publication-quality progression

0. Governance bootstrap (S001) — **PASS, administrative only**
1. Certified χ ≥ 10 biplanar construction (lower-bound only since D042) — **ACTIVE; no headline advance**
2. First result-specific novelty and priority check — NOT STARTED
3. Lean 4 kernel-checked formalisation (precisely the mathematical headline) — NOT STARTED
4. Final comprehensive novelty, assumptions and independent certification audit — NOT STARTED
5. Owner-approved Palomar verification/registration — OWNER-GATED
6. Journal-level paper and reproducibility package — NOT STARTED
7. Owner-approved arXiv and journal submission — OWNER-GATED

Gates are evidence-driven, not automatic. If no major theorem emerges, retain mathematical progress and keep attacking the headline; do not manufacture a paper.

## Navigation

Sessions run in Claude Code cloud containers; see [cloud environment](docs/CLOUD_ENVIRONMENT.md). Begin at [AGENTS.md](AGENTS.md) → [START_HERE](authoritative/START_HERE.md) → [STATE.json](authoritative/STATE.json) → [session protocol](docs/SESSION_PROTOCOL.md) → [S013 prompt](authoritative/NEXT_SESSION_PROMPT.md) (queued for execution when provided by the owner). Sources, claims, failure ledger, campaign registration, and downstream release gates are organized in their corresponding directories.

Inspired by the user's Davenport Counterexample Hunt, Almost Stacked Proof, and Homology–Homotopy programme governance; EMP-specific tests and research strategies are intentionally different.

## Session history (S002–S010)

Sessions S002–S010 ran under the earlier two-sided headline. Their upper-bound results are kept as history only and are not extended after D042.

## S002 results

- [All odd-cycle clique blow-ups are at most 9-colourable when biplanar](research/S002_ODD_CYCLE_BLOWUPS.md); novelty unchecked and short cases overlap existing work.
- [Apex/Hajós and join attacks](research/S002_AMPLIFICATION.md), including reconstruction of an existing 10-chromatic saturated-cone exclusion.
- [Critical-density and upper-bound attack](research/S002_UPPER_BOUND_ATTACK.md): a 12-critical witness must have n>=78+11D; an explicit checked 42-vertex graph disproves universal 10-degeneracy while admitting a 7-colouring.

These are structural progress and verified classical reconstructions, not a solution of EMP or a universal improved bound.

## S003 results

- [Clique blow-up census](research/S003_BLOWUP_CENSUS.md): every biplanar clique blow-up of a graph on <=6 vertices is 9-colourable; 271 alpha>=3 10-chromatic blow-ups of 7-8-vertex bases pass every counting obstruction — biplanarity UNKNOWN (primary construction frontier).
- [Face covers and facial deficit](research/S003_FACE_DEFICIT.md): apex characterization, codegree budget, rim lemma, outerplanar reductions.
- [Upper-bound route](research/S003_UPPER_BOUND.md): double-wheel lemma, correction of S002's n>=78 bound (superseded by Patil's n>=89), isolated Kempe obligation.
- Certified oracle: tools/biplanar_cegar.py + tools/check_cegar_certificate.py (K9 refuted, DRAT-verified).

## S004 results

- [Certified construction frontier](research/S004_FRONTIER.md): 271 exact 10-chromatic candidates, one checked 22-vertex exclusion; 270 biplanarity UNKNOWN.
- [Completion-face oracle and full corpus apex closure](research/S004_TRIANGULATION_COVER.md): calibrated proofs, 159 apices excluded, explicit trust/independent-challenge limits.
- [Single-Kempe-swap counterexample](research/S004_KEMPE_LOCK.md): degree-11 double-wheel locality alone does not force one-swap extension.

No headline advance: 9 <= chi_2 <= 12. S005 remains future and unexecuted.

## S005 results

- [Finite low-deficit frontier](research/S005_FRONTIER.md): 25 additional checked exclusions, including all 17 D=0 row; 245 candidates UNKNOWN.
- [Independent face reductions](research/S005_FACE_REDUCTIONS.md): necessary D=0/D=1 conditions, checked no-lex corroborations; SAT relaxations kept separate.
- [Criticality and two Kempe swaps](research/S005_UPPER_ROUTES.md): new necessary inequalities and exact extension of the noncritical S004 lock. No universal colouring improvement.

Only S005 executed; [S006](authoritative/NEXT_SESSION_PROMPT.md) is FUTURE UNEXECUTED. No headline, novelty, formalisation or publication gate advanced.

## S006 results

- [Certified frontier](research/S006_FRONTIER.md): 15 new checked finite exclusions; total41/271, 230 biplanarity UNKNOWN. D1 remaining UNKNOWN:[]. Registered UNKNOWN:[162, 155, 157, 159]; NOT_RUN:[157, 159]; wall-capped:[162, 155].
- [Sharp density route](research/S006_CRITICAL_DENSITY.md):61/16 forest and conditional high-deficit bounds.
- [Palette route](research/S006_PALETTES.md): fixed-boundary trap and published simultaneous-colouring budget; heavy components open.

Only through S006 executed; S007 FUTURE/UNEXECUTED.9..12 and novelty/formalisation/publication gates unchanged. Historical future labels superseded.

## S007 results

- [D2 frontier](research/S007_FRONTIER.md): S007 adds0 checked finite exclusions; total41/271, 230 biplanarity UNKNOWN. Full registered UNKNOWN:[162, 155, 157, 159]; NOT_RUN:[157, 159]; wall-capped:[162, 155].
- [Necessary encodings](research/S007_ENCODINGS.md): independent globalD2 models SAT_RELAXATION, directly checked; no planar converse.
- [Critical palettes](research/S007_CRITICAL_PALETTES.md): exterior deletionchi11 and heavyK8 support excess13; no universal colouring theorem.

Only throughS007 executed; S008 FUTURE/UNEXECUTED. Headline9..12, novelty/formalisation/publication gates unchanged. Historical future labels superseded.

## S008 results

- [Full-layer encoding](research/S008_ENCODING.md): necessary completionK5/inputK33 and tree-counter challenges; S008 adds4 checked finite exclusions; total45/271, 226 biplanarity UNKNOWN.
- [Shared supports](research/S008_SHARED_SUPPORT.md): all-order Euler expansion/Hall representatives and overlap-weighted excess.
- [No-spare extension](research/S008_NO_SPARE.md): exact simultaneous core extension criterion; no universal upper improvement.

Only through S008 executed; S009 FUTURE/UNEXECUTED. Headline9..12 and all downstream gates unchanged. Historical future labels superseded only through S008.

## S009 results

- [Full obstruction audit](research/S009_CONSTRUCTION.md): S009 adds7 checked finite row exclusions; total52/271, 219 biplanarity UNKNOWN.
- The checked K7 joined to independent5 obstruction implies that every seven-clique in a finite simple biplanar graph has at most four common outside neighbours, excluding the specified heavy K8 endblocks. This does not lower the universal colouring bound.
- [Global/mixed excess](research/S009_GLOBAL_CHARGE.md): arbitrary overlap charged once, stronger full-block Euler support expansion.
- [Simultaneous colours](research/S009_SIMULTANEOUS_COLOURS.md): exact equality-quotient/list reformulation and failure of pairwise/tree feasibility.

Only through S009 executed; S010 FUTURE/UNEXECUTED. Headline9..12 and downstream gates unchanged. Historical future labels superseded throughS009.

## S010 results

- [Structural reset](research/S010_BIPARTITE_RESET.md): hand K6,9 obstruction closes every heavy odd block of length>=7.
- [Simultaneous extension](research/S010_SIMULTANEOUS_EXTENSION.md): independentR/safe residual palette criterion and precise missing existence steps.
- [Strategic audit](research/S010_STRATEGIC_AUDIT.md): measured search yield/completeness; local P4-I9/C5-I9 planar exactchi3/4, no new row exclusion.

Only throughS010 executed; S011 FUTURE/UNEXECUTED. Headline9..12 and all downstream gates unchanged.


## S011 results and permanently reproducible S012 handover (2026-10-14)

S011 completed under D042's lower-bound-only scope, with **no chi>=10 biplanar witness** and no movement of the 9..12 classical interval. Positive-only double-planar-layer search (CAM0012) attempted all219 remaining fixed exact10-chromatic rows twice, 438 greedy trials and25 repairs; no split and all219 remain UNKNOWN. CAM0013's240 sampled single-edge deletions all led to a9-colouring; CAM0014 then produced and independently verified **863 explicit proper9-colourings**, one for *every* deleted edge of six fixed exactly10-chromatic rows2,55,59,61,199,200. This proves these six instances are edge-critical (CLM-0070), not that they are non-biplanar. A direct counting argument excludes the ordinary Mycielski lift of chi>=9 as a biplanar construction (CLM-0069; novelty unchecked).

Read [S011 research](research/S011_CONSTRUCTION.md), [permanent summary](validation/S011/SUMMARY.json), [full colour-certificate gzip](validation/S011/edge_critical_witnesses.json.gz), [closeout](sessions/S011/CLOSEOUT.md), and [full S012 handover prompt](authoritative/NEXT_SESSION_PROMPT.md). When ChatGPT lacks local checkout/hook, use tested **GitHub Actions D043 same-job setup + smoke**; exact workflows/runs/artifacts/source/native digests are all in the permanent S011 summary. Every future closeout MUST output the full next-session prompt alongside its pushed/merged report; a supplied next-session prompt itself authorises running that session (D047); no extra 'Run' message needed.

## S012 results and D047 session-prompt execution policy (2026-10-14)

The six specific S011 exactly10-chromatic edge-critical clique blowups **cannot recover chi10 via any one old-edge/old-nonedge swap** (CLM0071). The full finite space is **194,896** distinct labelled pairs, with positive nine-colour certificates generated by an analytic untouched-bag transposition and independently checked on GitHub Actions run38635879431 after full 271/271 cold DRAT environment acceptance. See [construction proof](research/S012_CONSTRUCTION.md), [registered campaign](campaigns/CAM-0015.md) and [evidence summary](validation/S012/SUMMARY.json). Also no biplanar 10-chromatic graph can be built by keeping the induced Sulanke K6 vee C5 and adjoining at most five new vertices (CLM0072). First open such extension: six vertices, K6 or K6-e among additions and 89/90 total edges (CLM0073). **The 219 original biplanarity cases remain UNKNOWN; 9<=chi2<=12 unchanged.**

**D047: if the owner provides a session prompt, execute that named session directly.** Never require a second special "Run S###" authorisation. A FUTURE/UNEXECUTED label means the session has not already run; it is immediately executable once the prompt is supplied. No automatic next-session execution from a prior session's closeout. Historical provenance is retained, substantive lower-bound-only D042 and strict evidence gates unchanged. [Full queued S013 prompt](authoritative/NEXT_SESSION_PROMPT.md).
