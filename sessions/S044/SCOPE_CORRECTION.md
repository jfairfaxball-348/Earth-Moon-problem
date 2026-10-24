# S044 correction to the Hajós-leaf quantifier

The 97 individual S042 non-biplanarity certificates are unchanged. The
sentence “each composition leaf L occurs in H as L minus one edge” in S042
RESEARCH is too strong for an iterated binary tree. It is true at the join
where a fresh operand enters; ancestors can delete further edges of that copy.
Consequently the stated containment proof does not justify excluding every
mixed composite merely because it has one leaf from the tested catalogue.
This is a gap in that implication, not a counterexample to its conclusion.

Here is a fixed control, using only Step-One Hajós joins. Start with triangles
A on {0,1,2}, B on {3,4,5}, and C on {6,7,8}. Delete 01 and 34, identify
3 with 0, and add 14. The first graph has edges
{02,12,05,45,14}. Now delete 02 and 67, identify 6 with 0, and add 27.
The final graph has edges {12,05,45,14,08,78,27}, a seven-cycle in order
(0,5,4,1,2,7,8). The specified image of A has only edge 12: two of its
original edges were deleted. It does not contain A-e on those vertices.
The seven-cycle does contain a three-vertex path elsewhere. Thus this control
refutes the claimed retention of each designated copy, not an unlabelled
noncontainment theorem or the global mixed-composite conclusion.

Corrected sufficient implication (CLM-0145). Let H be constructed from t>=2
disjoint leaf copies using only Step-One Hajós joins, with no further vertex
identifications or DHGO splits. Suppose for EVERY leaf L and every edge e,
K_a join (L-e) is non-biplanar, where a is fixed. Then K_a join H is
non-biplanar. Also sufficient is any explicit surviving copy of one of those
certified non-biplanar graphs, regardless of the rest of the tree.

Proof. The t-1 joins delete exactly 2(t-1) edges, each originally a leaf edge
or an edge inserted by an earlier join. A leaf's vertex map remains injective:
each join identifies one vertex across disjoint operands and never identifies
two vertices already in the same operand. Original leaf edges have unique
provenance; distinct leaf copies share at most one vertex. Hence if d_i is
the number of original edges lost by leaf i, sum d_i <= 2t-2. If all d_i>=2,
this would be at least 2t, a contradiction. Some leaf retains all but at most
one original edge. Its surviving copy contains L-e for some e, and the
universal a-clique supplies K_a join (L-e) inside K_a join H. Subgraph
monotonicity of biplanarity contradicts its certified non-biplanarity.

This proves the all-tested-leaves closure for the resolved source families
(and direct one-step joins with a certified deleted operand). It leaves the
arbitrary “one tested leaf somewhere in a mixed tree” implication unproved
unless a surviving subgraph map or another argument is supplied. No conclusion
is made for additional independent-set identifications or general DHGO splits.
The corrected quantifier is written into live CLM-0140/0141/0143 and STATE;
frozen S041/S042 sources, prompts, manifests and certificates remain intact.

Boutin–Gethner–Sulanke's primary preprint, Section 3.2, defines the Step-One
operation and separately lists further identifications as Step Two. Their
ordinary thickness result is not imported as a theorem about graphs after
adding a shared apex. The 2026 rStation post 77 also explicitly limits its
separate cone-chain argument; that source's broader results are not adopted.
