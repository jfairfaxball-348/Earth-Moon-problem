# regular566-rup-v1

The UTF-8 JSON object has format="regular566-rup-v1" and branches, a list
with q=2,3,4 in that order. Each branch record has:

- q: number of P vertices selecting Y on the type-T side.
- variables: maximum variable identifier in formula(q), 71834.
- input_clauses: regenerated clause count, 173170.
- core_clause_indices: zero-based indices into formula(q).clauses.
- rup_additions: ordered lists of nonzero signed integer literals. A positive
  integer is a Boolean variable; a negative one its negation. The last list
  is empty. Negating each addition and unit-propagating the current database
  must derive a contradiction before the addition enters the database.

Vertex labels are P=0..5, A=6..12, B=13..19; X=20..22, Y=23..25,
Z=26,27; roots=0,6,13. The type-U vertex t is20 and its other X pair is21,22.
The type-T parts are R_B=14,15,16 and Y=23,24,25, with isolates13,17,18,19.
Vertices0..q-1 select Y; the other P vertices select R_B. The choice of
labels is justified by relabeling within the partition, fixing its roots.

Edge variables1..378 follow itertools.combinations(range(28),2) in order.
Auxiliaries follow the deterministic loops of encode.py. Counters force
prefix thresholds forward and forbid the final threshold above the cap;
actual threshold values provide an extension of each legal edge assignment.
Degree11 is two caps: 11 on edges and16 on nonedges. Common-neighbor variables
are equivalent to the two-edge conjunction, and the final cap4 is guarded by
the tested pair being adjacent. No independent four-set is encoded by one
six-literal clause per four-set. K9-extension clauses forbid each nine-set
containing a whole original private clique. This last condition is necessary,
without claiming to enumerate every nine-clique. Root/clique units and the
125 branch units are listed by the two formula-building programs.

Clause-family counts: private cliques/root types138; degree31780; alpha20475;
nonedge common-neighbor caps118692; K9 extensions1960; branch units125.
A hypothetical graph therefore extends to a satisfying assignment of its
branch, whereas the retained RUP derivation proves that none exists.

The checker takes no initial satisfiability claim on trust. It constructs
its propagation database from the referenced literal input clauses and
checks each new clause independently under its negation. Deletions are not
needed: retaining extra clauses preserves each RUP consequence. Hashes are
integrity aids only. Assertions must remain enabled; the entrypoint rejects
Python's optimized mode. The essential trusted parts are the hand coverage,
necessary encoding semantics, and the small direct propagation algorithm.
