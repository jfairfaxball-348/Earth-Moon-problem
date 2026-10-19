# S028 preregistration — 2026-10-19

Entry main 7217d85 (tree 93517f5), branch `claude/S028-obstruction-closure`.
D042 lower-only. Controller `scripts/run_s028_local.py`: lock, native digests,
full smoke gate, one supervised heavy tree, 11 GiB cap, whole campaign <= 8 h,
any graph <= 4 h, durable journal/STATE. Tool hashes recorded at launch; executed
tools are not edited afterwards.

## Engineering pilots disclosed (not evidence)
Before this file: (a) size measurement of two-branch clause families on the
28-vertex P10-B10-0001: branch size 3 = 0.66M two-models, size 4 = 51.8M
(infeasible), so 28-vertex graphs use size 3; (b) a screening refilter of the 84
S027 survivors against the 28 certified obstructions (75 contained); (c) a 300 s
scratch run of tools/s028_source.py (16 profiles UNSAT, 4 new admitted). Outputs
discarded; the registered run repeats all of it.

## Obstructions
21 S025/S026 C5 + P29 (validated loader) plus S027: C5[2,3,4,3,5], C5[2,4,3,4,4],
C5[2,4,4,2,5], P29-del-bag12, P26-B11-0051, P27-B12-0040 (edge files equal to
regenerated blow-ups; certified summaries required). Descent and candidate
negatives are appended only after full certification.

## Arm 0 — controls
Size-3 two-branch positive controls (J1, C5[3,3,3,3,4]) with independent checker
and byte regeneration; deletion-child control (P29 bag-12 child equals the S027
certified edge file; weighted isomorphism test sanity); tools/s027_selftest.py.

## Arm 1 — deletion descent (CAM-0034)
Roots: P26-B11-0051, P27-B12-0040, P29-del-bag12. One child per bag (bag vertices
are closed twins; an emptied bag deletes its base vertex); weighted-base
isomorphism dedup; children containing a certified obstruction are skipped
(recorded). Each tested child: S025 minor CEGAR --lemmaC5, 120 s; UNSAT ->
clause justification, byte regeneration, native DRAT (1800 s caps). Greedy
depth-first: a certified child is descended immediately. <= 2400 s per root,
<= 7200 s total. A biplanar child is NOT a witness (counting certificate lost).
No minimality claims.

## Arm 2 — refilter (CAM-0035)
The 84 S027 filter-clean graphs against every certified obstruction: audit-form
quotient CNF under a 200000-conflict budget, smallest obstructions first; SAT maps
explicitly checked on the target (exclusion by certified subgraph). UNSAT here is
screening only.

## Arm 3 — source rerun (CAM-0035)
tools/s028_source.py: S027 code path, seed 270018, same 30 profiles and caps
(100 models/180 s per profile, 7200 s whole, <= 6 admitted, first clean model per
profile), all certified obstructions as filters, S027 PRELOAD/CONTAIN maps re-applied
as PRELOAD (re-validated on their supports), all 84 S027 survivors blocked as
KNOWN_SURVIVOR (domain dependencies unless excluded in Arm 2). Domains: independent
learned-clause check + byte regeneration + native DRAT (600/1200 s); a closure is
unconditional only with no unresolved blocking dependency.

## Arm 4 — exact processing queue
Order: S027 admitted not excluded, then S028 admitted, then S027 surplus not
excluded. Before each: re-screen against the current certified list. Then audit
DRAT absence proofs (all obstructions, 120/240 s each), S025 backtracking audit
(300 s), two 60 s anneals (checked split), 1800 s exact --lemmaC5, and if UNKNOWN
with >= 3000 s budget left, 1800 s two-branch size 3 (certified as S027). New
negatives join the obstruction list. Any checked split with alpha<=3 on 28 vertices
stops the campaign as a WITNESS CANDIDATE for independent verification.

## C5 pending
C5[3,3,4,3,4], C5[3,3,3,4,4]: PARKED. No genuinely new proved strengthening was
prepared; unchanged reruns are prohibited.

## Stop criteria
Whole budget exhaustion, queue end, witness candidate, smoke FAIL or assertion
failure (BLOCKED, never a decision).
