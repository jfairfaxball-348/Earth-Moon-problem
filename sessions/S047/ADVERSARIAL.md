# S047 adversarial review

1. Is "proof by contradiction" genuinely different? Only for template T3.
   T1/T2 arguments certify explicit graphs; their biplanarity still needs
   layers. By compactness every refutation of H implies a finite witness.
   Recorded in RESEARCH Q1; the D079 scope amendment is therefore narrow in
   practice.
2. O1 depends only on chi_2 <= 12 (classical Euler/degeneracy). It forbids
   uniform transfer lemmas, not one-shot ones: a single operation applied to
   a single seed is untouched. O1 is a design constraint, not an exclusion.
3. O3 depends on Kostochka-Yancey (SRC-0011/0020, statements inspected, not
   proofs) for k = 9; its conditions (n >= k, n != k + 1) hold for a
   9-critical subgraph. The closed form and finite ranges are checked
   mechanically; the general inequality is the displayed one-line algebra.
   Level conventions for generalised Mycielskians differ between papers;
   O3 covers every construction with at least two levels plus apex. The
   one-level case is the cone, deliberately cited to S041/S042, not redone.
4. O4 covers only Schrijver graphs SG(2k+8, k) for k <= 3 by computation and
   claims monotone growth for larger k only informally (degree grows with
   k); it is recorded as computed for k <= 3 only.
5. E2/A1 encoding soundness.
   - Colour clauses: lemma L1 uses that exactly nine colours exist; the
     checker regenerates the colour clauses without PySAT and confirms they
     are exactly the colour part of every archived eager CNF, and re-derives
     every learned A1 clause from its recorded (s, phi).
   - Filters (Euler on A ∪ B ∪ X' and A ∪ X'; no K9) are necessary
     conditions for biplanarity (Euler; CLM-0022). Cardinality constraints
     use PySAT's sequential counter, a standard encoding; native-mode
     checking regenerates the CNF byte for byte.
   - A1 restrictions: L3 holds only for a solution with minimum |X|; hence
     an individual A1(t) row does NOT say "no solution with exactly t added
     vertices". The certified statement is cumulative: E2 (t <= 4) plus A1
     rows t' = 5..T, all UNSAT, exclude every solution with at most T added
     vertices. L4 is a pure relabelling. L2 justifies an induced seed.
   - Positive controls: the encoder at k = 8 finds K6 v C5 from K5 v C5;
     without filters it finds K7 v C5 at t = 1; a brute-force colouring
     routine agrees with the t = 1 classification.
6. Scope of the exclusion. It concerns supergraphs of K6 v C5 only. A
   10-chromatic biplanar graph need not contain K6 v C5; BGS (SRC-0002)
   list 40 other 9-critical thickness-two graphs on 12-16 vertices and
   infinite permuted-layer families, untested here. "Not found" for capped
   rows is UNKNOWN.
7. Overlap with unrefereed claims: SRC-0062/0073 claim 9-colourability of all
   biplanar graphs on at most 18 vertices; if correct they already imply the
   E2/A1 statement up to t = 7. Our results are independent (hand proof
   t <= 5, DRAT for the computed rows) and do not rely on those claims.
8. Post-hoc amendment. A1 was registered after E2's t = 5 cap and before any
   A1 run; it does not change E2 rows or the gate. Its restrictions are
   proved in RESEARCH before use.
9. Hand proof L5 versus computation. Rows t <= 5 are implied by elementary
   counting; their DRAT proofs are controls, not independent progress. Only
   rows t >= 6 add information beyond L5.
10. Gate. Nothing found is a witness, a candidate, or a calibrated transfer
    operation with a k = 9 instance. Exclusions alone are PIVOT by the
    registered rule.
