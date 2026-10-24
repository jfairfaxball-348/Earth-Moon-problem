# S043 preregistration — exact Z3 slice, 24 October 2026

Registered before any new experimental output. Owner: `Run s043` (D047).
Existing main, ordinary non-force commit/push, no branch/PR. S036 stays stopped.
One experiment driver, one sequential solver; no other class or local search.

## Domain and encoding

V={0,...,27}, z=0, sigma(1+3i+r)=1+3i+(r+1 mod3), i=0,...,8.
The 378 unordered pairs partition into 126 size-three orbits. Boolean x[l,o]
selects orbit o in layer l. Each layer selects exactly26 orbits (78 edges),
and no orbit belongs to both layers. Sequential-counter cardinalities are
existential encodings of these exact equalities (PySAT CardEnc.seqcounter).
The 20475 four-sets partition into 6822 size-three orbits plus nine invariant
sets {z,1+3i,2+3i,3+3i}. For one representative of every orbit require at
least one of its six pairs in either layer. These clauses are exactly alpha<=3.

CLM0137 supplies one invariant facial triangle per layer, each a free vertex
orbit. These are different orbits by disjointness. Relabel the nine orbits
to make layer0 contain triangle0 and layer1 triangle1. This loses no solution;
we require presence, not faciality, so the relaxation can include more graphs.

## Symmetry soundness

The normaliser contains S9 permutations of free orbits, independent rotations
of each orbit, and global r -> -r (sigma -> sigma^2); layer swap also acts.
After fixing the two triangle presences, use the following stabilising
generators: rotate each orbit by one; swap adjacent orbit indices2..8;
global inversion; swap layers together with exchanging orbit0 and orbit1.
For each, impose X <=lex g(X), false<true, on all252 orbit variables.
Every generator preserves the pinned domain and original constraints. In each
finite orbit under this subgroup choose a lexicographically least X: it
satisfies ALL generator inequalities simultaneously. This proves no loss,
without asserting these inequalities select a unique representative or fully
quotient S9. Prefix-equality auxiliaries are defined by Boolean equivalences;
each implication at the next bit is p & a -> b. Unmoved positions are skipped.
No symmetry constraints outside this justified subgroup are admitted.

## Exact lazy planarity

Decode each SAT model to two explicit78-edge graphs. NetworkX planarity
produces either a sphere rotation (independently checked with stdlib Euler
and darts) or a Kuratowski subdivision. Independently suppress degree-two
vertices, check connectedness, and verify the resulting simple graph is K5
or K3,3. For its edge-orbit support S add OR[-x[l,o]:o in S]. Every graph
containing all these orbits contains that subdivision and is nonplanar.
The cut is automatically sigma-invariant because it uses whole pair orbits;
no unchecked permutation-lift or unverified obstruction is used. Store every
subdivision and its exact clause. Both nonplanar layers can contribute cuts.
All saved planar pairs require disjointness, symmetry, rotations and a separate
enumeration of all20475 four-sets. A positive alpha<=3 pair also needs explicit
proper colouring and the counting proof chi>=ceil(28/3)=10.

UNSAT from the incremental solver is provisional: export complete base+cuts
CNF, independently re-justify every clause including cardinality/symmetry,
then run pinned standalone CaDiCaL and drat-trim. Only verified DRAT closes
this entire slice. All other exits are UNKNOWN, never negative decisions.

## Limits and decision gate (never lowered)

Search: <=1800 cumulative driver CPU s; <=3600 wall s; <=20000 checked cuts;
one Glucose4 incremental solver, interruptible slices <=30 wall s. No result
from an interrupted solve. Parent RSS <=4GiB, free RAM>=1GiB, disk>=10GiB.
Reserve <=300 CPU s /600 wall s each for final native solver and checker if
UNSAT is found, supervised externally. Total experimental cap<=2400 CPU s,
below the owner's7200 s ceiling. Resource or certificate failures stop UNKNOWN.
Validation replays are separately metered. Controls: exhaustive small lex
truth tables, orbit counts and an explicit symmetric planar positive layer;
K5/K3,3 subdivision negatives. No threshold optimisation or near-miss search.

PROGRESS iff (A) certified chi>=10 biplanar witness, or (B) independently
checked order3 symmetric156-edge biplanar pair with <=40 independent
four-sets plus written mechanism. With alpha<=3 in this exact search, any
planar pair qualifies for A once fully certified. A certified exclusion is
learning, not progress. Otherwise PIVOT and queue S044 as a short owner-decision
audit of S037–S043: continue, pause or change target. No S044 execution here.
