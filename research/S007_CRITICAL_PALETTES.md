# S007 critical exteriors and heavy-endblock excess

These are necessary constraints on an actual finite simple12-critical biplanar graph, not an11-colouring theorem. Gallai low-block structure and the extension criterion retain the external dependency SRC-0027; K9 exclusion is SRC-0014. Novelty is not established. The source's Section2.3 already uses spare colours and independent exterior vertices; this application does not claim that method as new.

## A spare colour exposes each low component

Let L be the degree11 vertices, H its complement, and C any component of G[L]. Then

    chi(G-C)=11.

Proof. Criticality supplies the upper bound11. Suppose instead that F=G-C has a proper colouring with colours1..10. Colour11 is unused. Restrict to its vertices in H. SRC-0027 Theorem1.3 applies since every vertex outside H has degree11; components of L have no edges between them. If that restriction already satisfies criterion(a) or(b) for C, extend through C and retain the colouring of the other components from F, contradiction. Otherwise every exterior set is rainbow and noncut vertices in an endblock have the same exterior palette.

If C has a light pair x,y, their actual exterior sets X,Y differ and have equal sizes. Choose a vertex a in X\Y and recolour just a with the unused colour11. This is proper in all of F. The new palettes differ, so criterion(b) extends C.

If C is not light and has at least two vertices, choose an endblock B. All its noncut vertices have identical actual exterior set A. If B=K_s, s<=8, then |A|=12-s. If A were a clique, one noncut vertex together with A and the other noncut core vertices gives a clique of order12 when B=C, or11 when B has one cut vertex. Either contradicts K9 exclusion. Thus A has independent vertices a,b. Recolour both with colour11; they are nonadjacent and the colour was unused, so properness is preserved and criterion(a) holds. If B is an odd-cycle block (nontriangle), every noncut vertex has internal degree2 and |A|=9. A cannot be a clique by K9 exclusion, so the same recolouring applies. Triangles are included in the clique case. For C a singleton, its11 exterior neighbours cannot be a clique, and the same independent-pair recolouring applies. Extension again contradicts criticality.

This proof handles empty H by the supposition and disconnected F without any common planar embedding. It changes F only on H, so its existing colours on L-C remain proper and extend unchanged. Therefore chi(F)=11. In particular, when L is nonempty and connected, chi(G[H])=11. With several low components, deleting one component is not deleting all of L: no claim that chi(H)=11 in general follows. Nor can these separate recolourings automatically be performed simultaneously; chosen vertices for different components may be adjacent.

## Heavy clique endblock support bound

Let an endblock B=K_s, s<=8, of a nonsingle-block low component have noncut core T of order r=s-1, cut vertex z and identical actual exterior set A of order12-s. Every vertex of T has exactly the same outside neighbourhood A union{z}. For every independent Z subset A with |Z|=q>=2,

    sum_(a in Z)(deg_G(a)-12) >= (s-2)q-11.

Proof. Criticality gives a proper11-colouring phi of G-T. If two vertices of Z could be recoloured with the same colour i without affecting the rest, the colours appearing on A would repeat. The entire outside boundary of T would then use at most(|A|-1)+1=12-s=11-r colours, leaving at least r colours to assign injectively to T. That is a proper11-colouring of G, contradiction.

Consequently, for each of the11 colours, at most one vertex of Z has no neighbour of that colour in G-(T union Z). Z is independent, so these are exactly the constraints needed for the proposed simultaneous recolouring of two vertices. At least q-1 vertices of Z are blocked for each colour. Each edge from Z to G-(T union Z) contributes at most one such colour/vertex incidence, giving at least11(q-1) edges across that cut. Every a in Z also has r neighbours in T and none in Z. Summing its total degrees and subtracting12q gives

    rq+11(q-1)-12q=(r-1)q-11=(s-2)q-11.

All a belong to H by definition of exterior; the summands are nonnegative. No upper-degree premise or greedy extension of uncoloured exterior vertices is assumed. We start with an actual colouring of all G-T, keep all vertices outside the selected pair fixed, and use only the independence of Z. This is a counting constraint from criticality, not a positive graph construction.

For a heavy K8 endblock, its seven noncut vertices form K7. An edge within A would complete K9 with that core, so A is independent of order4. The inequality yields

    sum_(a in A)(deg_G(a)-12) >=13,

and at least one of these four exterior vertices has degree>=16. The local subgraph on T, A and z contains K7 joined to five independent vertices after deleting any edges from z to A. Its actual biplanarity challenge is recorded separately, not inferred from Euler or its8-colouring. A single-block K8 component is light as in S006; this heavy conclusion applies only to a genuine endblock with a cut vertex.

For a heavy single-block K_s component, the same counting proof with r=s and no cut yields sum_Z(deg-12)>=(s-1)q-11. A single-block K8 is already impossible as heavy by K9 exclusion. Different endblocks may reuse A and its edges, so summing these bounds over endblocks without controlling overlaps would double count. These conditions do not contradict unbounded Q, h or D.

## Rejected paths and remaining theorem obligations

Recolouring independent neighbours with an unused colour is legitimate only when the exterior colouring uses at most10 colours. An arbitrary11-colouring has no guaranteed spare colour. The triangle fan K1 joined to P4 has two nonadjacent path endpoints that are forced to have different colours in every proper3-colouring; this is a planar generic counterexample to dropping the spare-colour hypothesis. The programme does not extrapolate it to a12-critical witness.

The all-order result chi(G-C)=11 establishes precisely where the spare colour is absent in a critical obstruction. It does not bound chi(H) for multiple components, furnish a simultaneous independent selection, certify contractions/identifications in both layers, or prove any reducible configuration. K9-free heavy boundaries are not automatically flexible in an11-chromatic exterior. The high-excess support bound permits concentrated excess and repeated boundaries. Large-deficit control, all-component extension, a universal proof and independent adversarial review remain open. The S005/S006 Gallai inequalities both remain valid with their different component corrections.
