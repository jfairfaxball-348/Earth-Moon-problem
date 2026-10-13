# A degree-11 double-wheel can resist every single Kempe swap

This refutes a tempting local extension lemma, not the Earth–Moon problem
or reducibility under 12-criticality. There is no universal colouring theorem
here. All construction labels/layers/colourings are stored in
validation/S004/double_wheel_lock.json (generator tools/double_wheel_lock.py).

Let v=0 have neighbours 1..11. In layer 0 put the wheel with rim
1,2,3,4,5; in layer 1 put the wheel with rim 6,7,8,9,10,11. For each i<j
in 1..11 add two fresh vertices p_ij,q_ij and a length-three path
i-p_ij-q_ij-j. Put its two end edges in layer 0 and its middle edge in
layer 1. Layers are edge-disjoint. Layer 0 is its original wheel with
pendant leaves, together with stars at the other rim vertices; layer 1 is
its original wheel with a separate matching. Both are planar; their actual
LR rotations were independently checked by the stdlib sphere checker.
The graph has 122 vertices, 187 edges, D=533 and deg(v)=11. The original
link cycles around v in its two layers remain intact.

Give G-v an 11-colouring c(i)=i-1, c(p_ij)=j-1, c(q_ij)=i-1. Every added
path is alternating in its two endpoint colours. The rims are properly
coloured. Each pair of neighbour colours is therefore joined in the
induced two-colour subgraph, checked independently for all 55 pairs.
Every colour occurs at exactly one neighbour of v.

A Kempe swap on a component with no neighbour changes no neighbour colour.
A swap on a component containing a neighbour also contains the neighbour
with the other colour, because the alternating path joins them. It swaps
the two neighbour colours and leaves the neighbourhood rainbow. Thus no
single Kempe component swap allows this colouring to extend to v.

This graph is exactly 4-chromatic: its C5 wheel requires four colours;
colour v with 3, the first rim 0,1,0,1,2 and the second rim 0,1,0,1,0,1.
For every gadget set p_ij to 3 and q_ij to 1 if c(j)=0, otherwise 0.
That proper 4-colouring is checked on every edge. The construction is
not 12-critical, has large deficit and many degree-two vertices.

Limits: sequences of Kempe swaps, different initial colourings, additional
criticality constraints and the special D<=11 case are unrefuted. The
remaining upper-bound obligation must use those additional hypotheses;
the double-wheel local picture alone cannot ensure a single-swap extension.
Novelty unchecked; no priority or publication claim.
