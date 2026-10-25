# S046 adversarial review

## Diagnostics (E1)

- Census correctness. The 9-core of every one of the 642381 saved records was
  computed by NumPy peeling over the archived layer bits. Every one of the 300
  sampled records was independently re-parsed, its rotation systems and saved
  nine-colouring re-checked, and its 9-core order recomputed with NetworkX core
  numbers; all 300 agreed (assertion in scripts/s046_diagnose.py).
- An empty 9-core means repeated deletion of degree-<9 vertices removes the
  whole graph, so a smallest-last greedy colouring uses at most nine colours.
  Such a graph contains no subgraph of minimum degree nine and hence no
  10-critical subgraph. This is an elementary argument, not a solver claim.
- Exact duplicates use packed full bit strings as dictionary keys, not hashes.
  Isomorphism classes use a Weisfeiler–Lehman screen and VF2; every claimed
  isomorphism mapping was checked edge by edge. Non-isomorphism within a
  WL bucket relies on VF2's exact search; across buckets on WL invariants.
- Sampling limitations: strata are thirds of the global record index, not of
  wall time or slice; S045's first campaign file holds 272374 records, so the
  early stratum is entirely inside it. Sample proportions describe saved
  records only. The full-archive 9-core fraction is an exact census of saved
  records, not of the domain or of graphs the solver considered internally.
- The first E1 execution crashed while formatting its report (integer
  dictionary keys) after computing but before printing anything; no outcome
  was inspected. Both executions are charged to the E1 budget.

## Encodings and reductions

- Lemma S needs a relabelling-and-swap-closed target set. The non-9-colourable
  biplanar graphs of order n with minimum degree nine form such a set; the
  partition clauses and Kuratowski clauses never remove any member, so adding
  rules (i)+(ii) preserves existence. Exhaustive class checks at n=4,5 and
  graph checks at n=5,6 test the lemma and its CNF; they are not a proof for
  large n (the written proof is).
- The degree counter is two-sided; it is checked against all assignments up
  to eight literals and every threshold, including infeasible thresholds,
  which are encoded by complementary units because PySAT rejects an empty
  clause (found and fixed during controls).
- The first soundness control wrongly demanded representatives for classes
  outside the degree filter; corrected to restrict to the filtered domain.
  Both control failures are retained in this record; no experiment depended
  on them.
- K9-freeness, no cut vertex and edge-count bounds are necessary for cores but
  were not encoded. A non-9-colourable candidate is a witness irrespective of
  criticality, so omission cannot hide a witness.
- C/CS at order n are not "order at most n" domains. Selected orders never
  exhaust the orders in between.

## Pilots, calibration and decision

- Each arm is one 60 s run of a deterministic configuration (CaDiCaL has no
  seed here; the stop instant is timing-dependent). There is no replication,
  so the comparison is coarse; Wilson intervals describe only the analysed
  sample of each arm, not the domain.
- The targeting metric counts only drat-trim-checked non-8-colourability, and
  no candidate even required a SAT call: every analysed candidate has an
  explicit, independently checked colouring with at most 8 colours. Hardness
  of colouring instances was never used as evidence.
- Accounting: the first E2 invocation's per-arm guard charged in-slice
  Kuratowski audits (verification under the registration) to E2 and skipped
  n50-CS. The registered rule was applied and that arm ran afterwards in the
  registered position-independent way (fresh state). Raw totals including
  audits remain inside the 1800/3600 ceiling (validation/S046/BUDGET.json).
- A1 was registered after E3 results were known. It cannot alter the S046
  decision and is reported as a post-hoc calibration. Its "none in cap" rows
  are UNKNOWN for existence. Its strongest point is the B arm at n=15/20,
  where a padded K6 v C5 certainly lies in the domain and was not found.
- The unexecuted E4 checkpoint/acceptance drafts were deleted unrun because
  the gate failed; no unverified engineering is committed or claimed.
- No graph produced in S046 is claimed critical, new, or relevant to chi>=10.
  The K6 v C5 rediscoveries are classical (Sulanke) controls.
