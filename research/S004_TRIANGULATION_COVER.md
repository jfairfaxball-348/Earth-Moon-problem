# S004 triangulation completion and finite apex closure

All graphs here are finite and simple; planarity is topological. This does
not improve 9 <= chi_2 <= 12.

## Necessary encoding and provenance

SRC-0009 §4 motivates the face-incidence route. Our implementation allows
completion edges outside the input, so it tests a *cover* rather than the
source's fixed exact union. No novelty is claimed for the method.

For n>=4, extend each planar layer independently to a maximal planar graph
on the same labelled vertices. Its sphere embedding has 3n-6 edges, two
distinct incident facial triangles per edge, minimum degree at least three,
a connected graph and one cyclic link at each vertex. The completions may
overlap and may add edges missing from G. Thus every biplanar G gives a
model of the following constraints in tools/triangulation_cover.py:

1. Variables E_i(a,b) for every pair, F_i(a,b,c) for every triple, i=0,1.
   A selected face implies each of its three edges. For each pair, at most
   two incident face variables are true; a selected edge requires at least
   two. Each layer has exactly 3n-6 edges and minimum degree at least three.
2. Every input edge belongs to at least one layer. For an input pair,
   z_ab is equivalent to E_0(ab) AND E_1(ab). The total number of these
   doubled input pairs plus the number of selected noninput edge occurrences
   is exactly D=6n-12-m. This identity is just subtraction of the m required
   occurrences from the sum of the two layer edge counts. It does not assume
   that the completed union equals G.
3. All symmetry inequalities use one total order of the primary edge
   variables (layer 0 then layer 1, both lexicographic pair order). Layer
   swap and every input-graph automorphism preserve the constraints.
   The lexicographically least representative of the combined orbit satisfies
   every listed inequality simultaneously. Sequential auxiliary prefixes
   can be set to the actual equality status of preceding primary variables.
   An equality prefix forces equality of the next pair to propagate;
   beyond the first unequal pair, no further inequalities are required.
4. Connectivity cuts require an edge across a nonempty proper vertex set.
   Link cuts forbid a closed cycle of faces around v together with another
   neighbour outside that cycle. Both hold in every sphere triangulation;
   their labels, cycle distinctness, and exclusions are checked when emitted
   and when the archived CNF is regenerated. Short-link seeding merely
   adds all such cuts with cycle length three.

Therefore checked UNSAT excludes the fixed input graph. This implication
does not need a converse from arbitrary CNF models to planarity. For a
positive result, we explicitly check the completed layers with NetworkX
LR and the separate stdlib sphere-rotation checker, then partition the
original edges, assigning overlaps to layer 0. The original split is checked
again. Cases n<4 are outside this encoder and trivially biplanar.

Trust: the classical triangulation-completion fact, the stated reduction,
the generator/cardinality implementation, syntactically valid cuts and
symmetries, and drat-trim. CNF regeneration shares the generator: it is a
reproducibility check, not a separately implemented mathematical encoder.
This is neither a Lean result nor an external independent review.

## Finite apex closure (CLM-0027)

The source pool at live commit 5cb2ca9f7d4d6d195617c09f7348841636b646f6
contains 159 graph edge lists after excluding layer files. Every apex is
non-biplanar: 147 violate m(H)<=5n(H)-6; eight violate CLM-0016; the four
remaining H contain K8, so apex(H) contains K9. The four explicit nine-label
certificates are in validation/S004/apex_K9_certificates.json. The source
`19_12v_57e_w2` has 13 actual vertices with label 2 absent; we relabel its
actual label set bijectively before adding the apex. No extra vertex is
invented from max(label)+1. All source file hashes and counts are in
apex_pool_audit.json, reproducible by tools/audit_apex_pool.py.

The same four inputs were also refuted by the face CNF, with regenerated
CNFs and checked DRAT proofs retained compressed. These computations agree
with the short K9 proof. S003's four UNKNOWN cases were incomplete filtering,
not evidence of promising apex candidates. We retain the historical record
and supersede the obligation explicitly. No assertion about the source
graphs' exact chromatic numbers is required for this exclusion.

apex(C5[K3]) has no K9 and remains outside this elementary closure.
