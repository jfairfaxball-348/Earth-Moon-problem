# S046 research: diagnosis, reductions, matched pilots

Target unchanged (D042): one certified finite simple biplanar graph with
chi >= 10. Registration: sessions/S046/PLAN.md and
validation/S046/REGISTRATION.json (written before any experiment).

## 1. Reduction to critical cores (CLM-0147, PROGRAMME_PROVED)

Lemma R1. If G is biplanar with layers E1, E2 and chi(G) >= 10, then G has
a 10-critical subgraph H (chi(H) = 10, every proper subgraph 9-colourable), and
H is biplanar with layers E1 ∩ E(H), E2 ∩ E(H).

Proof. Choose a subgraph H of G with chi(H) >= 10 minimising |V(H)| + |E(H)|.
Every proper subgraph is 9-colourable. H has an edge e; a 9-colouring of H - e
plus one new colour on an endpoint of e colours H, so chi(H) = 10. A subgraph of
a planar graph is planar, so the restricted layers are planar. QED.

Lemma R2 (classical). A 10-critical graph H satisfies:
(a) minimum degree >= 9: if deg(v) <= 8, a 9-colouring of H - v extends to v;
(b) H is connected: otherwise one component already has chi >= 10;
(c) H has no cut vertex: if H = H1 ∪ H2 with V(H1) ∩ V(H2) = {v}, both Hi are
proper subgraphs, 9-colour each, permute the colours of H2 so v agrees, and
the union is a proper 9-colouring;
(d) H is K9-free when biplanar, because K9 is not biplanar (SRC-0014) and
biplanarity is subgraph-closed; H is not K10, so n >= 11;
(e) 9n/2 <= |E(H)| <= 6n - 12 (each planar layer has at most 3n - 6 edges).
Kostochka–Yancey (SRC-0011, STATEMENT_INSPECTED) gives the stronger lower
bound |E(H)| >= (88n - 70)/18 for 10-critical H other than K10; it is
recorded as a necessary condition and NOT encoded in S046.

Consequences for search domains.
- Arm C at order n searches labelled layer pairs on exactly n vertices whose
  union has minimum degree >= 9. By R1/R2(a) it contains a labelling of every
  10-critical biplanar graph of order exactly n. It is not an "order at most n"
  domain: a smaller witness padded with isolated vertices violates the degree
  rule. A complete certified exclusion of arm C at order n would exclude only
  10-critical biplanar graphs of order exactly n; every other order stays open.
- Arm B at order N (the S045 domain) contains padded copies of all smaller
  witnesses but no restriction toward cores.
- Colouring-partition clauses (CLM-0146) exclude only graphs properly coloured
  by the given 9-colouring; Kuratowski clauses exclude only assignments with a
  nonplanar layer. Neither ever removes a non-9-colourable biplanar candidate.
- R2(b)(c), K9-freeness and the edge bounds are necessary conditions not
  encoded as constraints (K9 is excluded implicitly by planarity). Any
  non-9-colourable candidate is a witness whether or not it is critical, so
  criticality need not be certified to claim a lower bound; it is not claimed.

## 2. Symmetry rules of arm CS (CLM-0148, PROGRAMME_PROVED)

Let D be a set of layer assignments on vertex set {0..n-1} closed under vertex
relabelling and under swapping the two layers (for example: both layers planar,
union minimum degree >= 9, union not 9-colourable). Write A for the union
adjacency matrix and t(A) for the concatenation of its full rows A[0] A[1] ...

Lemma S. If D is nonempty it contains an assignment with
(i) for all i < j, A[i] >=lex A[j] when both rows are read over the columns
    c not in {i, j} in increasing order; and
(ii) the first present union pair, in lexicographic pair order, lies in layer 1.

