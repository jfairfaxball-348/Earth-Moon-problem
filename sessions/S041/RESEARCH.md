# S041 research — comparative audit of construction routes, 24 October 2026

No chi>=10 witness; 9<=chi_2<=12. Audit plus registered exact probes P1-P4
(PLAN.md, PLAN_ADDENDUM.md). Every computed negative below concerns a precisely
stated finite class; no global exclusion of OP1(b) or of chi_2>=10.

## Cross-route context

- Counting routes (R1, R2, R4 and all of S025-S040) seek alpha<=3 at order28,
  i.e. chi_f>=28/3>9. rStation post141 (SRC-0051) conjectures F9: chi_f<=9 for
  every biplanar graph. If F9 holds, every counting route is empty. F9 is a
  universal upper bound and out of scope (D042); it is used only as a risk.
- Sulanke's 9-chromatic K6vC5 has chi_f=6+5/2=8.5 (join additivity): the known
  extremal example is an integrality-gap graph, not a counting one.
- The recurring obstruction is cross-layer K9-minor structure: S025 C5 blow-ups,
  S040 hub pairs completing K9/K10, and below, every tested apex leaf. Lemma B/C
  (CLM0090/0091) decide these instantly where Kuratowski CEGAR stalls.

## Lemma R1 (CLM-0137): layer-preserving symmetries at order28

Let sigma != id of odd prime order p act on a simple sphere triangulation T
(3-connected, so by Whitney every automorphism preserves the face structure and
is induced by a sphere homeomorphism). (a) sigma fixes no edge: if it fixed
adjacent vertices v,w it would fix the cyclic rotation at v (odd order cannot
reverse it) pointwise, hence by connectivity be the identity. (b) A face is
invariant only if p divides its length, so only for p=3. (c) sigma is
orientation preserving (odd order), so by the Lefschetz fixed-point theorem
L(sigma)=2 = #fixed vertices + #invariant faces (no fixed edges; an invariant
triangle is rotated, trace +1). Hence for p>=5 sigma fixes exactly two
vertices and n = 2 (mod p); for p=3, f+phi=2. For a 156-edge 28-vertex pair with
both layers sigma-invariant, the fixed vertex set is common: p>=5 needs p|26,
so p=13 with two fixed vertices; p=3 needs exactly one fixed vertex (n=1 mod 3)
and one invariant face per layer; orders 5,7,11,17,19,23 are impossible. This
explains why a fixed-point-free Z7 cannot preserve layers (cf. SRC-0048).

## P1 (CLM-0138): complete order-13 class

Vertices N,S fixed; A,B free orbits; 29 nontrivial pair orbits (NS excluded,
78=0 mod 13). Pair lemma: each layer has exactly one of NA/NB and one of SA/SB,
complementary across layers. All 50600 candidate layers are certified: 46016
fail T2 (an edge in fewer than two triangles), 4260 fail T1 (degree<3), 168
have stdlib-checked Kuratowski subdivisions, 156 are planar with checked
rotations (52 triangles). Of their pairs, 3510 are valid edge-disjoint planar
pairs; NONE has alpha<=3. The minimum number of independent four-sets is 767
(layers {NA,SB,AA1,BB1,AB0,AB1}, {NB,SA,AA2,BB2,AB2,AB4}), versus 79 from
local search. Symmetric layers are too regular: unions of invariant
triangulations keep large independent sets. CPU 9.23 s.

## P2 (CLM-0139): counting tables for non-alpha constructions

Conditional on Kostochka-Yancey (SRC-0011): (a) the Mycielskian, and every
generalized Mycielskian, of a 9-chromatic graph is never biplanar (3e+h >
12h-6 iff 34h>66 for the 9-critical core; checked to h=4000, 20 levels).
(b) A 10-chromatic join contains H1vH2 with H_i k_i-critical, k1+k2=10. Biplanar
counting plus the K_{m,n} bound leave only K1vH9, K2vH8 (unbounded h) and
K3vH7 (h<=16), plus K4vH6 (h<=9) and K5vH5 (h<=7). K9-freeness forces
omega(H)<=8-a for K_avH; with Gallai's theorem (k-critical graphs on <=2k-2
vertices are joins, SRC-0027) and the classical 11-vertex minimum for a
triangle-free 4-chromatic graph, no 6-critical H on <=9 vertices has omega<=4
and no 5-critical H on <=7 vertices has omega<=3, so those two cases die. Apex budget: e(H)<=5h-6, 4h-1,
3h+3 for a=1,2,3. If H is a Hajos join, its junction vertex is a cut vertex of
the layer without the bridge edge, so that apex layer is not a triangulation
and e(H)<=5h-7 is needed for a=1.

