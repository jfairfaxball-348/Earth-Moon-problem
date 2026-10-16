# Claim catalogue

Status records evidence; no programme claim resolves EMP.

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

Sources: None; programme proof/computation..

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

Sources: None; programme proof/computation..

Explicit planar matching quotient K12, symbolic proof; no new computation.

## CLM-0014 — PROGRAMME_PROVED

In a 12-critical biplanar graph, degree-11 vertices number 24+2D+sum_{d>=13}(d-12).

Sources: None; programme proof/computation..

Exact degree-sum identity; at least 24+2D, not an extension lemma or finite reduction.

## CLM-0015 — PROGRAMME_PROVED

apex(H) is biplanar iff E(H)=E1+E2 and V(H)=S1+S2 with Si on one face of a plane embedding of (V,Ei).

Sources: None; programme proof/computation..

research/S003_FACE_DEFICIT.md Lemma 1.

## CLM-0016 — PROGRAMME_PROVED

In a biplanar graph on N>=4 vertices, sum over edges with at most one common neighbour of (2-codegree) is at most 4(6N-12-e).

Sources: SRC-0017.

Lemma 2/Cor 3; generalizes the saturated bridge obstruction; overlap with SRC-0017 facial-incidence arguments likely; no novelty claim.

## CLM-0017 — PROGRAMME_PROVED

In a biplanar graph with deficit D at least N-4D vertices are wheel vertices in both layers; a 12-critical biplanar graph with D<=11 has at least 24-2D degree-11 double-wheel vertices.

Sources: None; programme proof/computation..

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

Sources: None; programme proof/computation..

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

Sources: None; programme proof/computation..

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

Sources: None; programme proof/computation..

Explicit layers, colourings and all 55 alternating paths checked; odd C5 wheel supplies chi>=4. D=533, not 12-critical. Does not refute multi-swap, criticality or D<=11 reducibility.

## CLM-0030 — COMPUTED_EXACT

An independent full 8^8-weight audit on each of the fixed bases GsUPOK and GrEKGc agrees with the S003 census for those two bases.

Sources: None; programme proof/computation..

GsUPOK: kept 485, colourable 458, F3 19, survivors 8; GrEKGc: kept 71, colourable 61, F3 0, survivors 10. Different chunk enumeration/MIS-cover method and main reruns. Not a full k=8 census check.

## CLM-0031 — COMPUTED_EXACT

Among positive C5 weights in {1,...,8} satisfying the registered F1-F3 filters, there are 297 dihedral classes and 13 maximal classes under dihedral componentwise containment.

Sources: None; programme proof/computation..

Full 8^5 enumeration in tools/s004_frontier.py; maximal list archived. This counts necessary-filter patterns, not biplanar graphs or an exhaustive graph universe.

## CLM-0032 — COMPUTED_EXACT

The explicit 22-vertex, 119-edge graph G|fH_K[4,2,2,2,2,2,2,6] (S003 alpha>=3 list index 165) is 10-chromatic and non-biplanar.

Sources: SRC-0009, SRC-0024, SRC-0025.

Checked chi=10 and regenerated completion-face CNF with 773 valid cuts; two DRAT-verified refutations. Compact core DRAT rechecked and publicly retained. Independent no-lex encoder found a non-planar SAT relaxation, not an independent exclusion. Finite result only, exact thickness/novelty not claimed.

## CLM-0033 — PROGRAMME_PROVED

C5[K3] is exactly 8-chromatic and its universal apex is exactly 9-chromatic.

Sources: None; programme proof/computation..

Alpha=2 on 15 vertices forces chi>=8; checked explicit 8-colouring. Universal join adds exactly one, with explicit 9-colouring checked. Biplanarity UNKNOWN; this calibration cannot lift the lower bound to ten.

## CLM-0034 — COMPUTED_EXACT

All 17 D=0 rows of the fixed 271-row S003 alpha>=3 list are 10-chromatic and non-biplanar.

Sources: SRC-0009, SRC-0024, SRC-0025.

