# S030 necessary conditions — 2026-10-19

No novelty claimed. Gethner–Sulanke OP1(b) is the order-28 target.

Let G have 28 vertices, alpha(G)<=3, and edge-disjoint planar layers.
Every subgraph inherits the two-layer split. K9 is not biplanar (SRC-0014;
inherited programme certificate, rechecked in this session's full smoke).
Thus G is K9-free. Euler's inequality on each spanning layer gives
m<=2(3*28-6)=156. Its complement is K4-free. By Turan, the most edges in
a K4-free graph on 28 vertices occur in the balanced complete tripartite
graph with parts 10,9,9: 90+90+81=261. Hence m>=378-261=117.

For any v, G-N[v] is biplanar and has alpha<=2: an independent triple in
it plus v contradicts alpha(G)<=3. SRC-0037's computer-assisted n<=18
theorem therefore implies 27-deg(v)<=18, hence delta>=9. This is CONDITIONAL
on that source theorem; its computational proof is not replayed here.
An unconditional run must not discard delta<=8 on this argument.
Since sum degrees=2m<=312<28*12, at least one vertex has degree<=11.
Therefore the conditional minimum-degree possibilities are 9,10,11.

If F is any triangle-free subgraph of G, its two inherited layers are
triangle-free planar graphs on at most 28 vertices (add isolated vertices
to make them spanning). Each has at most 2*28-4=52 edges, so e(F)<=104.
The planar bound applies also when disconnected: connect components by
bridges in the plane without creating triangles, then use face lengths
or the forest bound. Attribute this filter to Trivedi/Szeider [42,Q7.1],
SRC-0012/SRC-0037. Thus any explicit triangle-free 105-edge set is a
valid nonbiplanarity obstruction.

For C7[K4], use only edges between adjacent bags, omitting all intra-bag
edges. A triangle would project to a triangle in C7, impossible. There are
7*4*4=112 such edges, exceeding 104; this control is nonbiplanar.
Its independent sets use at most one vertex in each bag and at most three
bags, so alpha=3. This is prior art (rStation post152).

At minimum degree d the handshaking bound is m>=14d, strengthening the
117 lower bound to 126/140/154 at d=9/10/11. At d=11,m=154 every degree
equals 11. At m=155 the excess-degree partition is 2 or 1+1; at m=156 it
is 4,3+1,2+2,2+1+1,1+1+1+1. These are degree sequences, not independent
nonbiplanarity proofs. No source-stated exclusion is silently imported.

Encoding soundness: for every pair uv use g_uv,a_uv,b_uv with
g iff (a or b), and not(a and b). For each four-set add the disjunction
of its six g variables; this is exactly alpha<=3. Degree and edge counts
use fresh cardinality auxiliaries. If a layer contains a verified
nonplanar edge set K, add OR(-x_e:e in K). Every planar layer satisfies
this cut by subgraph closure; deleting it is unnecessary for any genuine
witness. A final UNSAT proof certifies only the generated necessary
formula and transfers to a stratum only after the generator, symmetries,
and all cuts are independently checked. A SAT model is a witness only
after both layers are planar and alpha/counts checked independently.

Unconditional fallback (Szeider's elementary complement argument, not its
computer-assisted theorem): a biplanar alpha<=2 graph Q on t>=3 vertices
has triangle-free complement R. Each R-neighborhood is independent in R,
hence a clique in Q and has size<=8 by K9 exclusion. Therefore e(R)<=4t,
e(Q)<=6t-12, and t(t-1)/2<=10t-12. Equivalently t^2-21t+24<=0, which
fails at t=20 and increases for all larger integer t. Thus t<=19 without
the computational theorem. Applied to G-N[v], this gives delta(G)>=8
unconditionally. S8 is therefore the explicit remaining fallback stratum;
it is not searched or excluded in this session. This is a necessary filter
for the construction domain, not universal colouring work.

Independent-triple anchor for S11 (proved before the strengthened run).
Choose a degree11 vertex v. Its antineighborhood has16 vertices. Since G
is K9-free those16 vertices cannot form a clique; take nonadjacent x,y there.
Relabel (v,x,y) as (0,1,2). Relabel the11 neighbors of v as3..13 and its
remaining14 nonneighbors as14..27. Thus it is sound, for existence up to
isomorphism, to fix g01=g02=g12=false, g0j=true exactly for3<=j<=13.
All S11 graphs possess this representation. With edge01 absent, use edge03
in layer1 to fix the layer swap. This requires no computational alpha2 theorem.

After fixing roots0,1,2 and the root0 neighbor block, permutations inside
3..13 and14..27 are still free. Sort each block by
2*[edge(1,v)]+[edge(2,v)]. This does not change the root0 star, the independent
triple, the graph, or layer planarity. For each consecutive u,v in a block,
forbid each of the six choices (a,b) with 0<=b<a<=3 of those two integers.
The resulting four-literal clause is false exactly on that descending pair.
Every graph can be so sorted, and assigning the roots' label permutation to
both layers preserves the represented biplanar object. This elementary type
partition overlaps the private-clique viewpoint of paper59; no novelty claimed.
