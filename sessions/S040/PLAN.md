# S040 preregistration — coordinated two-layer stars and D077 gate

Registered 24 October 2026 before any S040 objective value was computed. The
only prior computation was a sizing pilot that counted relaxed components and
compatible pairs (no scores observed): at 156/155/protected inputs, relaxed
components per layer 2092+1691 / 2542+4363 / 1692+2641; conflict-free
503+369 / 309+280 / 464+193; compatible pairs by type0/1/2
174147/37206/4357, 80461/35953/2278, 83108/33699/2092; about1 CPU s each.
REGISTRATION.json pins this file's SHA-256; the experiment script refuses to
run if the plan changes. One experimental process; <=7200 cumulative CPU s.

## D077 solid-progress criterion (fixed now; never lowered later)

Inputs: S039 arms/156-3900-star best (I4=82) and arms/155-3901-star best (79).
SOLID PROGRESS holds iff (A), (B) or (C); otherwise the closeout says PIVOT.

(A) Certified chi>=10 biplanar witness: explicit V,E1,E2 independently checked
simple, edge-disjoint and planar, with all20475 four-sets checked independent-
free at order28, or a drat-trim-verified non-9-colourability proof.

(B) Unprotected mechanism. For BOTH starts and BOTH seeds4000/4001 the
independently replayed `coord` saved best b satisfies all of:
B1 b <= floor(start/2), i.e. <=41 at156 and <=39 at155;
B2 some new-best step on its trace is a relaxed pair (type1 or type2);
B3 matched attribution: star_best > b and pair0_best - b >= (start-b)/2, so
relaxed compatibility, not mere pairing, gives at least half the decrease;
B4 a written explanation, backed by the registered diagnostics, of the
obstruction overcome. B4 is necessary, never sufficient.

(C) Protected candidate source. Both protected seeds4010/4011 give replayed
`coord` bests <=39 (half of the best unprotected start), with B2 and
star_best > b against the matched protected `star` arm.

Not progress: any decrease short of these thresholds, success at one start or
seed only, improvement through type0/single moves only, more CPU, more
implementation, more seeds or larger enumerations. Diagnostics and negative
findings are recorded as learning, separately from constructive progress.
PIVOT parks star/patch hill-climbing and queues S041 as a comparative audit of
at least two genuinely different construction routes (D077).

## Coordinated family and compatibility

Component: an S039 degree3..6 simple-disk star relocation (CLM0129) in one
layer, generated WITHOUT the opposite-layer filter. Effects deduplicated by
actual removed R and added A. Conflicts C=A intersect other layer. Components a
(layer0) and b (layer1) are compatible iff C_a <= R_b, C_b <= R_a and A_a,A_b
disjoint. Claim to prove and control: since each component keeps its own layer
simple and spherical, the final pair is valid iff it is compatible, because
L0' intersect L1' = (C_b - R_a) union (C_a - R_b) union (A_a intersect A_b).
Type0: both C empty (pairing two S039-legal neighbors). Type1: one C empty;
then applying the conflict-free component first makes the other S039-legal, so
it is a two-step sequential composition. Type2: both nonempty; neither order is
legal as two S039 steps. Only type1/2 are the new relaxed family; type2 is the
genuinely atomic part. Edge counts and the quad deficit are preserved per layer;
a77-edge layer keeps its quad. No completion assumption. Planarity and
disjointness are rechecked on every saved pair by separate code.

## Exact neighborhoods and independent replay

At both inputs enumerate every compatible one-star-per-layer pair (all types)
plus S039-legal singles. Degree bound3..6, all fillings via the S038/S039
filling enumerator, every triangular target face, no candidate limit, no cap.
Record counts by type, histogram, minimum, strict improvements, best per type,
CPU, and the SHA-256 of the canonical sorted effect/score table. Replay
independently: chord-subset/polygon-splitting component generation (S039
replay strategy), direct final-layer bitmask disjointness over the FULL
cartesian product, and delta scoring over affected four-sets (not OR masks).
Control: conflict-free singles at the S038 inputs must equal S039's frozen
766/1045 table exactly. Type1 pairs must decompose sequentially and type2 must
not, checked for every pair at both inputs.

## Registered four-set diagnostic (finite; states only what it proves)

At both inputs and at every saved arm best: independent four-set hypergraph H;
vertex and absent-pair incidences; hitting number tau(H) bracketed by an
explicit pair-disjoint packing (lower) and an explicit hitting set (upper),
with RC2 optimum reported as solver-stated unless the bracket closes. Proved
meaning: every alpha<=3 graph on the same labels adds at least tau absent pairs.
It is NOT a planar-pair construction or a nonexistence proof. Each useful absent
pair (in some H member) is classed: C1 addable by an S039-legal single move
(flip/patch r<=3 or legal star); C2 not C1 but added by a compatible type1/2
pair; C3 relaxed stars add it but no compatible pair; C4 no flip, patch or
relaxed star adds it in either layer. Counts are weighted by H-incidence.

## Matched arms

Methods: `star` = S039 top64 guided patches plus legal stars (frozen S039
search code, unchanged); `pair0` = star choices plus type0 pairs; `coord` =
star choices plus all compatible pairs. Same reverse tabu7, aspiration and
nonmonotone moves; pairs use seeded tie-breaking. Starts156/155 x seeds
4000/4001 x three methods = twelve arms. Each: <=150 CPU s, <=400 sweeps,
stop at plateau30 (no new best for30 steps). Projected <=1800 CPU s.

Protected-core arm: S039 protected/3912 best (193, exact chi9), each Sulanke
core edge frozen in its original layer (no component touching a core spoke,
as S039). Methods `star` and `coord`, seeds4010/4011, same caps: <=600 CPU s.
The core gives only chi>=9. No pure coning; no new seeds; closed through17
ranges are not reopened.

Stop everything on I4=0 and validate. Saved bests: independent checker,
alpha exact via all98280 five-sets when I4>0 and a five-set search is cheap,
proper colourings; if greedy needs >9 colours, one pinned-CaDiCaL9-colouring
attempt with DRAT logging and a 300 s cap per record (max24). SAT models are
decoded and checked; UNSAT counts only with verified DRAT; caps are UNKNOWN.
Traces retain every move, type, conflicts, scores and CPU.
