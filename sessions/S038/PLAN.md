# S038 preregistration — before scientific experiments

Fresh full271+K9 smoke must PASS. One experiment process; total <=7200 process
CPU seconds. No autonomous workers, scheduler, S036 restart or later session.
Inputs: S037 guided/arm-00 (156 edges,91 violations), pairs/arm-03 (155,125).
Recheck planarity, all20475 four-sets,43-flip trap and223-addition obstruction.

Represent actual plane layers by faces, including the unique quadrilateral in
the77-edge layer. Remove r=1,2,3 edges whose r+1 incident faces have tree dual
and a simple boundary cycle. Enumerate all polygon triangulations (and, if the
old quadrilateral is inside, all one-quadrilateral dissections) with exactly r
new diagonals, preserving the outside embedding and edge count. Reject chords
already elsewhere in the same layer or present in the other layer. This is an
exact selected disk-patch neighborhood, not all planar edge exchanges.

First exhaust all such neighborhoods at both saved starts. Preserve counts,
best moves, scores and patch boundary/removal/addition certificates. A separate
stdlib replay must enumerate the same finite neighborhoods and check scores.
Controls: Catalan counts for polygons4..7, near-polygon counts1,5,21,84;
small independent enumeration, random legal moves against NetworkX, deliberate
overlap/crossing/boundary-corruption negatives. Recheck objective directly.

Then compare baseline one-edge patches with guided r<=3 patches: two identical
starting states x seeds3800,3801,3802 x two methods, twelve arms. Each arm
<=20 process CPU seconds, <=2000 sweeps; stop after100 sweeps without best
improvement or zero violations. Same per-arm CPU ceilings/seeds/inputs; log
actual CPU because early plateau stops need not consume equal time. Rank patches
by coverage of current violated four-sets; initially examine the top64 selected
multi-edge patches per sweep, plus all one-edge patches. Bounded tabu/neutral
moves may escape plateaus; no completeness/mixing/global coverage claim.

If there is a material improvement, permit a second registered diagnostic within
the7200-second ceiling, based on the observed limitation; never fill the budget
with an unexplained grind. Stop on evidence stagnation or unsafe resource use.
Retain every best pair explicitly with independent rotation/four-set/colouring
checks. Exact finite lemmas need independent replay, caps remain UNKNOWN.
No bound promotion without the full construction and non9-colourability gates.

Measured second diagnostic (registered after the initial twelve arms): initial
one-layer r<=3 neighborhoods have no strict improvement at91/125. The search
arms retain91 at156 edges and reach123 at155. Test simultaneous two-layer disk
patches with support splits(1,1),(1,2),(2,1), then only on evidence consider
(2,2). A proposed chord may occupy an edge removed by the other layer, but final
layers must be disjoint. First exhaust these coupled neighborhoods at the two
original states and independently validate every reported escape. If useful,
run <=4 coupled repair arms at <=30 CPU seconds each, <=200 sweeps and plateau
30 sweeps, seeds3810,3811. Selected multi-patches must be stated explicitly;
global closure remains UNKNOWN. Retain exact enumeration counts and counterexamples
to any claim that a local minimum in each layer is a joint local minimum.

Final radius diagnostic, registered after the coupled arms: no strict original-
state improvement exists for the independently replayed one-layer r<=3 or joint
splits(1,1),(1,2),(2,1). The twelve matched arms reach91/123; coupled arms give
no improvement. Exhaust one-layer disk patches r=4 at both ORIGINAL states and
joint split(2,2) there. Extend polygon controls to n=8 (132 triangulations,
330 one-quadrilateral dissections). Cap this diagnostic at120 process CPU
seconds; preserve exact counts/best certificates and replay independently. This
locates the next finite radius boundary; no larger search follows automatically.
