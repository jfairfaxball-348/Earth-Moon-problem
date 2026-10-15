# S018 row148: seven-defect triangulation cover (structural reformulation, NOT a new global bound)

For original row148 of the fixed exact-ten-chromatic corpus, n=25, m=131, source edgefile SHA256 4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598. A simple planar graph on n=25 vertices has at most 3n−6=69 edges. If row148 is exactly partitionable E(G)=E1⊔E2 into planar layers, then 62≤|E_i|≤69 and (69−|E1|)+(69−|E2|)=7. These are necessary, not sufficient, global cardinality constraints (S016 CLM0081).

## Exact maximal-triangulation cover equivalence

For any simple finite graph G on n≥3 *labelled common vertices*, G is biplanar if and only if there exist two maximal planar triangulations T1,T2 on the same common vertex set such that E(G)⊆E(T1)∪E(T2).

Proof forward: any spanning planar layer on this vertex set can be augmented to a maximal planar triangulation on the same n labelled vertices by adding non-crossing missing edges, without removing its edges; do it independently for E1 and E2. Proof reverse: assign each G-edge present in T1 to the first layer and every remaining G-edge to the second layer (such a remaining edge lies in T2 by the cover hypothesis). Both resulting layers are spanning subgraphs of planar triangulations, edge-disjoint, and cover *every* original edge. This includes edges common to the two triangulations, which are assigned only once.

For row148, both triangulations contain exactly 69 edges. Write q=|E(T1)∩E(T2)| and r=|[E(T1)∪E(T2)]\E(G)|. Then, if they cover all 131 G-edges,

  131+r = |E(T1)∪E(T2)| = 138−q,

hence **q+r=7**, with nonnegative integers q,r. Thus any successful decomposition has a witness as a *pair of planar triangulations with at most seven shared-or-extra edges*; equivalently, finding such a pair covering all G-edges solves the exact positive layer problem. This is not a proof that any such pair exists, and G might still be nonbiplanar. The two triangulations need not be edge-disjoint; their intersection size is accounted for exactly.

This offers a qualitatively different S019 algorithmic avenue: search for *covering pairs of triangulations* with a seven-defect budget, preserving reproducible choices of embeddings/rotations. This is a simple known-style mathematical equivalence under standard planar augmentation, not claimed novel. A solver using it must independently check each 69-edge triangulation, the whole original 131-edge cover, and recover the edge-disjoint planar split before any χ₂≥10 claim.

## Local necessary constraints and certificates

For every vertex subset U of size ≥3 and every planar layer i, |E_i(G[U])|≤3|U|−6. This yields original-variable inequalities for the number of layer-1 edges of G[U]. They may strengthen a SAT encoding but must be independently checked for correct polarity, original graph indexing, existential projection of auxiliaries and full-source soundness; local Euler bounds alone do NOT certify a split or exhaustive negative.

S018's actual science is a bounded single-row LNS repair and exact no-lex/no-cardinality CEGAR, with checkpointed cuts and mandatory same-job cold chromatic proof replay. The above exact reformulation and inequalities are an analytic observation for subsequent algorithm design, not assertions that this runner implemented them or settled the row.
