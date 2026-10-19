# S027 adversarial review

1. **Executor identity.** The saved prompt said "through Codex"; the owner invoked
   S027 from a local Claude Code session on the same workstation. Same pinned
   binaries, full smoke gate, supervision and caps. Recorded in OWNER_INVOCATION;
   no scientific consequence.
2. **Pilots before registration.** Scratch pilots of the generator, self-test, a
   30 s size-4 run and one audit preceded PLAN.md, and two registered values
   (generator conflict budget, one-admitted-per-profile rule) were set after the
   first pilot. The pilot output is discarded; the registered run reproduced the
   pilot's counts exactly (deterministic seeds), so no cherry-picking among runs
   was possible, but the rules were not fixed blind. Disclosed in PLAN.
3. **Soundness of learned clauses.** Each clause rests on (a) a certified
   obstruction (S025/S026 native DRAT, K9 thickness 3) and (b) the support lemma.
   Every one of the 62918 clauses was rechecked by tools/s027_check_learned.py,
   which rebuilds obstructions from their definitions and imports neither the
   generator nor the encoder. Negative controls: the checker rejects a clause
   missing one support edge, a non-weight-preserving permutation, and an Euler
   clause one edge short. In-loop UNSAT answers are never used as evidence; only
   SAT maps (explicitly checked twice) create clauses.
4. **Domain claims depend on the edge-cardinality encoding.** A too-strong
   sequential counter would make "profile closed" unsound. The independent
   regenerator uses the same pysat CardEnc (shared library dependence, as in
   S026). Mitigation: scripts/check_s027_cardinality.py tested 1200 boundary-biased
   assignments over all 30 profiles (364 at counts 155-157): SAT exactly when the
   explicit blow-up count is <= 156. Not a proof of the library; recorded as a
   residual trust assumption.
5. **Domain scope.** "Closed" means: no alpha<=3, K9-free, <=156-edge blow-up in
   that labelled profile is biplanar. Profiles with alpha>=4 members, other
   weight vectors, other orders or non-blow-up graphs are untouched.
6. **alpha encoding.** "Every 4-set of base vertices has an edge" is equivalent to
   alpha(B[w])<=3 because an independent set of a clique blow-up meets each bag at
   most once and projects to an independent set of B. Rechecked by brute force on
   all 84 filter-clean 28-vertex graphs.
7. **UNKNOWNs are not negatives.** Four admitted graphs, 78 surplus graphs, 13 P29
   deletions and two C5 classes are UNKNOWN at caps. Anneal residues (7-15 edges)
   are heuristic. No graph is reported biplanar.
8. **Descent timing.** The single certified deletion finished in 58.9 s against a
   60 s cap; its certificate is complete and cold-replayed, but the other 13 at
   ~62 s are cap artefacts, not evidence.
9. **C5 strategy change.** Only branch-set size changed (3 -> 4) with the same
   proved lemma; seeded cuts were re-verified one by one. The independent S026
   checker places no size restriction on branch sets; regeneration uses the S027
   class with the recorded size flag. Positive controls passed. Internal SAT state
   was not resumed.
10. **Provenance.** Tool hashes were recorded at launch; all 35 match the committed
    bytes. Post-run, CLM numbers were renumbered (CLM-0101 already existed); the
    executed tools/s027_contain.py docstring therefore still names the support
    lemma "CLM-0101" — read it as CLM-0102. PLAN.md's reference was updated for the
    renumbering only.
11. **Repository size.** validation/S027 adds ~170 MB (three C5 DRAT proofs of
    28-49 MB gz). Certified-C5 cut checkpoints are omitted (superseded by full
    lemma records + DRAT); the two UNKNOWN checkpoints are kept for S028.
12. **Novelty.** rStation forum work (SRC-0042) already searches alpha3 clique
    blow-ups at orders 25-29 with K9-linking rejections; Patil and Trivedi cover C5
    blow-ups. No novelty or priority is claimed for any S027 result.
13. **Headline.** No certified chi>=10 biplanar graph. 9<=chi_2<=12.
