# Simultaneous extension through heavy cores

Work only under actual12-critical biplanar hypotheses. Keep actual neighbour sets distinct from palettes. This route tries to replace local spare-colour manipulations with an exact simultaneous extension test; it does not establish that the test can always be met.

Let T_1,...,T_t be disjoint heavy K8 noncut cores as in S008_SHARED_SUPPORT and F=G-(union T_i). For any actual proper11-colouring phi of F, set

    P_i=phi(A_i union {z_i}).

Every vertex in T_i has precisely that exterior neighbourhood and T_i is K7. There are no edges between different T_i. Therefore phi extends through ALL cores if and only if |P_i|<=4 for EVERY i. Necessity: seven distinct core colours must avoid P_i. Sufficiency: independently choose any seven distinct colours in {1,...,11} minus P_i for each clique. Other low vertices stay coloured in F; the z_i are outside the removed noncut cores, even when the block structure is a two-endblock component. No unreviewed contraction or shared planar embedding is used.

Criticality gives some colouring of F (a proper subgraph). Since G is12-critical, EVERY such colouring must have at least one i with |P_i|=5. It need not be the same i in different colourings. For t=1 this recovers the local obstruction; for t>1 it exposes the exact simultaneous obligation. One cannot infer that every block is bad in every exterior colouring from its individual-deletion theorem: F deletes more than one core.

To attack that obligation, take an uncoloured subset R of the exterior and define available colours L(v)={1,...,11} minus phi(N_F(v) minus R). Recolouring R is exactly proper list colouring of F[R] with lists L. Merely selecting one distinct support vertex per block (Hall) supplies no control of these lists. If R is independent, its individual assignments are unconstrained by adjacency, but the desired repeated-boundary colours couple assignments across blocks. If R has edges, Hall's matching condition describes the special sufficient tactic of assigning all of R distinct colours; it is not necessary for arbitrary proper list colouring and does not force the boundary repetitions we need.

The registered exhaustive512 availability triples over a three-colour universe check the elementary distinct-assignment Hall condition by independent permutation enumeration (247 admit an assignment). The explicit triple L_1=L_2=L_3={0,1} admits distinct assignments on every pair but none on all three. This is an abstract palette obstruction, not a12-critical biplanar graph or counterexample to a universal theorem. It falsifies replacing the simultaneous list obligation by pairwise checks. Conversely an independent triple with those same lists can all receive0: requiring distinct colours would introduce an unnecessary restriction. Both directions must be kept separate.

Other attempts remain blocked: identifying nonadjacent boundary vertices can destroy either layer's planarity (CLM0013); two-layer Kempe chains can switch layers; no degree upper bound on high vertices exists; deleting a single low component proves chi(G-C)=11 but does not force chi(H)=11 when L has several components. Published SRC0027's good-colouring budget treats unequal actual neighbourhoods, not arbitrary heavy repeated sets. No valid all-order contradiction for heavy components/large deficit was found. The exact extension criterion is a necessary research reformulation and is not a universal colouring theorem, headline bound advance or novelty claim.

## Heavy odd-cycle endblocks: remaining lengths and support

This paper route uses the same published blocking-count method, with no extra computation. Let an odd-cycle endblock B=C_r (r>=5) have one low cut vertex z and a common actual high-neighbour set A for all its r-1 noncut vertices. Each noncut vertex has internal degree2 and total degree11, so |A|=9. Delete z from B. The noncut path has r-1 vertices, r-2 edges and9(r-1) edges to A. The inherited biplanar subgraph has n=r+8,m=10r-11; Euler yields4r<=47, hence r<=11. If a whole low component is C_r with identical actual exterior A, its r core vertices/9 high vertices give n=r+9,m=10r and4r<=42, hence r<=9. These are all-order necessary bounds, not decisions that the surviving local graphs are biplanar.

For any independent Z subset A, |Z|=q>=2, criticality also forces

    sum_Z(deg_G(a)-12) >= (r-2)q-11

in the endblock case. Indeed colour G-T with11 colours, where T is the noncut path. If some colour can simultaneously recolour two vertices of Z while the rest of G-T stays fixed, A ceases to be rainbow. At most8 colours then appear on A, leaving at least3 for T. Only the two path endpoints additionally meet z; removing its colour leaves each endpoint at least2 available colours, and internal vertices at least3. Greedily colour the path from one endpoint to the other, excluding the predecessor's colour each time: the final endpoint still has at least one choice. This extends the exterior colouring, contradicting criticality.

Consequently each of11 colours blocks at least q-1 vertices of independent Z via neighbours in G-(T union Z). There are at least11(q-1) such edges, disjoint from the (r-1)q core edges. Subtract12q to obtain the bound. For a whole heavy odd-cycle component, recolouring a pair leaves3 available colours for an odd cycle (which has an explicit3-colouring); the same count with r core neighbours gives (r-1)q-11 instead. No clique-colouring requirement was imposed on the path. The argument does not require a spare colour: it proves how much blocking MUST occur if such a simultaneous recolouring is impossible.

K9 exclusion guarantees some independent pair in the9-element A. Thus length11 endblocks force excess at least7 on that pair; length9 endblocks force at least3. These conditions permit arbitrarily many blocks and concentrated/overlapping excess. Remaining endblock lengths5,7,9,11 and smaller heavy clique blocks are not eliminated, and all-order large-deficit/simultaneous extension remains open. No source-method novelty or universal11-colouring theorem is asserted.
