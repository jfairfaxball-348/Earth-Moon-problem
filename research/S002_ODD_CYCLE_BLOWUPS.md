# S002 theorem: the entire odd-cycle clique-blow-up route is blocked

Let C_m[w] replace vertex i of a chordless cycle by a clique of w_i vertices,
join consecutive cliques completely, and add no other edges. Weights are
nonnegative integers. **Every biplanar C_m[w], for odd m >= 3, is
9-colourable.** This is a programme proof with standard dependencies, not a
novelty or universal EMP claim. The C5 case overlaps Trivedi (SRC-0012);
the uniform C7 obstruction overlaps Szeider's concluding discussion
(SRC-0009). Do not represent those parts as new.

## Exact colouring lemma, with an elementary proof

For m=2s+1 >=5, put N=sum w_i and A=max_i(w_i+w_(i+1)). Then
chi(C_m[w]) = max(A, ceil(N/s)).

Interpret the graph as the line graph of a multicycle: edge i has multiplicity
w_i. Adjacent bundles need disjoint colour sets. Every matching contains at
most s edges, so A and ceil(N/s) are lower bounds.

For the upper bound prove by induction on k that A<=k and N<=sk suffice.
If a weight is zero, the support is a union of paths. Along each path choose
w_i colours avoiding the immediately preceding bundle; k>=w_(i-1)+w_i
ensures enough choices. Different paths reuse colours. This also covers
all-zero weights. If every weight is positive, some multicycle vertex has
degree strictly less than k: otherwise all degrees equal k, giving
2N=(2s+1)k>2sk (the k=0 case is incompatible with positive weights).
Delete such a vertex v from the underlying cycle. Its remaining even path
has a perfect matching of size s, using positive-weight bundles. Decrease
each matching bundle by one. At every vertex other than v the degree falls
by one; at v it was already <=k-1. The new total is N-s<=s(k-1).
Induction gives k-1 colours for the residual multicycle, and a fresh kth
colour on the removed matching completes the colouring. No matching,
SAT, perfect-graph or integer-rounding theorem is assumed here.

## Biplanar obstruction and all exceptional lengths

Use the classical non-biplanarity of K9 (Biniaz, SRC-0014, proof inspected).
Thus every adjacent weight sum is at most 8. Summing these inequalities gives
N<=4m=8s+4. If s>=4, ceil(N/s)<=9, so the colouring lemma gives chi<=9.

For m=7 (s=3), chi>=10 would require N>=28. The inequality above forces
N=28 and equality on every adjacent sum. Oddness forces every weight to be
4. Discard the internal clique edges: the remaining cross-edge graph is
triangle-free on 28 vertices and has 7*16=112 edges. Any triangle-free
biplanar graph on n>=3 vertices has at most 4n-8=104 edges, contradiction.
This Euler bound applies even when an individual layer is disconnected:
the usual simple triangle-free planar bound remains valid for n>=3.

For m=5, chi>=10 requires N>=19, and adjacent bounds give N<=20.
For any i, N=w_i+(w_(i+1)+w_(i+2))+(w_(i+3)+w_(i+4))<=w_i+16.
Hence every w_i>=3. For each adjacent pair,
(w_i-3)(w_(i+1)-3)>=0 implies w_i*w_(i+1)>=3(w_i+w_(i+1))-9.
Summing gives at least 6N-45 cross edges, while triangle-free biplanarity
allows at most 4N-8. This is impossible for N>=19 since 2N>37.

Zero weights already reduce to paths and give chi=A<=8. For m=3 the blow-up
is a complete graph, so biplanarity gives order and chromatic number <=8.
All orders, all weights and all odd cycle lengths are covered.

## What this does and does not close

This rules out nonuniform weights and arbitrary long odd cycles, not just
C7[K4]. It supplies a complete family exclusion without imported 2026 SAT
certificates. It does not exclude clique blow-ups of other base graphs,
partial joins between bags, or general independence-number-three graphs.
The exact colouring lemma is standard multicycle mathematics; priority of
the combined all-length corollary remains unchecked. No publication gate
is advanced.
