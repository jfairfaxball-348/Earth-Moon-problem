# Claim register after S004

Headline remains open, 9 <= chi_2 <= 12. Exact scopes and limitations below.

## CLM-0001 — SOURCE_STATED

EMP asks for the maximum chromatic number of finite simple edge-unions of two planar graphs.

Sources: SRC-0001, SRC-0004, SRC-0005.



## CLM-0002 — SOURCE_STATED

Every biplanar graph is 12-colourable via two Euler bounds and degeneracy.

Sources: SRC-0005, SRC-0008.



## CLM-0003 — SOURCE_STATED

Published example K6 join C5 has chromatic number 9 and admits thickness two.

Sources: SRC-0004, SRC-0005.

Published statement retained; independent programme proof is CLM-0007 with validation/sulanke.json.

## CLM-0004 — SOURCE_STATED

Historical and modern indexed baseline is 9 <= chi_2 <= 12.

Sources: SRC-0004, SRC-0005, SRC-0006.

Not an exhaustive claim about all 2026 new publications.

## CLM-0005 — SOURCE_STATED

Boutinâ€“Gethnerâ€“Sulanke report 40 small nine-critical thickness-two graphs.

Sources: SRC-0002.



## CLM-0006 — SOURCE_STATED

Patil primary deposit reports a 241-graph corpus and candidate/order exclusions; certificate README retains independent lex-leader validation gap.

Sources: SRC-0007.

Primary DOI 10.5281/zenodo.22103613 located and sampled proofs inspected; external machine certificates not replayed.

## CLM-0007 — PROGRAMME_PROVED

The explicit source-reconstructed K6 join C5 graph is biplanar and has chromatic number 9.

Sources: SRC-0002.

Classical reconstruction: 26/24-edge layers, two planarity validators, written join/odd-cycle lower bound. validation/sulanke.json.

## CLM-0008 — SOURCE_STATED

Every biplanar graph with independence number at most two is 9-colourable.

Sources: SRC-0009, SRC-0010.

Published textual proof inspected; not externally replayed or programme-formalized. Classical and compiled-check trust retained.

## CLM-0009 — PROGRAMME_PROVED

Every biplanar clique blow-up of any odd cycle, allowing nonnegative integer weights, is 9-colourable.

Sources: SRC-0012, SRC-0014.

Complete elementary proof research/S002_ODD_CYCLE_BLOWUPS.md. C5 overlap known, other overlap possible; novelty unchecked.

## CLM-0010 — COMPUTED_EXACT

An explicitly certified 42-vertex biplanar graph has minimum degree 11 (24 degree-11 and 18 degree-12 vertices) and a proper 7-colouring.

Sources: programme construction/argument.

CAM-0002 certificate validation/degree11_witness.json; disproves universal 10-degeneracy. Exact chromatic number NOT claimed.

## CLM-0011 — PROGRAMME_PROVED

A 12-critical biplanar graph with deficit D=6n-12-m has n>=78+11D; hence every biplanar graph of order at most 77 is 11-colourable.

Sources: SRC-0011.

Corollary of external Kostochkaâ€“Yancey Theorem 3, whose full proof is not rebuilt; no universal improved bound. S003 correction: superseded by SRC-0017 Observation 7.1.1 (n>=89, see CLM-0024), which predates S002 and was missed by the S002 prior-art audit.

## CLM-0012 — PROGRAMME_PROVED

The universal apex over a HajÃ³s join of two Sulanke graphs is 10-chromatic but non-biplanar for every deleted-edge choice.

Sources: SRC-0002, SRC-0007.

Known saturated bridge obstruction, reconstructed in research/S002_AMPLIFICATION.md; no originality claim.

## CLM-0013 — PROGRAMME_PROVED

Identification of independent sets need not preserve biplanarity.

Sources: programme construction/argument.

Explicit planar matching quotient K12, symbolic proof; no new computation.

## CLM-0014 — PROGRAMME_PROVED

In a 12-critical biplanar graph, degree-11 vertices number 24+2D+sum_{d>=13}(d-12).

