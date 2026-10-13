# S006 critical-density and large-deficit route

No universal improvement of twelve follows here. The conditional application is to finite simple 12-critical biplanar graphs. Gallai's low-vertex theorem remains an external source-stated dependency (SRC-0027), and K9 exclusion is classical (SRC-0014).

## Sharpened all-order block lemma

Let T be a Gallai forest (each nontrivial block a clique or an odd cycle), with l vertices, c components, maximum degree at most11 and clique number at most8. Let t be its number of K8 blocks and u=l-8t. Then

    e(T) <= (7/2)l + (5/2)t - (5/2)c
          = (61/16)l - (5/2)c - (5/16)u.

In particular e(T)<=(61/16)l-(5/2)c. This strengthens S005's coefficient31/8 to61/16, with a different component term. For l>=8c the new coarse bound is at least as strong; for isolated/small components use the displayed refined bound directly rather than claiming unconditional domination of both formulae.

Proof. Distinct K8 blocks cannot share a vertex: that would give degree at least14. Contract every K8 block to one marked vertex. Blocks of a graph form a block-incidence forest; contraction cannot identify two vertices of any other block, create parallel edges or merge two other blocks, since any such event gives a cycle in that incidence forest. Thus the resulting forest T' has t marked vertices, u unmarked vertices, c components and e(T')=e(T)-28t. All remaining clique blocks have order at most7. No remaining K6 or K7 block contains a marked vertex: an original vertex shared with K8 would have degree at least7+5=12. Odd cycles may contain marked vertices.

Assign weight5/2 to each marked vertex and7/2 to each unmarked vertex. In each component choose a root vertex; root the block-incidence tree there. Each nontrivial block has exactly one parent vertex, and its other s-1 vertices are new vertices, assigned to that block. These assignments partition all vertices except the component roots. For a clique of order s<=5, its edge count s(s-1)/2 is at most(5/2)(s-1), so the new vertices cover its edges with their weights. For K6 or K7 every vertex is unmarked, and s(s-1)/2<=(7/2)(s-1). For any odd-cycle block of order s>=3, s<=(5/2)(s-1), so its new vertices also cover its edges. Bridges are K2 blocks. Singletons have no blocks or edges. Summing over the forest, and dropping at least5/2 root weight per component, gives

    e(T') <= (5/2)t+(7/2)u-(5/2)c.

Adding28t and using l=8t+u proves both forms, including the empty graph (all terms zero).

## Sharpness and a failed stronger guess

Take one K8. Attach a K5 at a free vertex of that K8; identify each of the other four vertices of the K5 with one vertex of a new disjoint K8. Repeat at a free vertex of the newest K8. After b connectors there are4b+1 K8 blocks and b K5 blocks, l=32b+8, e=122b+28, c=1, u=0 and maximum degree11. Every attachment is a one-vertex sum, so no additional block or edge appears. Equality holds in the new bound for every b>=0. Consequently61/16 cannot be lowered while retaining a fixed component correction. These are Gallai forests, not12-critical witnesses. They are also biplanar: split each K8 using the known explicit K8 layers and each K5 using a planar K5-e and its omitted edge; iterated one-vertex sums preserve planarity of each layer. This observation needs no new chromatic claim.

The plausible stronger guess e<=(29/8)l-c, based only on bridge-linked K8s, is false. At b=1, l=40,e=150, while(29/8)40-1=144. The exact finite controls b=0..8 in Gallai_controls.json check the counts, blocks and degree; the general proof and all-order equality family are on paper, not inferred from those nine tests.

## Consequences under actual criticality

In a12-critical biplanar G, let L be degree11 vertices, H the vertices of degree>=12, l=|L|,h=|H|,c components of G[L], Q=sum_H(deg-12), e_H=e(G[H]) and D=6(l+h)-12-e(G). Minimum degree11 and the exact degree sum give l=24+2D+Q. Let t count K8 blocks of G[L] and u=l-8t>=0. Gallai's theorem and K9 non-biplanarity justify applying the block lemma. Hence

    e(L,H) >= (27/8)l+5c+(5/8)u.
    96h >= 648+54D+19Q+40c+16e_H+5u.

Since l>=24, c>=1, this forces h>=8. Thus the inherited biplanar high subgraph has h>=3 and D_H=6h-12-e_H>=0. Substituting16D_H=96h-192-16e_H gives

    16D_H >= 456+54D+19Q+40c+5u.

In particular D_H>=ceil(31+(27/8)D+(19/16)Q+(5/16)u) when c>=1. All constants follow by multiplication of the low/high cut identity; no planar layer boundary has been equated with the other layer's boundary.

This still leaves h and n unbounded. A large-deficit critical graph can have a correspondingly sparse high-induced subgraph. No contradiction with D_H>=0 or with Euler follows, and no extension through the low blocks is supplied. Using a lower bound on D_H as an upper bound on n would reverse the direction of the inference. A complete universal colouring theorem remains open.
