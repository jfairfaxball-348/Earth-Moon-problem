# S003 prior-art and overlap audit

Scope: searches on 2026-10-12 (Earth–Moon, biplanar, thickness two, 2026
records, doubly/singly outerplanar, Schnyder/SAT planarity encodings) plus
direct inspection of Patil's public repository. Not an exhaustive novelty
guarantee.

## Inspected this session

- SRC-0017 Patil, public repository github.com/Volkopat/earth-moon-biplanar,
  commit 5cb2ca9f6d4d6d195617c09f7348841636b646f6 (26 Aug 2026), CC BY 4.0
  data / MIT code. Read: README; paper/earthmoon.md §§3 (exclusions incl.
  3.3b), 4 (order ladder, Gallai join cases), 7.1–7.2 (upper side), 9–11
  (C5(3,4,3,4,3) thickness 3), 16 (open problems). Used: the 159 graph files
  of data/graphs/pool (apex lane). Their SMS verdicts take planarity theory
  lemmas as axioms; their certified status is SOURCE_STATED here.
- SRC-0018 Doria, Zenodo 10.5281/zenodo.21824308 (6 Aug 2026), record
  description only: every biplanar graph on <=16 vertices is 9-colourable,
  conditional on Lalonde's census of edge-7-critical graphs on 13 vertices.
- SRC-0009/0010 Szeider (alpha<=2) unchanged from S002; still SOURCE_STATED.
- SRC-0019 Schnyder (Order 5 (1989) 323-343, DOI 10.1007/BF00353652):
  metadata verified; the theorem "planar iff dimension <=3" is used in its
  standard textbook form (SECONDARY_ONLY), only for the v1-v3 encodings.
- SRC-0020 Kostochka–Yancey, A Brooks-type result for sparse critical
  graphs, arXiv:1408.0846: abstract only (equality characterisation). The
  y_k-refined bound used by SRC-0017 for n>=89 is not inspected by us.
- SRC-0021 Patil, github.com/Volkopat/earth-moon-chi10: search excerpt
  only ("candidates and obstructions for a 10-chromatic biplanar graph");
  fetch returned 404 and clone needed credentials. METADATA_ONLY.
- SRC-0022 Weaver, "Utilizing graph thickness heuristics on the Earth-moon
  problem", Rose-Hulman Undergrad. Math. J. 24(2): abstract and reference
  list only. SRC-0023 Wichman–Critchfield, "Exploring the earth-moon problem
  for doubly outerplanar graphs": known only from that reference list.
- SRC-0024 Wetzler–Heule–Hunt, DRAT-trim (SAT 2014, DOI
  10.1007/978-3-319-09284-3_31): tool citation (metadata).

## Overlaps and corrections

1. **S002 CLM-0011 is superseded** by SRC-0017 Observation 7.1.1 (n>=89
   for 12-chromatic biplanar graphs), which predates S002. S002's prior-art
   audit missed it. Recorded as a correction; CLM-0011 is retained as a
   weaker, correct statement with an annotation.
2. Small-order Gallai-join attacks are already done by SRC-0018/SRC-0017;
   S003 deliberately did not repeat them.
3. The face-deficit codegree lemma (S003 Lemma 2/Cor. 3) overlaps SRC-0017's
   "facial-incidence"/"edge-codegree" exclusions (statements not seen) and
   their double Euler identity; no novelty claimed.
4. The apex/K2-join reductions from singly/doubly outerplanar graphs (S003
   Observation 9) are elementary and quite possibly in SRC-0003, whose
   full text remains inaccessible (title mentions singly and doubly
   outerplanar graphs). No novelty claimed.
5. C5 clique blow-ups: S002 settled their chromatic side; SRC-0017 certified
   C5(3,4,3,4,3) and C5[4,4,4,4,3] non-biplanar (SMS with theory axioms).
   S003 biplanarity verdicts for other C5 patterns are new computations to
   our knowledge, not new theorems of a different kind.
6. The base FCptO (K4 with the three edges at one vertex subdivided) blow-up
   family of certified 10-chromatic graphs passing all counting filters:
   not found in SRC-0017's named candidates (its α<=2 quotient pocket and
   strong products differ); novelty of the candidate family itself is
   unchecked beyond this.

No publication, novelty or formalisation gate advances.