Sources: programme construction/argument.

Exact degree-sum identity; at least 24+2D, not an extension lemma or finite reduction.

## CLM-0015 — PROGRAMME_PROVED

apex(H) is biplanar iff E(H)=E1+E2 and V(H)=S1+S2 with Si on one face of a plane embedding of (V,Ei).

Sources: programme construction/argument.

research/S003_FACE_DEFICIT.md Lemma 1.

## CLM-0016 — PROGRAMME_PROVED

In a biplanar graph on N>=4 vertices, sum over edges with at most one common neighbour of (2-codegree) is at most 4(6N-12-e).

Sources: SRC-0017.

Lemma 2/Cor 3; generalizes the saturated bridge obstruction; overlap with SRC-0017 facial-incidence arguments likely; no novelty claim.

## CLM-0017 — PROGRAMME_PROVED

In a biplanar graph with deficit D at least N-4D vertices are wheel vertices in both layers; a 12-critical biplanar graph with D<=11 has at least 24-2D degree-11 double-wheel vertices.

Sources: programme construction/argument.

research/S003_UPPER_BOUND.md Lemma 6, Cor 7-8; not a reducibility result.

## CLM-0018 — PROGRAMME_PROVED

If a planar-union-outerplanar graph has chi>=9, or a union of two outerplanar graphs has chi>=8, then chi_2>=10 (apex / K2-join).

Sources: SRC-0003.

Observation 9; elementary, likely known in SRC-0003 (inaccessible).

## CLM-0019 — COMPUTED_EXACT

Every biplanar clique blow-up of a graph on at most 6 vertices is 9-colourable.

Sources: SRC-0014.

CAM-0004: reductions R1-R5 proved; zero survivors for k<=6; independent checker agrees k=3..6. Depends on K9 non-biplanarity.

## CLM-0020 — COMPUTED_EXACT

On bases with 7 (resp. 8) vertices, every clique blow-up with chi>=10 that passes the counting filters F1-F3 has a 10-core among 13 (resp. 828) explicit survivor vectors; 570 of the 841 have alpha=2, N=19.

Sources: programme construction/argument.

Independent checker agrees at k=7 only; k=8 not independently checked. validation/S003/census_*.json.

## CLM-0021 — COMPUTED_EXACT

The 13 order-7 survivors (base FCptO = K4 with the three edges at one vertex subdivided) and the 90 survivors of k=8 part 1 have chromatic number exactly 10.

Sources: SRC-0024.

DRAT-verified non-9-colourability (bag and vertex CNFs) plus checked 10-colourings; for FCptO also a hand proof N<=27-w5 for 9-colourings. Biplanarity of all of them is UNKNOWN.

## CLM-0022 — COMPUTED_EXACT

K9 is not biplanar, re-certified by a pure Kuratowski-lemma CNF (24946 independently checked lemmas, lex-leader symmetry breaking) with a drat-trim VERIFIED refutation.

Sources: SRC-0014, SRC-0024.

Calibration of the CAM-0003 v4 oracle; classical result, not new.

## CLM-0023 — COMPUTED_EXACT

K9-e, K9-P3, K9-K1,3, K2v(K4+K6+K6), K2v(K5+K5+K6), K3v3K5 and K10-C4 are biplanar.

Sources: programme construction/argument.

Explicit layers in validation/S003/splits checked by NetworkX LR and the stdlib rotation checker (K10-C4 split not archived; reproducible). Biplanarity of K9-e may be known.

## CLM-0024 — SOURCE_STATED

Every 12-chromatic biplanar graph has at least 89 vertices; every 10-chromatic one has at least 17 vertices.

Sources: SRC-0017, SRC-0018, SRC-0020.

n>=89 is SRC-0017 Obs 7.1.1 via KY Brooks-type refinement (not inspected); n>=17 is SRC-0018 (census-conditional) and SRC-0017 (SMS-certified).

## CLM-0025 — COMPUTED_EXACT

