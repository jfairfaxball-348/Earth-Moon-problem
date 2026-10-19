# S027 preregistration — 2026-10-18

Entry main 4d74c5f276a2a512b2588d3267a5496a7cba134b (tree c439fe83...), session
branch `claude/S027-learned-obstruction`. Owner invocation and executor note in
OWNER_INVOCATION.md. D042 lower-only; no upper-bound, Lean, publication work.

## Gate and environment
Local Windows workstation, 16 threads, 15.7 GiB RAM. Pinned native CaDiCaL and
drat-trim (artifacts/tmp/S004, digests checked by the controller). Controller
`scripts/run_s027_local.py`: single lock, full `scripts/cloud_smoke.py` first
(FAIL blocks science), one heavy process tree, 11 GiB private-memory cap and wall
cap per child (tools/s026_supervision.run_step), durable RUN_JOURNAL.jsonl, atomic
STATE/summary JSON. Whole campaign <= 8 h after smoke; any graph <= 4 h absolute.

## Engineering pilots disclosed (not evidence)
Before registration, scratch-directory pilots of the new generator (60 s and 120 s
whole-source caps), the self-test, a 30 s seeded size-4 two-branch run on
C5[3,3,4,3,4] and one candidate audit were executed to check correctness, speed and
memory. Their outputs are discarded; nothing below relies on them. After the first
pilot two registered values were changed: generator conflict budget 10000 -> 200000
per SAT call (profile00 hit the old budget) and the admission rule below (the
first pilot admitted six labelled near-copies from one profile).

## Arm 0 — controls (before science stages)
* Size-4 two-branch clauses: known checked splits J1 and C5[3,3,3,3,4] satisfy every
  minor clause under actual meanings; independent S026 checker plus S027 byte
  regeneration pass on both control CNFs. K9 retained/fresh proof in same-run smoke.
* tools/s027_selftest.py: in-loop assumption containment vs audit-form CNF vs S025
  backtracking agree on seeded random bases (two profiles); every found map remains
  valid on random supersets of its support; the independent learned-clause checker
  rejects three corrupted clauses (missing support edge, non-weight-preserving
  permutation, Euler one edge short).

## Arm A0 — P29 bounded deletion descent (CAM-0033)
P29-B14-0001 = B14[2^14]. The two vertices of a bag are true twins, so the 28
one-vertex deletions form 14 isomorphism classes (bag 0..13 in order). Each:
S025 minor CEGAR --lemmaC 5, 60 s search; UNSAT requires independent clause
justification, byte regeneration and native DRAT (1800 s each cap). Stop when the
descent total reaches 1800 s. Accepted negatives become extra certified
obstructions for Arm A. No minimality claim.

## Arm A — learned-obstruction source (CAM-0032, main arm)
Profiles: S026 scheme with seed 270018: balanced weights for base orders 9..14,
plus random weight vectors (max part <= 7) for orders 9..11, 30 fixed profiles,
total 28 vertices. Base formula as S026: every 4-set of base vertices has an edge
(alpha<=3, so chi>=ceil(28/3)=10 by counting), every minimal clique of weight >= 9
forbidden (K9-free), blow-up edges <= 156 (seqcounter).
Learned clauses (sound per CLM-0102, all recorded with maps for audit):
PRELOAD from all 2180 S026 FILTER_TRANSFERS maps plus the 4 S026 candidate
transfers, transferred to any S027 profile of the same base order whose capacities
dominate the map's bag usage (fresh capacity validation), and identity maps of
whole-profile obstructions; CONTAIN from in-loop certified-obstruction maps;
EULER from whole-bag sets T whose recorded base edges already exceed 6w(T)-12; each
with up to 32 random weight-preserving relabelled images. Learning only from the
22 certified obstructions (21 C5 + P29) plus Arm A0 negatives, never from UNKNOWN.
Per model: Euler subset test; containment with one incremental solver per
obstruction under assumptions (20000 conflicts each; SAT decoded and explicitly
checked on the model AND on the support alone). Then global max-cut <= 104 test,
universal-K6 closed source, omega and alpha rechecks. The FIRST filter-clean model
of a profile is ADMITTED while fewer than 6 are admitted; later filter-clean models
are SURPLUS_FILTER_CLEAN (blocked, recorded, biplanarity UNKNOWN). Caps: 100
models/profile, 180 s soft/profile, 7200 s whole source. A conflict cap or SAT
budget is UNKNOWN.
Profile-domain statements: a GENERATOR_UNSAT profile writes its full CNF; the
independent checker (tools/s027_check_learned.py, imports neither generator nor
encoder) justifies every learned clause and regenerates the CNF byte-identically;
native DRAT (600 s solve / 1200 s check). The statement is a finite theorem only
when blocking dependencies are empty or themselves certified non-biplanar.
Admitted graphs: audit-form quotient CNF native DRAT absence proof for each
certified obstruction (120 s/240 s per CNF), separate S025 backtracking audit
(300 s cap total), two 60 s flip-anneal positive trials (split checked
independently), then 600 s exact S025 minor CEGAR --lemmaC 5 with clause
justification, regeneration and native DRAT (1800 s caps).

## Arm B — C5 continuation (CAM-0033), remainder of the 8 h budget
Order 33434, 23435, 24344, 24425, 33344 (33434 first: no K8, Lemma C inactive).
Independent audit of S026 checkpoint inputs: graph edges equal, every seeded cut
re-verified as a K5/K3,3 subdivision inside E(G). ONE changed strength strategy:
the same proved two-branch lemma with connected branch sets of size 2..4 (S026:
2..3), seeded with the S026 Kuratowski cuts; internal SAT state is not resumed.
Search <= 3600 s per graph (less if the whole budget is short; below 900 s left:
NOT_RUN), checkpoints every 60 s. UNSAT: S026 independent two-branch checker,
S027 byte regeneration, native DRAT 1800 s solve / 1800 s check. SAT: explicit
split check; a sum17 positive refutes the threshold and is reported. No repetition
of unchanged caps. The full C5 iff only if all 26 are certified.

## Stop criteria
Whole-budget exhaustion, all stages complete, smoke FAIL, or any assertion
failure (recorded as BLOCKED, never as a decision).
