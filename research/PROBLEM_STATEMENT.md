# Mathematical charter: EMP

Let G=(V,E) be a finite simple undirected graph. A thickness-2 *witness* is E=E₁ ⊔ E₂ with both G_i=(V,E_i) planar. Define χ₂ = sup{χ(G): G admits such a witness}. It is a maximum because classical χ(G)≤12 for every witness, and attainable chromatic numbers are integers.

**Historical baseline:** 9 ≤ χ₂ ≤ 12 (the full problem is to determine which integer).

**Programme target (owner decision D042, 2026-10-14):** prove χ₂ > 9, i.e. χ₂ ≥ 10, by one explicit certified construction. Required: a finite simple labelled graph G, an explicit edge-disjoint partition E = E₁ ⊔ E₂, an independently checked planarity witness for each layer, and a rigorous checked proof that G admits no proper 9-colouring (hand proof, or a CNF with an independently checked LRAT/DRAT refutation). Upper-bound theorems and full resolution of EMP are out of scope.

**Elementary upper-bound derivation:** for n≥3, each simple planar layer has ≤3n−6 edges, whence |E(G)|≤6n−12. Every subgraph inherits a two-planar-layer decomposition, so for every nonempty subgraph of order ≥3 its average degree is <12 and therefore it has a vertex of degree at most 11; graphs on <3 vertices trivially meet that bound. Thus G is 11-degenerate, yielding a 12-colouring by induction. This is classical, not an original programme theorem.

**Lower-bound witness provenance obligation:** χ(K₆ ∨ C₅)=χ(K₆)+χ(C₅)=6+3=9, but that equation alone does not establish thickness≤2. One must reproduce or check an actual decomposition of all 50 edges into two planar layers before claiming an independently reconstructed 9 lower-bound witness. S002 now reconstructs its actual 26/24-edge partition in validation/sulanke.json and supplies independent sphere rotations and the written chromatic proof.

**Possible definitive answers (context only):** 9,10,11,12. Determining χ₂ exactly needs both a construction and a universal theorem; this programme now pursues only the construction side. A certified 10-chromatic witness proves χ₂ ≥ 10 and leaves 10..12 open; it does not resolve EMP. If χ₂ = 9 is the truth, no witness exists and the programme's target is unattainable; repeated search failures are recorded honestly and are not proof of that.

**Not synonymous:** thickness≤2 concerns topological embeddings separately; geometric thickness≤2 requires common straight-line vertex positions and is strictly a different assertion. No 3D graph drawing or 'two-page book embedding' can silently replace biplanarity.
