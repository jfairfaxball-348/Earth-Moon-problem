# S003 — clique blow-ups of all small bases (CAM-0004)

## Statement targeted

For a graph B on vertex set [k] and w∈Z_{>=0}^k, B[w] replaces i by a clique
Q_i of w_i vertices and joins Q_i completely to Q_j when ij∈E(B). Odd cycles
(S002, CLM-0009) and complete multipartite substitutions are special cases.

**Theorem 5 (target of CAM-0004).** For every graph B on at most K vertices
and every weight vector w, if B[w] is biplanar then chi(B[w])<=9.
K is the largest base order for which CAM-0004 completed (see results).

## Reductions (complete proofs)

R1 (zero weights). B[w] with w_i=0 equals B'[w'] for the induced base on the
support; it has fewer base vertices.

R2 (components). If B is disconnected, B[w] is the disjoint union of the
blow-ups of its components and chi is the maximum.

R3 (true twins). If ij∈E(B) and N[i]=N[j], then Q_i∪Q_j is a clique with the
same outside neighbourhood, so B[w]=B/ij[w'] with w'_{ij}=w_i+w_j on a base
with one vertex fewer.

R4 (weights <=8). A bag with w_i>=9 contains K9, which is not biplanar
(classical; proof inspected in SRC-0014). So every biplanar instance has
w∈{0..8}^k, and after R1-R3 it is a positive-weight blow-up of a connected,
true-twin-free base on <=k vertices.

R5 (10-core). If chi(B[w])>=10 and bag i has closed weighted degree
c_i=w_i+sum_{j~i}w_j<=9, then chi(B[w-w_i e_i])>=10: a 9-colouring of the
rest leaves at least 9-(c_i-w_i)>=w_i colours free for Q_i. Repeating, every
chi>=10 blow-up contains (as an induced subgraph, hence still biplanar) a
chi>=10 blow-up whose bags all have c_i>=10. The residue is again reduced
by R1-R3; closed weighted degrees are unchanged by R2 and R3.

Hence Theorem 5 for base order <=K follows if every positive weight vector
on every connected true-twin-free base of order <=K that satisfies
c_i>=10 for all i either violates a necessary biplanarity condition below
or admits an explicit 9-colouring.

## Necessary conditions (theorems)

F1 weighted clique number <=8 (K9-freeness).
F2 every union X of whole bags with |X|>=3 has e(X)<=6|X|-12 (Euler, two
   layers; valid for disconnected layers).
F3 if S is a set of bags and F⊆E(B[S]) is triangle-free, the cross edges
   along F form a triangle-free subgraph of B[w] (a triangle would need three
   pairwise F-adjacent bags), so there are at most 2(2|S|-4)=4|S|-8 of them
   when |S|>=3 (triangle-free planar graphs on n>=3 vertices have <=2n-4
   edges; again valid for disconnected layers).

These are exactly the arguments of S002's C5/C7 proof and of SRC-0007's
strong-product exclusion, applied uniformly.

## Method and independent check

tools/blowup_census.py: DFS over weights 1..8 with F1/F2-prefix and 10-core
pruning (each pruned subtree is counted with its multiplicity, so every one
of 8^k vectors per base is accounted for; the program asserts the total);
leaf: all-subset F2, greedy colourings in three orders, then an exact SAT
9-colouring (pysat/CaDiCaL 1.5.3 inside python-sat); only non-9-colourable
vectors are tested with F3 (exact maximum triangle-free sub-weight by
branch and bound); vectors failing F3 are excluded, the rest would be
SURVIVORS. Every 9-colouring found is re-checked edge by edge in the program.

tools/blowup_census_check.py: an independently written route — NetworkX
graph6 parsing and clique enumeration, numpy materialisation of all 8^k
vectors, vectorised F1, 10-core and full-subset F2 filters, a separate exact
colouring by search over multisets of maximal independent sets, and a
separate triangle-free maximisation (branching on a triangle's three
edges). The counts "kept = colourable + F3 + survivors" must coincide with
COL+F3+SURV of the main tool.

## Results

Counts from validation/S003/census_*.json (main tool) and the checker.

| k | twin-free bases | COL | F3 | survivors | checker |
|---|---|---|---|---|---|
| 1-4 | 1/0/1/3 | 0/0/0/24 | 0 | 0 | agrees k=3,4 |
| 5 | 11 | 168 | 15 | 0 | agrees |
| 6 | 61 | 1739 | 18 | 0 | agrees |
| 7 | 161 | 29986 | 282 | 13 | agrees exactly (same 13) |
| 8 | 7442 | 1016154 | 3232 | 828 | NOT run (infeasible here) |

**Theorem 5 holds for K=6 (CLM-0019).** It is not established for K=7,8.

Order 7: all 13 survivors are blow-ups of the single base FCptO (K4 with
the three edges at one vertex subdivided: hub h, subdivision bags s_i,
triangle bags t_i, edges h-s_i, s_i-t_i, t_i-t_j), N=25-26, 133-138 edges.
chi=10 exactly (CLM-0021): hand proof — bag h lies only in independent
sets of size <=2 and all others have size <=3, so a 9-colouring covers at
most 2w_h+3(9-w_h)=27-w_h vertices, while every survivor has N+w_h>=28;
plus DRAT and explicit 10-colourings. They pass F1-F3, exact max-cut
(<=84 vs 92/96) and exact maximum triangle-free subgraph (<=92 vs 92/96).
Each contains one of three 18-vertex cores J1-J3 and a K9 minus a 2- or
3-edge star, but all of those are biplanar (CLM-0023). Biplanarity of the
13 graphs: UNKNOWN after Schnyder v2/v3 (3600 s) and CEGAR v4 runs.

Order 8: 828 survivors on 32 bases. 570 have alpha(B)=2 and N=19: exactly
the Gethner–Sulanke 19-vertex pocket, closed by Szeider (SOURCE_STATED) —
an external consistency check of the census. The other 271 have
alpha(B)∈{3,4}, N=22..32, on 30 bases (validation/S003/survivors_alpha_ge3.json);
chi=10 certified for the 90 survivors of part 1 only.

Every survivor contains an induced C5 sub-blow-up. 235 of the 271 alpha>=3
survivors contain one of the 18-vertex C5 patterns (2,6,2,6,2), (2,3,5,2,6),
(2,4,4,2,6), (2,5,3,3,5), (2,3,5,3,5), (2,4,4,4,4), (2,4,4,3,5), (3,3,4,3,5);
36 have no C5 sub-blow-up larger than 17 vertices. A certified
non-biplanarity verdict for a pattern removes every survivor containing it.
The four patterns attempted were all UNKNOWN (CAM-0003 Amendments F-H).
There are exactly 13 maximal C5 patterns passing F1-F3 (nine with N=18,
four with N=17); (3,4,3,4,4) dominates SRC-0017's certified non-biplanar
C5(3,4,3,4,3).

Facial identity for C5 blow-ups (proved in S003, used to explain why hand
counting stalls): with X cross edges, each layer satisfies
2X_L = 4n-8-δ_L-2t3_L-Λ_L-4(c_L-1) (δ_L internal-edge sides on faces of
length >=4, t3_L facial triangles inside one bag, Λ_L=Σ(len-4), c_L
components). Hence a biplanar C5 blow-up has total penalty exactly 4n-8-X
(12 for (2,6,2,6,2)); a side-coverage bound only forces penalty >=4 there.
