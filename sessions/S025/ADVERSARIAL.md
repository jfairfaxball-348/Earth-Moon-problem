# S025 ADVERSARIAL audit

1. **Dependency on K9.** Lemmas B and C reduce to "K9 has thickness 3". This is classical, and the programme holds a DRAT certificate (S003, re-verified today). It remains an imported theorem. Our DRAT proofs certify only the CNF; clause validity rests on the Lemma B/C hand proofs plus K9.
2. **Clause validity versus DRAT.**
   - drat-trim checks that the CNF is unsatisfiable.
   - `tools/s025_check_minor_cert.py` independently checks that every clause is an instance of a valid family:
     - regenerated lex-leader base;
     - re-checked Kuratowski subdivisions;
     - spanning trees of G[R];
     - adjacency implications with qy ∈ E(G);
     - Lemma C preconditions (Q a K8, R ∩ Q = ∅, r ∈ R, each q ∈ Q∖N(r) has a G-neighbour in R).
   - Auxiliary variables are checked fresh and distinct, so a c- or a-variable cannot double as another literal.
   - Remaining trust: the checker reuses `biplanar_cegar.Cegar` to regenerate lex-leader clauses. That code was audited in S003 and asserts every listed permutation is an automorphism.
3. **Lex-leader soundness with lazily added, non-invariant clause sets.**
   - Soundness needs only that every added clause holds for every biplanar split (aux variables set to their meanings), and that the set of biplanar splits is invariant under the automorphism group and the layer swap. Both hold.
   - The lex-min orbit representative of any split therefore satisfies the CNF. Invariance of the clause *family* is not needed.
4. **Direction of encodings, checked by hand.**
   - x_e = 1 means layer 1.
   - Tree clauses: (∨¬x_e) ∨ c[R,1] and (∨x_e) ∨ c[R,2].
   - Adjacency: (¬x_{qy} ∨ a) for layer 1 and (x_{qy} ∨ a) for layer 2.
   - Lemma C: ¬c[R,j] ∨ ∨¬a[q,R,j].
   - A wrong direction would make clauses vacuous (weaker), not unsound, except that a swapped c1/c2 pairing *could* be unsound. The checker regenerates the pairing from the JSON and the tree orientation.
5. **Transfer soundness.** A row is declared non-biplanar only via an explicit injective vertex map under which every obstruction edge is a row edge (`explicit_check`). The bag-map search can only miss maps; it cannot create false ones. Subgraphs of biplanar graphs are biplanar.
6. **Row labelling.** Rows are regenerated from validation/S003/survivors_alpha_ge3.json with tools/blowup_graph.py, the same generator as S018. The regenerated row148 edge text must hash to 4f8dab6c…; see validation/S025/TRANSFER_271.json, edges_sha256 for row 148.
7. **The C5 threshold is not a theorem about χ₂.**
   - Positive side: 262 explicit splits, re-checked as both layers planar plus partition.
   - Negative side: only for classes with a DRAT certificate (count in validation/S025/C5_CERTIFICATES.json). The rest are UNKNOWN, not negative; the annealing defect 1 is only a heuristic lead.
8. **Annealing results are heuristic.**
   - Row148's "always 4", the n=17 "defect 1", and the α-frontier minima are search outcomes, never lower bounds.
   - The α-frontier statements (e.g. "α≤3 graphs exist up to n=24") are positive certificates only for the n where 0 was reached; checker run on n=24.
9. **Resource deviation (F071).**
   - About 14 concurrent processes exhausted local RAM.
   - One CEGAR run (C5[2,3,4,3,5]) died with MemoryError; three runs and the plain-CEGAR baseline vanished without output; one certification batch died during proof compression.
   - All are recorded as NOT_COMPLETED. Nothing was inferred from them. The baseline comparison "plain Kuratowski CEGAR on C5[2,5,2,6,2]" therefore has no final number; only S004's 120 s UNKNOWN and S003's F014 3600 s UNKNOWN on 18-vertex C5 blow-ups remain as historical baselines.
10. **No GitHub Actions run** was used for science in S025. The local workstation counts as owner-authorised by the session message. The smoke was run on the same machine and toolchain before science, but not in the "same job" sense of D044, since the D044 Actions fallback was not needed.
11. **The 271 corpus is a biased, restricted source.** Its complete negative decision does not reduce the space of possible χ ≥ 10 biplanar graphs beyond these rows, plus any graph containing a certified C5 obstruction.
