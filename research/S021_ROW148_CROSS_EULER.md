# S021 original graph148 cross-bipartite Euler constraints and bounded exact search

## Elementary necessary inequality (CLM-0082; NOT novel)

Let G be a finite simple graph whose original edges split as E1⊔E2, each spanning layer planar. Fix *disjoint nonempty labelled* vertex sets A,B and s=|A|+|B|≥3. Define E(A,B) to be only the original edges with one endpoint in A and one in B; all internal edges of G[A] and G[B] are excluded. For each i, the subgraph on A∪B with edges Ei∩E(A,B) is simple, planar and bipartite. By the standard bipartite planar Euler bound it contains at most 2s−4 edges. Therefore a genuine biplanar split satisfies

  |E1(A,B)| ≤ 2s−4,   |E2(A,B)| ≤ 2s−4,   and   |E(G)(A,B)| ≤ 4s−8.

The final inequality is a *direct negative obstruction* only when an explicit A,B and independently counted original edges violate it. Otherwise it provides at most two necessary SAT constraints; it is not enough to imply biplanarity. The direct inequality is not a new Earth–Moon lower-bound theorem.

Index the m=131 immutable original edges by 1,...,131. Use original Boolean x_e=1 for E1 and x_e=0 for E2. If S is the correct set of indices for crossing edges, the two at-most inequalities are sum_{e∈S}x_e≤2s−4 and sum_{e∈S}(1−x_e)≤2s−4. Each PySAT sequential-counter encoding has the usual existential extension property: it is satisfiable for some fresh auxiliary assignment iff the stated original-literal inequality holds. Taking a *new* auxiliary namespace for each counter proves all true biplanar assignments survive the conjunction. Check that every S consists solely of source edges actually crossing A,B, with fresh index bounds and the two polarities, not the full induced G[A∪B].

A deterministic finite candidate generator enumerates each tri-state bag partition into A/B/outside and 5000 vertex-scale seeded partitions, ranks those with crossing edge count exceeding the one-layer bound and selects at most120 strongest (smallest two-layer slack). This is not enumeration of all 3^25 possible disjoint labelled vertex-pair assignments, and it cannot prove that no direct violating cross pair exists. No symmetry or vertex permutation is imposed on the original SAT assignment.

## Continuation and limits

S021 resumes the original graph148 n=25 m=131 SHA256 4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598; the S020 checked six-unplaced partial and 67862 saved original Kuratowski obstructions. The positive route is bounded reversible obstruction-guided insertion (at most8 ejections/100000 states/130s); it is not exhaustive over all original biplanar splits. In particular a remembered state must distinguish the minimum ejection cost for a mathematically complete bounded-radius dominance argument; S021's inherited visited-state pruning does NOT have that proof. The equality |T1∩T2|+|(E(T1)∪E(T2))\E(G)|=7 concerns only a covering pair of 69-edge triangulations and does not justify eight or seven ejections from a chosen partial.

The exact CEGAR arm adds global Euler edge-count bounds 62..69, 100 local induced Euler bounds, then the chosen cross-bipartite counters. Every original Kuratowski cut forbids monochromatic placement of a source-labelled K5/K3,3 subdivision. This is a sound necessary-CNF approach without unverified symmetry: a genuine biplanar split is never excluded, provided all source-index and counter audits pass. A SAT model is only a proposed assignment until both complete layers pass independent planarity. An UNSAT result requires full native proof and projection/source audit. If the wall cap is hit, outcome remains UNKNOWN and all saved cuts are only necessary constraints.

Scientific outcomes, actual same-job setup/271 original chromatic DRAT/K9 smoke, selected A/B records, counters, independent audit and immutable runner/native artifacts belong to validation/S021 and sessions/S021/CLOSEOUT.md, not to this pre-specified mathematical proof.
