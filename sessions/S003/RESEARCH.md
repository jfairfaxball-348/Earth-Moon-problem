# S003 research dossier

Outcome: **EMP remains open; 9 <= chi_2 <= 12 unchanged.** No certified
biplanar chi>=10 graph, no universal improvement of 12. Session ended at the
owner's request before the pending oracle runs finished.

Substantive results (details in the research/ dossiers):

1. **Certified pure-CNF biplanarity oracle (CAM-0003 v4).** Kuratowski
   lemma clauses, each independently re-checked as a K5/K3,3 subdivision,
   plus sound lex-leader symmetry breaking; final refutation DRAT-checked.
   Calibration: K9 non-biplanar, 24,946 lemmas, drat-trim VERIFIED, 0 RAT
   (CLM-0022). No planarity "theory axioms" (unlike SMS). Positive verdicts
   are explicit layers checked by two planarity checkers (CLM-0023).
2. **Clique blow-up census (CAM-0004).** Exact reductions (zero weights,
   components, twins, K9, 10-core) plus Euler/triangle-free filters and
   exact 9-colourings. Every biplanar clique blow-up of a graph on <=6
   vertices is 9-colourable (CLM-0019). At 7 and 8 base vertices the census
   leaves 13 and 828 counting-feasible chi>=10 survivors; 570 are Szeider's
   alpha=2 pocket; **271 alpha>=3 candidates on 30 bases are new candidate
   families** — e.g. the base FCptO (K4 with three edges at one vertex
   subdivided), chi=10 by hand proof and DRAT, surviving max-cut, maximum
   triangle-free, codegree and local K9-minus-star tests (CLM-0020/21).
   Their biplanarity is UNKNOWN; every one contains an induced C5
   sub-blow-up, so a C5 classification would decide most of them.
3. **Apex/face-cover lane.** Face-cover characterization (CLM-0015),
   facial-deficit codegree bound (CLM-0016, generalizes the saturated bridge
   obstruction), rim lemma, outerplanar reductions (CLM-0018); applied to the
   SRC-0017 corpus: 155 of 159 apex bases excluded, 4 UNKNOWN (CLM-0025).
4. **Upper bound.** Double-wheel lemma (CLM-0017): a 12-critical biplanar
   graph with deficit D<=11 has >=24-2D degree-11 vertices whose
   neighbourhoods are two link cycles. The Kempe-chain step still fails for
   layer-switching chains; obligation isolated in research/S003_UPPER_BOUND.md.
5. **Record correction.** S002's CLM-0011 (n>=78+11D) is superseded by
   SRC-0017 Obs. 7.1.1 (n>=89), missed by S002 (CLM-0024 SOURCE_STATED).

UNKNOWN (not negative) items: biplanarity of all 271 alpha>=3 survivors,
of the C5 patterns (2,6,2,6,2), (2,3,5,2,6), (2,5,3,3,5), (2,3,5,3,5)
(1 h CEGAR each, the last stopped at closeout), the 4 corpus apex targets,
apex(C5[K3]); k=8 census has no independent cross-check; chi=10
certificates missing for the 738 part-0 survivors (incl. alpha>=3 ones).
