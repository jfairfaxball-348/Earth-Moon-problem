# Reduced heavy classes and a simultaneous extension criterion

Work in an actual finite simple12-critical biplanar G. Let L={degree11 vertices}, H=V-L. Gallai/Theorem1.3 and the published good-colouring Lemma3 are dependencies SRC0027, not new methods. The heavy long-odd and heavyK8 exclusions leave smaller heavy clique blocks, C5, and light components unresolved. The following is a SUFFICIENT criterion with an explicit missing existence hypothesis, not a universal theorem.

## An independent repeated-colour set

Choose an independent R subset H. For every nonlight low component C choose a noncut vertex x_C in an endblock, with its actual common high-neighbour set A_C. Require |R intersection A_C|>=2. This also covers a whole/singleton block if it has the stated neighbourhood; if no such choice exists, the criterion is simply unavailable.

For each light component choose a noncut endblock pair with distinct equal-size actual exterior sets X,Y. Call the pair safe for R if at least one of the following holds:

1. One of |X intersection R|,|Y intersection R| is at least2.
2. These two intersection sizes differ.
3. Both intersection sizes are equal and at most1, and X-R != Y-R.

In case3 the residual sets have equal cardinalities and are unequal, so collect those residual pairs in M. Assume EVERY chosen light pair is safe, and

    e(G[H-R])+|M| <=54.

SRC0027 Lemma3 produces a proper t-colouring of H-R good for every pair in M with choose(t,2)<=54, hence t<=10. Empty H-R uses zero colours; duplicates in M may be discarded, weakening the budget. Use colours1..10 and assign colour11 to EVERY vertex of R. Independence of R and the unused colour make the entire high-graph colouring proper, including edges to H-R.

Every heavy component has a selected vertex with two high neighbours coloured11, satisfying Theorem1.3(a). For a safe light pair, case1 also gives(a); case2 gives different exterior palettes because exactly one set has colour11 when both intersection counts<=1 (if one count>=2 use case1). In case3, good residual colouring supplies a repeated residual colour or unequal residual palettes; adjoining the same colour11 to both palettes when intersection size1 preserves this condition, because11 is absent from every residual palette. Thus Theorem1.3(a) or(b) holds for EVERY component of L. Extend independently through each; no edges run between components. This gives a proper11-colouring of G, contradicting12-criticality.

Therefore an actual12-critical biplanar graph cannot admit such R, safe pair choices and the residual54 budget simultaneously. This all-order conditional obstruction includes R empty/all-light with budget54; the older direct all-light budget65 is stronger there and remains valid. It permits R to reduce the high edge budget, but no existence of R, safe light pairs or a bounded residual graph is proved. No high colouring or low-block contractions are assumed to preserve planar layers.

## Why local repeated-pair choices do not supply R

The graph with one edge01 and isolated vertex2 has marked sets{0,2},{1,2}. Each individually has a nonadjacent pair. Requiring both sets nonrainbow forces0=2=1, contradicting edge01, for ANY number of colours. This also prevents an independent R from containing two vertices of each set. An edge plus a low-component count is not by itself a general good-colouring theorem for identical heavy sets. The finite registered domain has2692 marked instances on all labelled graphs of order1..4 with one/two eligible set multisets and all proper3 assignments:2521 feasible,171 infeasible with three colours. The explicit first counterexample is impossible with arbitrarily many colours by the hand argument; other finite infeasibilities are only3-colour results.

An attempted augmentation that marks an independent pair by ADDING an edge forces those vertices different, whereas heavy extension needs a repeated colour. Individually recolouring one marked endpoint with a common spare colour cannot be performed simultaneously if chosen endpoints are adjacent. Independent support selection and light-pair safety have to be proved, not inferred from each local independent pair or Hall representatives.

Likewise the source Lemma3 vertex-deletion budget cannot be copied from unequal equal-size pairs to arbitrary rainbow-forbidden sets. If two previously coloured vertices of a three-set use0,1, every old colour2..10 makes that set rainbow when used on its last vertex: NINE colours can be forbidden by one constraint. The source's one-forbidden-colour-per-pair charging premise fails. This is an abstract assignment counterexample, not an actual critical biplanar graph.

These failures do not disprove the desired EMP theorem or the sufficient criterion above: the toy marked sets have size2 rather than actual heavy boundary sizes, and they do not include all criticality/degree/K9 constraints. A lift with three common clique vertices and marked five-sets still only refutes the generic marked-set assertion; attaching a heavyK7 core would create K9, so it is not a critical-counterexample construction. All-order large deficit and actual simultaneous existence remain the essential open obligations.
