# S027 research record

Target (D042): one certified biplanar graph with chromatic number >= 10. Result:
no witness; 9 <= chi_2 <= 12 unchanged. Executed locally (Claude Code) after a
full 271+K9 smoke; one supervised heavy tree, peak private memory 2.7 GiB;
science 19:45-23:55 UTC (15028 s of the 8 h budget).

## Arm A0 — P29 bounded deletion descent (CAM-0033)
P29-B14-0001 = B14[2^14]; the 28 one-vertex deletions form 14 twin classes.
At 60 s exact (S025 --lemmaC5) each: 13 UNKNOWN at cap, one certified:
P29 minus a vertex of bag 12 (27 vertices, 143 edges) is NON-BIPLANAR (UNSAT
58.9 s, 79 iterations; clauses justified, CNF byte-identical, native solve 3.7 s,
drat-trim 2.8 s). It entered the source filter as a 23rd obstruction but excluded
no generated model (27/28-vertex obstructions are too specific to prune).

## Arm A — learned-obstruction source (CAM-0032, main arm)
Mechanism and proof: research/S027_LEARNED_OBSTRUCTIONS.md (CLM-0102). The S026
generator only blocked each labelled model; S027 forbids the CONJUNCTION of the
base edges an explicit obstruction map uses, plus weight-preserving relabelled
images and whole-bag Euler-excess sets.

| quantity | value |
|---|---:|
| profiles (seed 270018) | 30 |
| preloaded S026 maps fitting a new profile | 3167 |
| generated labelled models | 1831 |
| excluded by checked obstruction-support map | 1401 |
| excluded by Euler subset clause | 346 |
| cut density / closed universal-K6 / filter UNKNOWN | 0 / 0 / 0 |
| filter-clean (admitted + surplus) | 6 + 78 |
| learned clauses recorded and independently checked | 62918 |
| profile domains closed with native DRAT | 13 |

Closed profiles (no blocking clause; every learned clause justified by
tools/s027_check_learned.py; CNF byte-identical; drat-trim verified; cold replay):
indices 0-8, 15, 16, 17, 25 — e.g. [4,3^8], [5,5,4,3,3,3,2,2,1], [6,5,5,3,2,2,2,1,1,1],
[6,6,4,3,3,1^6]. S026 closed 5 profiles (by the base formula alone). Statement
(CLM-0103): in each closed profile no alpha<=3, K9-free, <=156-edge 28-vertex
clique blow-up is biplanar. Remaining 17 profiles hit the 100-model cap.
Most frequent obstructions: C5[1,3,5,3,5] (203 models), C5[1,3,5,2,6],
C5[1,4,4,3,5], C5[3,3,3,3,5], C5[1,2,6,2,6].

All 84 filter-clean graphs were independently rebuilt and brute-force rechecked:
28 vertices, <=156 edges, no independent 4-set (alpha<=3, chi>=10 by counting),
omega<=8 (scripts/check_s027_candidates.py).

Admitted graphs (each: 23 audit-form native DRAT absence proofs, S025 backtracking
agreement, two 60 s flip anneals, 600 s exact):

| graph | edges | anneal best uncovered | exact | final |
|---|---:|---|---|---|
| P10-B10-0001 | 154 | 15, 14 | 810 it, 237k cuts | UNKNOWN |
| P11-B10-0067 | 156 | 13, 13 | 772 it | UNKNOWN |
| P20-B11-0070 | 156 | 13, 12 | 806 it | UNKNOWN |
| P22-B11-0043 | 155 | 10, 12 | 783 it | UNKNOWN |
| P26-B11-0051 | 155 | 10, 10 | UNSAT 7.9 s | NON-BIPLANAR certified |
| P27-B12-0040 | 154 | 7, 8 | UNSAT 31 s | NON-BIPLANAR certified |

The two new 28-vertex negatives avoid every previously certified obstruction
(native DRAT), so they are new certified obstructions (CLM-0104), not witnesses.
Anneal residues are heuristic only and never evidence either way.

## Arm B — C5 continuation (CAM-0033)
Preregistered single change: the S026 two-branch lemma with branch sets of size
2..4 (S026: 2..3), seeded with the S026 Kuratowski cuts after re-verifying every
cut as a K5/K3,3 subdivision of G. Positive controls J1 and C5[3,3,3,3,4] satisfy
every size-4 clause under true meanings; independent checker and byte
regeneration pass.

| class | search | iterations | cuts (seeded -> final) | verdict |
|---|---:|---:|---|---|
| C5[3,3,4,3,4] | 3668 s | 1915 | 412724 -> 810511 | UNKNOWN |
| C5[2,3,4,3,5] | 136 s | 50 | 301234 -> 306977 | NON-BIPLANAR (DRAT 61 s / check 105 s) |
| C5[2,4,3,4,4] | 682 s | 856 | 317125 -> 392382 | NON-BIPLANAR (DRAT 262 s / check 552 s) |
| C5[2,4,4,2,5] | 229 s | 74 | 338363 -> 347052 | NON-BIPLANAR (DRAT 143 s / check 194 s) |
| C5[3,3,3,4,4] | 3655 s | 1273 | 334731 -> 539064 | UNKNOWN |

Now 24/26 sum17 classes are certified; the C5 threshold iff remains open on
C5[3,3,4,3,4] (no K8: Lemma C inactive) and C5[3,3,3,4,4]. The three successes all
have a bag of size 2, where size-4 branch sets dominate more K7 cliques.

## Interpretation
Learning from certified obstruction supports turns most of the alpha3 blow-up
profile space into checked negatives quickly; the survivors are few (84) and the
ones tested exactly are either quickly certified non-biplanar or stubborn
UNKNOWNs. The S028 lever is generality: deletion descent on the new negatives to
obtain smaller obstructions, which prune far more than 27/28-vertex ones.
Prior art: rStation forum papers (SRC-0042) already search alpha3 clique blow-ups
at orders 25-29 and find K9-linking certificates for all collected candidates.
