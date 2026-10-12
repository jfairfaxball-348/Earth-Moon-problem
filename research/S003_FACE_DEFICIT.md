# S003 — face covers, facial deficit and the universal-apex lane

Programme proofs (status PROGRAMME_PROVED unless marked). Graphs are finite
and simple. For a planar graph P on a vertex set of size N>=3 put
d(P)=3N-6-|E(P)|>=0. For a biplanar G=P1∪P2 (edge-disjoint, both spanning)
on N>=3 vertices, D(G)=6N-12-|E(G)|=d(P1)+d(P2).

## Lemma 1 (face-cover characterization of biplanar apices)

Let H be a graph and apex(H)=H+a with a adjacent to every vertex. Then
apex(H) is biplanar iff E(H)=E1⊔E2 and V(H)=S1⊔S2 such that, for i=1,2,
(V,Ei) has a plane embedding with all of Si on the boundary of one face.

*Proof.* Given layers of apex(H), let Si be the neighbours of a in layer i
and Ei=E(layer i)\{at: t}. Deleting a from a plane drawing of layer i merges
the faces around a into one face whose boundary contains Si. Conversely
place a inside the face carrying Si and join it to Si by non-crossing arcs
(possible because Si lies on that face boundary). ∎

Consequences used below: Hi[Si] is outerplanar (all its vertices lie on one
face), so e(Hi[Si])<=2|Si|-3 for |Si|>=2; e(Hi)+|Si|<=3(|H|+1)-6; summing,
e(H)<=5|H|-6 (the familiar budget), and the budget is the only content of
the density condition. A density-feasible apex is NOT thereby a face cover.

## Lemma 2 (facial deficit bounds low-codegree edges; planar)

Let P be a planar graph on N>=4 vertices. Call an edge uv of P *thin* if u,v
have at most one common neighbour in P, and give it weight 2-c(uv) where
c(uv)∈{0,1} is that number. Then

    sum over thin edges of (2-c(uv))  <=  4 d(P).

*Proof.* Embed P. Let the components with at least three vertices be
P_1..P_r, with N_j vertices and e_j edges, embedded separately; let k1 and
k2 count isolated vertices and single-edge components. For a connected
plane graph with N_j>=3 vertices the facial walks have length >=3 and
sum_f(len f-3)=2e_j-3F_j=3N_j-6-e_j=:d_j by Euler (F_j=e_j-N_j+2).

(i) Inside P_j with N_j>=4: if uv lies on two triangular faces uvx and uvy
then x≠y (if x=y the triangle uvx bounds both of its sides, so by the
Jordan curve theorem P_j is that triangle, contradicting N_j>=4), so uv has
two common neighbours. Hence a thin edge has at least 2-c(uv) incidences
with faces of length >=4 (an edge bounding the same face twice is a bridge
and counts twice; that face has length >=4 because a walk of length 3 cannot
traverse an edge twice). A face of length l>=4 offers l<=4(l-3) incidences,
so thin weight in P_j is <=4 d_j.
(ii) If N_j=3, P_j is a path (d_j=1, thin weight 2+2=4<=4d_j) or a triangle
(d_j=0, thin weight 3).
(iii) A single-edge component contributes thin weight 2.

Globally d(P)=sum_j d_j+6(r-1)+3k1+5k2 when r>=1 and d(P)=3k1+5k2-6 when
r=0 (direct count). Let t be the number of triangle components. If r=0:
thin weight 2k2 and N=k1+2k2>=4 give 2k2<=4(3k1+5k2-6). If r>=1, thin weight
<=4 sum d_j + 3t + 2k2, and 4(6(r-1)+3k1+5k2) covers 3t+2k2 unless r=t=1 and
k1=k2=0, i.e. P is a triangle and N=3, excluded. ∎

The bound is attained: a quadrilateral face with its four sides thin
(e.g. C4 inside a larger triangulated region) uses exactly 4 incidences per
unit of deficit. The constant 4 cannot be improved in general.

## Corollary 3 (biplanar codegree budget)

If G is biplanar on N>=4 vertices then, with c_G(uv) the number of common
neighbours in G,

    sum_{uv: c_G(uv)<=1} (2-c_G(uv))  <=  4 D(G).

*Proof.* Each edge lies in one layer; its common neighbours inside that
layer are among those in G, so a G-thin edge is thin in its layer with at
least the same weight. Add Lemma 2 for both layers. ∎

At D=0 this is S002's bridge obstruction (no edge of codegree <=1),
reconstructed from SRC-0007 §3.3. It is a strict generalization: it gives
a quantitative trade between Euler slack and low-codegree edges. Novelty is
NOT claimed: Patil's audit (SRC-0007 §3.3b) uses "facial-incidence" and
"edge-codegree" obstructions of the same kind; we have not seen their exact
statement, so the overlap is likely and is recorded as such.

