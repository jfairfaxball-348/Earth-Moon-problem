# S026 preregistration — 2026-10-18

Entry main 96c9f3c9d482844a5c952d856132b99579b660bd, tree
afb10c266491fa83a2430f80eced7d2a361c5f0a. Clean checkout; no open PR;
PR33 merged with two parents; main governance run39140590201 success.
Rulesets empty; branch protection endpoint404 (not protected).

## CAM-0030: eight pending C5 classes

Serial order24335,23525,23534,23435,24344,24425,33344,33434.
No recoverable uncommitted S025 CNFs are assumed. Regenerate each using unmodified
S025 minor CEGAR --lemmaC5, then independently justify clauses, regenerate byte
for byte, run pinned native CaDiCaL with DRAT and drat-trim. Each graph has an
absolute four-hour maximum; initial search budget3600s, native solve1800s,
check1800s, checker/regeneration600s each. External process caps supersede the
in-process solver clock. UNKNOWN survives every cap or missing proof.
One heavy process tree at a time; Linux address-space limit12GiB, no parallel
classes. Checkpoints, input/source/native digests, elapsed time and peak RSS
are preserved. No classification theorem until the complete finite reduction
and every required certificate have been independently checked.

## CAM-0031: obstruction-aware larger bases (main arm)

Source: clique blow-ups of labelled bases of orders9,10,11. Fixed balanced bag
weights total28: (4,3x8), (3x8,2x2), (3x6,2x5). Require no independent4-set,
so alpha<=3 and28 vertices imply chi>=ceil(28/3)=10 by a hand counting proof.
SAT base generator enforces every4-set has an edge and forbids every clique
of weight>=9. No quotient symmetry reduction: counts are labelled trials,
NOT an exhaustive nonisomorphic census. Deterministic seed260018.
At most2000 models/order and900s/order, stopping after12 fully filtered distinct
edge sets. Reject Euler violations, all detected bipartite-cut density
violations, complete certified C5 subgraph tests, and old closed anchored families.
Any capped containment test leaves filter status UNKNOWN and candidate unadmitted.
Quantitative motivation: alpha3 requires at least28 vertices; these are the first
three balanced quotient orders beyond the retired <=8-base corpus. K9 constraints
are eager, rather than paying for repeated known obstruction decisions.
Every admitted graph stores explicit edges, weights, all base independent sets,
K9-free check and complete bag-map containment outcomes for all18 certified C5s.
Each gets annealing seeds1,2 at60s each, then minor CEGAR300s, with full native
proof pipeline for any UNSAT; every zero-defect split checked independently.
Generation and all science require same-job full smoke PASS first. Job total
maximum350minutes (Actions hard timeout360). Generation precedes serial C5 work
so the main arm has a guaranteed budget. Arm3 omitted: no new LP-dual rationale.

## Scientific boundaries

9<=chi2<=12 unchanged unless all witness obligations pass. A missing split is
UNKNOWN. SAT-model exhaustion without a checked proof is not a mathematical
negative result. No upper-bound research, Lean, registration or outreach.
Search prior art at entry and again before closeout; no novelty guarantee.
