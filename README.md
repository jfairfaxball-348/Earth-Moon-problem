# Earth–Moon Problem — Long-Form Research Programme

**Headline:** Determine the exact maximum chromatic number of graphs of thickness at most two (the Earth–Moon problem, EMP). **Status (2026-10-13): UNSOLVED; S005 mathematics complete, 25 additional finite exclusions, 245 listed candidates UNKNOWN; bounds still 9..12.**

## Exact target

A finite simple graph G=(V,E) is biplanar when E partitions as two edge-disjoint sets E1 and E2 for which (V,E1) and (V,E2) are both planar. Define χ₂ = max {χ(G): thickness(G)≤2}. Classical bounds are **9 ≤ χ₂ ≤ 12**. The ultimate objective is to prove **χ₂=9, 10, 11, or 12** with auditable evidence, not merely find a graph with a plausible high colouring number.

A rigorously verified **10-chromatic biplanar graph** would improve the lower bound; so would an 11- or 12-chromatic example. A universal improved upper bound (11, 10 or 9) is equally welcome. In particular, χ₂=12 would settle the question by construction; χ₂=9 would settle it by universal theorem. Achieving lower bound 10 alone does **not** settle EMP.

## Founding baseline — not this programme's result

- Ringel posed the problem in 1959. The classical 12 upper bound follows from the planar edge bound and an 11-degeneracy argument.
- The known 9 lower bound is exemplified by K₆ joined to C₅: the join has χ=6+3=9. A two-planar-layer embedding is attributed in the literature to Sulanke; **independently reconstructed and checked in validation/sulanke.json**.
- Boutin–Gethner–Sulanke (2008) and Gethner–Sulanke (2009) constructed many nine-critical thickness-two graphs. S002 inspected Patil's primary 2026 deposit and Szeider's September 2026 alpha<=2 exclusion; external machine certificates were not replayed.
- This is not a claim that a complete 2026 literature search has been conducted.

## Research architecture

**Constructive track:** explore genuinely 10/11/12-chromatic graphs, preserve both explicit planar layer witnesses and independently checkable chromatic lower-bound certificates.

**Universal track:** structural inequalities, low-degree/reducible configurations, discharging, critical graph obstructions, layer compatibility and proof of χ≤11/10/9. A finite search cannot, by itself, prove a universal upper bound.

**Infrastructure track:** rebuild published 9-chromatic witnesses, validate independent planarity and colouring checks, pre-register finite search domains, validate SAT unsatisfiability proof traces and eventually formalise in Lean.

## Publication-quality progression

0. Governance bootstrap (S001) — **PASS, administrative only**
1. Exact primary-source frontier, ambitious proof/counterexample research — **ACTIVE; no headline bound advance**
2. First result-specific novelty and priority check — NOT STARTED
3. Lean 4 kernel-checked formalisation (precisely the mathematical headline) — NOT STARTED
4. Final comprehensive novelty, assumptions and independent certification audit — NOT STARTED
5. Owner-approved Palomar verification/registration — OWNER-GATED
6. Journal-level paper and reproducibility package — NOT STARTED
7. Owner-approved arXiv and journal submission — OWNER-GATED

Gates are evidence-driven, not automatic. If no major theorem emerges, retain mathematical progress and keep attacking the headline; do not manufacture a paper.

## Navigation

Begin at [AGENTS.md](AGENTS.md) → [START_HERE](authoritative/START_HERE.md) → [STATE.json](authoritative/STATE.json) → [session protocol](docs/SESSION_PROTOCOL.md) → [S008 prompt](authoritative/NEXT_SESSION_PROMPT.md) (future, unexecuted). Sources, claims, failure ledger, campaign registration, and downstream release gates are organized in their corresponding directories.

Inspired by the user's Davenport Counterexample Hunt, Almost Stacked Proof, and Homology–Homotopy programme governance; EMP-specific tests and research strategies are intentionally different.

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
