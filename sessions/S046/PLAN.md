# S046 preregistered plan

Registered before any diagnostic or pilot computation. Machine-readable copy,
sample indices, seeds and budgets: validation/S046/REGISTRATION.json (its
sha256 and registration epoch are recorded in the closeout). Runtime root
artifacts/tmp/S046 (git-ignored); permanent evidence under validation/S046.
Target unchanged: one certified finite simple biplanar graph with chi>=10.

## Budget (experimental computation only)

Total ceiling 1800 CPU s and 3600 wall s, absolute experimental deadline
registration epoch + 4 h. Allocation:

| Block | CPU s | Wall s | Content |
|---|---:|---:|---|
| E1 S045 diagnostics | 360 | 480 | full archive census pass + 300-record sample measurements |
| E2 matched pilots | 1050 | 1150 | 5 orders x 3 arms, 60 s native solve clock each, plus preparation |
| E3 pilot candidate analysis | 180 | 240 | up to 30 candidates per arm, 12 s wall cap per arm |
| E4 conditional acceptance | 200 | 260 | only if the targeting criterion passes |
| Total | 1790 | 2130 | 10 CPU s unallocated |

Smoke, independent audits (planarity rotation checks, colouring checks,
Kuratowski subdivision audits, drat-trim runs), encoding controls and closeout
replays are verification costs and are recorded separately. Every
experimental block appends measured process-tree CPU and wall time to
artifacts/tmp/S046/BUDGET.jsonl; a block that would exceed its allocation is
not started, and an exhausted block is reported as capped.

Resources: one heavy native generator plus a serial colouring oracle;
3 GiB aggregate private-memory hard cap, 1.5 GiB available-RAM floor,
10 GiB free-disk reserve, checked by the driver at every poll.

## E1 — diagnose saved S045 candidates

Input: the 60 journals of validation/S045/final/ARCHIVE_INDEX.json in their
listed (chronological) order, archive bytes checked against the index;
expected total 642381 records (validation/S045/final/AUDIT.json).

Full census pass (deterministic, all records): from each record's layer bit
string compute union/layer edge counts, minimum/maximum degree, isolated
vertices, and whether the 9-core (repeated deletion of vertices of degree
below nine) is empty; exact labelled duplicate unions and layer assignments
by packed bit strings (exact keys, not hashes). NumPy peeling is cross-checked
against NetworkX core numbers on every sampled record.

Stratified sample: strata early [0,214127), middle [214127,428254), late
[428254,642381) by global record index; 100 indices per stratum drawn with
random.Random(46046).sample, strata in that order. For each sampled record:
connectivity, cut vertices, degeneracy and 9-core order; explicit
smallest-last greedy and DSATUR colourings (validated); maximum clique by
exhaustive Bron–Kerbosch (validated clique, 2 s cap); 8-colourability by
PySAT CaDiCaL 1.9.5 with a 2 s cap, SAT colourings independently validated;
UNSAT re-solved by the pinned cadical.exe with a DRAT proof and checked by
the pinned drat-trim (verification cost); a timeout is UNKNOWN. Exact
isomorphism classes of the 300 union graphs: Weisfeiler–Lehman (3 rounds)
screen, then VF2 with each returned mapping checked edge by edge.
Timing decomposition from the archived SLICES.jsonl receipts (no rerun);
oracle time re-measured on the sample.

Registered classification: "mainly easy" if at least 50% of all saved
records have an empty 9-core; "mainly redundant" if at least 50% of the
sample falls in non-singleton isomorphism classes; "plausible cores" if at
least 50% of the sample has a nonempty 9-core and a checked non-8-colourability
proof; otherwise "undetermined by this bounded diagnosis". Proportions are
descriptive of saved records, never coverage or witness probability.

## E2 — matched pilots

Orders n in {24, 28, 32, 40, 50}; executed n ascending, arms B, C, CS for
each n. Every arm: target k=9, colouring-partition feedback (CLM-0146), S045's
selected positive edge phases, PySAT Glucose 4 oracle (cap min(60 s, remaining
slice time)), independent rotation and colouring checks of every candidate
before feedback, fresh runtime directory, no clause transfer between orders,
arms or from S045, 60 s native solve clock from READY, startup ceiling 120 s.

- B (baseline): the S045 domain at order n: all pairs optional, layer
  disjointness only.
- C (core filters): B plus union degree >= 9 at every vertex (sequential
  at-least counter on the 2(n-1) incident layer literals). Domain: labelled
  biplanar graphs of order exactly n with minimum degree at least nine; it
  contains every 10-critical biplanar graph of order n. It is not a padded
  "order at most n" domain.
