# S041 adversarial audit

No subagent or external review is claimed; this is the executor's own
falsification and replay.

- Registration order: PLAN hashed 12:40:30Z; the P1 certification scheme was
  revised at 12:41:51Z BEFORE any probe ran (cost estimate), with both hashes
  kept and the orbit-count typo (28->29) corrected in the same pre-run
  revision. P3, P3b and P4 were each appended and hashed after the previous
  result and before their own computation. P3b's first run was interactive;
  its archive re-ran only the clause checker.
- Lemma R1 uses classical inputs (triangulations 3-connected, Whitney, Lefschetz
  on S^2). It covers layer-PRESERVING symmetries of 156-edge pairs with both
  layers triangulations; layer-swapping symmetries, involutions, order3 and
  155-edge pairs are not decided.
- P1 completeness rests on the pair lemma and the T1-T3 tests; each is a proved
  necessary condition for a triangulation, and each failure is a re-checkable
  certificate. Planar layers are checked by an independent stdlib rotation
  traversal; Kuratowski subgraphs by the stdlib subdivision checker. The
  portable checker regenerates orbits and all 50600 candidates without NetworkX.
- Alpha search uses orbit representatives N,S,a0,b0; correctness relies on
  sigma being an automorphism of both layers. Full itertools enumeration agreed
  on 165 pairs (all with few four-sets plus a 5% sample).
- P2 is conditional on SRC-0011 (statement inspected) and, for the K4vH6/K5vH5
  cases, on Gallai's join theorem and the 11-vertex minimum triangle-free
  4-chromatic graph. Counting survivors are necessary-only, not constructions.
- P3/P3b/P4 negatives: UNSAT is accepted only with pinned CaDiCaL DRAT verified
  by pinned drat-trim and every clause justified (layer swap, lex-leader for
  checked automorphisms, spanning-tree and adjacency definitions, Lemma B/C
  instances). The K9 non-biplanarity premise of Lemma B/C is CLM0022 (DRAT).
  The portable CI checker verifies archive hashes and regenerates the graphs;
  DRAT and clause justification are local receipts, as in S025.
- Plain Kuratowski CEGAR returned UNKNOWN at 600 s for the first leaf graph;
  that cap was never used as a negative. Cover-anneal plateaus (1-2 uncovered
  edges) are heuristic only.
- Only three leaf shapes were tested; R3 is ranked first because it does not
  need chi_f>9, not because any positive evidence exists. If F9-like K9-minor
  obstructions extend to all leaves, R3 closes too; S042's gate says so.
- Rankings are judgements under registered criteria, not theorems.

Frozen S036-S040 artifacts and sources unchanged. S036 stopped; nine sorted
prefixes UNKNOWN; star/patch/coordinated hill-climbing stays parked.
