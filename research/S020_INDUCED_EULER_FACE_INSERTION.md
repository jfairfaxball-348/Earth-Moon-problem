# S020 — exact induced Euler constraints and reversible Kuratowski insertion (methodology; not a biplanarity verdict)

## Fixed original graph, source correctness

The only active original object is index 148 in validation/S003/survivors_alpha_ge3.json, reconstructed with tools/blowup_graph.py. It has n=25 and m=131; the ordered edge-file SHA256 must be 4f8dab6cb2f936ba0c69613decab88f578e4692926baa09b4d387289cefae598. Historical χ(G)=10 is inherited from independently checked S004 original nine-colour UNSAT certificates together with a proper ten-colouring, not re-established merely by a planar partial.

## Soundness of necessary global and induced constraints

If E(G)=E1 disjoint_union E2 and each layer is planar, then every vertex subset U of size at least three induces a planar simple subgraph on |U| vertices within each layer. Therefore |E_i(G[U])|<=3|U|-6 for i=1,2. Applied to the whole labelled vertex set, each layer holds at most69 original edges, and the total131 forces at least62 in each.

The S020 formula has one original Boolean x_e per each of the 131 *original edges*. For every preregistered dense subset U, let M_U be precisely the original edges with both endpoints in U, and b_U=3|U|-6. Add the two at-most constraints sum_{e in M_U} x_e<=b_U and sum_{e in M_U}(1-x_e)<=b_U. The PySAT sequential-counter encoder introduces fresh auxiliaries starting above the previous maximum variable ID for EACH constraint. By the at-most encoder's existential extension property, a truth assignment of the original variables satisfies the new CNF for some values of those distinct auxiliaries if and only if it obeys both necessary local counts. Every actual two-planar edge split can be extended to a satisfying assignment to these counters. Unlike complete embedding constraints, the Euler bounds are only necessary; they cannot establish biplanarity from SAT.

A vertex subset U with |M_U|>2b_U would be an elementary independent nonbiplanarity obstruction; the code raises an explicit audit-needed event if one is found. Such a finding would require independent re-generation and count from the immutable original before status promotion; an error/flag alone is not certification. The same applies to all numerical source or formula assertions.

## Bounded obstruction-guided insertion

Start from the exact verified S019 split into E1 (62 original edges), E2 (63), and six unplaced source edges, with disjoint union equal to all 131. Search states preserve two individually planar layers and their complement of still-unplaced original edges. For a pending edge e, either planar layer can receive it if an independent planarity test passes. If adding e to a currently planar layer produces a Kuratowski obstruction K, then K necessarily includes e, since the layer without e was planar. Any route that retains e *and makes that layer planar solely by deleting existing edges* must remove at least one old edge of K; branching on each candidate deletion is therefore a sound local case split. Displaced edges remain pending and must eventually be assigned; nothing is silently dropped. Every full positive must pass independent exact edge cover, original source, and full planarity/rotation checks plus original chromatic proof smoke.

This finite search is NOT globally exhaustive: S020 imposes bounded displaced-edge depth, wall time, node limit, a specific initial partial and visited states. Even exact exhaustion of this **restricted** search tree cannot prove the original graph nonbiplanar. In particular the seven-defect triangulation-cover identity of S018, q+r=7, says NOTHING about the number of edge flips between an arbitrary six-unplaced partial and a full split.

## Independent follow-on constraint family (S021 conditional, not executed here)

For disjoint A,B with s=|A|+|B|>=3, the subgraph consisting only of original edges crossing A to B is bipartite. Its restriction to either planar layer is simple planar bipartite and has at most2s-4 edges. Hence a sound potentially stronger pair of original-variable counters (at most2s-4 in each polarity) may be added; any original cross-edge count >4s-8 would supply an elementary nonbiplanarity obstruction after independent audit. Internal edges within A or within B MUST be excluded when defining the cross edge set. This is a future algorithmic option, not a claim it was computed during S020.

## Evidence standard

The exact job's real terminal run/job/artefact IDs, actual original-source hashes, recorded dense U selection, loaded Kuratowski obstructions, native checked DRAT if any and complete witness if any must be recorded in S020/validation after the run ends. Until there is a full positive or independently checked complete sound negative, graph148 remains BIPLANARITY_UNKNOWN; no new global χ₂ lower bound follows from partials, counters or caps.
