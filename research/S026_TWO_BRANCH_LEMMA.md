# S026 two-branch single-layer contraction lemma

Used only as a necessary filter on construction candidates. Depends on K9 having
thickness three (SRC-0014; full old/fresh programme smoke). No novelty claim.

Let G=L1 union L2 be a biplanar split. Let Q be a clique of size seven,
R,S disjoint connected vertex sets in layer j, disjoint from Q, and choose
r in R and s in S. Suppose:

1. Every q in Q nonadjacent to r has a layer-j neighbour in R.
2. Every q in Q nonadjacent to s has a layer-j neighbour in S.
3. Either rs is an edge of G, or a layer-j edge joins R to S.

These conditions are impossible. Contract R and S separately in layer j;
in the other layer delete R except r and S except s. Keep Q in both.
Both resulting graphs are planar minors. Identify the two contracted nodes
with r and s respectively across the layers. Every edge of Q survives.
For qr (and similarly qs), an original qr edge survives in its own layer;
when qr is absent, assumption1 provides its replacement in layer j.
An original rs edge survives in its own layer; otherwise assumption3 provides
the replacement. Thus their union contains K9, contradiction.

The construction is valid because R and S are disjoint; contraction never
identifies vertices of Q or the two representatives with each other. Parallel
edges may be discarded. Extra G vertices/edges are deleted. The claim makes no
assertion that arbitrary simultaneous contraction in the UNION preserves
biplanarity; the two specified planar minor operations are essential.

Encoding: c[R,j] is implied by every monochromatic spanning tree;
a[q,R,j] is implied by each layer-j edge qy, y in R;
p[R,S,j] is implied by each layer-j edge between R,S. For each model add

    -c[R,j] OR -c[S,j]
      OR (OR_{q not adjacent r} -a[q,R,j])
      OR (OR_{q not adjacent s} -a[q,S,j])
      OR (-p[R,S,j] if rs absent).

Assign c,a,p their actual connectivity/adjacency meanings in every biplanar
split. All implications and model clauses hold. Hence the family is sound even
when only a subset of models or spanning trees is generated. Existing lex
symmetry remains sound by the orbit-minimum argument of S025.

Pilot family: Q size7, connected R,S of sizes2..3, each dominating Q,
all pairs of representatives and both layers. These caps affect strength,
not soundness or the completeness of the underlying Kuratowski CEGAR.

Motivation: pending C5[3,3,4,3,4] has clique number seven, so S025 Lemma C
generates zero K8 models. The two-branch family can apply to this candidate.
Independent clause checker and byte regeneration plus native DRAT are required
before any negative graph claim. Known positive J1/C5 splits must satisfy every
new minor clause under its actual meanings; K9 negative control remains checked.
