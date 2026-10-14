# Structural compression of the heavy odd-block frontier

All graphs are finite simple. Biplanar means an edge-disjoint union of TWO planar layers; restrictions to a subgraph retain that property. This dossier proves an all-order forbidden-subgraph consequence, not an improved universal colouring bound. Classical bipartite Euler counting is attributed; novelty unestablished.

## Bipartite layer bound, including disconnected cases

A simple bipartite planar graph on n>=3 vertices has at most2n-4 edges. For a connected component with a cycle, every facial walk has length at least4 (bridges count twice), so Euler and2m>=4f give the bound. A tree of order n>=3 has n-1<=2n-4 edges. For disconnected graphs, components on>=3 vertices contribute at most2n_i-4, two-vertex components at most1, and singletons0. If there is a component on>=3, summing preserves the global bound; if all components have order1/2, m<=floor(n/2)<=2n-4 for n>=3 (n3 explicitly1<=2). Thus isolated vertices or different embeddings do not invalidate it.

Restrict both hypothetical planar layers to a complete bipartite subgraph K_a,b on a+b>=3 vertices. Both restrictions are bipartite irrespective of any extra edges in the original graph. Their disjoint union therefore requires

    ab <=4(a+b)-8, equivalently (a-4)(b-4)<=8.

For K6,9 this is54<=52, impossible. Both selected sides may have internal edges in the ORIGINAL graph: delete those edges before applying bipartite Euler. Applying2n-4 directly to a layer containing clique/cycle edges would be invalid.

The minimal unordered positive-integer pairs that violate this edge bound are(5,13),(6,9),(7,7). Proof: order a<=b; a<=4 never violates when a+b>=3. For a5 the first b is13; for a6 the first b is9; for a>=7 and b>=a the graph contains K7,7. These are only minimal EULER obstructions, not a classification of biplanar complete bipartite graphs; in particular equality can still be non-biplanar. The small a=b=1 case is exempt, and all a+b3 boundary cases are covered.

## Heavy odd blocks now reduce to C5

Let G be an actual12-critical biplanar graph, L its degree11 vertices, H its high vertices. Gallai low-block structure is an attributed dependency SRC0027. A heavy odd endblock B=C_r (r>=5 odd), with one low cut z, has identical ACTUAL exterior set A for each of its r-1 noncut vertices. Each such vertex has two low neighbours and hence exactly nine high neighbours: |A|=9. The sets A and the noncut core are disjoint. If r>=7 choose any six core vertices and retain their54 edges to A, deleting every path/cycle/other edge. This gives K6,9, contradicting the preceding proof. Hence r=5.

For a whole heavy odd component C_r the same actual common-nine-neighbour premise holds on all r vertices. If r>=7 choose six and obtain the same contradiction. Thus r=5 again. This is stronger than CLM0055's earlier endblock<=11/whole<=9 bounds. Triangles are clique blocks; light blocks with unequal actual neighbourhoods are NOT excluded. Equal palettes under one colouring do not imply these premises.

Consequently CLM0060's e11,e9,w9,w7 terms are all zero in an actual12-critical biplanar graph. Its t8 term is separately zero by cold-checked CLM0063. The mixed charge theorem remains a valid conditional inequality, but its selected family is empty on this class. Further optimisation or SAT search on P10 join I9/C9 join I9 would now be redundant. This resets the proof frontier to heavy smaller cliques/C5, light blocks, and simultaneous/all-order existence; it does not assert that those remaining types occur in a critical graph.

## Complete finite detector and controls

In a clique blow-up B[w], enumerate every allocation x_j in0..w_j with sum x_j=a. Actual vertices inside a bag are interchangeable, so use the first x_j labels. If S is the used bag support, a candidate common outside bag j must be adjacent to every used bag other than itself; each bag is internally complete. Its available count is w_j-x_j. The common-neighbour total over eligible bags is therefore exact, even when the selected side is not a clique. Every a-set is an image of precisely such a bag allocation under within-bag automorphisms; no inducedness is needed. Choose any b actual common neighbours for the other side and independently check all ab edges/disjoint labels.

The independently expanded graph6 corpus has977231 allocation cases across813 source-row pairs (three sources times271). No map was found. This is complete no-containment for these THREE sources on these fixed rows; it gives no new row exclusion and no planar witness.4096 maximum-neighbour comparisons against direct vertex-subset intersections cover all64 labelled four-vertex bases, all16 positive{1,2}^4 weights and all four selected-side sizes;16384 threshold comparisons and9999 elementary arithmetic cases passed. Finite tests corroborate the detector, not the all-order Euler proof.

Explicit K2,9 two-star layers survive independent LR and sphere checks after discarding isolated vertices componentwise. This refutes an attempted prohibition of EVERY common-nine-neighbour set: the six-core threshold is essential. The archived K6 join I6 split likewise remains biplanar/exactchi7 under independent checks; smaller heavy clique local joins cannot all be dismissed by the long-odd argument. Local P4/C5 endpoints have their separately registered prospective model and actual outcomes in SUMMARY; no graph outside the registered universe is claimed decided.