Rows161,163,164,154,158,160,176,171,120,126,128,130,42,44,133,135,262. S005 regenerated completion CNFs and DRAT-verified each original and compact proof; inherited chi=10 certificates/upper colourings cold-hash audited. Not a theorem for every D=0 biplanar graph or all clique blow-ups.

## CLM-0035 — COMPUTED_EXACT

Nine of those D=0 exclusions have independently implemented reduced-encoding DRAT certificates; row120 also has a separate no-lex direct-incidence certificate.

Sources: SRC-0009, SRC-0024, SRC-0025.

Global selected-triangle cover excludes158,171,120,130,42,44,133,135; layer-consistent reduction also excludes262. Thirteen independent full-incidence positive controls and eleven relabellings of a real D=0 witness for reduced controls. Shared classical premise/library/checker; no external review. Row165 no-lex challenge UNKNOWN at620s.

## CLM-0036 — PROGRAMME_PROVED

A biplanar n>=4 graph with D=0 has a 0/1 triangle selection covering every edge twice; with D=1 its completion has exactly one new pair or one doubled input pair and a 0/1 facial selection with respective edge incidence demands two or four.

Sources: SRC-0009.

research/S005_FACE_REDUCTIONS.md. Repeated facial triangle would require at least three doubled edges, impossible at D<=1. Necessary encodings only; relaxed SAT has no planarity converse. Actual completion controls for both D=1 cases passed.

## CLM-0037 — PROGRAMME_PROVED

The stored S004 122-vertex, 187-edge one-swap Kempe-lock colouring of G-v extends after two complete Kempe component swaps.

Sources: None; programme proof/computation..

Choose neighbours1,6 and third colour at2, recolour one gadget vertex then neighbour1; both complete induced components have size one. Exact layers/rotations, properness at every stage and full extension verified. This graph is4-chromatic and not12-critical; no universal multi-swap theorem.

## CLM-0038 — PROGRAMME_PROVED

A Gallai forest with l vertices, c components, maximum degree at most 11 and clique number at most 8 has at most (31/8)l-3c edges. In a 12-critical biplanar graph, 48h>=312+26D+9Q+24c+8e_H and 8D_H>=216+26D+9Q+24c.

Sources: SRC-0027, SRC-0014.

Full block-contraction proof and algebra in research/S005_UPPER_ROUTES.md. h high(degree>=12) vertices, Q=sum(deg-12), c low-forest components, e_H high-induced edges, D_H=6h-12-e_H; h>=7 follows. Uses externally source-stated Gallai theorem; no independent proof of that theorem, order upper bound, reducible configuration or improved universal colouring bound.

## CLM-0039 — COMPUTED_EXACT

The fixed D=1 candidate rows 177,179,180,102,103,117,123,143 are 10-chromatic and non-biplanar.

Sources: SRC-0009, SRC-0024, SRC-0025.

S005 full completion-face CNF regeneration and checked DRAT certificates; inherited exact chromatic certificates cold-hash audited. Other registered D=1 rows UNKNOWN: []. Total 25 new finite exclusions; 245 of the original 271 remain UNKNOWN. No stronger thickness, novelty or headline bound claimed.

## CLM-0040 — PROGRAMME_PROVED

A Gallai forest with l vertices, c components, maximum degree at most11 and clique number<=8, t K8 blocks and u=l-8t, satisfies e<=(7/2)l+(5/2)t-(5/2)c=(61/16)l-(5/2)c-(5/16)u. The61/16 coefficient is sharp for this class.

Sources: None; programme proof/computation..

Full contraction/root-weight proof including empty/singleton cases and all-order K8/K5 equality family in research/S006_CRITICAL_DENSITY.md. Nine actual layer/rotation/colour controls are corroboration, not universal proof. No novelty or12-critical equality witness asserted.

## CLM-0041 — PROGRAMME_PROVED

Every12-critical biplanar graph obeys96h>=648+54D+19Q+40c+16e_H+5u and16D_H>=456+54D+19Q+40c+5u, with h>=8 and u the number of low vertices outside K8 blocks.

Sources: SRC-0027, SRC-0014.

