# S014 — seven-new-vertex Sulanke boundary: a Hall/K9 closure

Date 2026-10-15. LIVE main pinned `2bdfc91363ee4b2a021dbb07cfa2b04623ac7981`, tree `08fa38266c6e0b90291d00e1f673b755bedc06fd`. S013 authored `e8f6791addec039a1a9ca575e5022823b3b5e98d`, PR #16, actual two-parent merge `2bdfc91363ee4b2a021dbb07cfa2b04623ac7981`, parents `f1e89c50e3014e84292beb34597e8b2aa0e7df81` and S013 authored. S013 main hosted scaffold run 38641064088 SUCCESS, PR run 38640962127 SUCCESS; no open PR. Rulesets [] reachable; main-protection 403 UNKNOWN. No local checked-out repo/hook/native toolchain: this session performs no scientific COMPUTATIONS and inherits no runner-smoke status.

## CLM-0078 — the 11-vertex Sulanke H is edge-critical (analytic)

H=K6 join C5 has chi(H)=9 and 50 edges. Its automorphism group S6 × D5 is transitive on three edge orbits: 15 K6 edges, 30 join edges, 5 cycle edges. Remove any K6 edge: K6-e is 5-colourable, and the C5 uses 3 disjoint colours, total 8. Remove any C5 edge: C5-e is a path on five vertices, hence 2-colourable, plus the K6's 6 colours, total 8. Remove a join edge uw, with u∈K6 and w∈C5: colour K6 with six colours and colour C5 with three colours so that w is the unique vertex of its C5 colour (colour C5-w as the alternating 2-colour path); reuse u's colour on w and give the other four cycle vertices two fresh colours: total 8. All these subgraphs contain an 8-chromatic subgraph (K6-e join C5, K6 join path5, or another suitable 8-chromatic subgraph), but the only conclusion used here is upper bound 8. No claim that deleting edges elsewhere retains a preexisting chromatic lower proof.

## CLM-0079 — near-complete seven-new-vertex boundary CLOSED

**Theorem.** Let G be a finite simple biplanar graph on 18 vertices containing H=K6 join C5 as a subgraph. Let X denote its seven other vertices. If G[X] is K7 or K7-e, then χ(G)=9.

**Reduction.** By CLM0076, any biplanar H copy is induced: an added C5 chord creates K9. Deleting any x∈X leaves a biplanar H-containing graph on 17 vertices, which is 9-colourable (CLM0076). Therefore IF G required at least ten colours, each x∈X would have degree at least nine: otherwise a 9-colouring of G-x could be extended greedily to x (at most eight neighbour colours). Let m∈{0,1} be the number of missing edges in G[X], and m_i their degrees at x_i. Then b=e(G[X])=21-m, c_i=|N_H(x_i)|, c=Σc_i, and 50+b+c≤6·18−12=96. Thus c≤25+m. Since deg(x_i)=6−m_i+c_i≥9, write c_i=3+m_i+δ_i with integers δ_i≥0. Sum gives 21+2m+Σδ_i≤25+m, i.e. Σδ_i≤4−m.

**Hall proper-subfamily bound.** Fix any proper nine-colouring κ of H. For each x_i, let L_i⊆[9] be colours absent from its neighbours in H; |L_i|≥9−c_i = 6−m_i−δ_i. Put d_i=m_i+δ_i; Σd_i=2m+Σδ_i≤4+m≤5. If a set I of s≤6 indices violated Hall, its union of lists would have size ≤s−1. Hence every i∈I would have |L_i|≤s−1, yielding d_i≥7−s and Σd_i≥s(7−s). For s=1,2,3,4,5,6 these right sides are 6,10,12,12,10,6, all exceeding 5. Therefore Hall holds for EVERY proper subset of the seven lists. Full Hall fails only if the union of all seven lists has ≤6 colours.

**Two degree-three vertices.** For m=0, all seven m_i=0 and Σδ≤4, so at least three vertices have c_i=3. For m=1, five vertices have m_i=0 and Σδ≤3, so at least two have c_i=3. Select two such vertices a,b with old three-neighbour sets A,B⊆V(H). If A or B is not a triangle in H, some two of its neighbours lie in C5 nonadjacent and can receive the same colour in an appropriate proper three-colouring of C5. That vertex has at least seven allowed colours, so full Hall holds. Assume each A,B is a triangle.

If A≠B, choose v∈A\B. If v is a K6 vertex, its colour occurs nowhere else in H. If v∈C5, three-colour C5 with v as a singleton colour class (the other four vertices form a path and are bipartite). In either case κ(v) is forbidden at a but allowed at b. Their six-element allowed lists differ, so their union contains at least seven colours; by the proper-subfamily bound, Hall gives seven DISTINCT colours for X. These are certainly a proper colouring of G[X], whether or not its missing edge is used.

