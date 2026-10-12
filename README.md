# Earth–Moon Problem — Long-Form Research Programme

**Headline:** Determine the exact maximum chromatic number of graphs of thickness at most two (the Earth–Moon problem, EMP). **Status (2026-10-12): UNSOLVED; programme bootstrap only.**

## Exact target

A finite simple graph G=(V,E) is biplanar when E partitions as two edge-disjoint sets E1 and E2 for which (V,E1) and (V,E2) are both planar. Define χ₂ = max {χ(G): thickness(G)≤2}. Classical bounds are **9 ≤ χ₂ ≤ 12**. The ultimate objective is to prove **χ₂=9, 10, 11, or 12** with auditable evidence, not merely find a graph with a plausible high colouring number.

A rigorously verified **10-chromatic biplanar graph** would improve the lower bound; so would an 11- or 12-chromatic example. A universal improved upper bound (11, 10 or 9) is equally welcome. In particular, χ₂=12 would settle the question by construction; χ₂=9 would settle it by universal theorem. Achieving lower bound 10 alone does **not** settle EMP.

## Founding baseline — not this programme's result

- Ringel posed the problem in 1959. The classical 12 upper bound follows from the planar edge bound and an 11-degeneracy argument.
- The known 9 lower bound is exemplified by K₆ joined to C₅: the join has χ=6+3=9. A two-planar-layer embedding is attributed in the literature to Sulanke; **not yet independently reconstructed here**.
- Boutin–Gethner–Sulanke (2008) and Gethner–Sulanke (2009) constructed many nine-critical thickness-two graphs. A recent 2026 computational preprint indexed under Digvijay Patil also requires direct primary-source audit before any priority claim.
- This is not a claim that a complete 2026 literature search has been conducted.

## Research architecture

**Constructive track:** explore genuinely 10/11/12-chromatic graphs, preserve both explicit planar layer witnesses and independently checkable chromatic lower-bound certificates.

**Universal track:** structural inequalities, low-degree/reducible configurations, discharging, critical graph obstructions, layer compatibility and proof of χ≤11/10/9. A finite search cannot, by itself, prove a universal upper bound.

**Infrastructure track:** rebuild published 9-chromatic witnesses, validate independent planarity and colouring checks, pre-register finite search domains, validate SAT unsatisfiability proof traces and eventually formalise in Lean.

## Publication-quality progression

0. Governance bootstrap (S001) — **PASS, administrative only**
1. Exact primary-source frontier, ambitious proof/counterexample research — **NOT STARTED**
2. First result-specific novelty and priority check — NOT STARTED
3. Lean 4 kernel-checked formalisation (precisely the mathematical headline) — NOT STARTED
4. Final comprehensive novelty, assumptions and independent certification audit — NOT STARTED
5. Owner-approved Palomar verification/registration — OWNER-GATED
6. Journal-level paper and reproducibility package — NOT STARTED
7. Owner-approved arXiv and journal submission — OWNER-GATED

Gates are evidence-driven, not automatic. If no major theorem emerges, retain mathematical progress and keep attacking the headline; do not manufacture a paper.

## Navigation

Begin at [AGENTS.md](AGENTS.md) → [START_HERE](authoritative/START_HERE.md) → [STATE.json](authoritative/STATE.json) → [session protocol](docs/SESSION_PROTOCOL.md) → [S002 prompt](authoritative/NEXT_SESSION_PROMPT.md) (future, unexecuted). Sources, claims, failure ledger, campaign registration, and downstream release gates are organized in their corresponding directories.

Inspired by the user's Davenport Counterexample Hunt, Almost Stacked Proof, and Homology–Homotopy programme governance; EMP-specific tests and research strategies are intentionally different.