Proof. Take X in D and a relabelling maximising t(A) lexicographically; call
the result B (still in D). Suppose (i) fails for i < j: at the first column
k not in {i,j} where the rows differ, B[i][k] = 0 and B[j][k] = 1, with equality
on earlier such columns. Let B' be B with labels i and j exchanged.
Case k < i: rows r < k are unchanged because B[r][i] = B[i][r] = B[j][r] = B[r][j];
in row k only positions i and j change, and B'[k][i] = B[j][k] = 1 > 0 = B[k][i],
so t(B') > t(B).
Case k > i: rows r < i are unchanged by the same equalities (r < i < k). Row i of
B' is B[j] read with positions i and j fixed to B[i][i] = 0 and B[i][j]; it
agrees with B[i] before column k and has 1 > 0 at column k, so t(B') > t(B).
Both contradict maximality, so B satisfies (i). Rule (i) depends only on the
union. If the first present union pair of B lies in layer 2, swap the layers:
the union, hence (i) and membership in D, is unchanged and (ii) now holds. QED.

These rules remove equivalent labellings; they never require a nontrivial
automorphism or a symmetric graph. Because partition and Kuratowski clauses
never remove a member of D, the CS search is a sound search of the C domain.
This is the lex-leader idea of Codish et al. (SRC-0072, attribution only);
the proof above is self-contained. Multiple layer decompositions of one union
are handled by partition feedback: one colouring clause excludes every split
of every union it colours.

Encodings (tools/s046_encode.py): an exact two-sided sequential counter for
"at least 9 of the 2(n-1) incident layer literals" (at most one per pair by
disjointness), union variables u = x1 OR x2, a standard prefix-equality lex
encoding, and a prefix chain for rule (ii). Controls
(validation/S046/CONTROLS.json, verification cost 34 s): the counter against
all assignments for L <= 8 and every threshold (4606 cases); the full CS CNF
against an independent predicate on all 729 assignments at n = 4 (thresholds 0
and 2) and all 59049 at n = 5 (threshold 2); soundness of rules (i)+(ii) on all
36 (n=4) and 247 (n=5, degree >= 2) classes under relabelling x layer swap;
rule (i) alone on all 1024 graphs on 5 and 32768 graphs on 6 vertices.

Native end-to-end controls with known answers, each found graph checked for
planar layers and its non-k-colourability DRAT-verified by the pinned
drat-trim: K4 at (n=4, k=3) in arms C and CS; K5 at (n=5, k=4, CS); K6 at
(n=6, k=3, B); the infeasible (n=4, k=4, C) returned native UNSAT and the
degree CNF alone has a verified DRAT refutation. Positive control at the
classical boundary: (n=11, k=8, CS) found after 51 feedback candidates and
5.1 s a non-8-colourable biplanar graph which is exactly K6 v C5 (Sulanke's
9-chromatic graph), non-8-colourability DRAT-verified. These are controls of
the encodings and protocol only, not Earth–Moon results.

## 3. Diagnosis of the saved S045 candidates (E1; CLM-0149, COMPUTED_EXACT)

validation/S046/diagnostics/E1.json; certificates E1_CERTS.json.gz. All 60
archives matched validation/S045/final/ARCHIVE_INDEX.json byte hashes; the
pass counted exactly 642381 records. Experimental cost 69.9 CPU s (two
executions, see ADVERSARIAL.md).

Full census (every saved record):
- 640299 of 642381 records (99.676%) have an EMPTY 9-core, hence are
  8-degenerate and explicitly 9-colourable by smallest-last greedy; only 2082
  have a nonempty 9-core (maximum order 48).
- No record has minimum degree 9 or more (maximum observed minimum degree 8;
  median 6). No isolated vertices. Union edges: median 285 of the planar-pair
  maximum 288; mean 277.1. Layer sizes median 143/143 of 144.
- Exact labelled duplicates: 0 union graphs, 0 layer assignments (as expected:
  each partition clause excludes every split of the coloured union).

Stratified sample (100 per early/middle/late stratum, seed 46046): every one
of the 300 records is explicitly coloured with at most 8 colours by greedy or
DSATUR (best counts early 5:7 6:13 7:56 8:24; middle 6:9 7:79 8:12; late
6:14 7:52 8:34); no SAT call was needed and no checked non-8-colourability
proof exists. Clique numbers 5–8 (a K8 in 55 records); degeneracy 5–8; every
sampled union is connected with no cut vertex; 300 distinct isomorphism
classes (no redundancy detectable at this sample size). Oracle re-timing:
mean 3 ms per record.

Timing decomposition from the archived slice receipts
(validation/S046/diagnostics/S045_TIMING.json): over the 52 memory-recycle
slices, 38089 s wall split into 2022 s native loading, 8282 s solving
(including the oracle) and 27784 s preparation plus post-slice audit (78%);
in the last eight slices 86% of wall time was preparation/audit and they added
1126 records. The receipts do not separate preparation from audit.

Registered classification: MAINLY EASY (yes), mainly redundant (no), plausible
cores (no). S045 visited near-maximal-density layer pairs whose unions are
8-degenerate; it never visited a graph that could itself be 10-critical. This
describes saved records only, not the domain or any internal solver state.

## 4. Matched pilots (E2/E3; CLM-0150, COMPUTED_EXACT for the stated runs)

validation/S046/pilots/{E2,E3}.json, E3_CERTS.json.gz, runs/*. Each arm: one
60 s native solve clock, k=9, fresh state, identical driver and oracle.

| n | arm | instance clauses | validated | per s | geometric cuts | native CPU s | peak MiB | analysed | best colours (count) | omega (count) | min deg | empty 9-core | checked non-8 | T |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|
| 24 | B | 276 | 4453 | 74.2 | 15969 | 6 | 533 | 30 | 6:3 7:23 8:4 | 6:23 7:5 8:2 | 6-7 | 30 | 0 | fail |
| 24 | C | 35268 | 377 | 6.3 | 448317 | 56 | 692 | 30 | 6:9 7:21 | 5:11 6:19 | 9 | 0 | 0 | fail |
| 24 | CS | 54311 | 22 | 0.4 | 371665 | 59 | 637 | 22 | 6:8 7:14 | 6:22 | 9 | 0 | 0 | fail |
| 28 | B | 378 | 4129 | 68.8 | 10609 | 6 | 534 | 30 | 6:1 7:27 8:2 | 6:14 7:16 | 5-6 | 30 | 0 | fail |
| 28 | C | 49042 | 132 | 2.2 | 350416 | 58 | 654 | 30 | 6:8 7:22 | 5:12 6:18 | 9 | 0 | 0 | fail |
| 28 | CS | 79659 | 14 | 0.2 | 344690 | 59 | 637 | 14 | 6:13 7:1 | 5:14 | 9 | 0 | 0 | fail |
| 32 | B | 496 | 3891 | 64.8 | 16525 | 7 | 540 | 30 | 6:1 7:12 8:17 | 5:1 6:9 7:3 8:17 | 5-7 | 30 | 0 | fail |
| 32 | C | 65072 | 32 | 0.5 | 424890 | 59 | 702 | 30 | 6:10 7:18 8:2 | 5:17 6:13 | 9 | 0 | 0 | fail |
| 32 | CS | 111199 | 11 | 0.2 | 317446 | 60 | 657 | 11 | 6:4 7:7 | 5:11 | 9 | 0 | 0 | fail |
| 40 | B | 780 | 3202 | 53.4 | 29973 | 10 | 549 | 30 | 6:2 7:19 8:9 | 5:15 6:6 7:1 8:8 | 6-7 | 30 | 0 | fail |
| 40 | C | 103900 | 9 | 0.1 | 417901 | 60 | 723 | 9 | 6:1 7:8 | 5:8 6:1 | 9 | 0 | 0 | fail |
| 40 | CS | 195159 | 0 | 0.0 | 146840 | 60 | 613 | 0 | - | - | - | 0 | 0 | fail |
| 50 | B | 1225 | 3208 | 53.4 | 37631 | 13 | 560 | 30 | 6:3 7:18 8:9 | 5:3 6:23 7:1 8:3 | 6-7 | 30 | 0 | fail |
| 50 | C | 165125 | 4 | 0.1 | 516712 | 60 | 799 | 4 | 6:1 7:3 | 5:4 | 9 | 0 | 0 | fail |
| 50 | CS | 345199 | 0 | 0.0 | 133158 | 60 | 654 | 0 | - | - | - | 0 | 0 | fail |

All 300 analysed candidates carry an explicit checked colouring with at most
8 colours (E3_CERTS); none needed SAT, so p9 = 0 in every arm, with Wilson 95%
upper bounds 0.11 (30 analysed) to 0.49 (4 analysed). T fails everywhere;
T1 also fails for every CS arm and for C at n=40, 50. No labelled duplicate
union occurred; every analysed set had all-distinct isomorphism classes.

Reading. The core filter does what it claims structurally (minimum degree 9,
nonempty 9-core) but the resulting graphs have smaller cliques (omega 5–6)
and are still 6–7-colourable. Candidate throughput collapses with n (C: 377
at n=24 to 4 at n=50) as Kuratowski CEGAR dominates (hundreds of thousands of
cuts). Static lex-leader breaking slowed every order and produced nothing at
n=40, 50 in 60 s; it is a sound reduction but not a measured improvement.
Single 60 s runs per arm, one deterministic configuration each and small
analysed samples: the comparison is coarse and the zero rates are bounded only
by the stated intervals. No hard colouring instance occurred, so "hardness"
played no role in any conclusion.

## 5. Amendment A1: k=8 positive-control calibration (CLM-0151, COMPUTED_EXACT)

Registered after E3 (validation/S046/AMENDMENT_A1.json); it does not change
the decision. Same driver with k=8 (seek non-8-colourable biplanar graphs),
40 s solve clock, stop at first alert. validation/S046/calibration/A1.json.

| arm | n | outcome | candidates before hit / in cap | seconds |
|---|---:|---|---:|---:|
| C | 11 | hit: K6 v C5, chi=9 | 914 | 11.3 |
| B | 11 | hit: K6 v C5, chi=9 | 88 | 1.1 |
| C | 13 | none in cap | 3044 | 40 |
| C | 15 | none in cap | 3033 | 40 |
| C | 17 | none in cap | 2520 | 40 |
| C | 20 | none in cap | 2612 | 40 |
| C | 24 | none in cap | 2335 | 40 |
| B | 15 | none in cap | 3415 | 40 |
| B | 20 | none in cap | 3177 | 40 |
| CS | 15 | none in cap | 349 | 40 |
| CS | 20 | none in cap | 28 | 40 |

Both hits are exactly Sulanke's K6 v C5 (six universal vertices of degree 10,
the other five inducing C5); planar layers checked, non-8-colourability
drat-trim VERIFIED (validation/S046/certificates/k8-n11-*), and a checked
9-colouring gives chi=9. In arm B at n=15 and n=20 the padded K6 v C5 lies in
the domain, so the generator demonstrably missed a known boundary object
within the cap; for arm C at 13 and 15, 9-critical thickness-two graphs on
12–16 vertices are source-stated (SRC-0002), not re-verified here. "None in
cap" is UNKNOWN for existence; it measures this generator's sensitivity only.

## 6. Decision and next hypothesis

Registered decision: PIVOT / INCONCLUSIVE. No arm passed the targeting
criterion; E4 (operational acceptance and checkpoint repair) was conditional
and NOT RUN; no domain or design is selected for sustained search. The S045
checkpoint redesign is not needed for any selected design and was not built;
an unexecuted draft was discarded. S045's 50-vertex domain is not supported
as a target: its saved records are 99.7% 8-degenerate.

Evidence-based reading: unguided colouring-partition generation (S045 and the
S046 B/C/CS variants) explores overwhelmingly easy graphs; core filtering and
static symmetry breaking do not move it toward the 9-chromatic boundary, and
on the known-feasible k=8 analogue its sensitivity disappears beyond n=11.
Long runs of this mechanism at any registered order are not justified by the
evidence. This is a statement about the mechanism, not about whether a
witness exists at any order.

Next distinct hypothesis (S047, FUTURE/UNEXECUTED): a construction mechanism
must first pass a k=8 calibration ladder (rediscover certified 9-chromatic
biplanar graphs at orders >= 13 within a registered cap, where the S046
generator found none) before any k=9 computation. The mechanism proposed for
test is seeded generation: pin a certified biplanar seed (for k=8: K8, which
K6 v C5 contains; for k=9: K8 or K6 v C5) and search its biplanar supergraphs
with the same checked colouring feedback, against one co-certificate
amplification arm and the S046 baseline. If neither beats the A1 baseline,
the recommendation is to PAUSE construction search (reaffirming S044).
