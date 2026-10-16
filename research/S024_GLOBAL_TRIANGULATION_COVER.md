# S024 — exact global sphere-triangulation cover: proved specification, not solver execution

## Objective and baseline
Original fixed source row148 is a graph G on the labelled vertices 0..24 with **131 original edges** and source SHA256 4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598. It has a previously verified no-9-colouring certificate, but **NO** complete two-planar-layer partition or checked full nonbiplanar refutation. The accumulated 75,653 CEGAR obstructions are sound necessary clauses for their historic encoding; they are not a certificate of original nonbiplanarity.

## CLM-0087 exact equivalence and q+r=7
For ANY simple G on n>=3 vertices, the following are equivalent:
(1) G has thickness at most 2, i.e. E(G)=A disjoint_union B and A,B are planar spanning subgraphs.
(2) There are two labelled (combinatorial) sphere triangulations T1,T2 on the same complete vertex set with E(G) subset of E(T1) union E(T2).

(1)->(2): add edges to each planar spanning layer without changing the vertex set until each is a maximal simple planar graph, hence a sphere triangulation with 3n-6 edges. (A maximal planar completion exists for n>=3 even if the original spanning layer has isolates or multiple components.) The original disjoint partition is covered.
(2)->(1): for each original G edge present in both triangulations, arbitrarily choose one; every other original edge has its forced covering layer. Both assigned subgraphs are planar and disjoint. No requirement that the completion triangulations themselves be edge-disjoint.

For n=25, each triangulation has 69 edges. Set q=|E(T1) intersect E(T2)|, r=|(E(T1) union E(T2)) minus E(G)|. The cover yields 131+r=69+69-q, whence EXACTLY q+r=7, with q,r nonnegative and individually <=7. This is a *seven-edge total cover defect*, NOT a bound on the number of baseline split switches, vertex flips, face changes, or CEGAR iterations.

## Complete orientation/triangular-face Boolean encoding to implement
Let x_{i,uv} be the Boolean that unordered edge {u,v} occurs in triangulation i in {1,2}. For each labelled triple a<b<c create two Boolean oriented face variables f_{i,abc}^{+} (boundary a->b->c->a) and f_{i,abc}^{-} (a->c->b->a). Never select both orientations of the same triple.

For **each directed dart** (u,v), form F_{i,u->v} of all oriented face literals whose clockwise boundary contains the dart u->v, and require the exact Boolean equality SUM(F_{i,u->v}) = x_{i,{u,v}}. Encode exactly-one conditional cardinality by a sound independently audited sequential or totalizer encoding. This ensures every selected edge has exactly one incident oriented face on each side; an unselected edge has none. Impose SUM_{u<v}x_{i,uv}=3n-6=69. Optionally assert SUM(face literals)=2n-4=46 and validate it independently; it is also forced by incidence arithmetic.

**Crucial topology clauses (without which this formulation is NOT complete):**
- For each vertex v, build its directed link on the selected neighbours: an oriented face (v,a,b) gives a directed link arc a->b. Require that all selected neighbours of v belong to ONE simple directed link cycle, not merely disjoint cycles. This is encodable by root/reachability or sound subtour-elimination SAT cuts for all nonempty proper link subsets, with fully proved decoder-to-embedding equivalence.
- Require the entire selected triangulation's graph to be connected (e.g. Boolean reachability from vertex 0 through selected x-edges at most n-1 steps). This excludes a sphere component plus torus components with the same total Euler characteristic.
- Require all 25 labelled vertices to appear in the connected triangulation, each with degree>=3. The surface made from selected oriented triangles is then a connected closed orientable combinatorial 2-manifold. Euler V-E+F=25-69+46=2 forces genus zero (a sphere); its 1-skeleton is a valid planar triangulation.

Finally enforce for EACH original edge e: x_{1,e} OR x_{2,e}. There is no constraint that x_{1,e} and x_{2,e} cannot both be 1; overlapped triangulation edges are assigned once only in the subsequent graph partition. At full models, independently decode every rotation, traverse each oriented dart exactly once, require all 46 distinct triangular faces and Euler=2, check planarity with a second graph checker, and produce canonical A,B assignments. The SAT formula is finite and logically equivalent to biplanarity ONLY if the link and connectedness clauses, cardinality reification and source input are all encoded correctly.

## Benchmark/negative certification contract
First solve a small publicly reproducible known positive split (e.g. validation/S003/splits/J1) with independent rotations and complete source cover. Then run **K9** as a known negative with a native full proof and independent DRAT/LRAT check; mere UNSAT output is insufficient. Finally load row148 immutable original edges and compare the new formula's variables, clauses, memory, live checked cuts and time-to-decision against S021's 75,653-cut historic CEGAR. Any timeout leaves row148 BIPLANARITY_UNKNOWN; without small known controls and K9 native certificate the new encoding remains NOT VALIDATED. S024 is specification/elementary proof only: no oriented-face SAT CNF or global benchmarks were generated in this session.

## Research limitations
The two-completion equivalence and q+r count were known already in S018/S023 and in primary methodological literature (e.g. Szeider 2026); CLM0087 is a restatement with an explicit complete encoding contract, NOT an originality claim or improved bound. The fully quantified topology conditions stop a false positive from a disconnected pseudomanifold. A specification is not an executed complete decision of 131 original edges.
