# S037 results — 24 October 2026

No certified 10-chromatic biplanar witness. 9 <= chi_2 <= 12. S11 remains UNKNOWN.

## The 247/9 theorem (CLM-0123)

The S030 graph variables are numbered lexicographically on the 378 pairs.
S032 bijectively renames graph variable i to 756+i, interleaving the two layer
variables below 757. The 28 fixed graph units are the root-0 star and absent
edge 12. The first eight remaining variables are 785..792, for edges
(1,3)..(1,10). S034 enumerates False/True tuples in lexicographic order, most
significant bit first. All historical cell assumptions agree with this mapping.

For consecutive vertices u,v, put t(w)=2*g(1,w)+g(2,w). The six clauses forbid
exactly t(u)>t(v): all 16 truth-table rows were checked, and all 138 clauses in
both sorted blocks occur in the actual frozen 336030-clause formula. The
committed original formula and mapping reproduce the exact native base hash
3066258744e74f5bef453caeb9f0c8cbfd43f702721d2c124950e62366d1681d.

If g(1,u)=1 and g(1,v)=0 then t(u)>=2>1>=t(v), whatever the two remaining
bits. Thus sorted types force nondecreasing first bits. Conversely any
nondecreasing eight-bit prefix extends to sorted types: choose all its second
bits zero and complete the remaining three types with type 3. This proves
exactly nine prefixes survive sorting alone: 0^(8-k)1^k, k=0..8, with IDs
0,1,3,7,15,31,63,127,255. A separate exhaustive enumeration of all 65536
first/second-bit assignments and a full-eleven-position dynamic program agree.

The forbidden set equals ALL 247 historical DRAT certificate IDs, without a
single mismatch. This is a new independent tiny proof, not fresh replay of those
historical DRAT files. It does not satisfy the other S11 constraints. The 96.5%
regional closure figure measures built-in symmetry bookkeeping; it does not
show substantive exclusion of the surviving sorted search space, nor proximity
to a solution. Retain the historical proofs and provenance without inflating
their mathematical significance. A clean replacement is the nine prefix cases
above with the original sorting constraints retained; no restart is needed.
Alternatively parameterise the four type multiplicities in each sorted block
(364 possibilities on 11 vertices, 680 on 14), with all remaining graph/layer
constraints still required. These are search coordinates, not solved cases.

## Planar-pair prototypes (CLM-0124)

At n=28 the per-layer bound is 78. Total 156 forces 78+78; total 155 forces
78+77. Twelve seeded random-move arms used 13.3125 process CPU seconds and
180000 attempted proposals. Eleven produced checked feasible pairs; arm 3704
failed packing (six overlaps) and remains a failed heuristic. Two seed families
were used (stacked insertion and bipyramid), each diversified by 840 flip
attempts; flips can leave stacked families. Modes were random flips, mixed
flips/vertex transpositions, and a swap kick after stagnation. No uniformity,
mixing, all-triangulations coverage or completeness claim is made.

Best independent-four-set counts:

| Stage | 156 edges | 155 edges |
|---|---:|---:|
| Random/mixed/kick batch | 180 | 125 |
| All-legal-flip tabu refinement | 91 | 125 |
| Fixed-template bijection SAT | 180 | 125 |

Four guided arms used 7.625 CPU seconds and stopped at the preregistered
300-sweep plateau. Every saved planar pair has an independently verified proper
colouring with at most nine colours. There are 19 checked saved layer records,
including duplicates across methods, not 19 distinct new graphs. Direct checking
enumerated all 20475 four-sets per record; rotation certificates independently
certify the two spherical embeddings in portable stdlib CI. Explicit V,E1,E2,
rotations, colourings and hashes are retained. Failed alpha3 targets do not
establish impossibility. The 91-count pair itself has an 8-colouring.

## Fixed-first-layer hitting and exact templates

For fixed T1, let F={S subset V: |S|=4, E(T1[S])=empty}. For every S in F,
sum_{e subset S} x_e >= 1 is necessary and sufficient for alpha(T1 union T2)<=3,
when x selects T2 edges from the complement of T1. Every other four-set already
has a T1 edge. This is exact for independence; it imposes no planarity.

