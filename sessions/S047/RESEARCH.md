# S047 research — contradiction-route feasibility (D079)

Notation: a graph is biplanar if its edge set splits into two planar graphs on
the same vertex set. H = "every finite biplanar graph is 9-colourable". The
seed S = K6 v C5: A = {a1..a6} a clique, B = b0..b4 a 5-cycle, A complete to
B; n = 11, m = 50, chi(S) = 9, biplanar (E1 re-certifies this). Kostochka-
Yancey (KY, SRC-0011/SRC-0020): a k-critical graph on n vertices (k >= 4,
n >= k, n != k+1) has at least ceil(((k+1)(k-2)n - k(k-3)) / (2(k-1))) edges.
Euler: a biplanar graph on n >= 3 vertices has at most 6n - 12 edges.

## Q1 What a contradiction proof must do

1. Compactness. By de Bruijn-Erdos, H fails iff some finite biplanar graph
   has chi >= 10. Every refutation of H therefore proves that a finite
   witness exists; "proof by contradiction" can only change how the witness
   is certified or whether it is named.
2. Three template classes.
   - (T1) Argument-certified explicit constructions: colour-transfer
     operations (Mycielski-type: "a 9-colouring of Phi(G) yields an
     8-colouring of G") and colour-forcing gadgets. These are constructive
     in disguise: the contradiction argument is a human-readable certificate
     that the explicit graph Phi(G) has no 9-colouring, replacing a DRAT
     proof. They need the same biplanarity certificate for Phi(G).
   - (T2) Disjunctive constructions: "one of the finitely many explicit
     graphs G_1..G_N is a witness", proved without deciding which. Each G_i
     must be biplanar for this to help; the disjunction only saves the
     chromatic certificate.
   - (T3) Genuinely non-constructive routes: counting (chi >= n/alpha),
     fractional chromatic number via LP duality, probabilistic models,
     topological lower bounds.
3. Consequence for this programme: every T1/T2 success yields an explicit
   finite graph that the existing certification rules (labelled layers,
   planarity checks, non-9-colourability) already accept; the D079 scope
   amendment matters only for T3.

## Q3 Obstructions (proved; mechanical checks in scripts/s047_checks.py)

O1 (no uniform transfer). Let Phi map biplanar graphs to biplanar graphs.
Then it is false that chi(Phi(G)) >= chi(G) + 1 for every biplanar G.
Proof: otherwise chi(Phi^4(S)) >= 13, contradicting Ringel's bound
chi_2 <= 12 (SRC catalogue, classical Euler argument). More precisely, if a
class C of biplanar graphs is closed under Phi and contains a graph of
chromatic number >= 9, no such inequality can hold on all of C. So a
colour-transfer proof for biplanar graphs must be one-shot: the hypothesis it
uses about G must fail for Phi(G) (or after at most three steps). Mycielski's
proof works because its hypothesis ("G is any graph") is preserved; no
analogue can be preserved here. []

O2 (density window). A 10-critical biplanar graph on n vertices has
ceil((88n - 70)/18) <= m <= 6n - 12, i.e. average degree between about
9.78 - 7.8/n and 12 - 24/n. KY with k = 10 gives (11*8*n - 70)/18; Euler
gives the upper bound. Any T1 operation must land in this window.
(S046 used the weaker min-degree bound 9n/2.) []

O3 (Mycielskians are never biplanar). For every graph G with chi(G) >= 9 and
every r >= 1, the generalised Mycielskian M_r(G) (vertex set V x {0..r} plus
apex z; edges (u,0)(v,0) and (u,i)(v,i+1) for uv in E, (v,r)z; M_1 is the
classical Mycielskian) is not biplanar.
Proof: G contains a 9-critical subgraph H on h >= 9 vertices with
e = e(H) >= (70h - 54)/16 (KY, k = 9). M_r(H) is a subgraph of M_r(G), with
(r+1)h + 1 vertices and (2r+1)e + h edges. Then
16[(2r+1)e + h - (6((r+1)h + 1) - 12)] >= 44rh - 10h - 108r + 42
= r(44h - 108) - 10h + 42 >= 34h - 66 > 0,
so M_r(H) violates Euler's bound; biplanarity is closed under subgraphs. []
Example: the Mycielskian of S has 23 vertices and 161 > 126 edges.
The cone (apex) raises chi by exactly one; its biplanarity is the S041/S042
apex route (97 leaf graphs certified non-biplanar), not redone here.

O4 (Schrijver graphs). The 10-chromatic Schrijver graphs SG(2k+8, k), the
vertex-critical subgraphs of the Kneser graphs whose chromatic number is
proved topologically, are not biplanar for k = 1 (K10 contains K9,
CLM-0022) and k = 2, 3 (54 vertices/999 edges and 210/10353, far above
6n - 12); for k >= 2 the degree grows with k. So the classical topological
lower-bound families are unusable directly. The zig-zag theorem
(Simonyi-Tardos) forces a multicoloured K5,5 in every proper colouring of a
topologically 10-chromatic graph; K5,5 is biplanar, so this gives no
obstruction either way. []

## Seeded one-step extensions of K6 v C5 (E2 and amendment A1)

Every Mycielski-type or gadget operation with Phi(G) ⊇ G, applied to the
canonical seed, produces a supergraph of S. E2(t) asks whether a biplanar G'
with chi(G') >= 10 exists on V(S) ∪ X, |X| = t, with G'[V(S)] ⊇ S.

L1 (colourings of S). In every proper 9-colouring of S, A receives six
distinct colours and B only the other three; C5 needs all three, so B is
split {b_s}, {b_{s+1}, b_{s+3}}, {b_{s+2}, b_{s+4}} for one of five s.
Hence G' is 9-colourable iff for some s and some placement of X into the nine
classes no added vertex is adjacent to its class and no two added vertices in
the same class are adjacent. (Also true for k colours and K_{k-3} v C5.) []

L2 (seed induced). A chord of B creates a triangle T in B, and A ∪ T = K9,
which is not biplanar (CLM-0022). So G'[V(S)] = S in any biplanar G'. []

L3 (minimal solutions have high degree). If a solution with |X| <= t exists,
take one with minimum |X| = t'. Each x in X has degree >= 9: otherwise G' - x
contains S, is biplanar, and has t' - 1 added vertices, so it is
9-colourable by minimality, and the colouring extends to x. []

L4 (symmetry). All constraints are invariant under permuting X, so the
seed-adjacency rows of X may be assumed lexicographically non-increasing. []

L5 (hand proof for t <= 5). In a minimal solution, all 50 seed edges are
present (L2), so m(G') = 50 + sum_x deg(x) - e(X) >= 50 + 9t' - e(X), while
m(G') <= 6(11 + t') - 12. Hence e(X) >= 3t' - 4, impossible inside C(t',2)
edges for 2 <= t' <= 5. For t' = 1, L1 forces x to be adjacent to all of A
(each a in A is a singleton class) and to a set meeting every class of every
partition, i.e. all of B (each b is the singleton for some s); then x, A and
an edge of B form K9. So no biplanar non-9-colourable graph contains K6 v C5
with at most five added vertices. []

Computation (registered E2, then post-hoc amendment A1):

| Run | t | n | clauses | result | solver s | proof |
|---|---:|---:|---:|---|---:|---|
| E2 eager | 1 | 12 | 51 | UNSAT_VERIFIED | 0.004 | validation/S047/e2_t1.drat.gz |
| E2 eager | 2 | 13 | 667 | UNSAT_VERIFIED | 0.003 | validation/S047/e2_t2.drat.gz |
| E2 eager | 3 | 14 | 5127 | UNSAT_VERIFIED | 0.026 | validation/S047/e2_t3.drat.gz |
| E2 eager | 4 | 15 | 38592 | UNSAT_VERIFIED | 2.776 | validation/S047/e2_t4.drat.gz |
| E2 eager | 5 | 16 | 314246 | CAPPED_UNKNOWN | 300.015 | - |
| A1 CEGAR | 5 | 16 | 19680 | UNSAT_VERIFIED | 0.518 | validation/S047/a1_t5.drat.gz |
| A1 CEGAR | 6 | 17 | learned 6189 | CAPPED_UNKNOWN | 240.143 | - |

E2 used 301.362 CPU s, A1 237.757 CPU s
(experimental). E2 stopped by rule after its t = 5 cap; A1 rows t = 7..12
NOT_RUN after its t = 6 cap. A1 controls (validation/S047/A1_CONTROLS.json):
t = 2, 3, 4 UNSAT with drat-trim-verified proofs and zero learned clauses
(counting alone, as L5 predicts); without filters t = 1 returns K7 v C5.
E2 controls (validation/S047/CONTROLS.json): C1 one model (x complete to
S), C2 k = 8 calibration recovers K6 v C5 from K5 v C5, C3 brute force over
all 2^11 neighbourhoods agrees.

Certified statement (CLM-0153): no biplanar graph with chi >= 10 contains
K6 v C5 together with at most five further vertices (n <= 16). Hand proof L5;
drat-trim-verified UNSAT for E2 t = 1..4 and A1 t = 5 as controls.
UNKNOWN: six or more added vertices (A1 t = 6 capped after 6189 lazily
learned colourings; every candidate it produced was 9-colourable).

Interpretation for the contradiction route. A one-shot colour-transfer
operation applied to K6 v C5 must add at least six vertices, and by O3 it is
not a (generalised) Mycielskian; by O1 its correctness proof cannot rest on
a property preserved by the operation. The A1 t = 6 behaviour (thousands of
distinct 9-colourable candidates, each killed by one colouring) shows that
the colouring structure of K6 v C5 leaves too much freedom for small sparse
extensions: L1 says an added vertex missing an A-neighbour can reuse that
A-colour unless an added neighbour already holds it, so forcing requires added vertices of degree close to the
full seed, which the Euler budget (at most 4 + 6t new edges) forbids. No
template survived with positive evidence.

## Gate

Registered rule: PROGRESS needs a witness/candidate or a surviving template
with calibrated positive evidence. Results are exclusions only (O1-O4,
CLM-0153) plus UNKNOWN rows. Decision: PIVOT. Recommendation: PAUSE
construction and contradiction-route work; re-enter only with a genuinely
new one-shot transfer idea meeting O1-O3 and the O2 window, a new seed
outside the K6 v C5 neighbourhood with a written forcing argument, or new
literature (S048 re-entry gate, FUTURE/UNEXECUTED).