- CS (core + symmetry breaking): C plus union variables u=x1 OR x2, the
  lex-leader constraints row_i >=lex row_j (columns other than i,j) for all
  i<j on the union adjacency matrix, and the layer-swap rule that the first
  present union pair lies in layer 1. These remove equivalent labellings; they
  never require a nontrivial automorphism.

The preservation arguments for these filters/rules are in RESEARCH.md and
are checked by exhaustive small controls before E2. No alpha, regularity,
exact density, triangulation or automorphism requirement is imposed.

Registered unrun arms: a variable-active-core encoding at 50 (budget);
SAT modulo symmetries (blocked: CaDiCaL admits one external propagator and the
planarity propagator occupies it; integration is engineering beyond S046);
Kostochka–Yancey edge lower bound and 2-connectivity encodings (necessary
core conditions not encoded; a non-nine-colourable candidate is a witness
regardless). A native NONCOLOUR alert stops all pilots and is preserved for
standalone verification.

## E3 — pilot candidate analysis and targeting criterion

Per arm, analyse all candidates if at most 30, else a uniform sample of 30
(random.Random(46046 + arm_index)). Per candidate: minimum degree, 9-core,
cut vertices, clique number (validated), greedy/DSATUR colour counts, PySAT
8-colourability with a 0.5 s cap; each UNSAT re-solved with pinned cadical
DRAT (5 s) and drat-trim (15 s) as verification. Per-arm analysis wall cap
12 s; unreached candidates are NOT_ANALYSED. Exact labelled duplicates and
exact isomorphism classes among analysed candidates as in E1.

Targeting criterion T for arm A in {C, CS} at order n, with p9(A) = analysed
candidates carrying a checked non-8-colourability proof / analysed:
- T1: at least 20 validated candidates and at least 20 analysed;
- T2: p9(A) >= 0.25 and the Wilson 95% lower bound of p9(A) exceeds the
  Wilson 95% upper bound of p9(B) at the same n.
Timeouts and unchecked UNSAT never count toward p9. Passing arms are ranked
by (validated candidates per solve second) x p9, ties to the smaller order.

## E4 — conditional engineering and operational acceptance

Only if some arm passes T. Implement the S045 bottleneck repair needed for
the selected design: sealed immutable journal segments reloaded by byte-hash
verification (no per-record mathematical re-audit), post-slice audit of only
the new geometric tail, and a bounded resident clause set with checked lazy
re-addition of archived colouring rules. Acceptance: at least 120 s genuine
native solve time and at least 50 newly independently checked records below
the resource caps, then a restart from the sealed checkpoint. Controls:
corrupt and truncated checkpoint rejection, byte hashes, stop/deadline in
preparation/loading/solving/audit, memory recycling, no-progress stop, native
UNSAT concurrent with recycling, first-cause and PID/create/exe identity.

## Decision

SELECT only if T passes for some arm and E4 acceptance passes; otherwise
PIVOT/INCONCLUSIVE with the next distinct hypothesis. A selection is an
empirical research choice, not evidence a witness exists. No long run,
automation or S047 is started in S046. Any native UNSAT is UNKNOWN without a
standalone checked proof; any candidate claim needs checked layers, colouring
and a standalone checked non-nine-colourability proof.

## Amendment A1 — k=8 positive-control calibration (registered after E3)

Registered after E3 returned no passing arm, before any A1 computation. It
cannot change the S046 decision, which the registered criterion has already
fixed as PIVOT/INCONCLUSIVE. Measured justification: across 15 matched arms,
no analysed candidate needed more than 8 colours, so the open question for the
next hypothesis is whether this colouring-feedback generator finds boundary
objects that are known to exist. A1 runs the same driver with k=8 (target:
non-8-colourable biplanar graphs, which exist from order 11, e.g. K6 v C5):

- arm C (minimum degree >= 8) at n in {11, 13, 15, 17, 20, 24};
- arm B at n in {11, 15, 20}; arm CS (minimum degree >= 8) at n in {15, 20};
- 40 s native solve clock each; a run ends at the first NONCOLOUR alert
  (time-to-first-hit) or COLOUR_TIMEOUT; every alert graph gets independent
  planar-layer checks, a drat-trim-verified non-8-colourability proof and a
  checked 9-colouring (verification cost).
- Budget: at most 450 CPU s / 500 wall s from the unused E3/E4 allocations;
  total S046 experimental use stays below 1800 CPU s / 3600 wall s.
- Reported per run: hit or not within cap, seconds and candidates to hit,
  found graph's order, size, minimum degree, clique number. "Not found within
  cap" is UNKNOWN, not non-existence. Found graphs are calibration objects with
  chi=9; no novelty, criticality or Earth–Moon claim is made.