Uses CLM-0040 and the source-stated Gallai low-vertex theorem. Exact low/high cut algebra in research/S006_CRITICAL_DENSITY.md. No upper bound on counterexample order, colouring extension or universal upper improvement.

## CLM-0042 — PROGRAMME_PROVED

An explicit40v/60e biplanar chi8 graph with degree11 K8 core and pairwise disjoint external neighbourhoods has identical rainbow four-colour exterior palettes whose fixed11-colouring cannot extend.

Sources: None; programme proof/computation..

Labelled private leaves, exact disjoint layers/rotations, proper8-colouring and K8 lower bound checked; fixed boundary leaves only seven core colours. External vertices degree1; not12-critical. Refutes unconditional extension/common-neighbour inference, not actual criticality.

## CLM-0043 — SOURCE_STATED

Bradshaw2026 Theorem1.10 states K_(d+1)-free graphs of mad<=d+1/28 are correspondence d-colourable for d>=3.

Sources: SRC-0029.

Primary statement and local deduction inspected, full main proof not audited. At d=11 biplanarity only supplies mad<12; the required threshold is unproved. No headline improvement or transfer of list-criticality to ordinary criticality.

## CLM-0044 — PROGRAMME_PROVED

In a12-critical biplanar graph, if every degree11 low component has an endblock pair of noncut vertices with unequal actual exterior neighbour sets, then e_H+c>=66. In particular this holds if every low component is a single K8.

Sources: SRC-0027, SRC-0014.

Published Section2.2 Lemma3 good-colouring edge budget and Theorem1.3 extension, both local proofs inspected. Programme deduction in research/S006_PALETTES.md. Identical-cardinality actual sets required; heavy components not excluded, edge budget unbounded; no universal upper improvement or novelty.

## CLM-0045 — COMPUTED_EXACT

S006 adds15 checked non-biplanarity exclusions among the fixed271 chi10 candidates, rows[17, 29, 35, 46, 47, 80, 81, 82, 187, 189, 190, 195, 197, 258, 260]; 230 remain UNKNOWN.

Sources: SRC-0009, SRC-0024, SRC-0025.

Each new necessary Cover CNF regenerated and original/retained compact DRAT freshly checked. All19 target lower chromatic proofs replayed and upper colourings checked. D1 remaining[]; registered UNKNOWN[162, 155, 157, 159], NOT_RUN[157, 159]. Finite domain only; no thickness-minimality, novelty or headline advance.

## CLM-0046 — PROGRAMME_PROVED

For biplanar n>=4 inputs of deficit D<=2, two planar sphere completions have disjoint facial triple sets; the S007 global multiplicity CNF and stronger planar-subset/K5 Cover cuts are necessary.

Sources: SRC-0009.

Surplus/necessity/orbit-minimum proof in research/S007_ENCODINGS. StrongCover implementation is restricted to at most11 closed-twin classes; mathematical cuts are necessary in general. Distinct faces disabled at D>=3; both encodings lack a SAT converse. Finite controls are not the proof.

## CLM-0047 — PROGRAMME_PROVED

For every low component C in an actual12-critical biplanar graph, chi(G-C)=11. If the low subgraph is nonempty and connected, chi(G[H])=11.

Sources: SRC-0027, SRC-0014.

Complete spare-colour/endblock proof in research/S007_CRITICAL_PALETTES; uses published Gallai and extension theorem. No conclusion chi(H)=11 for disconnected L, simultaneous extension, universal upper improvement or novelty.

## CLM-0048 — PROGRAMME_PROVED

A heavy K8 endblock in a12-critical biplanar graph has four independent common exterior neighbours with total excess sum(deg-12)>=13, hence one has degree>=16.

Sources: SRC-0027, SRC-0014.

Actual common neighbour set, K9 exclusion and11-colour blocking count; general independent-Z bound (s-2)|Z|-11 in research/S007_CRITICAL_PALETTES. May not be summed over overlapping boundaries; no contradiction with unbounded Q/D.

## CLM-0049 — COMPUTED_EXACT

The explicit12v/51e graph K6 joined to independent6 is biplanar and exactly7-chromatic.