Thus possible non-nine-colourability forces every c_i=3 vertex to have the same triangular H-neighbourhood S. For any other x∈X not adjacent to some vertex v∈S, choose an H nine-colouring in which v has a unique colour among H (automatic for K6, choose singleton on C5 otherwise). Any c_i=3 vertex forbids exactly the three distinct colours on S and therefore has the same six-element allowed list L. The vertex x missing v allows κ(v), which lies outside L. Consequently the union of all allowed lists has at least seven colours, and Hall extends the colouring. Hence to avoid a nine-colouring, EVERY x∈X must be adjacent to every vertex of S.

But S is a K3, and G[X]=K7 or K7-e contains a K6. The complete join of S and that K6 is a forbidden K9 subgraph of G. Biplanarity forbids K9 (the earlier independently certified CLM0022); contradiction. Therefore χ(G)≤9. Since H⊆G and χ(H)=9, equality holds.

**Scope.** This eliminates exactly K7 and K7-e new-side extensions, NOT all H-containing 18-vertex graphs and NOT all graphs of order18. It assumes certified K9 nonbiplanarity from pre-existing programme evidence, with no new solver use. The key Hall inequality is robust against C5 colour coincidences and against reuse of a colour on the nonadjacent new pair, because it constructs a stronger all-distinct matching.

## CLM-0080 — exact remaining 18-vertex H-anchored arithmetic (necessary only)

For ANY m≤4, the above biplanarity/criticality reduction yields 21+2m+Σδ≤25+m, hence 0≤m≤4 and Σδ≤4−m. By CLM0079 m∉{0,1} for a hypothetical 10-chromatic biplanar G; so 2≤m≤4. The allowed missing-edge sets are all subsets of size2,3,4 of the 21 K7 edges: C(21,2)=210, C(21,3)=1330, C(21,4)=5985, total **7525 labelled new-side edge patterns**, WITHOUT any symmetry quotient, cross-edge assignments, planarity certification or computational enumeration. For m=4 there is NO cross-degree slack, each c_i=3+m_i. For m=3 at most one unit slack; for m=2 at most two. These are necessary filters and do not imply each labelled pattern has a completion.

## Route A — destroy/rotate Sulanke anchor

CLM0078 shows all single H edge deletions admit 8-colourings, in three S6×D5 edge orbits. That is not a no-go theorem for 10-chromatic completions: a new graph may recover chromatic constraints using replacements, vertex splits or edges to newcomers. Any such graph needs a **fresh** non-9-colouring proof; neither the H chi9 proof nor S011 source row DRAT transfers. Unlike retained-H r7, deleting H edges breaks CLM0076's vertex-deletion premises, so its minimum-degree-9 inference must NOT be copied.

## Route B — first retained-anchor frontier

The K7 and K7-e cases close by the proof above. Remaining m2..4 have strict incidence budget Σδ≤4−m. A good next attack considers complement missing-edge degree sequences and list-colour reuse at nonedges (rather than requiring seven distinct new colours), starting with m=4 no-slack. Avoid claiming that all 7525 labelled patterns have been tried or that their biplanarity has been decided.

## Route C — independent planar layer-first

For n between20 and30, the maximal two-layer edge budget is 6n−12 (108..168 edges). Any genuine edge-disjoint near-triangulation pair remains biplanar by its explicit certified layers; a diagonal flip only preserves a layer if its quadrilateral has the prescribed two triangular faces AND the new diagonal is absent from the other layer. A union with greedy10 colours is still at most10-colourable and gives no lower bound; demand fresh non9 proof. S013's 17v90e 45+45 control is explicitly 8-colourable, not a source of inherited chi10. Without the prescribed same-runner setup and full cold cloud smoke, **no new scientific computation was attempted**, no fresh planar examples were sampled, and no candidate SAT/DRAT certificates were produced.

## Adversarial boundaries

* Hall uses the sets of colours actually forbidden, not number of old neighbours; ≥ bounds hold when C5 neighbours share colours.
* In the pair A≠B, a K6 colour is globally unique and any chosen C5 vertex may be made singleton in a proper 3-colouring.
* The K9 contradiction needs S a triangle AND a new clique of size6; K7-e indeed has a K6.
* The m0/m1 closure is conditional on biplanarity, H as a subgraph and n=18; beyond18 the deletion step does not invoke CLM0076.
* The recent Szeider arXiv:2609.28102 theorem that every biplanar graph with α≤2 is 9-colourable is external independent prior art, with inspected primary introduction/theorem but un-reconstructed full proof, and does not itself settle α≥3 candidates.
* No novel universal bound, no actual chi10 split, and no source-independent priority claim.
