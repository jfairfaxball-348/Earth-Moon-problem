# S005 upper routes: criticality, low blocks and two Kempe swaps

No universal improvement of twelve is proved. All graphs in the conditional
criticality discussion are finite simple **12-critical biplanar** graphs.
The single stored lock is not critical and supplies no theorem about them.

## The S004 lock admits two swaps

In the exact S004 graph choose neighbours i=1 and j=6 from different wheels,
and k=2 as a third neighbour colour. Its gadget is i-p-q-j, initially coloured
(i,j,i,j), where colour names abbreviate initial neighbour colours.
The vertex p has precisely the two neighbours i and q, both of colour i.
Thus in the subgraph induced by colours j and k, p is an isolated component.
Swap that whole component to recolour p from j to k.

Now consider the colours i and j. The neighbours i and j are nonadjacent
(different wheels). Among the gadgets, only their own gadget could give an
alternating connection between them: an internal vertex with colour i or j
in any other gadget has its two neighbours coloured by that gadget's other
endpoint colour, which is outside {i,j} unless both endpoints are i,j.
The rim edges at i,j have other colours because the neighbourhood is rainbow.
In fact i is now isolated in this induced subgraph. Swap its complete
component from i to j. Colour i disappears from the neighbours of the centre,
so assigning it to the centre extends the colouring.

tools/s005_kempe.py checks the exact partition, both sphere rotations, each
complete two-colour component, properness after each swap and all edges of
the extended 11-colouring. The two components have size one. The same proof
works for this gadget construction over any rainbow neighbourhood with a
nonadjacent pair and a third colour; it does not hold for arbitrary Kempe
locks. The existing counterexample still refutes the one-swap premise.

## Low-vertex Gallai forest: a necessary cut inequality

External dependency: SRC-0027 Theorem 1.1 (Gallai's low-vertex theorem, primary
statement inspected in Kostochka--Stiebitz, 1998). Let L be the vertices of
degree 11, l=|L|, H=V\L, h=|H|, c the number of components of G[L]. Let
Q=sum_{v in H}(deg(v)-12) and e_H=|E(G[H])|. K9 non-biplanarity implies
every clique block of the Gallai forest G[L] has order at most eight.

**Block lemma.** A Gallai forest T with maximum degree at most eleven,
clique number at most eight, l vertices and c components satisfies

    |E(T)| <= (31/8)l - 3c.

Proof, including isolated components: clique blocks of orders seven/eight
are vertex-disjoint. Two such blocks sharing a vertex would give degree at
least 6+6=12 there. Write their counts t7,t8. Contract each such block to
one vertex. The block-incidence forest shows that contraction creates no
loop, parallel edge or merger of other blocks: otherwise the original
incidence forest would contain a cycle. The resulting graph has
l'=l-6t7-7t8 vertices, c components, and only clique blocks of order at most
six and odd-cycle blocks. Every such block B satisfies e(B)<=3(|B|-1)
(for a clique this is t/2<=3; for an odd cycle of length >=3 this is
t<=3(t-1)). Summing over the block forest gives e'<=3(l'-c), also valid
for isolated vertices. Reinsert removed block edges:

    e(T) <= 3(l-c)+3t7+7t8.

Disjointness gives 7t7+8t8<=l, and
3t7+7t8 <= (7/8)(7t7+8t8) <= (7/8)l. This proves the lemma.
Equality includes disjoint K8 components. We assert no sharp asymptotic
constant or novelty.

Consequently the low/high edge cut satisfies

    e(L,H)=11l-2e(G[L]) >= (13/4)l+6c.

The high-degree sum is 12h+Q=2e_H+e(L,H). The previously proved exact
charge identity gives l=24+2D+Q (D=6n-12-m>=0), so

    48h >= 312+26D+9Q+24c+8e_H.

Since l>=24, c>=1. These are necessary structural restrictions, not an
unavoidable reducible configuration. They are weaker than the known
order bound for many parameter choices. In particular, h and n remain
unbounded as D grows; the inequality cannot close the large-deficit lane.

The displayed cut inequality itself forces h>=7. Hence the inherited
biplanar high subgraph has a legitimate deficit
D_H=6h-12-e_H. Substitution cancels 48h and gives the stronger useful form

    8D_H >= 216+26D+9Q+24c,

so D_H>=30+(13/4)D+(9/8)Q when c>=1 (with integer ceilings when used).
This explains why the high subgraph cannot be close to a triangulation
union even when the full critical graph has small D. It still provides no
bound on n and no extension of a colouring of H through the Gallai blocks.

## Endblock palette route and the missing step

SRC-0027 Theorem 1.3(a,b), with its induction proof inspected, supplies a
different extension route. For a component C of G[L], every 11-colouring
of G-C must fail to extend to C, by criticality. Neighbours outside C lie
in H. Thus each low vertex's external neighbours must be rainbow under
that colouring; otherwise condition (a) extends. The external colour
sets at two noncut vertices of any same endblock must also agree; otherwise
condition (b) extends. A clique endblock K_t, t<=8, therefore has the same
external palette of size 12-t>=4 at all its noncut vertices. An odd-cycle
endblock has palette size nine at its noncut vertices.

This is **colour-set equality**, not equality of the actual external
neighbour sets. It does not force a complete bipartite subgraph: different
external vertices can carry the same colours in one colouring. Moreover,
paths of a two-colour component may switch layers and need not respect
either endblock's plane rotation. Thus a proposed palette-to-common-neighbour
or palette-to-planar-separation reduction lacks its key implication. We do
not infer reducibility from it. A substantial surviving route is to force
two distinct endblock palettes in an 11-colouring of G-C, using actual
criticality and both layers; this has not been achieved here.
