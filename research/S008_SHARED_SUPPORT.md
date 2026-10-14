# Heavy K8 supports: all-order expansion and its limits

Target: an actual finite simple12-critical biplanar G. Use the source-stated Gallai theorem (SRC0027), classical K9 exclusion (SRC0014) and S007's proved heavy-endblock prerequisites. No universal11-colouring theorem or novelty is asserted.

Let B_i be heavy K8 endblocks with a genuine cut vertex z_i, T_i their seven noncut vertices and A_i their four common neighbours in H. Each T_i induces K7, each A_i is independent by K9 exclusion, and every vertex of T_i has neighbourhood (T_i minus itself) union {z_i} union A_i. Distinct K8 low blocks cannot meet: a common vertex would have low degree at least14>11. Thus T_i are pairwise disjoint, and no edges join different T_i (a noncut low vertex lies in only its own block). The sets A_i consist of high vertices and are disjoint from all these low cores.

## Expansion for every subfamily

For a nonempty subfamily I, put t=|I| and A=union_(i in I) A_i, a=|A|. The subgraph on A union (union T_i) contains21t core edges and28t core-to-boundary edges, all distinct, hence49t edges on7t+a vertices. Extra high-high edges only increase the count. Every subgraph inherits thickness<=2, so Euler gives

    49t <= 6(7t+a)-12,
    a >= ceil((7t+12)/6).

The order is at least11, so the small-order Euler exceptions cannot arise. This holds for EVERY subfamily, with no assumption that its A_i are disjoint or have a common embedding. In particular two endblocks cannot have identical A_i: t=2,a=4 would give98 edges on18 vertices, exceeding96. Union size always exceeds t, supplying Hall's condition and a selection of one distinct high neighbour per block. This is an injective selection of vertices, not simultaneous recolouring or a selection among only vertices of degree>=16.

For completeness, the finite Hall selection principle used here has an elementary induction proof. For a family S_1,...,S_t satisfying |union_(i in J)S_i|>=|J| for every J, if a proper nonempty J has equality, inductively match J into its union and match the complement into sets with that union deleted; its Hall inequalities follow by applying the original inequalities to J union K and subtracting |J|. If no proper J has equality, choose one vertex from S_t, delete it from the other sets, and apply induction: all their formerly strict inequalities remain nonnegative. The empty family is trivial, and the singleton case follows from nonemptiness. Our stronger inequality satisfies these hypotheses. This is the classical Hall principle, not a claimed new method.

## Overlap-aware excess accounting

Write q_v=deg_G(v)-12>=0 on H and r_v=number of selected boundaries A_i containing v. Summing the VALID local CLM0048 gives precisely

    sum_(v in A) r_v q_v >=13t.

Consequently if r_v<=M everywhere, sum_(v in A)q_v>=ceil(13t/M). Without that premise the unweighted13t conclusion is invalid. Also each v is adjacent to7r_v distinct core vertices, so q_v>=max(0,7r_v-12), a separate necessary degree constraint. The expansion controls union size/average multiplicity, not maximum multiplicity: A_i={a,b_i,c_i,d_i} with private triples has a=3t+1, passes the expansion inequalities, and lets r_a=t. This abstract incidence family is not asserted to be realised by a biplanar12-critical graph. It shows exactly why the derived inequalities alone do not bound M or provide distinct high-excess representatives.

The5 registered two-core examples in upper_controls.json have overlap0..4, explicit labelled edges and exact counts. Only overlap4 violates Euler; passing Euler cases remain UNKNOWN. These are subgraph arithmetic controls, not witnesses or a complete obstruction classification.

## Attempted universal conclusion and failure

Deleting the disjoint T_i from critical G supplies an11-colouring of the exterior. It does not guarantee that the distinct support representatives have a common available colour, or that changes at selected representatives preserve the palettes of other blocks. High-high edges can join them. Expansion says nothing about the number of colours blocked in that particular exterior colouring. The no-spare obstruction therefore survives this packing result. The S005/S006 inequalities still allow arbitrarily large h,D,Q; these support conditions supply no upper bound on graph order or deficit, contradiction, reducible configuration, or improved chi_2. External universal review and novelty gates remain open.

## Registered local obstruction transfer

The new tree-model challenge of K7 joined to independent5 has a separate finite verdict in validation/S008/heavy_tree/result.json. Here is the complete conditional transfer, without anticipating that verdict. For a heavy K8 endblock with cut z, its noncut core T consists of7 vertices. Each is adjacent to z and to the same four high vertices A. The five vertices z union A are distinct from T; delete all edges among these five, and all vertices outside T union A union {z}. The remaining subgraph is exactly K7 joined to independent5. A checked non-biplanarity proof for that local graph therefore excludes this entire heavy-endblock class by restricting both planar layers along this injection. It would NOT exclude all K8 blocks, all heavy smaller endblocks, odd blocks or actual12-critical graphs in general. Conversely a checked8-chromatic biplanar local graph merely refutes this local-obstruction route; its five outside vertices have degree7, so it is not12-critical and cannot lift the current lower bound9. Caps/unverifiedUNSAT have neither consequence.
