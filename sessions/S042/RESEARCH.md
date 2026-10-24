# S042 research — certified apex-leaf census (route R3), 24 October 2026

No chi>=10 witness; 9<=chi_2<=12. D077-style gate: **PIVOT** (no live leaf).
All statements concern the registered finite census (PLAN.md, PLAN_ADDENDUM.md).

## Leaf lemma and scope (CLM-0141)

Let H be a Hajos composite of (10-a)-critical graphs, a in {1,2,3}. Each
composition leaf L occurs in H as L minus one edge e (Hajos deletes xy from one
operand and xw from the other and identifies x), so K_avH contains
Lambda(L,e) = K_av(L-e). For every e exactly one holds: (i) omega(Lambda)=9, so
K_avH contains K9; (ii) e(Lambda) > 6|Lambda|-12, which holds for every e
exactly when e(L) exceeds the leaf budget (6-a)n+6a-11-a(a-1)/2; (iii) Lambda is
a census leaf graph. Hence K_avH is not biplanar as soon as ONE leaf L lies
outside the UNRESOLVED classes and all census leaf graphs of L are
non-biplanar. For general DHGO composites this covers the edge-deleted operand
only; a vertex-split operand contributes G2-z plus split edges (not covered).

## Type reduction (CLM-0142)

By Gallai (SRC-0027) L = K_c v F_1 v ... v F_r with join-irreducible critical
factors, k_j>=3, |F_j|>=2k_j-1; 3-critical irreducible factors are odd cycles.
Factor edges obey Kostochka-Yancey, with equality iff k-Ore, and non-Ore
factors obey the Theorem 6 bound of SRC-0020 (y_k = max{2k-6, k^2-5k+2}). For
|L|<=21 exactly 45 (a,c,factor) types meet the leaf budget; a separately
written stdlib derivation reproduces the table. Fifteen are RESOLVED: C5 with
c=7-a; 6-Ore on 11 with c=4-a; 7-Ore on 19 with c=3-a; and 7-critical factors on
17 or 18 vertices, where only Ore graphs could fit and none exist. Thirty are
UNRESOLVED non-Ore windows: 9-critical irreducible on 17-21 vertices (a=1,
c=0), 8-critical irreducible on 15-21 (a=1 c=1; a=2 c=0), 7-critical
irreducible on 13-16 (a=1 c=2; a=2 c=1; a=3 c=0). No claim about them.

## Generation and census (CLM-0143)

k-Ore graphs were generated as every DHGO composition with the registered
Aut(K_k) reduction; full and reduced generation agree on 6-Ore/11 (2 classes)
and 7-Ore/13 (3 classes). Counts: 6-Ore/11: 2; 7-Ore/13: 3; 7-Ore/19: 91;
8-Ore/15: 3; 9-Ore/17: 4. Over all types, 23514 (a, L, e) choices were tested
for omega and budget; they collapse to 97 non-isomorphic leaf graphs. The Ore
leaves from 8-Ore/15 and 9-Ore/17 give none: every deletion leaves a K9.

| Leaf graphs | n / m (slack) | Source | Lemma B / C models | Verdict |
|---|---|---|---|---|
| 1 | 12 / 60 (0) | C5, (K7-e)vC5 | 80 / 440 | non-biplanar |
| 2 | 15 / 78 (0) | 6-Ore/11, (K4-e)vF | 444-560 / 3400-4288 | non-biplanar |
| 3 | 16 / 82 (2) | 7-Ore/13 (PARTIAL type) | 790-984 / 6388-7952 | non-biplanar |
| 91 | 22 / 120 (0) | 7-Ore/19, (K3-e)vF | 4680-13404 / 42744-122496 | non-biplanar |

Every verdict: Lemma-B/C K9-minor CEGAR UNSAT in one iteration with zero
Kuratowski lemmas (at most 4.1 s), pinned CaDiCaL DRAT verified by pinned
drat-trim, every clause re-justified by tools/s025_check_minor_cert.py. The K9
premise is CLM0022. An independent replay (separately written DHGO, joins and
omega computed on each leaf graph, NetworkX could_be_isomorphic prefilter plus
exact VF2, no WL hashing) maps each of its 133 raw leaf graphs to exactly one
recorded graph and hits all 97 (76 CPU s); a slower degree-only-prefilter
variant was stopped unfinished as redundant. CNF and lemma files regenerate byte-identically
from the committed edge lists; the committed DRAT proofs re-verify against them.

Consequence: within the resolved domain no apex leaf exists, so no K_avH with a
Hajos composite H having a leaf from these types is biplanar, for a=1,2,3. In
particular apex-over-Hajos constructions from odd cycles, 6-Ore and 7-Ore
graphs (19 vertices included) are closed. What remains of R3 is the non-Ore
near-extremal critical graphs of the UNRESOLVED windows (where K1vF with F
9-critical, omega(F)<=7, e(F)<=5|F|-6 would be a direct witness) and DHGO
vertex-split operands; neither can be enumerated with current sources.

## Gate

(A) no witness. (B) no live leaf: all 97 leaf graphs are certified
non-biplanar. Decision PIVOT. Per the registered fallback S043 is R1's exact
order-3 layer-symmetric class at order 28 (CLM-0137); its prompt carries its
own gate and, on PIVOT, an owner-decision audit instead of further slices.

Experimental CPU 2671.4 s of 3600 (includes the stopped first run, 900 s, and
generation 622.1 s); one further failed start after the reduction control
(node-label bug, under two minutes) is not separately metered. Replay and
local DRAT re-verification are separate.
