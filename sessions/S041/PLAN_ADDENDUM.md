# S041 addendum — probe P3, registered after P1/P2 and before running P3

Motivation from P2 and RESEARCH analysis (not from any P3 output): among
chi10 joins only K1vH9, K2vH8 and K3vH7 survive counting with the K9 clique
bound. A concrete K1vH9 family is apex-over-Hajos composites of Sulanke
graphs, with each Hajos deletion inside a K6 so omega(H)=7. Every such
K1vH contains, at a leaf copy, K1v(Sulanke minus a K6 edge) = (K7-e)vC5 =
K5 v pentagonal bipyramid (12 vertices, 60 edges, chi 9).

P3: decide biplanarity of that fixed graph with the existing lazy-Kuratowski
CEGAR (tools/biplanar_cegar.py, --seed-small), certify SAT by explicit layers
checked with rotations, or UNSAT by pinned CaDiCaL DRAT + drat-trim plus
tools/check_cegar_certificate.py. Calibration controls first: Sulanke K6vC5
must be SAT and K9 UNSAT. If (K7-e)vC5 is NOT biplanar, the whole apex-over-
Hajos(Sulanke) family is excluded (subgraph monotonicity). If it IS
biplanar, run one explicit K1vH3 (three Sulanke copies, chain, K6-internal
deletions; 32 vertices, 179 edges; chi=10 by Hajos + join) with a 600 s cap;
a cap is UNKNOWN. Separate sequential process; total S041 CPU stays <=1800 s.

P3b, registered after P3 returned UNKNOWN at its cap (plain Kuratowski CEGAR,
264464 lemmas) and before any P3b computation. Same fixed graph K5 v pentagonal
bipyramid. Negative engine: tools/s025_minor_cegar.py --lemmaC 5 (Kuratowski
plus Lemma B/C K9-minor clauses, CLM0090/0091), cap 420 s; UNSAT only counts
after pinned DRAT (tools/s025_certify.py) and tools/s025_check_minor_cert.py.
Positive engine: tools/s025_cover_anneal.py, seeds4101/4102, 45 s each; a
cover with zero uncovered edges counts only after an independent split check.
Caps give UNKNOWN. Cumulative S041 CPU must stay <=1800 s.

P4, registered after P3b certified (K7-e)vC5 non-biplanar and before any P4
computation. Apex-over-Hajos composites need every Hajos leaf L (9-critical)
to have an edge e with omega(L-e)<=7 and K1v(L-e) biplanar. Sulanke fails
(P3b). Two further small 9-critical joins with nonnegative apex budget:
L_b = K3 v Hajos(K6,K6) (14 vertices, 65 edges; leaf graph (K4-e) v
Hajos(K6,K6), 15 vertices, 78 edges) and L_c = K2 v Hajos(K7,K7) (15 vertices,
68 edges; leaf graph (K3-e) v Hajos(K7,K7), 16 vertices, 82 edges); Hajos(Kk,Kk)
is unique up to isomorphism and the K8-killing edge lies in the small clique.
Decide both leaf graphs exactly as in P3b: s025_minor_cegar --lemmaC 5 (cap
180 s each, UNSAT only with DRAT plus s025_check_minor_cert) and
s025_cover_anneal seeds4101/4102 x45 s (SAT only with an independent split
check). Caps give UNKNOWN. Cumulative S041 CPU stays <=1800 s.