Sources: None; programme proof/computation..

Labelled exact disjoint split, independent LR/sphere rotations and proper7-colouring in validation/S007/heavy_search.json; K7 clique lower bound. Local heavy-K7 control only, not12-critical or chi>=10.

## CLM-0050 — PROGRAMME_PROVED

Completion K5/input K3,3 clauses and the S008 totalizer representation are necessary in the registered full-layer CNFs.

Sources: SRC-0009.

Euler/bipartite Euler and orbit-minimum proof in research/S008_ENCODING; library counter trust,27 direct controls/23 independent enumeration/2304 truth tests/23 tree pins. No SAT converse.

## CLM-0051 — PROGRAMME_PROVED

For every nonempty family of t heavy K8 noncut cores in a12-critical biplanar graph, its common exterior boundaries have union size at least ceil((7t+12)/6), hence admit distinct high-neighbour representatives.

Sources: SRC-0027, SRC-0014.

All-order49t-edge Euler subgraph proof and classical Hall induction in research/S008_SHARED_SUPPORT. Overlap-weighted excess only; not distinct high-excess representatives, recolouring or universal upper improvement.

## CLM-0052 — PROGRAMME_PROVED

An11-colouring of G minus a family of heavy K8 noncut cores extends simultaneously through them iff every five-vertex exterior boundary uses at most four colours.

Sources: None; programme proof/computation..

Exact clique/list argument in research/S008_NO_SPARE. No existence theorem for a suitable exterior colouring; actual criticality forces at least one bad block in every such colouring, possibly different blocks.

## CLM-0053 — COMPUTED_EXACT

S008 adds4 checked non-biplanarity exclusions among the fixed271 exactchi10 candidates, rows[155, 157, 159, 162]; 226 remain UNKNOWN.

Sources: SRC-0009, SRC-0024, SRC-0025.

New full-layer negatives use their own cold CNF/counter representation and original/compact/cold retained DRAT checks; any transfer uses independently checked labelled injection from a checked obstruction. Fresh lower chromatic proofs/proper10-colourings separate. Finite inputs only, no thickness-minimality/novelty/headline advance. Exact per-lane/transfer artifacts in validation/S008.

## CLM-0055 — PROGRAMME_PROVED

A heavy odd-cycle endblock in an actual12-critical biplanar graph has length r<=11; a whole heavy odd-cycle low component has r<=9. Independent exterior Z obeys excess>=(r-2)|Z|-11 for an endblock and(r-1)|Z|-11 for a whole component.

Sources: SRC-0027, SRC-0014.

Euler subgraph and published-method blocking count with explicit path/cycle extension in research/S008_NO_SPARE. Actual common9-neighbour sets; overlaps cannot be summed freely. Necessary all-order constraints, no universal upper bound or novelty. S010 CLM0065 sharpens both odd-length bounds to5 under the same actual-common-neighbour premise; prior bounds remain valid but weaker.

## CLM-0056 — PROGRAMME_PROVED

For every selected family of t heavy K8 noncut cores in an actual12-critical biplanar graph, unweighted excess on the union of their high boundaries is at least4t, with arbitrary support overlap.

Sources: SRC-0027, SRC-0014.

Complete all-order truncated-demand/degree-multiplicity proof in research/S009_GLOBAL_CHARGE.md;3331 finite charge checks corroborate only. Arithmetic equality model is not an actual critical biplanar witness. No maximum multiplicity, distinct high-excess representatives, universal colouring or novelty.

## CLM-0057 — PROGRAMME_PROVED

For every nonempty selected family of t heavy K8 endblocks in an actual12-critical biplanar graph, common high-boundary union size is at least ceil((8t+12)/6).

Sources: SRC-0027, SRC-0014.

Distinct full eight-vertex low blocks contribute56t distinct edges on8t+a vertices. Complete Euler/subfamily/boundary proof in research/S009_GLOBAL_CHARGE.md. Stronger than noncut-only expansion, no colour/list conclusion.

## CLM-0058 — PROGRAMME_PROVED