Of the 159 SRC-0017 pool graphs, 147 have e>5n-6 and 8 more are excluded by CLM-0016 as apex bases; the apices of the remaining 4 have UNKNOWN biplanarity.

Sources: SRC-0017.

Corpus chromatic numbers source-stated.

## CLM-0026 — COMPUTED_EXACT

Every one of the 271 listed alpha>=3 S003 blow-up survivors has chromatic number exactly 10.

Sources: SRC-0024, SRC-0025.

S004 independently checked F1/F2/F3, 271 bag and 271 vertex DRAT refutations of 9-colourability, and 271 explicit proper 10-colourings. Bag proofs retained compressed; biplanarity not inferred.

## CLM-0027 — COMPUTED_EXACT

Every universal apex of the 159 graphs in the pinned SRC-0017 pool is non-biplanar.

Sources: SRC-0017, SRC-0014, SRC-0024.

147 Euler exclusions, 8 CLM-0016 exclusions, 4 explicit K9 subgraphs. Last four also have checked face-CNF DRAT proofs. Supersedes S003 apex UNKNOWN obligation only; corpus chromatic numbers not assumed.

## CLM-0028 — PROGRAMME_PROVED

For each finite simple labelled n>=4 input supported by the triangulation-cover encoder, biplanarity implies satisfiability of its CNF with any well-formed registered connectivity/link cuts and automorphism lex constraints.

Sources: SRC-0009.

Necessary-condition proof in research/S004_TRIANGULATION_COVER.md; allows completion edges outside the input, overlapping layers and exact excess D. Implementation/cardinality/DRAT checker remain trust dependencies. No Lean or universal colouring theorem.

## CLM-0029 — PROGRAMME_PROVED

A 122-vertex, 187-edge biplanar graph with a degree-11 double-wheel vertex has an 11-colouring of its deletion for which no single Kempe component swap frees a neighbour colour; the graph itself is exactly 4-chromatic.

Sources: programme construction/argument.

Explicit layers, colourings and all 55 alternating paths checked; odd C5 wheel supplies chi>=4. D=533, not 12-critical. Does not refute multi-swap, criticality or D<=11 reducibility.

## CLM-0030 — COMPUTED_EXACT

An independent full 8^8-weight audit on each of the fixed bases GsUPOK and GrEKGc agrees with the S003 census for those two bases.

Sources: programme construction/argument.

GsUPOK: kept 485, colourable 458, F3 19, survivors 8; GrEKGc: kept 71, colourable 61, F3 0, survivors 10. Different chunk enumeration/MIS-cover method and main reruns. Not a full k=8 census check.

## CLM-0031 — COMPUTED_EXACT

Among positive C5 weights in {1,...,8} satisfying the registered F1-F3 filters, there are 297 dihedral classes and 13 maximal classes under dihedral componentwise containment.

Sources: programme construction/argument.

Full 8^5 enumeration in tools/s004_frontier.py; maximal list archived. This counts necessary-filter patterns, not biplanar graphs or an exhaustive graph universe.

## CLM-0032 — COMPUTED_EXACT

The explicit 22-vertex, 119-edge graph G|fH_K[4,2,2,2,2,2,2,6] (S003 alpha>=3 list index 165) is 10-chromatic and non-biplanar.

Sources: SRC-0009, SRC-0024, SRC-0025.

Checked chi=10 and regenerated completion-face CNF with 773 valid cuts; two DRAT-verified refutations. Compact core DRAT rechecked and publicly retained. Independent no-lex encoder found a non-planar SAT relaxation, not an independent exclusion. Finite result only, exact thickness/novelty not claimed.

## CLM-0033 — PROGRAMME_PROVED

C5[K3] is exactly 8-chromatic and its universal apex is exactly 9-chromatic.

Sources: programme construction/argument.

Alpha=2 on 15 vertices forces chi>=8; checked explicit 8-colouring. Universal join adds exactly one, with explicit 9-colouring checked. Biplanarity UNKNOWN; this calibration cannot lift the lower bound to ten.
