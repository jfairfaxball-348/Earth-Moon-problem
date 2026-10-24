# S042 addendum — registered after the type table, before any leaf output

1. The first generation run was stopped (about 900 CPU s, counted in the 3600 s
cap) because composing every edge, vertex and split of K_k copies is massively
redundant; it produced only CENSUS_TYPES.json (unchanged by this addendum).
Reduction: if G2=K_k every (z, N1) is equivalent under Aut(K_k) to z=0 with N1
the first s neighbours, s=1..k-2; if G1=K_k every edge is equivalent to (0,1).
Other operands keep every edge, vertex and split. Control: full and reduced
generation must give identical isomorphism classes for 6-Ore on 11 and 7-Ore
on 13 vertices.

2. Ore members of UNRESOLVED types (9-Ore on 17, 8-Ore on 15, 7-Ore on 13) are
also generated and their leaf graphs decided, reported as PARTIAL results; those
types stay UNRESOLVED and no claim is made about their non-Ore windows.

3. Decision order per leaf graph: Lemma-B/C CEGAR first (cap 300 s); only if it
does not return a certified UNSAT, cover annealing seeds4201/4202 x30 s. The
certification rules of PLAN.md are unchanged.
