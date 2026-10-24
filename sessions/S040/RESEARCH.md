# S040 research — coordinated two-layer stars and the D077 gate, 24 October 2026

No chi>=10 witness; 9<=chi_2<=12. All results concern explicit finite labelled
states, fixed embeddings and registered move families. S11 remains UNKNOWN.
D077 decision: **PIVOT** (no criterion (A), (B) or (C) of PLAN.md was met).

## Compatibility lemma (CLM-0133)

Let L0, L1 be the disjoint layers. A component a in layer0 removes R_a and adds
A_a, staying a simple sphere map with the same edge count and quad deficit
(CLM0129); C_a = A_a intersect L1. Define b in layer1 symmetrically. Then

  L0' intersect L1' = (C_b - R_a) union (C_a - R_b) union (A_a intersect A_b),

because L0 and L1 are disjoint, A_b meets L0 exactly in C_b and A_a meets L1
exactly in C_a. So the pair is a valid planar pair iff C_a <= R_b, C_b <= R_a and
A_a, A_b are disjoint. Type0 (both C empty) is a pairing of two S039-legal
neighbors. Type1 (exactly one C empty): apply the conflict-free component
first; the other is then S039-legal against the updated layer, so type1 is a
two-step sequential S039 path. Type2 (both nonempty): neither component is
legal first, so it is not a two-step composition of these components. Only
types1/2 are the new relaxed family; type2 is the genuinely atomic part.
Controls (CONTROLS.json): the test equals direct final-layer disjointness on the
FULL cartesian products (3,537,572 and 11,090,746 component pairs); every
type0/1/2 pair obeys the decomposition statement; 240 sampled pairs pass a
separate link-cycle, Euler and NetworkX planarity check; conflict-free singles
at the S038 inputs reproduce S039's frozen 766/1045 table exactly.

## Exact coordinated neighborhoods (CLM-0134)

Inputs S039 arms/156-3900-star (I4=82) and 155-3901-star (79); degree3..6
simple-disk relaxed stars, all fillings and triangular targets, no cap.

| Input | Components (conflicted) | Singles min | Type0 n/min | Type1 n/min | Type2 n/min | Strict improvements |
|---|---|---:|---:|---:|---:|---:|
|156 / 82|2092+1691 (1589+1322)|872 / 82|174147 / 89|37206 / 90|4357 / 96|0|
|155 / 79|2542+4363 (2233+4083)|589 / 80|80461 / 83|35953 / 88|2278 / 79|0|

Both inputs are strict local minima for every one-star-per-layer coordinated
move and every S039-legal single star (7 neutral singles at156, one neutral
type2 pair at155). Canonical tables (216,582 and 119,281 rows) are replayed by
an independent chord-subset generator over the full cartesian product, with
delta four-set scoring locally (NEIGHBORHOOD_REPLAY.json) and Python-int OR
masks in the portable checker; all SHA-256 values agree. Selected-family result
only: other embeddings, larger or multi-star moves are not excluded.

## Matched arms and D077 evaluation (CLM-0135)

Twelve unprotected arms (two starts x seeds4000/4001 x star/pair0/coord) and
four protected arms (best193, seeds4010/4011, star/coord), caps150 CPU s,
plateau30, <=400 sweeps. Every unprotected arm ended at its start (82 or 79)
after31 nonmonotone tabu steps; star arms used about3 CPU s, pair0 24-33 s,
coord26-39 s. Protected: star193/193; coord192 (seed4010, one type1 pair at
step2) and193 (seed4011). All482 transitions replay. Hence B1 fails for all
four unprotected coord arms (82>41, 79>39), B2/B3 are moot, and C fails
(192>39). Verdict NO SOLID PROGRESS -> PIVOT. Two seeds and early plateaus are
not a statistical statement. All24 saved records (8 neighborhood bests, 16 arm
bests) have checked <=9-colourings (six by decoded pinned-CaDiCaL models);
protected bests keep the core and have exact chi9. No witness.

## Registered four-set diagnostic (CLM-0136)

| State | I4 | tau (packing=hitting) | Useful pairs | C1 | C2 | C3 | C4 |
|---|---:|---:|---:|---:|---:|---:|---:|
|156 input|82|5|139|137 (483)|2 (9)|0|0|
|155 input|79|7|144|138 (455)|5 (17)|1 (2)|0|
|protected4011|193|10|170|152 (997)|8 (41)|5 (51)|5 (69)|

Bracket closed exactly: every alpha<=3 graph on the same labels adds at least
tau absent pairs. 156 hitting set {10-27,11-21,11-22,12-17,23-25}; 155 {1-14,
1-23,1-24,4-15,9-22,12-26,14-17}. Parentheses give H-incidence. Every four-set
has a pair addable by an S039-legal single move (none needs relaxed pairs; no
locked four-set). Opposite-layer occupancy, the obstruction S040 targeted,
blocks only2/5 useful pairs (9/17 incidence). The plateau is not reachability.

## Post-hoc explanation (not part of the gate; PLAN_ADDENDUM.md)

Unrestricted single union-edge swaps, ignoring planarity entirely: 1631 of
34632 (156) and1358 of34565 (155) lower I4, best -31 (drop free edge5-19,
add10-27) and -19 (drop0-20, add14-17); two/one union edges are free (no
four-set relies on them). So the labelled objective is NOT locally minimal;
local fixed-embedding moves cannot pair a remote free removal with a hub
addition, because a planar insertion must delete the edges it crosses.

The hubs are K9 completions. Each union has omega=8, yet adding the exact tau
hitting set creates K10 (156: K10 minus matching {10-27,12-17} on vertices
1,7,10,12,14,17,19,24,26,27; 155: K10 on0,1,6,10,11,14,17,21,23,24). Five of
139 (two of144) useful pairs individually complete K9 and carry84/492 (27/474)
incidence. The K9-safe hitting number is exactly17 (11), bracket closed by a
safe-pair packing, and even that safe set jointly yields omega9 (10). A max-
safe label-fixed repair gives explicit alpha<=3 156-edge graphs at edit
distance10 (13), both containing K10, so not biplanar. Protected best192:
tau10, tau_safe16. Interpretation: minimizing four-sets at maximal density
drives the unions into near-K9 clusters; the residual four-sets sit on pairs
that biplanarity forbids, and local moves only trade them against critical
edges. This is negative/diagnostic learning, not a construction.

Experimental CPU315.15625 s (neighborhoods4.75, arms279.796875, diagnostics
30.609375); post-hoc7.15625+24.75 s; controls6.078125 s, replay70.33 s, pair
checks1.59 s separate; total far below7200. One experiment process; no S036
or scheduler action. A first validator invocation used an option this CaDiCaL
build lacks (`-t`), returned UNKNOWN for six colour attempts, and was rerun
with a subprocess timeout before any record was kept; disclosed in failures.
