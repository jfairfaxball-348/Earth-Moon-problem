# Mathematical charter: EMP

Let G=(V,E) be a finite simple undirected graph. A thickness-2 *witness* is E=E₁ ⊔ E₂ with both G_i=(V,E_i) planar. Define χ₂ = sup{χ(G): G admits such a witness}. It is a maximum because classical χ(G)≤12 for every witness, and attainable chromatic numbers are integers.

**Historical baseline:** 9 ≤ χ₂ ≤ 12 (the main problem is to determine which integer).

**Elementary upper-bound derivation:** for n≥3, each simple planar layer has ≤3n−6 edges, whence |E(G)|≤6n−12. Every subgraph inherits a two-planar-layer decomposition, so for every nonempty subgraph of order ≥3 its average degree is <12 and therefore it has a vertex of degree at most 11; graphs on <3 vertices trivially meet that bound. Thus G is 11-degenerate, yielding a 12-colouring by induction. This is classical, not an original programme theorem.

**Lower-bound witness provenance obligation:** χ(K₆ ∨ C₅)=χ(K₆)+χ(C₅)=6+3=9, but that equation alone does not establish thickness≤2. One must reproduce or check an actual decomposition of all 50 edges into two planar layers before claiming an independently reconstructed 9 lower-bound witness. S002 now reconstructs its actual 26/24-edge partition in validation/sulanke.json and supplies independent sphere rotations and the written chromatic proof.

**Possible definitive answers:** 9,10,11,12. To demonstrate χ₂=k, give a k-chromatic biplanar graph AND a universal χ≤k theorem. For k=12 universal half is already known; a 12-chromatic construction solves EMP immediately. If k=9, the existing published lower bound suffices only with sound source provenance; the new universal upper bound would be the headline.

**Not synonymous:** thickness≤2 concerns topological embeddings separately; geometric thickness≤2 requires common straight-line vertex positions and is strictly a different assertion. No 3D graph drawing or 'two-page book embedding' can silently replace biplanarity.
