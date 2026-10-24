# S039 research — star relocation, 24 October 2026

No chi>=10 witness; 9<=chi_2<=12. All results below concern explicit finite
constructions or selected fixed-embedding neighborhoods. S11 remains UNKNOWN.

## Star lemma (CLM-0129)

Let a connected simple spherical plane layer have triangular faces, with at
most one quadrilateral. Select a vertex v of degree d, 3<=d<=6, whose incident
faces form a disk, with simple rim and no other interior vertex. Let q in {0,1}
count incident quadrilaterals. Counting face incidences gives rim length d+q:
the d triangular faces contribute one rim edge each, and a quadrilateral
contributes one extra. Removing v and its d spokes leaves that polygonal hole.

A filling with triangles and q quadrilaterals has (d+q)-3-q=d-3 internal
diagonals, by disk Euler and face-edge counting. Enumerate its noncrossing
chords, forbidding edges already outside the hole or in the other layer.
Insert the SAME labelled v in any triangular face of the filled map, joining
it to the three face vertices; forbid these spokes in the other layer. Gluing
the disk and subdividing the target face preserve the sphere embedding.
The edge change is -d+(d-3)+3=0, and the number of quadrilaterals remains q.
The layer thus retains its actual edge deficit, including a true77-edge case.
No disjoint triangulation completion is assumed. Reject a repeated rim,
non-disk star, duplicate/outside diagonal or overlapping opposite-layer edge.

The target can lie in the old hole or elsewhere. This family is different
from S038's boundary-only tree patches, which had no interior vertex. It does
not include degree2, degree>6, non-simple links, two-layer atomic relocations,
or arbitrary changes of embedding. These omissions are not impossibility proofs.

## Exact neighborhoods (CLM-0130)

Inputs are the frozen S038 91/123 states, not the original S037 91/125 pair.
Effects are deduplicated by layer and actual removed/added edge sets.

| Edges | Initial I4 | Unique neighbors | Minimum I4 | Strict improvements |
|---|---:|---:|---:|---:|
|156|91|766|83|4|
|155|123|1045|116|5|

Independent enumeration chooses chord subsets and splits polygons, rather than
using the author's recursive filling generator. All1811 effects and exact
scores agree. The saved best156 move relocates layer0 vertex7 from degree3,
rim[0,9,25], to triangle[12,14,22]. The best155 move relocates layer0 vertex11
from degree3, rim[12,25,27], to triangle[1,9,26]. Both targets lie outside their
old holes. Their saved pairs have proper9- and8-colourings respectively.

## Matched bounded search (CLM-0131)

All arms use the same two inputs, seeds3900/3901, CPU ceiling15s and plateau50.
Patch-only choices are the frozen S038 top64 guided patch family. Star arms
include those choices plus degree3..6 stars, with reverse tabu7 and nonmonotone
moves. Equal ceilings do not imply equal consumed time. Every arm plateaued.

| Edges | Seed | Patch best / CPU s | Star+patch best / CPU s |
|---|---:|---:|---:|
|156|3900|91 /4.265625|82 /5.140625|
|156|3901|91 /4.546875|82 /5.515625|
|155|3900|123 /4.843750|91 /7.890625|
|155|3901|123 /4.453125|79 /8.296875|

This gives concrete constructive improvements from both basins, not a
statistical superiority theorem from two seeds. Saved155 scores91/79 have
alpha exactly4: a positive independent four-set exists, and all98280 five-sets
contain an edge. The156 score82 pair has an explicit independent five-set;
its alpha was not computed exactly. Every saved graph has a proper<=9-colouring.
The score79/82 witnesses therefore do not improve the chromatic lower bound.

## Protected nine-chromatic source (CLM-0132)

The old Sulanke record has eleven vertices and exactly K6 join C5: clique
[0,1,2,3,4,5], odd cycle[7,9,6,8,10], all cross edges, total50. The two disjoint
layers have26/24 edges and independently checked spherical rotations. K6
requires six colours, C5 requires three, and their join requires disjoint
palettes; a supplied proper9-colouring proves chi=9. Source attribution is
inherited from the existing Sulanke catalogue; no novelty claim.

Audit of CLM0072..0076/S012/S013 finds the retained-core ranges through order17
already closed. Only order28 is generated here. Each new vertex cones a pair
of faces with disjoint boundaries, preserving old edges and avoiding duplicate
cross-layer spokes. Initially there are one/three quadrilaterals; coning makes
only triangles. Every insertion has <=8 earlier neighbors. Given the core's
nine-colouring, choose a missing colour at each insertion in FORWARD insertion
order (equivalently remove the latest vertex first to obtain the extension
induction). Consequently pure coning can NEVER produce chi10 in this family.
These seeds are calibration controls. PLAN's phrase 'reverse-order greedy
extension' means this deletion/induction argument; the actual recorded colour
construction proceeds in insertion order, as required for correctness.

Four seeds reach156 edges. Odd seeds delete one noncore second-layer edge,
merging two triangles into one quadrilateral to obtain155. Non-insertion star
and patch changes then preserve every original core edge IN ITS ORIGINAL layer.
The coning upper-bound proof need not survive such changes; the core lower
bound9 does. Independent saved colourings happen to prove every result chi=9.

| Seed | Edges | Initial variant I4 | Best I4 |
|---|---:|---:|---:|
|3910|156|1286|304|
|3911|155|1413|210|
|3912|156|1260|193|
|3913|155|1520|231|

These are a strict protected-embedding subset, not an exhaustive extension
search. All four arms plateaued; none surpassed the unprotected source.

Experimental CPU: neighborhood enumeration0.1875s, matched arms44.953125s,
protected generation/search34.578125s, total79.71875s. Saved classification1s
separate; no bounded SAT colouring attempt was needed (all greedy colourings
already <=9). Controls2.140625s and portable replay separate. All experiments
finished, far below7200s, with no old process or scheduler action.

All22 saved records have explicit V,E1,E2, sphere rotations, simplicity and
disjointness checks, direct20475 four-set enumeration and proper colourings.
All762 search transitions and four17-insertion seeds are independently replayed.
The portable checker imports no search generator, NetworkX or PySAT; frozen
stdlib certificate helpers remain pinned by their earlier manifests.
