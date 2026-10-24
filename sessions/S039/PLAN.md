# S039 preregistration

One experimental process, <=7200 cumulative process CPU seconds; no unattended
worker/scheduler/legacy restart. Fresh full271+K9 and frozenS037/S038 replays PASS
before experiments. Controls/replay recorded separately. S040 not executed.

Main inputs: S038 arms/156-3800-patch (91 independent four-sets) and
arms/155-3800-patch (123). Keep all28 labels and actual78+78/78+77 layers.

Vertex-star move: choose a vertex of degree3..6 in one layer. Its incident faces
must form a disk with simple boundary, with that vertex its only interior
vertex. If q=0/1 quadrilateral lies in the star, hole boundary has d+q vertices.
Enumerate all hole fillings with d-3 diagonals and q quadrilaterals, respecting
other-layer disjointness, then insert the SAME vertex in any triangular face
of the filled graph. Record whether target lies inside the old hole or elsewhere.
Deleting d edges, adding d-3 hole chords and3 new spokes preserves edge count.
Degree2, degree>6 and nonsimple links are explicitly omitted, not ruled out.
If quad is incident, preserve its deficit in the hole filling; never assume a
77-edge layer completes to a disjoint triangulation.

First enumerate the full selected star neighborhood at both inputs and preserve
unique effect tables/best move. Independently replay with chord-subset filling
enumeration, not the generator recursion. Controls must cover ordinary and
quad-incident stars, malformed links/overlaps, direct objective counts, planarity
and rotations. A selected-family negative is not global nonexistence.

Matched search: two starts x seeds3900,3901 x methods patch-only and star+patch,
eight arms, <=15 CPU seconds each, <=500 sweeps, plateau50 sweeps. Same ceilings,
seeds/inputs; actual consumed time recorded. Star arm includes the same top64
S038-style patch choices plus star relocations. Preserve non-monotone moves and
tabu traces. Stop on zero violations pending independent witness checks.

Protected-core seed arm: verify exact K6-join-C5 core and its26/24 planar layers,
9-colouring and written chi=9 proof. Build four order28 seeds (3910..3913) by
inserting a new vertex into a pair of faces with disjoint boundary vertices,
coning each face. Prefer reduction of planar deficit, but record actual edge
counts/failures; do not assume155/156 is attainable. No core edge may be lost.

Important entry deduction: the given core has one quadrilateral in layer1 and
three in layer2, all other faces triangles. Pure coning never creates larger
faces, so every added vertex has at most8 neighbors at insertion. Reverse-order
greedy extension of the core9-colouring gives an explicit9-colouring. Thus PURE
coning seeds are guaranteed calibration controls, not possible chi10 witnesses.
To obtain a new candidate source, apply non-insertion patch/star changes after
construction, freezing each original core edge in its initial layer. This is a
strict subset of protected-core embeddings, not an exhaustive extension search.

Four bounded protected arms, <=20 CPU seconds each, <=150 sweeps, plateau40,
star+patch choices restricted to retain core edges; alternate155/156 when a
full156 seed permits deletion of a noncore second-layer edge. Record explicit
core-preservation9 lower bound, proper colourings, all20475 four-sets and actual
edge counts. Any claimed new result needs independent rotations and traces.
No headline promotion from a heuristic or a capped exact/colour search.

Post-search classification, registered before use: independently validate all
saved bests and four protected seed variants. If greedy colouring uses>9 colours,
attempt a9-colouring with <=5000 native conflicts per record, max24 records.
SAT models must be decoded and checked; a capped/UNSAT response gives no negative
colourability certificate. Record this CPU separately within7200. Also enumerate
all98280 five-sets where useful to distinguish alpha=4 from an unmeasured alpha
estimate. These checks classify saved constructions, not an upper-bound route.
