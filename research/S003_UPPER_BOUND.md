# S003 — the 11-colouring route through criticality

Outcome: no universal improvement of 12. This dossier records (1) a
correction of the S002 record against prior art, (2) one new structural
lemma about critical counterexamples, (3) the exact point where every
reduction attempt failed, with the adversarial reason.

## 1. Correction: S002's n>=78+11D is superseded by prior work

SRC-0007 (Patil, 26 Aug 2026), Observation 7.1.1, already proves that a
12-chromatic biplanar graph has at least 89 vertices: a 12-critical
subgraph is K10-free, hence not a 12-Ore graph, so the Kostochka–Yancey
Brooks-type refinement e>=((k+1)(k-2)n-y_k)/(2(k-1)) with y_12=86 applies,
and 22(6n-12)>=130n-86 forces n>=89. With the deficit D=6n-12-e the same
arithmetic gives n>=89+11D. S002's CLM-0011 (n>=78+11D, from the plain KY
bound) is correct but strictly weaker and was published in this repository
without citing that observation; S002's prior-art audit missed it. We do
not independently inspect the Brooks-type paper (arXiv:1408.0846); the
stronger bound is recorded SOURCE_STATED (CLM-0024) and CLM-0011 is
annotated, not deleted.

## 2. Lemma 6 (double-wheel vertices) — PROGRAMME_PROVED

Call v a *wheel vertex* of a plane graph P if v lies in a component with at
least four vertices, has degree >=3, and every face angle at v lies in a
triangular face; then the neighbours of v form a cycle (its link) in the
rotation order. For a planar graph P on N>=4 vertices, at most 4d(P)
vertices are not wheel vertices.

*Proof.* Use the component bookkeeping of Lemma 2 (S003_FACE_DEFICIT.md).
In a component with N_j>=4, a vertex that is not a wheel vertex has an angle
in a face of length >=4 (a degree-<=2 vertex whose angles are all
triangular would make the component a triangle; a cut vertex appears twice
on some facial walk, which then has length >=6). Faces of length l>=4 carry
at most l<=4(l-3) vertex occurrences, so such vertices number <=4d_j.
Vertices of components with <=3 vertices are paid for by the terms
6(r-1)+3k1+5k2 exactly as in Lemma 2 (3 vertices of a triangle component
against 6 or against 12k1+20k2; 2 vertices of an edge component against 5;
an isolated vertex against 3). ∎

**Corollary 7.** In a biplanar graph G on N>=4 vertices with deficit D, at
least N-4D vertices are wheel vertices in both layers ("double-wheel"):
N(v)=N_1(v)⊔N_2(v), each N_i(v) carries a cycle of layer i of length
d_i(v)>=3.

**Corollary 8.** Let G be 12-critical and biplanar with deficit D<=11. Then
at least 24-2D vertices of degree 11 are double-wheel vertices, with
(d_1,d_2) ∈ {(3,8),(4,7),(5,6)} up to order.
(*Proof.* |L|>=24+2D degree-11 vertices (CLM-0014) minus at most 4D
non-double-wheel vertices.)

Use and limits: this converts the large low-vertex set into vertices with
rigid two-layer local structure. It does not make them reducible; see §3.
Novelty unchecked (it is a routine facial count; SRC-0007's "double Euler
identity" uses the same accounting).

## 3. Reduction attempts and why each fails

(a) *Two adjacent degree-11 vertices.* Not reducible by criticality alone:
the low-vertex subgraph of a k-critical graph is a Gallai forest (blocks
are cliques or odd cycles), and K2 blocks are allowed. Biplanarity only
caps clique blocks at K8.

(b) *Kempe extension at a double-wheel vertex v.* G-v has an 11-colouring
in which the 11 neighbours are rainbow; failure to extend forces every pair
of neighbours to be joined by a two-coloured path. In the plane case the
link cycle C_1 of layer 1 separates, so two chains between interleaved
pairs of C_1 must cross. Here a chain between x,y∈N_1(v) may leave layer 1
and re-enter: layer-2 edges are drawn in a different sphere and do not
respect C_1. Adversarial check (computed on the stored S002 certificate
validation/degree11_witness.json): all 24 degree-11 vertices of that
42-vertex union are double-wheel vertices with (d_1,d_2)∈{(5,6),(6,5)}; for
17 of them some layer-2 edge joins two vertices of the layer-1 link that
are not consecutive on it, and every one of them has between 1 and 12 edges
joining N_1(v) to N_2(v). These are precisely the connections a planar
separation argument would have to exclude, and they occur in an honest
biplanar graph. (That graph is 7-colourable, so it shows only that the
configuration is realizable, not that it is irreducible.)

(c) *Density.* The KY Brooks-type slope 65/11 is below Euler's 6; any
clique-restricted strengthening at k=12 (Postle's conjecture, or
Kelly–Postle with epsilon>2/3) would finish, as isolated in SRC-0007 §7.2.
We found no route to such a strengthening.

(d) *Deficit arithmetic.* n>=89+11D bounds nothing above; Corollary 8
needs D<=11 and becomes vacuous for large deficits, where critical
counterexamples could have many non-triangular faces.

## 4. Surviving proof obligation (stated exactly)

Show that a degree-11 double-wheel vertex (or a bounded configuration of
them) is reducible for 11-colouring in every biplanar graph, i.e. find a
two-layer Kempe-compatibility statement that survives layer-switching
chains; and separately control the large-deficit regime D>=12. Either part
alone does not give chi_2<=11.
