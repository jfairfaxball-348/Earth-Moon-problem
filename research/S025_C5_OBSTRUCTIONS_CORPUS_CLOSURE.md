# S025 — cross-layer K9-minor lemmas, the C5 blow-up threshold, and closure of the original 271 corpus

**Date:** 2026-10-16. **Scope:** D042 lower-bound programme only. Everything below is finite, checked mathematics about specific graphs or explicit hand lemmas. **No χ ≥ 10 biplanar witness exists in this session; 9 ≤ χ₂ ≤ 12 is unchanged.**

## 1. Summary of results

1. **Engines.**
   - Arm B's complete two-sphere-triangulation SAT encoding was implemented and validated (CLM-0089). It is too weak for exact refutations: K9 cover was UNKNOWN at 600 s.
   - Two new tools did the work instead:
     - a flip-annealing **positive oracle** over pairs of labelled sphere triangulations;
     - a **Kuratowski CEGAR strengthened with cross-layer K9-minor lemmas** (Lemma B, CLM-0090; Lemma C, CLM-0091).
2. **Row148 obstruction.** Annealing descent from row148 (best covering of all 131 edges is 4 short, against 6 in ten earlier sessions) found that the hardness lives in 17-vertex clique blow-ups of C5.
3. **C5 threshold (CLM-0092/0093).** Write C5[a₁,…,a₅] for the clique blow-up with all aᵢ ≥ 1.
   - All 262 dihedral classes with aᵢ + aᵢ₊₁ ≤ 8 and Σaᵢ ≤ 16 are biplanar, each with an explicit independently checked split.
   - Of the 26 classes with Σaᵢ = 17 that survive the counting filters, **18 are DRAT-certified non-biplanar**. Three more are CEGAR-UNSAT with DRAT not completed, and five runs are NOT_COMPLETED. All 26 had annealing defect 1 (heuristic).
   - Hence the conjectured classification, that C5[a] has thickness ≤ 2 **iff** aᵢ + aᵢ₊₁ ≤ 8 for all i and Σaᵢ ≤ 16, is proved except for those 8 classes.
4. **Corpus closure (CLM-0094).** Explicit, edge-by-edge-checked subgraph maps embed certified C5 obstructions into **every one of the 219 BIPLANARITY_UNKNOWN rows**, row148 included. The original 271 exactly-10-chromatic clique blow-up corpus is therefore **entirely non-biplanar**: 52 rows earlier, 219 now. This ends the D051/D054 priority queue with a complete negative decision. It is not a χ₂ statement.
5. **Arm A (chromatic pressure).** χ ≥ ⌈w(V)/α_w⌉ (weighted independence) was made the objective of the triangulation-pair annealer. Every corpus row has χ_f ∈ {28/3, 37/4}, so its χ ≥ 10 is a fractional certificate of exactly this kind. Exploratory frontier (heuristic only):
   - biplanar graphs with α ≤ 3 were found up to n = 24;
   - the minimum number of "bad" independent 4-sets rises 1, 4, 13, 35 for n = 25…28;
   - weighted variants with total weight 28 bottom out at ≥ 8 bad sets.

## 2. Arm B engine and why it was replaced

`tools/s025_tricover.py` encodes, for each layer i, pair variables x[i,ab] and triangle variables t[i,abc]:
- F1: a triangle implies its three edges;
- F2/F3: every selected pair lies in exactly two selected triangles;
- F4: exactly 3n−6 edges;
- F5: every vertex is covered;
- lazy LINK and CONN cuts.

**CLM-0089 (PROGRAMME_PROVED, elementary).** A model violating no cut is a sphere triangulation.
1. Each edge lies in two faces and each vertex link is one cycle, so the complex is a closed simplicial 2-manifold.
2. CONN makes it connected.
3. With E = 3n−6 and F = 2E/3, the Euler characteristic is V−E+F = 2. So the surface is a sphere, and its 1-skeleton is a planar triangulation.

Conversely, every sphere triangulation on n ≥ 4 vertices satisfies F1–F5 and every cut:
- LINK: the link of v is one cycle through a and u, so it leaves S;
- CONN: a triangulation spans and is connected.

So the encoding is complete. Unoriented triangles replace the S024 oriented-dart specification: orientability is automatic for a χ = 2 closed surface. An independent decoder (`tools/s025_check.py`) re-orients the faces, rebuilds rotations, traces every dart, checks Euler, and re-tests planarity with NetworkX.

Controls (all splits independently checked):

| Graph | Result | Time |
|---|---|---|
| K8 | SAT | 0.02 s |
| K9P3 | SAT | 0.1 s |
| J1 | SAT | 143 s |
| J2 | SAT | 81 s |
| K9 | UNKNOWN (466 iterations) | 600 s |
| chromatic mode, trivial n=10, k=9 | UNKNOWN | 500 s |
| α≤2 existence, n=16 | UNKNOWN | 900 s |