For a fixed11-colouring outside all selected heavy-core boundaries, simultaneous extension exists iff some nonadjacent pair choice in each boundary induces independent equality classes whose quotient admits proper colouring from common-list intersections.

Sources: SRC-0033.

Complete logical equivalence including cuts/overlaps/all edges/empty cases in research/S009_SIMULTANEOUS_COLOURS.md. Classical contraction idea attributed; no planar contraction or guaranteed feasible pair/list choices.1029 abstract list controls, not critical witnesses or universal theorem.

## CLM-0059 — PROGRAMME_PROVED

All completion K3,3 subgraph clauses in the registered S009 small full-layer tree model are necessary for every genuine planar completion.

Sources: SRC-0009.

Bipartite Euler/six-set partition enumeration/orbit-minimum proof in research/S009_CONSTRUCTION.md;23 actual full pins/rotations and independent enumeration controls. Not all Kuratowski subdivisions, no SAT converse or verdict from partial CNFs.

## CLM-0060 — PROGRAMME_PROVED

For disjoint selected heavy low cores in an actual12-critical biplanar graph, total high excess Q is at least4t8+4e11+2e9+3w9+w7, counting K8 endblocks, C11/C9 endblocks and wholeC9/C7 components respectively.

Sources: SRC-0027, SRC-0014.

All-order truncated mixed demand/degree-budget proof in research/S009_GLOBAL_CHARGE.md. Independent16384 Cartesian arithmetic vectors/16 integer knapsacks validate smallq; q>=16 analytic. Supports may overlap across types; selected cores must be disjoint. Shorter/smaller/light/all-deficit colouring still open; no novelty or headline advance. S010 shows all these selected heavy types absent from the actual critical class (CLM0063/0065); inequality valid but vacuous there.

## CLM-0062 — COMPUTED_EXACT

The explicit12v56e graph K7 joined to independent5 is non-biplanar.

Sources: SRC-0009, SRC-0024, SRC-0025.

Necessary all-completionK33 tree CNF independently cold regenerated; original/compact/cold retained native DRAT checked. Labelled edges and source proof chain in validation/S009/heavy_extended/result.json; the initial validation/S009/heavy/result.json remains UNKNOWN. Exactchi8 follows from proper8-colouring/K8 clique, not a lower-bound lift; novelty unchecked.

## CLM-0063 — PROGRAMME_PROVED

Every7-clique in a finite simple biplanar graph has at most4 common neighbours outside it; in particular an actual12-critical biplanar graph has no heavy K8 endblock with a genuine low cut vertex.

Sources: SRC-0009, SRC-0024, SRC-0025, SRC-0027.

Necessary all-completionK33 tree CNF independently cold regenerated; original/compact/cold retained native DRAT checked. Explicit local subgraph transfer in research/S009_CONSTRUCTION.md. Does not exclude lightK8 endblocks/allK8 blocks/smaller heavy blocks/odd blocks or prove universal11-colouring. Finite source proof plus all-order conditional deduction; novelty unchecked.

## CLM-0061 — COMPUTED_EXACT

S009 certifies additional non-biplanarity for fixed exactchi10 rows[15, 23, 24, 28, 38, 41, 45]; 219 of271 remain UNKNOWN.

Sources: SRC-0009, SRC-0024, SRC-0025.

Each direct negative has necessary cold LF CNF and original/compact/cold retained native DRAT; any transfer independently checks actual injection/source cold certificate and target non9/proper10. Exact source and per-lane provenance in validation/S009. No minimality, census closure, novelty or headline advance.

## CLM-0064 — PROGRAMME_PROVED

No finite simple biplanar graph contains K5,13, K6,9 or K7,7; for a+b>=3 these are exactly the minimal unordered complete-bipartite violations of the two-layer bipartite Euler edge bound.

Sources: SRC-0009, SRC-0034.

Complete independent all-order proof with connected/tree/disconnected/small cases in research/S010_BIPARTITE_RESET.md. Classical counting attributed; not a complete bipartite thickness classification or novelty claim.

## CLM-0065 — PROGRAMME_PROVED

