# S041 preregistration — comparative route audit

Registered 24 October 2026 before any probe result. Audit plus two small exact
probes in ONE process, <=1800 cumulative CPU s, fresh smoke already PASS. No
star/patch/coordinated hill-climbing, no S036 action, no publication.

## Routes and evidence standard

R1 symmetry-first; R2 graph-first then exact split; R3 non-alpha structure
(integrality gap, joins, apex/Hajos/Mycielski); R4 optional different exact
encoding of the nine UNKNOWN S11 prefixes. For each: (i) sources and grades,
(ii) closed/failed ranges by ID, (iii) mechanism and how it avoids the S040
near-K9 barrier, (iv) certification path, (v) cost, failure modes and one
falsifiable first experiment with stop rules. Ranking criteria, in order:
1 a credible path to a CERTIFIED chi>=10 witness (not merely exclusions);
2 independence from the counting premise chi_f>9, which rStation conjecture
F9 (SRC-0051, chi_f<=9 for biplanar graphs) would make impossible;
3 exact two-sided decisions of precisely stated finite classes;
4 bounded cost; 5 no overlap with closed or actively owned ranges.
An honest "no route merits heavy computation yet" is an allowed outcome.

## Probe P1 (R1): order-13 layer symmetry at order28

Lemma to prove in RESEARCH (classical inputs: triangulations are 3-connected,
Whitney's unique embedding, Lefschetz fixed points on S^2): if sigma != id of
odd prime order p preserves a simple sphere triangulation, it fixes no edge,
fixes a face only if p=3, and #fixed vertices + #invariant faces = 2. Hence for
a 156-edge 28-vertex biplanar pair whose two layers are both sigma-invariant,
p in {3,13}; p=13 forces exactly two fixed vertices N,S and two free orbits
A,B; p=3 forces one fixed vertex. Each p=13 layer is a union of six of the
29 nontrivial pair orbits (N-S excluded since 78 = 0 mod 13).

Revision before any probe ran (registered hash change disclosed): exhaustive
Kuratowski extraction for every degree-feasible six-orbit set was estimated at
hours. Pair lemma used instead: in a valid pair each layer contains EXACTLY one
of N-A/N-B and one of S-A/S-B (two N-orbits in one layer leave N isolated in
the other), so the layers use complementary ones. Enumerate every such layer
(2x2 choices times all 4-subsets of the 25 remaining orbits = 50600 sets).
Nonplanarity certificates, each re-checkable cheaply: a simple planar graph on
28 vertices with 78 edges is a triangulation, so it needs (T1) every degree
>=3, (T2) every edge in >=2 triangles, (T3) each neighbourhood inducing a
connected graph of minimum degree >=2 (it contains the link cycle). A failed
T-test, or a Kuratowski subdivision extracted by NetworkX and checked by the
stdlib checker, certifies nonplanarity; planarity is certified by a NetworkX
rotation independently re-traversed (stdlib, Euler). Then test EVERY
edge-disjoint pair of planar layers with complementary N/S orbits for
alpha<=3: independent four-set search from orbit representatives N,S,a0,b0
(every four-set has an image containing one of them), cross-checked by full
enumeration on a sample. Proves: complete classification of 156-edge order28
biplanar pairs with a layer-preserving automorphism of order13, given the
lemmas. Any alpha<=3 pair stops everything for witness validation (explicit
layers, all20475 four-sets, K9 check). Not a statement about p=3, involutions,
layer-swapping symmetries, 155-edge pairs or non-symmetric graphs.

## Probe P2 (R3): exact counting tables

Exact integer arithmetic with the Kostochka-Yancey bound
f_k(n)=ceil(((k+1)(k-2)n-k(k-3))/(2(k-1))) for k>=4 critical graphs
(SRC-0011, STATEMENT_INSPECTED; results conditional on it), odd cycles for
k=3, K2/K1 for k=2/1, biplanar budget 6n-12 and the necessary K_{m,n}
condition mn<=4(m+n-2). Tables: (a) Mycielski and generalized Mycielski
(cone) of any 9-critical graph never biplanar; (b) all Dirac joins H1 v H2
with chi1+chi2=10 that pass counting, h<=60; (c) the same for chi=9 joins with
omega bounds; (d) apex budget e(H)<=5h-6 and clique condition omega(H)<=8-a.
Proves only these necessary-count statements.

Total CPU projected <300 s. Records: validation/S041/, independent stdlib
checker scripts/check_s041_records.py in CI. Then rank, write the comparison
matrix and an S042 prompt carrying its own D077-style gate.