For the 91-state's T1, |F|=4821 and there are 300 permitted complement edges.
A 77-edge SAT hitting assignment was independently decoded, disjoint, and had
zero independent four-sets; its second layer contains an explicit independently
checked Kuratowski subdivision. The separate 78-edge solve hit its conflict cap
(UNKNOWN); adding one unused complement edge to the 77-edge assignment directly
gives a 78-edge hitting solution, still nonplanar. Both explicit relaxations are
preserved and rejected as biplanar witnesses. Thus covering within this edge
budget is feasible for this fixed T1; realizing a planar cover is the obstacle.

The genuinely different bounded exact formulation fixes TWO planar templates and
searches a 784-variable vertex bijection. Exactly-one row/column constraints
encode the permutation; binary clauses forbid mapping a template edge to T1.
Every model therefore has planar, disjoint layers by construction. Each violated
independent four-set supplies 24 sound clauses forbidding all bijections between
the relevant independent four-sets. Exhaustive 5! controls compare this encoding
with direct permutations; an impossible two-K4 packing is rejected. Four arms
found 338 feasible labelled pairs, with no improvement over their initial saved
states, then reached 20000-conflict limits (native overshoot at most five).
They used 21.125 CPU seconds and accumulated 4849776 separated clauses. No UNSAT
or template exclusion is certified. This formulation avoids Kuratowski cuts but
still suffers from many equivalent local four-set obstructions.

All six exact arms plus both local-search batches used 44.625 measured process
CPU seconds; ceilings were deliberately not filled after the stopping rules.
Nonextension certificate generation used a further 15.5625 CPU seconds. Full
smoke and short controls/checking are recorded separately. No long worker,
scheduled restart or S036 process was launched.

## Structural reductions and falsification (CLM-0125)

A simple planar n>=5 graph with 3n-7 edges is 2-connected: disconnection allows
at most 3n-9 edges, and gluing at a cutvertex gives at most 3n-8 (pendant case)
or 3n-9 (two pieces of order at least three). Euler then gives
sum_faces(length-3)=1, so each embedding has one quadrilateral and all other
faces triangular. Only a missing diagonal of that quadrilateral can complete
THAT embedding. A different embedding can admit different additions. These are
elementary facts also covered in SRC-0059; no novelty claimed.

Deleting one vertex from a 78-edge layer and applying Euler gives degree>=3;
the same argument for a 77-edge layer gives degree>=2. Therefore a fixed
triangulation of maximum degree 26 cannot pack with any 77/78-edge second
layer at n=28. Necessary per-vertex filters are d1+d2<=27, hence d1<=24 for
78+78 and d1<=25 when T1 is triangulated and T2 has 77 edges. These elementary
filters reject overly concentrated seeds; they do not decide packing.

The tempting assertion that every disjoint 78+77 pair is just an edge deletion
of a disjoint 78+78 pair is FALSE with the given layers fixed. In the best
155-edge pair (pairs/arm-03) both quadrilateral diagonals lie in T1. More
strongly, all 223 missing union edges were tried as additions to T2; each has
a retained K5/K3,3 subdivision in T2+e, checked without NetworkX. The same
is true of arm-11: 446 certificates in NONEXTENSION.json. This proves fixed
split nonextension across ALL embeddings, not nonbiplanarity of the union,
and does not exclude a new partition after repartitioning edges. Both unions
are already biplanar and <=9-colourable. Restricting 155-edge discovery to
deletions of disjoint triangulation pairs would miss these explicit pairs.

The best 156-edge state is a strict minimum for single legal disjoint diagonal
flips in its embeddings: exactly 43 moves, every resulting count at least 93
versus its 91. A separate direct four-set enumeration checks every neighbor.
This is a finite neighborhood certificate, not a theorem about all moves or
global search. Coordinated patch moves are the concrete missing capability.

## Direction ranking

1. Best supported: exact small face-patch replacements preserving planar
   embeddings, including genuinely near-triangulated 77-edge layers. Start
   from the 91/125 states, with multi-edge escapes from certified local traps.
2. Useful auxiliary: four-set hitting to rank/select patches and isolate why a
   planar cover fails. Use the explicit nonplanar hitting solution as a negative
   control, never as a witness or input known to have a planar realization.
3. Lower priority: whole-template permutation SAT; tiny tests are sound but
   the measured clause growth did not improve a candidate. Random swap kicks
   can fail to pack or effectively freeze, so do not extrapolate their runtime.
4. No basis to restart the nine S11 cells. S037 explains their enumeration but
   decides none of their substantive satisfiability questions.