In an actual12-critical biplanar graph, a heavy odd low endblock or whole heavy odd low component with identical actual exterior neighbour sets has length exactly5.

Sources: SRC-0027, SRC-0009.

Any length>=7 gives six distinct low noncut/core vertices complete to nine distinct high vertices, hence K6,9. Triangles treated as cliques; light blocks/palette equality excluded from premise. This closes long-heavy-odd subroute, not universal colouring.

## CLM-0066 — PROGRAMME_PROVED

A12-critical biplanar graph cannot admit an independent high set R meeting each chosen heavy boundary at least twice, safe light-pair residual choices, and e(H-R)+|M_residual|<=54 simultaneously.

Sources: SRC-0027.

Full sufficient-extension contradiction, three safe-pair cases/unused colour/component boundaries in research/S010_SIMULTANEOUS_EXTENSION.md.112640 exact palette cases corroborate only. Existence of R/safe pairs/residual budget not proved; no universal upper improvement or new method priority.

## CLM-0067 — COMPUTED_EXACT

The explicit P4 joined to independent9 (13v39e) and C5 joined to independent9 (14v50e) are biplanar and exactly3-/4-chromatic respectively.

Sources: None; programme proof/computation..

Public labelled disjoint layers, independent LR/component sphere rotations, proper3/4 and hand path/cycle-plus-join lower proofs in validation/S010/local/results.json. New13/14 model pins/calibration and cold baseline gates passed. Local positives do not construct actual12-critical heavy components or lift9; no minimality/novelty claim.

## CLM-0068 — COMPUTED_EXACT

None of the fixed271 S003 exactchi10 rows contains an edge-preserving K5,13, K6,9 or K7,7 subgraph.

Sources: None; programme proof/computation..

977231 complete bounded bag allocations across813 source-row pairs; independent4096 direct-subset controls, labels in validation/S010/bipartite_detector.json. No row exclusions, planar converse, whole-census or distinct-isomorphism-class claim.


## CLM-0069 — PROGRAMME_PROVED

The ordinary Mycielski lift of any finite simple graph with chromatic number at least 9 cannot be biplanar.

Sources: SRC-0036 (primary abstract only; S011 proof self-contained).

Induced 9-critical H has minimum degree at least 8, hence m>=4n. M(H) is induced in M(G), has 2n+1 vertices and 3m+n>=13n edges, versus the 2-planar Euler limit 12n-6. Details in research/S011_CONSTRUCTION.md. Obstruction is only a construction-family filter, not EMP resolution or novelty.

## CLM-0070 — COMPUTED_EXACT

The six *specific labelled* S003 rows 2,55,59,61,199,200 are edge-critical exactly-10-chromatic graphs.

Sources: in-repository proof computations; no external priority claim.

Original no-9 DRAT proofs cold checked, explicit proper10 checked. All 863 edge deletions produced a valid 9-colouring independently checked in a separate standard-library implementation using a second graph6 expander. Permanent full witness archive validation/S011/edge_critical_witnesses.json.gz (SHA256 d43bfe323a52666a7811630f8cff549e7eed8fd8b628f2ff6a1cf84cbf26e554). Other rows/biplanarity remain UNKNOWN.

## CLM-0071 — PROGRAMME_PROVED

All original-edge / original-nonedge single swaps of a clique blow-up with bag sizes>=2 preserve the existence of a proper q-colouring after edge deletion; for S011's six fixed 10-edge-critical rows every one of **194,896 swaps is properly nine-colourable**. Source: original in-repository CAM0014 colours. Hand proof and independent complete CAM0015 witness audit in research/S012_CONSTRUCTION.md, validation/S012/SUMMARY.json; no biplanarity exclusions, general singleton/multi-swap claim or novelty assurance.

## CLM-0072 — PROGRAMME_PROVED

A finite simple biplanar graph retaining the original **induced** 11v50e nine-critical Sulanke H=K6 vee C5 and adding <=5 vertices is at most 9-chromatic. Direct criticality/degree/Euler induction (r1 universal apex density; r2..5 degree>=9 versus two-layer bound) in research/S012_CONSTRUCTION.md. Modifying H or taking 6+ new vertices is outside scope; no general chromatic upper bound or originality claim.