The encoding is complete but practically too weak for exact refutation; its symmetry is too large. It is retained as a validated tool, but row148 was **not** decided with it. The S021 75,653 Kuratowski cuts were not imported.

## 3. Flip-annealing positive oracle

`tools/s025_cover_anneal.py`:
- **State:** two labelled sphere triangulations T₀, T₁ on V(G).
- **Objective:** the number of uncovered G-edges.
- **Moves:** one edge flip in one layer. A flip keeps a simplicial sphere triangulation, changes the objective by at most ±1, and costs O(1); about 2.5·10⁵ moves/s in Python.
- **Output:** objective 0 gives a split by CLM-0087, re-checked independently.

| Instance | Result |
|---|---|
| J1, J2 | split in 23 s |
| K9P3 | split in 0.03 s |
| K9 | best 1 |
| row148, 5 seeds × 120–900 s (≈ 2.3·10⁸ moves each) | always exactly 4 uncovered |

A positive objective is never used as evidence of non-biplanarity.

## 4. Obstruction descent

`tools/s025_descent.py` decrements one bag at a time, keeping the child with the largest annealed defect.

| Graph | Annealed defect |
|---|---|
| Row148 = B[1,5,2,2,5,2,2,6] (base G\|fH_K), n=25 | 4 |
| B[1,0,0,2,5,2,2,6], n=18 | 2 |
| every 17-vertex child | 1 |
| C5[2,5,2,6,2] (bags 3,4,5,7,6 form an induced 5-cycle of the base) | 1 |

Exhaustive annealing classification of C5 blow-ups (`tools/s025_c5_classify.py`):
- Filters, each a proved necessary condition: K9 (aᵢ + aᵢ₊₁ ≤ 8); Euler; the triangle-free cross-edge bound Σaᵢaᵢ₊₁ ≤ 4n−8.
- Exactly **297** dihedral classes survive, reproducing S004's independent count.
- n ≤ 16: all 262 classes have explicit splits.
- n = 17: all 26 classes stall at defect 1.
- n = 18: all 9 classes stall at ≥ 2.
- Every K9-free vector with n ≤ 16 passes the other filters. Every n = 18 class contains an n = 17 class. No K9-free vector with n ≥ 19 passes the filters.

## 5. Cross-layer K9-minor lemmas