## Application to the apex lane (fixed public corpus)

For apex(H), D=5|H|-6-e(H), and an H-edge with no common neighbour in H
has exactly one (the apex) in apex(H). Apex edges at in-H-degree >=2 vertices
are never thin. So Corollary 3 requires

    c0(H) := #{uv in E(H): N_H(u)∩N_H(v)=∅}  <=  4(5|H|-6-e(H)).

Applied to the 159 graph files of SRC-0007's public pool (commit 5cb2ca9f,
files without the `_layer` suffix): 147 have e(H)>5|H|-6, so their apex
violates Euler; 12 meet the budget. Eight of these (21v/99e Hajós-type,
44_21v_99e and 77_21v_99e_c3..c9) have D=0 and one codegree-0 edge, so
Corollary 3 excludes them (this is the known saturated cone). Four survive
the lemma: 19_12v_57e_w2 (13v/57e, D=2, c0=1), 49_12v_53e_subdivface
(12v/53e, D=1, c0=0), 79_dh_7_8_31v_148e and
79_doubleHajos_single_31v_148e (31v/148e, D=1, c0=2). Their apices are
CAM-0003 targets; see validation/S003_MANIFEST.json for outcomes.

Scope: the corpus' chromatic numbers are SOURCE_STATED; whether these
graphs are 9-critical is not used by the lemma.

## Hajós apex towers: what the lemma does and does not do

The tower level k (iterated Hajós sums over Hajós(Sulanke,Sulanke) plus a
universal apex; SRC-0007 §3.3b) has 10k+12 vertices, 59k+61 edges, so D=k-1,
and (at least) k bridge edges whose only common neighbour is the apex. The
lemma needs k<=4(k-1), which fails only at k=1. So Corollary 3 alone kills
only level 1; SRC-0007 reports a sharper "four units of deficit per
exceptional edge" argument for level 2 which we have not reconstructed.
No claim is made about levels >=2.

## Lemma 4 (rim lemma) and what it leaves open

Let layer i of a biplanar apex(H) on N=|H|+1>=4 vertices have deficit d_i
and let a have degree s_i=|S_i|>=2 in it. If the face at an angle of a
between rotation-consecutive neighbours u,v is a triangle, then uv∈E_i.
A facial walk of length l visits a at most l/2 times (consecutive visits
are at least two steps apart in a simple graph), and l/2<=2(l-3) for l>=4,
so at most 2d_i angles at a lie in non-triangular faces. Hence S_i is
covered by at most max(2d_i,1) vertex-disjoint paths of H_i, each running
through rotation-consecutive neighbours of a; if d_i=0 the layer is a
triangulation and the rotation at a is a Hamiltonian cycle of H_i[S_i]
(|S_i|>=3). Consequently V(H) is covered by at most 2D+2 vertex-disjoint
paths of H. ∎

This is a genuine structural property of non-saturated cones, but for
dense 9-critical H it is weak: we found no 9-chromatic H for which it
decides biplanarity. It is recorded as an available pruning rule, not as
an exclusion theorem.

## The surviving obligation on this lane

A 10-chromatic biplanar cone exists iff some 9-chromatic H (necessarily
biplanar, K8-free, e(H)<=5|H|-6) admits two complementary face covers.
Nothing proved here or in the cited literature excludes this for |H|>=17;
SRC-0007 reports the {1,9} lane open beyond its finite windows.

## Observation 9 (outerplanar reductions to EMP) — PROGRAMME_PROVED

(a) If G=P∪O with P planar and O outerplanar on the same vertex set, then
apex(G) is biplanar (layers P and O+a; O+a is planar because O has an
embedding with every vertex on one face). Hence chi(G)>=9 implies chi_2>=10.

(b) If G=O1∪O2 with both outerplanar, then K2∨G is biplanar: put apex a1 in
layer 1 with O1, apex a2 in layer 2 with O2, and the edge a1a2 in either
layer. Hence chi(G)>=8 implies chi_2>=10.

Degeneracy caps: such G have at most 5n-9 (resp. 4n-6) edges, so chi(G)<=10
(resp. <=8): question (b) asks whether the degeneracy bound for doubly
outerplanar graphs is attained. These reductions narrow the search space
(one layer of the target becomes outerplanar, i.e. determined by a cyclic
order plus a polygon triangulation) but no candidate was searched in S003.
Novelty: not claimed (SRC-0003 studies singly/doubly outerplanar
thickness-two graphs; its content is not accessible to us).