## P3/P3b/P4 (CLM-0140): apex leaves are K9-minor obstructed

A Hajos composite of 9-critical biplanar graphs is 9-critical and biplanar
(BGS, SRC-0002). For K1vH to be K9-free each Hajos leaf L loses one edge e
with omega(L-e)<=7, and K1v(L-e) must be biplanar. Controls: the lazy
Kuratowski CEGAR found Sulanke biplanar (explicit checked layers) and K9 not
(DRAT verified). Leaf graphs, all certified NON-biplanar by the S025 Lemma-B/C
CEGAR with pinned DRAT and full clause justification (no Kuratowski lemmas
needed), each in under one second:

| Leaf L (9-critical) | Leaf graph K1v(L-e) | n / m (budget) | Lemma B / C models |
|---|---|---|---|
| K6vC5 (Sulanke) | (K7-e)vC5 = K5 v pentagonal bipyramid | 12 / 60 (60) | 80 / 440 |
| K3 v Hajos(K6,K6) | (K4-e) v Hajos(K6,K6) | 15 / 78 (78) | 560 / 4288 |
| K2 v Hajos(K7,K7) | (K3-e) v Hajos(K7,K7) | 16 / 82 (84) | 984 / 7952 |

The plain Kuratowski CEGAR left the first UNKNOWN after 600 s (264464 lemmas);
cover annealing plateaued at one or two uncovered edges. Consequence: every
apex-over-Hajos composite with any of these leaves is non-biplanar (subgraph
monotonicity), including all Sulanke-based ones (any H containing K6vC5 minus
at most one edge gives K9 or (K7-e)vC5 inside K1vH). Hajos(K_k,K_k) is unique
up to isomorphism, so the table is complete for those leaf shapes.

## Comparison matrix

| | R1 symmetry-first | R2 graph-first, exact split | R3 non-alpha joins/apex | R4 S11 cells, new encoding |
|---|---|---|---|---|
| Sources | SRC-0048, 0042, 0002; S037 | SRC-0055, 0049, 0050, 0042 | SRC-0002/0003, 0011, 0020, 0027, 0043, 0051 | SRC-0045, 0050, 0055 |
| Closed/failed | C7[K4] thickness3; fpf-Z7 (claimed); S037 permutation SAT capped; S041 orders not in {2,3,13} impossible, Z13 class empty (best 767) | 271 corpus; C5 sum<=17 classes; 16/30 profiles; twinned slice (claimed); 11-regular (claimed); S040 repairs contain K10 | joins except K1/K2/K3 apex; Mycielski; Sulanke cores through17 (CLM0072-0076); three apex leaf shapes (S041) | 247/256 regions; nine UNKNOWN after S036 |
| Mechanism | orbit reduction | screen then decide | chi = a+chi(H) by construction | complete exact search |
| Needs chi_f>9 (F9 risk) | yes | yes | no | yes |
| Avoids S040 barrier | no evidence; P1 far worse | must, unsolved | by omega bound, but hits K9-minor lemmas | n/a |
| Certification | layers + four-sets; DRAT exclusions | S025 stack | layers + Hajos/join proof; DRAT | DRAT |
| Cost / next test | Z3 class: 126 orbit variables, SAT + Kuratowski | generator unsolved | sub-second leaf decisions | days-weeks; S036 stopped |
| Rank | 2 | 3 | 1 | 4 (parked) |

Ranking under the registered criteria: R3 is the only route whose witness
does not require chi_f>9, its decisions are exact and fast, and it is not an
owned or closed range beyond the leaves tested here. Its live risk is that
K9-minor lemmas kill every leaf; S041 tested only three shapes. R1 is exact but
counting-dependent and P1 suggests symmetry pushes away from alpha<=3. R2 has
no new generator. R4 stays parked (no genuinely new bounded test).

Recommendation (S042): an exhaustive, certified apex-leaf census for K1vH9,
K2vH8 and K3vH7: every leaf L with the apex budget among a precisely sourced
finite list of small critical graphs (complete graphs, odd cycles, k-Ore/Hajos
graphs of cliques, Gallai joins on <=16 vertices, BGS 9-critical biplanar
graphs where obtainable), every K8-killing edge, decided both ways. A live
leaf with slack enables composites with certified chi=10; no live leaf closes
the census range and returns to the comparative list.

CPU: P1/P2 9.25 s; P3 640.5 s (controls 30.4 s, capped 610.1 s); P3b 90.6 s;
P4 about 181 s; total about 921 s of the registered 1800 s. No probe was
rerun; archiving only re-ran the P3b clause-justification checker.