K9 has thickness 3 (classical; programme DRAT certificate re-verified in today's smoke). Let (L₁, L₂) be any biplanar decomposition of G.

**Lemma B (CLM-0090).** Let:
- Q be a clique;
- R₁,…,R_k be pairwise disjoint vertex sets, disjoint from Q, with |Q| + k = 9;
- each Rᵢ dominate Q (every q ∈ Q has a G-neighbour in Rᵢ);
- every pair Rᵢ, Rⱼ be joined by a G-edge.

Then some L_j[Rᵢ] is disconnected.

*Proof.* Otherwise:
1. Contract every Rᵢ in both layers, after deleting all other vertices. Minors of planar graphs are planar.
2. Every G-edge survives in its own layer as an edge of the quotient.
3. The union of the two quotient layers therefore contains K9, a contradiction.

**Lemma C (CLM-0091).** Let:
- Q be a K8;
- R be disjoint from Q, with r ∈ R;
- j be a layer.

If L_j[R] is connected and every q ∈ Q∖N(r) has an L_j-neighbour in R, then G is not biplanar.

*Proof.*
1. Contract R in L_j. In the other layer, delete R∖{r}.
2. Identify the contracted node with r.
3. For q ∈ Q ∩ N(r), the edge qr lies either in L_j (giving q to the contracted node) or in the other layer (giving q to r).
4. Every other q is adjacent to the contracted node by hypothesis, and Q's own edges are untouched.
5. Both layers stay planar and their union contains K9, a contradiction.

**Encoding.** In `tools/s025_minor_cegar.py`, x_e = 1 means layer 1.
- c[R,1] ⇐ T ⊆ L₁, and c[R,2] ⇐ T ⊆ L₂, for every spanning tree T of G[R].
- a[q,R,j] ⇐ (qy ∈ L_j) for y ∈ R.
- Lemma B clause: ∨ᵢ(¬c[Rᵢ,1] ∨ ¬c[Rᵢ,2]).
- Lemma C clause: ¬c[R,j] ∨ ∨_q ¬a[q,R,j].

In any biplanar split, set c and a to their true meanings: every clause holds. An UNSAT verdict therefore refutes biplanarity, given K9's thickness. The inherited lex-leader symmetry breaking stays sound, because every added clause is valid for every biplanar split and the set of splits is invariant under the automorphism group and the layer swap.

`tools/s025_check_minor_cert.py` independently re-justifies **every** CNF clause:
- base clauses are regenerated;
- each Kuratowski lemma is re-checked as a K5/K3,3 subdivision and non-planar;
- each tree is checked to be a spanning tree;
- each Lemma C/B precondition is re-verified;
- auxiliary variables must be fresh and distinct.

`tools/s025_certify.py` re-solves with the S004-pinned CaDiCaL (DRAT output) and requires drat-trim `s VERIFIED`.

**Benchmark on C5[2,5,2,6,2]** (17 vertices, 76 edges):

| Method | Result |
|---|---|
| Plain v4 Kuratowski CEGAR | run lost under memory pressure without output (F071); historically UNKNOWN at S004 120 s caps and F014 3600 s caps |
| + Lemma B (K8+1, K7+2), rmax 5 | UNKNOWN at 3600 s, two runs |
| + Lemma C (rmax 5) | **UNSAT in 551 s** after 1,253 iterations |

Its certificate:
- CNF: 6,204 variables, 171,521 clauses, all justified, sha256 0c91fe37…;
- native refutation: 20.6 s;
- drat-trim VERIFIED: 27 s, DRAT 12.7 MB.

## 6. Certified results

**C5 obstructions.** 18 of the 26 Σ=17 classes are DRAT-certified non-biplanar. CEGAR times range from 43 s to 2392 s. Per-graph times, lemma counts, CNF/DRAT hashes and certificates are in validation/S025/C5_CERTIFICATES.json and sessions/S025/CLOSEOUT.md.

**Corpus closure.** In validation/S025/TRANSFER_271.json, every row lists an explicit injective map from the vertices of a certified C5[u] into its own labels. Every obstruction edge is checked to be a row edge, independently of the search. Four certified classes settled all 219 UNKNOWN rows: C5[2,5,2,6,2] (189 rows), C5[2,3,4,2,6] (21), C5[2,2,5,3,5] (6) and C5[1,4,4,4,4] (3). Row148 contains C5[2,5,2,6,2] on bags 3,4,5,7,6.

**Hand cross-check (CLM-0095).** C5[1,1,7,1,7] is two copies of K9−e glued at a vertex r, plus the edge pq joining the free endpoints. Suppose it were biplanar, with pq ∈ L₁.
- If p and r are joined by a path inside L₁ ∩ H₂, then q–p–…–r is an L₁-path outside H₁. The edge qr can be added to L₁∩H₁ (Lemma A), so K9 = H₁ + qr is biplanar.
- Otherwise p and r lie in different components of L₁ ∩ H₂. The edge pr can be added there, so K9 = H₂ + pr is biplanar.

Both cases contradict K9's thickness 3. This agrees with its DRAT certificate.

## 7. Arm A — chromatic-pressure campaign (exploratory)

- The naive colouring CEGAR over triangulation pairs (`chrom` mode) is too weak (F069).
- New objective: weighted independence (`tools/s025_indep_anneal.py`). The first k vertices weigh 2, the rest 1. A state is bad if any independent set has weight ≥ W+1. Objective 0 certifies χ ≥ ⌈(n+k)/W⌉ with no SAT involved (independent checker `tools/s025_weighted_check.py`).
- An LP gives χ_f = 28/3 for 269 corpus rows and 37/4 for two rows. Corpus χ ≥ 10 is thus a W=3, w(V)=28 certificate. The annealer searches the same certificate class, but only over graphs that are biplanar by construction.

Best minima found (one or a few seeds, 900 s each; heuristic, not bounds):

| W | Configuration | Best minimum |
|---|---|---|
| 2 | n = 14, 16 | 0 |
| 2 | n = 17 | 1 |
| 2 | n = 18 | 2 (consistent with Szeider's theorem) |
| 3 | n = 22, 24 | 0 (graphs with α=3, χ=8, explicitly coloured) |
| 3 | n = 25, 26, 27, 28 | 1, 4, 13 (two seeds: 13), 35–58 (three seeds) |
| 3, total weight 28 | (n,k) = (22,6), (23,5), (24,4), (25,3), (26,2), (27,1) | 8, 10, 13, 21, 17, 19 |

W=4 frontier: see validation/S025/ARM_A_FRONTIER.json. Retire the S024 overlap objective, and do not treat these minima as non-existence statements.

## 8. Limits and adversarial notes

See sessions/S025/ADVERSARIAL.md. In short:
- Every negative depends on K9 having thickness 3. That is classical and programme-certified (S003 DRAT, re-verified today), but it is an imported dependency.
- All runs were on the owner's local Windows workstation with the S004-pinned native binaries, after a full 271+K9 smoke PASS. There was no GitHub Actions run.
- The 271 rows are a restricted, biased source family. Closing them says nothing about χ₂.
- Novelty of the C5 threshold and of Lemmas B/C is NOT established. Contraction arguments with K9 are classical in spirit (Battle–Harary–Kodama/Tutte).
