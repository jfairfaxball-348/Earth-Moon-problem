# S006 endblock palettes, fixed-boundary obstruction and missing flexibility

SRC-0027 Theorem1.3(a,b) applies to an actual12-critical G with L degree11 and H its complement. For a component C of G[L], every11-colouring of G-C fails to extend. Thus the external neighbourhood of every low vertex is rainbow, and the external colour sets agree at the noncut vertices of every endblock. A clique endblock K_s has common external palette of size12-s; this leaves s-1 colours for its noncut clique vertices. A single-block K8 component has eight vertices competing for the same seven colours. These are necessary obstructions under each fixed exterior colouring, not proof that actual exterior neighbourhoods coincide.

## Explicit trap against an unconditional extension lemma

Use labelled core0..7 inducing K8. For each core vertex v, attach four private leaves8+4v+j, j=0..3, and no other edges. Put all pendant edges in E1 and use the archived exact K8 split for its28 core edges. Both layers remain planar; exact disjoint60-edge union and separate sphere rotations were checked and retained in validation/S006/palette_trap.json. Each core vertex has degree11, external vertices degree1. Colour every private leaf indexed j with colour j. This is a proper11-colouring of the exterior with identical rainbow four-colour palettes at all core vertices, although all eight exterior neighbourhoods are pairwise disjoint. The core has only colours4..10 available, and K8 requires eight distinct colours: that fixed boundary cannot extend.

The full graph is exactly8-chromatic: the core supplies the lower bound and the explicit unrestricted colouring core(v)=v, leaf(v,j)=(v+1) mod8 is proper. Hence this is not12-critical, and it does not meet the external high-degree or minimum-degree hypotheses of a critical counterexample. It refutes the unconditional assertion that planarity plus degree11 plus identical palettes forces extension, and separately refutes palette equality implying common actual neighbours. No assertion under actual criticality is refuted.

## What criticality still has to force

In the trap, deleting the core leaves isolated leaves. One can recolour one leaf from0 to4 as a complete singleton Kempe component, changing one external palette; Theorem1.3(b) then allows extension. Arbitrary critical exteriors may bind those leaves into Kempe components that meet other endblocks. S004 shows a one-swap lock and S005 resolves only its explicit noncritical gadget by two swaps. Copying that gadget's private-vertex argument to a critical exterior is unsupported: the required isolated component is absent from the hypotheses.

A surviving route is to prove that every11-colourable exterior of an actual12-critical biplanar graph admits an exterior recolouring that either repeats a neighbour colour or gives distinct palettes at two noncut endblock vertices, while preserving properness at every step. Chains may switch layers; neither planar cyclic order individually separates them. We obtained no such recolouring theorem, bounded multi-swap completeness result or reducible configuration. The density bound in S006_CRITICAL_DENSITY constrains the size of the high/low cut but supplies no common embedding or palette flexibility. These are substantial blocked proof routes, not a lowered upper bound.

## A genuine simultaneous-palette route with a finite edge budget

Further primary inspection of SRC-0027 Section2.2, Lemma3 and its complete local induction proof supplies a useful global statement. For a finite simple graph F and a finite collection M of unequal equal-size pairs(X,Y) of vertex subsets, there is a proper t-colouring good for every pair, with

    binomial(t,2) <= e(F)+|M|.

Good means a colour repeats within X or within Y, or the two colour sets differ. This is a published source lemma, not programme novelty. Its proof is an induction deleting a vertex v: pairs where v lies in both sets or neither retain the good property; a pair with v in exactly one set forbids at most one colour. Each incident graph edge also forbids one colour. If every existing colour is forbidden, those charged edges/pairs pay for the increase from binomial(t,2) to binomial(t+1,2). A new unused colour preserves all remaining good-pair conditions. Equal set cardinalities are essential; identical pairs do not impose a usable constraint. The source's base case uses the elementary e(F)>=binomial(chi(F),2).

Call a low component light if it has an endblock with two noncut vertices x,y whose actual exterior neighbour sets in H differ. Those sets have the same size since both vertices have degree11 and the same internal block degree. If every component of G[L] is light, choose one such pair per component and apply the source lemma to F=G[H]. If e_H+c<=65, the lemma gives t<=11. Regard the colouring as an11-colouring; Theorem1.3(a,b) extends it through every component, and components have no edges between them. This contradicts12-criticality. Therefore

    every low component light  ==>  e_H+c >= 66

for an actual12-critical biplanar graph. This is a conditional programme deduction from precisely inspected published lemmas, not a universal colouring improvement. It avoids assuming palettes equal to actual neighbourhoods: the source lemma deliberately changes the exterior colouring to make the relevant palettes good simultaneously.

A component that is a single K8 must be light in a K9-free critical graph. Each of its eight vertices has four exterior neighbours; if all actual neighbour sets agreed, any one common exterior neighbour together with the core would form K9. Hence a hypothetical12-critical biplanar graph all of whose low components are single K8s obeys e_H+c>=66. Other Gallai components may have every endblock pair sharing an actual exterior set; the argument does not dispose of them. Even in the all-light case e_H+c can grow beyond65 with graph order, so the finite edge-budget condition does not settle large deficit or EMP. The heavy-component route and an all-order simultaneous recolouring argument remain open.