## CLM-0073 — PROGRAMME_PROVED

Any **hypothetical** biplanar 10-chromatic six-new-vertex extension of induced Sulanke H must have K6 or K6-e among new vertices and total 89 or90 edges on17 vertices; the K6-e case forces90 and both layers triangulations. Only necessary arithmetic; no such witness constructed. Details and scope in research/S012_CONSTRUCTION.md.


## CLM-0074 — PROGRAMME_PROVED
K6-e six-new-vertex induced Sulanke extension with necessary biplanar 90-edge budget always has nine-colouring by allowed-colour Hall (two nonadjacent new vertices may share a colour); details research/S013_CONSTRUCTION.md. Only conditional construction-family statement.

## CLM-0075 — PROGRAMME_PROVED
K6 six-new-vertex induced Sulanke extension with necessary 89/90 edges is nine-colourable unless it contains K9: five new degree-4-to-H neighbourhoods must coincide as a K4 if Hall extension fails under every proper H 9-colouring. Classical K9 nonbiplanarity CLM0022/SRC0014, independently checked.

## CLM-0076 — PROGRAMME_PROVED
Every biplanar G on <=17 vertices containing Sulanke H as ANY subgraph has chi(G)=9. H's five missing C5 chords individually create K9, so any biplanar H copy is induced; apply S012 <=5 and S013 six-extension cases. No claim about arbitrary 17-vertex graphs or general upper bound, novelty not cleared.

## CLM-0077 — COMPUTED_EXACT
GitHub Actions CAM0016 run38639416513 job116110828710 generated eighty 17v unions of actually planar edge-disjoint layers, LR+component rotation/Euler+proper colouring checked. Retained 17v90e 45+45 split with proper8 colour in validation/S013/layer_pair_control.json. Forty-eight tested two-edge modifications of six source blowups all partial, best12 unplaced, never classified nonbiplanar. Same-job full D043 smoke PASS 271/271 and native K9. No 10-chromatic split.

## CLM-0078 — PROGRAMME_PROVED

H=K6∨C5 is nine-chromatic and any single original edge deletion permits an eight-colouring, in three automorphism edge orbits (K6, join, cycle). See research/S014_CONSTRUCTION.md. This does not preserve non9 under rewiring.

## CLM-0079 — PROGRAMME_PROVED

A biplanar 18-vertex graph containing H with induced new-side K7 or K7-e has chi=9. CLM0076 deletion-critical degree condition, Euler deficit, Hall's theorem and old-C5 singleton recolouring show nine-colourability unless it contains forbidden K9. Full proof research/S014_CONSTRUCTION.md. Not all order18 graphs.

## CLM-0080 — PROGRAMME_PROVED

Remaining hypothetical biplanar chi>=10 H-containing order18 extensions require K7 minus m=2..4 edges, c_i=3+m_i+δ_i, Σδ_i<=4-m. Exactly7525 labelled missing-edge sets, only a combinatorial formula; no cross-incidence search or planar certification run. See research/S014_CONSTRUCTION.md.

## CLM-0081 — PROGRAMME_PROVED (elementary, NOT NOVEL)

For a simple n-vertex m-edge graph with an exact edge-disjoint biplanar partition E1,E2, Euler gives |E_j|<=3n-6 and hence max(0,m-(3n-6))<=|E_j|<=min(m,3n-6). Rows156,3/9,173 require respectively 62..66,63..72,64..69 edges in each planar layer. This does not prove a split exists, disprove biplanarity or improve χ₂; S016 exact SAT did NOT encode these new constraints. Source SRC-0005; proof in research/S016_ORIGINAL_CERTIFICATES.md.


## CLM-0082 — PROGRAMME_PROVED (elementary / non-novel)

For disjoint nonempty A,B with s≥3, the subgraph consisting exclusively of edges crossing A|B within each planar layer is bipartite planar and has at most 2s−4 edges; original G hence has at most4s−8 total crossing edges. Standard Euler fact, *necessary only*, no S021 biplanarity decision. See research/S021_ROW148_CROSS_EULER.md, source SRC-0005, independently verified120 source-indexed cross SAT inequalities.


