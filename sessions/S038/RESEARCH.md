# S038 results — 24 October 2026

No certified 10-chromatic biplanar graph. Bounds9<=chi_2<=12 unchanged. The nine
S11 prefixes remain UNKNOWN; no S036 process or archived record was modified.

## What was constructed

The implementation works on actual spherical faces, not unconstrained graph
edges. It handles both78+78 and78+77, keeping the unique quadrilateral in the
actual77-edge layer. Selected patches are connected trees of r+1 faces with
r internal removed edges, a simple cyclic boundary, and no interior vertex.
All noncrossing fillings use the complement of the other layer and preserve
the outside embedding and edge count. The two fixed seeds already satisfy per-vertex packing bounds; final
disjointness enforces d1(v)+d2(v)<=27 for every move, with no global S11 degree
restriction. No new concentrated seed was admitted.

No whole-graph straight-line embedding
or geometric thickness assumption occurs: a cyclic polygon parameterises an
abstract topological disk.

## Elementary patch lemma (CLM-0126; no novelty claim)

Let such a patch have q quadrilateral faces (q=0 or1), all other faces triangles.
Its boundary length is p=r+3+q. With no interior vertex, any filling by triangles
and q quadrilaterals has r diagonals. Conversely r pairwise noncrossing diagonals
in this polygon create r+1 cells; the total face excess over triangles is
p+2r-3(r+1)=q. Each cell has at least3 sides, so q=0 forces all triangles and
q=1 forces exactly one quadrilateral. This gives an exact enumeration of this
selected disk family. Disallowing a diagonal already outside the patch prevents
a duplicate graph edge; disallowing another layer's edge preserves disjointness.
The topological disk gluing proves planarity with the outside embedding fixed.

Triangulations were generated recursively. A one-quadrilateral filling can be
obtained by triangulating that quadrilateral and then deleting its added
diagonal, so enumerating triangulations followed by deleting one internal
diagonal is complete, with duplicates removed. Independent chord-subset
enumeration agrees for polygons4..8: triangle counts2,5,14,42,132; deficit-one
counts1,5,21,84,330. Eighty sampled actual moves were checked separately by
planarity, spherical rotations and direct20475-four-set enumeration.

For fixed T1 the exact hitting family remains F={independent four-sets of T1}.
The union violates exactly those members not hit by T2. More generally let B
be the current union's independent four-sets. If proposed added edges hit none
of B, deleting edges cannot eliminate any member of B; therefore a strict
improvement is impossible. Coverage of B is a sound necessary improvement
filter and a ranking signal, not a sufficient condition. Search ranked patches
by that coverage and evaluated the actual objective including newly exposed
four-sets. The top64 multi-edge patches were selected per heuristic sweep;
the initial finite neighborhood enumerations themselves were exhaustive.

## Independently replayed finite neighborhoods (CLM-0127)

Original states: S037 guided/arm-00 has91 violations at156 edges; S037
pairs/arm-03 has125 at155 edges. Frozen S037 replay passed, including all43
old single flips and223 forbidden second-layer completions of the155 state.

| One-layer support r | 156 neighbors | Minimum score | 155 neighbors | Minimum score |
|---:|---:|---:|---:|---:|
|1|43|93|48|127|
|2|154|93|167|125|
|3|577|93|639|125|
|4|2343|93|2705|125|

Support r is the number of initially removed internal edges; a filling may
retain some, so the actual symmetric difference can be smaller. Counts are
distinct ordered layer graphs WITHIN each support family, and families overlap.
These are not all r-edge exchanges, all patches, or all embeddings.

We also enumerated simultaneous patches in both layers. A proposed edge may
be currently occupied by the other layer if that same atomic move removes it;
only final disjointness is required. This is a larger family than composing
individually disjoint moves.

| Support split | 156 neighbors | Minimum score | 155 neighbors | Minimum score |
|---|---:|---:|---:|---:|
|1+1|477|91|560|129|
|1+2|1674|91|1966|129|
|2+1|1763|91|1952|126|
|2+2|6128|91|6843|126|

No tested original-state family strictly improves either starting state. The
91-state is strict for the one-layer disk families and weak for the coupled
ones. The125-state has neutral moves in the larger one-layer families.
Unsearched1+3/3+1, patches with an interior vertex, disconnected supports,
other embeddings, larger moves and other starting states are NOT excluded.

All28039 family-member records were matched exactly against independent
stdlib replay. The generator expands dual-connected face sets and recursively
triangulates polygons; the replay instead brute-enumerates removed-edge
subsets, reconstructs their boundary, and chooses noncrossing chord subsets.
It independently reconstructs every score. Stored compressed full neighbor
tables permit exact comparison, not merely agreement of minima or counts.

## Matched bounded search and results (CLM-0128)

Two identical starts, seeds3800..3802, and20 CPU-second ceilings were used for
both one-edge and guided r<=3 patch methods. Each stopped after100 sweeps without
best improvement (or a finite cap). Because plateau stopping was allowed,
actual CPU differs; these are equal ceilings, not equal consumed time.

| Start | Method | Best scores across seeds | Actual CPU seconds |
|---|---|---|---:|
|156/91|single|91,91,91|3.40625|
|156/91|patch|91,91,91|24.21875|
|155/125|single|124,123,125|5.578125|
|155/125|patch|123,124,124|43.078125|

The extra patch machinery gave no best-score advantage in this tiny comparison.
Both methods can reach123 at155 edges after non-improving transitions; absence
of a strictly improving initial move does not imply inability to escape by a
walk. Three seeds give no statistical or global efficiency conclusion.

Four additional coupled arms, seeds3810/3811 with30 CPU-second ceilings and
30-sweep plateau stops, retained91/125 and used21.234375 CPU seconds total.
They include single-layer moves as alternatives; every best/trace is preserved.
No UNSAT or impossibility result follows from these heuristic stops.

All22 saved layer records (including duplicates and neighborhood minima) have
independently checked sphere rotations, simplicity, disjointness,78+78/78+77
counts and all20475 four-set scores. Each has a proper colouring with at most
nine colours. Both saved123 states have explicit8-colourings, so they are not
10-chromatic witnesses. An independent stdlib checker also replays every patch
transition, its disk filling, the atomic two-layer updates and exact score.

Total registered experimental CPU101.09375s: initial neighborhoods0.578125,
twelve search arms76.28125, coupled neighborhoods0.40625, coupled arms21.234375,
radius-four diagnostic2.59375. Full271+K9 acceptance, controls and independent
verification are separately recorded. No cap was filled without a reason and
no unattended job was launched. Historical native DRAT certificates were not
replayed apart from the fresh required environment smoke controls.

## Consequence for the construction target

Boundary-only disk replacements are sound and now independently reproducible,
but these two seeds lie in stronger local traps than S037 established. Their
finite obstructions are tools, not substitutes for a witness or a whole-stratum
decision. Neither a larger fixed wall time nor a new chat changes that evidence.

The measured next direction is to change the seed and move representation:
test relocation of a vertex/star (an interior vertex absent from this patch
family) and construct seeds retaining a certified nine-chromatic core. Keeping
such a core would prevent an8-colourable intermediate seed, although it does
not force ten colours or good alpha3 counts. The known Sulanke core is already
recorded in validation/sulanke.json; older closed small-extension cases must
be checked before new work. This is a future experiment, not a claimed escape.
Compare those changes against the frozen91/123 baselines with finite caps;
do not continue the same boundary-only radius expansion without new evidence.
