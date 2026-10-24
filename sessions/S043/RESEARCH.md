# S043 research — layer-preserving order3 at order28

Bounds9<=chi_2<=12. This is a finite construction slice, not a universal
colouring result. Measured outcomes are recorded in validation/S043/RESULT.json
and summarised at closeout. Registration: PLAN.md and REGISTRATION.json.

## Exact orbit reduction (CLM-0144)

Conditional on the S041 CLM0137 proof, every156-edge pair in this class has
one common fixed vertex and nine free3-orbits. Each layer has78 edges, hence
26 pair-orbits. There are126 pair-orbits: nine z-to-orbit, nine internal
triangles, and3*binom(9,2)=108 between distinct free orbits. None has size1.
Among the20475 four-sets, the only invariant ones are a whole free orbit
plus z (nine). Thus (20475-9)/3=6822 other orbits. Selecting at least one
union edge in each representative is equivalent to alpha<=3, not just
a sampling test. A qualifying graph satisfies chi>=ceil(28/3)=10.

The invariant-face argument permits pinning two distinct internal triangles,
one in each layer. S9 relabelling sends them to indices0 and1. Their edges
cannot belong to both layers. We require edge presence, not faciality; this
weakens the relaxation without removing any valid pair. The17 lex
inequalities act inside the pinned domain. A lex-minimum member of every
finite subgroup orbit satisfies them all. Generator inequalities need not
be closed under composition to retain at least one such minimum. They do
not give full canonicalisation and leave substantial redundant search.

## Clause semantics and independent verification

The four-set, disjointness, pin and permutation clauses are reconstructed
from separately enumerated subsets and vertex permutations by the stdlib
checker. It shares neither search orbit construction nor NetworkX.

For a cardinality input x_0,...,x_(n-1), auxiliary s_(r,j) represents at
least r+1 true inputs in the prefix x_0,...,x_(j+r), with
0<=r<k and0<=j<n-k. The triangular counter clauses propagate the threshold
along j and from s_(r,j) plus x_(j+r+1) to s_(r+1,j); overflow forbids
s_(k-1,j) together with x_(j+k). Any k+1 true inputs force such an overflow;
when at most k inputs are true, assigning every auxiliary its stated prefix
meaning satisfies every clause. Therefore existential auxiliaries encode
at most k. Applying this to126 negative literals with k=100 and126 positive
literals with k=26 enforces exactly26. The independent code regenerates the
actual clause ordering and auxiliary allocation, then compares every byte.
Small exhaustive SAT controls additionally check cardinality and lex encodings.

For lex order, q iff p AND(a=b) is checked on all16 local truth assignments;
p AND a implies b forbids a first differing bit1 on the left and0 on the
right. Positions whose variables are identical need no new prefix variable.
Every generator is independently checked to centralise sigma or invert it,
permute all252 orbit variables, and preserve the pinned triangle requirements.

Every lazy clause records a connected subdivision of K5 or K3,3 and its
precise layer-orbit support. The search verifies it by suppressing degree2
vertices; the separate checker traces internally disjoint branch paths and
checks their simple skeleton. Selecting the full support contains every edge
of this nonplanar subgraph, so its negative clause is valid in all planar
layers. Whole orbits make the cut invariant without assuming an unverified
normaliser-lift. Base+cut CNF and the explicit subdivisions are retained.

## Certification boundaries

Only checked rotations of both layers, disjointness, every four-set and a
proper colouring would establish a witness. A successful single-layer
control is environment validation, not a156-edge biplanar pair. Failure to
find even a planar layer in relaxation models is a property of this run,
not a theorem about planar layers or the slice. Counts of cuts/models are
activity, not coverage. The saved CNF and cuts retain semantic information;
private CDCL state is not a checkpoint. UNKNOWN must not be used as a
negative premise. A genuine UNSAT requires independent clause justification
and pinned standalone DRAT verification before promoting any exclusion.

The prescribed progress gate is fixed. Certified exclusions are useful
learning but do not pass it. Any PIVOT queues only the S044 decision audit;
order2, S11 and alternative sources remain unexecuted.

## Measured result

UNKNOWN at registered20000-cut cap: 10000 relaxation models, 20000 independently checked cuts, 0 planar layers, 1026.703 CPU s. The entire order3 slice remains UNKNOWN; this run supplies no certified exclusion. Gate PIVOT; no witness or qualifying pair. See CLOSEOUT.md and validation/S043/RESULT.json. No additional source, symmetry class or local search was attempted.