## CLM-0083 — PROGRAMME_PROVED (elementary / non-novel)

For fixed disjoint labelled A,B,U partitioning E(G), every complete two-layer edge assignment uniquely corresponds to the set F of baseline-placed edges changing sides together with one of two layer choices for each edge of U. Thus exactly `binom(|A|+|B|,r)·2^|U|` complete assignments differ on exactly r baseline-placed edges. Planarity is hereditary under edge deletion: any nonplanar layer prefix in the exhaustive branching cannot become planar by adding remaining edges. Consequently fully exhausted radii rigorously describe that restricted labelled neighbourhood, **never** unrestricted original nonbiplanarity. See research/S022_ROW148_EXACT_NEIGHBOURHOOD.md.

## CLM-0084 — COMPUTED_EXACT (restricted radius, non-novel)

S022 CAM-0024 [run38765947247](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/38765947247) completed exactly r=0,1,2,3 switchsets around the original148 frozen 62+63+6 partial: **1 + 125 + 7,750 + 317,750 = 325,626** distinct switch subsets, with all six unplaced edge placement possibilities explored or soundly pruned by nonplanarity. All radii marked EXHAUSTED_LOCAL_RADIUS with zero completed split; first unplaced (0,1) had no planar placement at any surviving baseline state. Source SHA256 4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598, elapsed305.53s, peak39.4MiB; same-job 271/271 original CNF/native DRAT and K9 smoke PASS. This COMPUTED_EXACT finite search is not a checker-independent full original negative, does not classify graph148, and does not change 52 certified NONBIPLANAR/219 UNKNOWN or χ₂ classical9..12.


## CLM-0085 — PROGRAMME_PROVED (restricted conditional / novelty unchecked)
K6 universally joined to H within any biplanar graph forces chi(H)<=3 and hence chi<=9. Euler bounds e(H)<=9; K9 prohibition makes H triangle-free; triangle-free graphs with <=9 edges are 3-colourable by 4-critical minimum degree and the unique triangle-free cubic six-vertex graph K3,3. Complete hand proof and scope in research/S023_UPPER_VS_LOWER_AUDIT.md. Source: classical SRC-0005, SRC-0014.

## CLM-0086 — PROGRAMME_PROVED (necessary obstruction / novelty unchecked)
Every degree-11 vertex in any biplanar graph has >=6 nonedges between its 11 neighbours (induced 12-vertex Euler bound). In any 12-critical graph, all these nonedges must be Kempe-locked in every proper 11-colouring after deleting v. Not a reducibility theorem or universal chi<=11 bound. Hand proof and S004 adversarial witness in research/S023_UPPER_VS_LOWER_AUDIT.md. Sources: SRC-0005, SRC-0014.

## CLM-0087 — PROGRAMME_PROVED, elementary/non-novel
Thickness<=2 iff the original simple graph is edge-covered by two maximal sphere triangulations on the same vertices: complete each planar layer, or choose one covering triangulation for each original overlapping edge. For 25v131e row148, triangulation edge total 2*69=138 implies **q+r=7** (q common triangulation edges, r new exterior edges). This is global cover defect NOT edge-switch radius. Research in research/S024_GLOBAL_TRIANGULATION_COVER.md; full topology clauses specified, not implemented. Existing S018/Szeider prior art, no originality claim.

## CLM-0088 — COMPUTED_EXACT in finite recorded CAM0026 ONLY
Actions run38862555457 job116847945627 with full original271 and native retained/fresh K9 smoke passed. 18 preregistered maximal-planar pair trials: 17 edge-disjoint n22/28/36 pairs with explicit edges, checked rotation/Euler and SAT produced proper colourings using <=8 colours, one n28 overlapping pair. Thus every 17 candidate **fails** to be chi>=9; no original219 classification and no improvement to 9<=chi2<=12. Permanent validation/S024 and tools/s024_layer_first.py. A proper colour assignment is an upper chromatic certificate, never a lower certificate.
