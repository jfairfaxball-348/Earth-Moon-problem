# S002 universal upper-bound attempt and surviving obstruction

## Critical graph / Euler deficit theorem

Let G be a 12-critical biplanar graph, n=|V|, m=|E|, and
D=6n-12-m>=0. Here critical means every proper subgraph is 11-colourable.
The primary Kostochka–Yancey Theorem 3 (SRC-0011, statement inspected)
gives 22m >=130n-108. Substituting m=6n-12-D gives
**n>=78+11D**. Consequently every biplanar graph on at most 77 vertices
is 11-colourable: a non-11-colourable graph would contain a 12-critical
subgraph (or a minimal non-11-colourable subgraph, which is 12-chromatic),
which inherits biplanarity and violates the bound. This is a corollary of
known density theory, with an external theorem dependency, not a new
universal 11 bound. We do not claim the source proof independently rebuilt.

For an edge-disjoint planar witness D=(3n-6-e1)+(3n-6-e2). So a minimal
12-chromatic witness with deficit one already needs n>=89, and deficit
two needs n>=100. These are necessary conditions, not a finite reduction.
The integer ceiling does not turn 78 into 79. Equality cases would require
additional structural work; none is silently excluded.

Criticality gives delta>=11. Summing degrees yields
sum_v(12-d(v))=24+2D.
If L is the set of degree-11 vertices and Q=sum_(d>=13)(d-12), then
|L|=24+2D+Q. Any such counterexample therefore has at least 24+2D
degree-11 vertices. This exact charge identity is useful, but does not
make one of them reducible.

## Why strengthened greedy deletion fails

CAM-0002 supplies a concrete 42-vertex graph whose two edge-disjoint layers
are triangulations, each with 120 edges and 80 faces. The union has 240
edges, 24 vertices of degree 11 and 18 of degree 12. Thus delta=11 and
D=0. The independent rotation checker establishes biplanarity, not just
a planarity API assertion. Its displayed 7-colouring checks edge by edge.

This disproves universal 10-degeneracy, and rules out a proof of chi<=11
that merely tries to sharpen Euler's forced degree from 11 to 10.
It also defeats the false premise that layer saturation forces a high
chromatic number: the witness is 7-colourable. The charge count of 24
low vertices is attained exactly; the charge identity alone cannot force
more. It does not refute an 11-colouring theorem based on extension or
criticality: this example is not asserted to be 12-critical.

## Colour extension and the actual missing lemma

In a minimal non-11-colourable graph every vertex has degree >=11.
Deleting a degree-11 vertex gives an 11-colouring; if a neighbour colour
is missing, extension succeeds. In the obstruction case its 11 neighbours
use all 11 colours. Swapping two colours in a Kempe component extends
the colouring if their two neighbours lie in different such components.
Hence failure forces the corresponding neighbours to be connected by
two-colour Kempe chains for every colour pair in that particular colouring.

The planar five-colour proof cannot be transplanted: a chain may alternate
between layers and has no common plane rotation or Jordan separation.
Independent layer embeddings do not order the union neighbourhood.
No proof that some pair of chains can be separated has been found. Treating
each layer's degree-five vertex as the same vertex is also invalid. The
42-vertex witness gives explicit disjoint degree-five sets (each of size 12).

Attempting stronger generic critical-density results likewise fails at the
current hypotheses: Gould–Larsen–Postle's improvement (SRC-0013) assumes
k>=33; Kelly–Postle's clique-free density theorem (SRC-0015) requires
sufficiently large k. Neither may be specialized to k=12. The needed
strengthening would force average degree at least 12 for the relevant
K9-free 12-critical class, which remains unproved here.

## What survives for the next serious attack

A two-layer criticality/discharging argument might exploit the many
degree-11 vertices, their different layer rotations, and constrained
colour extension. A proof must supply an unavoidable configuration and
an extension valid for arbitrary neighbour colours; deficit arithmetic
alone leaves unbounded n. Alternatively construct an alpha>=3,
non-cycle-substitution 10-chromatic witness, or a non-saturated apex with
a certified face cover. No universal improved bound or headline solution
was established in S002.
