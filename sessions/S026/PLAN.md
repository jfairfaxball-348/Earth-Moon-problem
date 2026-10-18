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

## Preregistered revision after initial source results, before revised science

Initial WIP4f061de / Actions39141223033: source full smoke PASS, base9 generator
UNSAT UNCHECKED; base10 and11 each2000 models, all4000 Euler-filtered. No candidate
passed to a biplanarity test. Cancelled the remaining redundant cold-search batch
after discovering all three S025 UNSAT checkpoints still on disk. Cancellation is
NOT_COMPLETED, never negative evidence. Original workflow/source remains immutable
on its WIP commit. Recovery is packaging only; original/raw/compressed hashes saved.

Revised CAM0030: regenerate and certify recovered24335/23525/23534 without search.
For the other five, pilot600s using the proved two-branch single-layer lemma
(research/S026_TWO_BRANCH_LEMMA.md), R,S sizes2..3. Independent extended checker,
byte regeneration, J1 and C5-33334 positive split/clause controls, same-job retained
and fresh native K9 proofs required before use. Absolute4h maximum still applies;
600s is a first method pilot, not a claim of completion. If capped, preserve UNKNOWN
and assess strength before allocating a continuation. Native/check caps unchanged.

Revised CAM0031 remains ONE clique-blow-up source. Move exact Euler bound into CNF
via equivalent fresh Boolean copies and sequential cardinality. Thirty fixed
weight profiles: nine deterministic sorted compositions of28, parts1..7, at each
base order9,10,11 (including balanced); balanced profiles at orders12,13,14.
Seed260018; at most100 models/profile,180s checked between solver calls, outer
7200s process cap (an in-flight SAT call can exceed180s, so this is not a hard
per-call promise). At mostSIX distinct admitted labelled edge sets; each60sx2
annealing plus300s old minor CEGAR. All model graph6 strings retained, including
filtered ones. All admitted candidates must avoid all18 certified C5s by complete
bag-assignment search, K9, and the S023 universal-K6 source. S013/S014 anchored
<=18-vertex families are avoided by candidate order28. Native DRAT is attempted
on zero-model generator domains (60s solve/120s check); unchecked/domain-capped
UNSAT remains an observation, never a graph-family exclusion.

## Owner-directed local continuation

Owner explicitly requests local laptop execution through Codex on2026-10-18.
Cancel hosted39142133864 after its completed main source stage; retain all output.
Local native paths are absolute S004-pinned binaries, and a NEW full271+K9 smoke
must PASS before science. Register `scripts/run_s026_local.py`: eight C5 targets
serially,11GiB aggregate private-memory supervision and4h absolute per-graph cap;
recovered3 use saved CNFs, remaining5 first get600s method pilots. New two-branch
CEGAR saves atomic compressed theory-cut checkpoints about every60s when solver
control returns, using10000-conflict bounded SAT calls. Restart reuses only saved
Kuratowski cuts, not the internal SAT solver memory. Checkpoint eager metadata
must match regenerated input/source. Native/check/regen caps remain as above.
Durable start/heartbeat/end events, atomic QUEUE and HANDBACK. No model calls in
the runner. Windows tree-private-memory observer is reused verbatim from S005;
external wall/private-memory guards pass independent toy-process exit/cap tests.
Job Object attachment was denied by the Codex parent job; it was replaced by the
already-established external supervisor BEFORE any local mathematical computation.

Local first pass completed all3 recovered DRAT certificates. Five new-family
pilots were BLOCKED_BEFORE_SEARCH by a Path-vs-string harness error in the J1
control reader; no graph decision was inferred. Fix only the path conversion,
retain the first-pass receipts, restart the same serial queue with verified3
skipped and only the five blocked targets executed. The independent source audit
already checked all2180 maps, all4 alpha3/K9-free certificates,72 native DRAT
absence certificates for the old18 obstructions, and explicit new-C5 maps closing
all4 candidates. On a later audit reuse those exact checked case receipts after
hash/input validation; do not repeat successful native proof work.

## Final single-model filter recovery preregistration

The sole original containment timeout P29-B14-0001 is retained by exact graph6 and weights. After the serial C5 queue AND existing four-candidate audit finish, use the independent quotient SAT algorithm on this one model against certified obstructions, new classes first. At most26 cases,45s external cap each,20000 PySAT conflicts,native10s/check20s;one11GiB tree. Stop at an independently checked positive map. A missing proof remains UNKNOWN. If every certified obstruction is proved absent, independently check alpha3/K9-free and apply the unused fifth candidate slot (two60s positive trials and300s exact). This is continuation of the SAME registered source, not a new family. Quantitative reason:72 earlier independent absence audits were inexpensive compared with the original backtracking timeout. Preserve the frozen initial source counts and record later recovery separately.
