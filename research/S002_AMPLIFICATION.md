# S002 construction and amplification attack

## Sulanke, fully reconstructed

The author-hosted SRC-0002 preprint Figure 3 (PDF page 6) is reconstructed
in validation/sulanke.json. Labels are source labels minus one: clique
0..5; cycle [7,9,6,8,10]. The 26- and 24-edge planar layers partition all
50 edges. NetworkX LR and an independent coordinate-derived rotation/Euler
check verify both. The literal 9-colouring is checked. Every clique vertex
requires a different colour, no such colour can appear on the joined odd
cycle, and that cycle needs three colours. Hence chi=9 by a hand lower
bound, not an UNSAT verdict. This verifies a classical witness and does
not discover a new lower bound. For the subsequent Hajós argument we
also check 9-criticality directly. Deleting a clique edge permits its
endpoints to share a colour, leaving five clique colours and three cycle
colours. Deleting a cycle edge makes that part a bipartite path, using
two colours besides the six clique colours. Deleting a cross edge ab
permits cycle vertex b to use clique vertex a's colour, with the other
four cycle vertices forming a path requiring two further colours.
Deleting a clique or cycle vertex likewise leaves an 8-colourable graph.
Thus every proper subgraph is 8-colourable, so the Hajós input really is
9-critical; no external criticality certificate is assumed.

## Joins: density and cut filters

If A join B is biplanar, with a,b>=1 and a+b>=3, its cross edges give
ab<=4(a+b)-8, i.e. (a-4)(b-4)<=8. Also
e(A)+e(B)+ab<=6(a+b)-12. These are necessary, not sufficient conditions.
For K7 join C_m with m odd >=5, e=21+8m exceeds 6(m+7)-12=6m+30.
The triangle case contains K9. Thus increasing the clique in Sulanke cannot
reach 10. Joining two 9-critical witnesses is vastly too dense, and joining
odd-cycle clique blow-ups is subject to the same cut obstruction. None of
these filters bounds general chi_2.

## Hajós: preserved criticality is not amplification

For two k-critical graphs H,K, delete edges xu and yv, identify x,y as z,
and add uv. In any (k-1)-colouring, each deleted-edge graph forces its two
endpoints equal, hence u,z,v all equal, contradicting uv. Conversely a
k-colouring of the two originals can be palette-permuted to match z and
make u,v distinct for k>=3. Thus the standard operation preserves k;
it does not lift 9 to 10. Its planar-layer closure is witnessed by arranging
the deleted edges on the outer faces of corresponding layers, gluing at z,
then joining u to v along the exposed face. Other layers glue at a vertex.
This reconstructs the usable closure direction of SRC-0002 Proposition 3.
No arbitrary identification closure is assumed.

## Universal apex: a genuine 10-chromatic candidate killed exactly

Adding a universal vertex to a 9-chromatic graph lifts chromatic number to
10. For H of order h this can be biplanar only if e(H)<=5h-6. Sulanke
has 50>49, so its apex fails immediately. The Hajós join of two Sulanke
graphs instead has h=21 and e=99=5h-6. Its universal cone has 22 vertices,
120 edges and chromatic number 10: it exactly meets the biplanar density
boundary, so Euler counting alone does not reject it.

Nevertheless it is not biplanar. In any simple biplanar graph of order
n>=4 and 6n-12 edges, each layer must have 3n-6 edges and hence be a
sphere triangulation. Every layer edge then lies in two distinct triangular
faces, so its endpoints have at least two common neighbours in the union.
In the Hajós join the new edge uv has no common neighbour: its endpoints
are in different copies, the only potential common vertex is the glued
vertex z, and zu,zv have both been deleted. In the cone the only common
neighbour is the apex. This contradicts the necessary two-common-neighbour
condition. The argument holds for every choice of the deleted edges.

This reconstructs an existing exclusion of an actual 10-chromatic candidate
family at the saturated boundary. Patil's primary PDF, DOI
10.5281/zenodo.22103613, Section 3.3 contains this same cone/bridge argument.
The overlap is confirmed; this is not a new result or priority claim.

For non-saturated cones the triangle argument no longer applies automatically.
A connected planar layer admits insertion of the apex if its assigned
neighbours all lie on one face. Thus a useful surviving route is a 9-critical
core with e(H)<5h-6 and two compatible face covers of its vertices. Neither
the density inequality nor an arbitrary 9-colouring proves such a cover
exists. No surviving such core has been constructed here.

## Identification is the unproved edge

Arbitrary identification of independent sets does not preserve biplanarity:
take one disjoint edge for each pair in K12 (a planar matching on 132
vertices). Identify endpoints carrying each of the twelve target labels.
Each label class is independent, yet the quotient is K12, which has 66
edges > 6*12-12=60 and is non-biplanar. It has chromatic number 12 while
the initial matching is 2-colourable. An amplification gadget must therefore
prove layer-compatible identifications; Hajós step two alone is insufficient.

The matching example is a symbolic explicit definition; no graph search or
new 132-vertex computation was run.
