# S047 preregistered plan — contradiction-route feasibility (D079)

Registered before any experiment. Machine-readable copy:
validation/S047/REGISTRATION.json. Runtime root artifacts/tmp/S047
(git-ignored); permanent evidence under validation/S047.

Hypothesis to refute: H = "every finite biplanar graph is 9-colourable".
By the de Bruijn-Erdos theorem H is equivalent to its infinite version, and
refuting H is equivalent to the existence of a finite biplanar graph with
chi >= 10. A contradiction proof may avoid exhibiting or machine-checking the
witness; it cannot avoid its existence.

## Q1 Logic (written analysis, no computation)

Classify templates: (i) argument-certified explicit constructions
(Mycielski-type colour transfer, colour-forcing gadgets), which are
constructive in disguise; (ii) disjunctive constructions ("one of finitely
many explicit graphs is a witness"); (iii) genuinely non-constructive routes
(counting/alpha, fractional LP duality, probabilistic, topological).

## Q2 Prior art

Searches registered: Mycielski-type operations and planar/thickness classes;
generalised Mycielskians; Kostochka-Yancey edge bound; Gallai join theorem;
topological lower bounds (zig-zag theorem); thickness-two colouring
2008-2026; earth-moon lower bound recent work. SRC/CLM with honest grades.

## Q3 Obstructions (proofs plus mechanical checks, verification cost)

- O1: no operation that maps biplanar graphs to biplanar graphs can satisfy
  chi(Phi(G)) >= chi(G) + 1 for every biplanar G.
- O2: density window for 10-critical biplanar graphs from the
  Kostochka-Yancey bound and Euler: 88n - 70 <= 18m <= 108n - 216.
- O3: for every graph G with chi(G) >= 9 and every r >= 1, the generalised
  Mycielskian M_r(G) (r+1 levels plus apex; M_1 = classical Mycielskian) is
  not biplanar. The cone raises chi by one; its biplanarity is the S041/S042
  apex route (cited, not redone).
- Mechanical check: scripts/s047_checks.py verifies the integer
  inequalities for all n in the stated range and symbolic identities.

## E1 Control (verification cost)

K6 v C5 with the archived S046 layers (validation/S046/calibration/runs/
k8-n11-C/ALERT.json): both layers planar (NetworkX LR plus the archived
rotation systems re-checked), union is exactly K6 v C5, explicit 9-colouring,
drat-trim-verified non-8-colourability.

## E2 Seeded one-step extension ladder (experimental)

Template test: any Mycielski-type or gadget operation Phi with Phi(G) ⊇ G
applied to the canonical seed S = K6 v C5 (A = K6, B = C5) produces a
supergraph. Question E2(t): does a biplanar graph G' with chi(G') >= 10 exist
with V(G') = V(S) ∪ X, |X| = t, G'[V(S)] ⊇ S?

Reduction (proved in RESEARCH before use): (a) G'[V(S)] = S, since any chord
of B creates a triangle in B and A + triangle = K9 (non-biplanar, CLM-0022);
(b) every proper 9-colouring of S gives A six distinct colours and B the other
three, with B partitioned {2,2,1} by one of five partitions; so G' is
9-colourable iff for some partition P and placement phi: X -> 9 colour
classes no conflict occurs. E2(t) SAT encoding: variables for the 11t
seed-to-X adjacencies and C(t,2) X-internal edges; one clause per (P, phi)
listing the adjacency literals that would make phi conflict (5 * 9^t
clauses). Necessary biplanarity conditions added (each a theorem used as a
filter only): for every X' ⊆ X, |E(G'[A ∪ B ∪ X'])| <= 6(11 + |X'|) - 12 and
|E(G'[A ∪ X'])| <= 6(6 + |X'|) - 12 (cardinality networks); no K9 subgraph
(CLM-0022); no K6,9 / K5,13 / K7,7 complete bipartite subgraph is NOT added
(kept as a post-filter only). UNSAT with a drat-trim-verified DRAT proof
certifies: no biplanar non-9-colourable supergraph of K6 v C5 with exactly t
added vertices, hence none with at most t (an isolated added vertex
preserves biplanarity and chi, so E2(t') true implies E2(t) true for t' < t;
each t is still run independently as a control). A SAT model
is a candidate only; its biplanarity is then decided separately and reported
UNKNOWN until certified.

Ladder t = 1, 2, 3, 4, 5, 6 in order; per-t solver cap 300 s wall; stop the
ladder at the first capped t (later t reported NOT_RUN). Controls (run before
t >= 2, verification cost): (C1) encoder without biplanarity filters at t = 1
has exactly one model, x adjacent to all 11 seed vertices (hand lemma);
(C2) k = 8 calibration with seed K5 v C5 and 8 colours at t = 1 must be SAT
with the model x complete to the seed, whose result is K6 v C5 (biplanar);
(C3) brute-force cross-check of C1 by enumerating all 2^11 neighbourhoods
with an independent colouring routine.

## Gate (registered)

PROGRESS only if S047 yields a witness/candidate, or a template survives with
positive evidence (a calibrated transfer operation reproducing a known
k = 8 result and a non-refuted k = 9 instance or concrete finite next step
whose success would refute H). Negative theorems alone (exclusions of
templates) narrow the route but are PIVOT. On PIVOT, recommend one of:
PAUSE, or a named alternative with a stated reason.

## Budget and resources

Experimental ceiling 1800 CPU s / 3600 wall s, E2 allocation 1500 CPU s /
2400 wall s; absolute experimental deadline registration + 4 h. Smoke,
controls, DRAT checks, symbolic checks and closeout replays are verification
costs, recorded separately. One heavy solver at a time; 3 GiB memory cap;
10 GiB disk reserve. No unattended run or automation.

## Amendment A1 (post-hoc, registered after E2 stopped, before any A1 run)

E2 gave drat-trim-verified UNSAT at t = 1..4 and CAPPED_UNKNOWN at t = 5
(300 s, no symmetry breaking); t = 6 NOT_RUN by the registered rule. E2's
rows stand unchanged. A1 asks the same question with two sound restrictions
proved in RESEARCH (L3: in a solution with minimum |X| every added vertex has
degree >= 9; L4: all constraints are invariant under permuting X, so the
seed-adjacency rows of X may be taken lexicographically non-increasing) and
lazy colour clauses (CEGAR, tools/s047_cegar.py): each learned clause is the
E2 clause of the (P, phi) read off an independent 9-colouring of the current
candidate, so the final formula is implied by the full one. UNSAT of A1(t')
for every t' <= T (with E2 for t' <= 4) certifies that no biplanar
non-9-colourable graph contains K6 v C5 with at most T added vertices.
Ladder t = 5..12, per-t wall cap 240 s, stop at the first capped t; final
formula of every UNSAT row re-solved by native CaDiCaL with DRAT and checked
by drat-trim. A model that survives colouring is a candidate, biplanarity
UNKNOWN until decided. Controls (verification): A1 at t = 2, 3, 4 must be
UNSAT; with biplanarity filters removed, A1 at t = 1 must yield K7 v C5.
A1 allocation: at most 1100 CPU s / 2000 wall s, inside the remaining E2
allocation. Gate unchanged.
