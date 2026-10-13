# S005 independent small facial-cover reductions

These reductions supply necessary conditions and finite exclusions. They
neither construct a graph nor improve the universal 12-colour bound.
The sphere-completion premise is the same classical premise used in
SRC-0009 and the S004 completion oracle; no method novelty is claimed.

## D=0: selected input triangles, with and without layer consistency

Let G have n>=4 vertices, m=6n-12 edges and an edge-disjoint planar split.
Both spanning layers then have 3n-6 edges and are sphere triangulations.
There are no added or shared edges. Each input edge lies in exactly two
distinct facial triangles of its assigned layer. A triangle cannot be a
face of both layers, because its three edges would be shared. Thus there
is a **0/1 selection of input triangles covering every edge exactly twice**.

tools/dense_face_cnf.py global mode uses one Boolean per input triangle and
an equals-two counter for its incidence at each edge. Its UNSAT therefore
excludes biplanarity. Its SAT says only that this facial-cover relaxation
is possible. In layer mode an extra bit assigns each edge to a layer;
selecting a triangle forces its three bits equal, and exactly 3n-6 bits
are true. This is also necessary. We deliberately omit connectivity,
single cyclic links and positive layer degree, so SAT has no planarity
converse. In particular, layer models may have isolated vertices.

The original 42v/240e witness and ten seed5005 relabellings calibrate both
encodings: actual LR embeddings are checked by the separate sphere-rotation
checker, all actual facial triangles are enumerated, and their exact edge
and triangle assignment is extended through SAT assumptions. These are
eleven labelings of one graph, not eleven independent construction families.

Checked global-mode exclusions: rows 158,171,120,130,42,44,133,135.
Checked layer-mode exclusions include those eight and row262. Every
negative has regenerated LF CNF hashes and drat-trim VERIFIED proofs.
The other global/layer SAT models are relaxations, not graphs certified
biplanar. Their saved assignments directly satisfy every regenerated clause;
all eight layer models have multiple isolates and a checked Kuratowski
subdivision in at least one layer. See relaxed_model_audit.json.
No full finite-universe completeness beyond these 17 labelled
targets is asserted.

## D=1: one surplus pair

Suppose m=6n-13. Extend both planar layers to sphere triangulations. Their
combined count is 6n-12, exactly one edge occurrence above the required
input cover. Consequently precisely one of the following holds:

* one noninput edge occurs in a completion, with every input edge occurring
  once; or
* one input edge occurs in both completions, all others once, and no
  noninput edge occurs.

This is an occurrence identity; it does not assume the input union is
already maximal. A triangle cannot be facial in both completions, since
that would require three doubled input edges and deficit at least three.
Thus facial triangles are again selected 0/1. In the first case every edge
of G plus the selected noninput edge has two incident faces. In the second
case the doubled input edge has four **distinct** incident selected faces,
while every other input edge has two.

tools/deficit_one_cnf.py chooses one surplus pair. Faces with a noninput
pair imply that pair was chosen; triples with two or more missing pairs
are impossible and omitted. Gated cardinality constraints express the
two/four demands above. Noninput unchosen pairs have no selected face by
those implications. The one-hot selection forces the same surplus choice
throughout the formula. Therefore a genuine biplanar G gives a model.
No orientation, connectivity or layer-consistency converse is asserted.

Two actual controls are obtained from the stored D=0 witness: remove a
layer edge and complete it back (new-pair case), or flip an edge to a
diagonal already in the other layer (doubled-pair case). Both resulting
layer embeddings/facial assignments are independently rotation checked
and satisfy the encoder through actual SAT assumptions. A source or
solver description is not being substituted for those controls.

## Independent full incidence challenge

tools/independent_cover_search.py extends the S004 separate direct-incidence
encoder with complete lazy global/link separation and checked Kuratowski
clauses. The numbering, face counters and edge counters differ from Cover;
there is no lex symmetry or explicit excess equation. Every connectivity
and cyclic-link clause is checked syntactically. A Kuratowski clause forbids
all edges of an explicit K5 or K3,3 subdivision in one layer: suppressing
its degree-two paths must produce the respective simple core. This remains
valid even when some edges are completion edges absent from the input.
Actual planar completions survive all these clauses.

Thirteen positive controls passed (ten seeded K8 subgraphs, K8, Sulanke,
K9-e) with exact input partitions and separate rotation checks. Row120
was independently refuted with no initial cuts: 16,802 variables,
1,568,552 clauses; the initial direct-incidence solve took 35.985 seconds.
A standalone proof, compact extraction and fresh compact proof check all
VERIFIED. The no-lex row165 challenge reached its external 620 s cap before
even a saved first-iteration model and remains UNKNOWN. The initial 773
cuts were valid but did not make this negative proof affordable.

This is separately implemented computational corroboration, with shared
classical completion premise, Python/PySAT libraries, and native checker.
It is not external mathematical review, Lean formalisation or a novelty
audit. Satisfiable relaxations and failed transfers are never exclusions.
