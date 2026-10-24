# S042 preregistration — certified apex-leaf census (route R3)

Registered 24 October 2026 before any census output. One experiment process,
<=3600 cumulative CPU s. No hill-climbing, symmetric OP1(b) or S11 work.

## Objects

For a in {1,2,3} a LEAF is a (10-a)-critical graph L with an edge e such that
the leaf graph Lambda = K_a v (L-e) has omega <= 8 and satisfies the planar
budget e(Lambda) <= 6|Lambda|-12, i.e. e(L) <= 5n-5, 4n, 3n+4 for a=1,2,3
(n=|L|). Every K_a v H with H a Hajos/DHGO composite containing L as a
composition leaf contains Lambda, so a non-biplanar Lambda kills all such
composites; a biplanar Lambda is a live leaf.

## Census domain and completeness (stated now)

Gallai (SRC-0027): a critical graph is K_c v F_1 v ... v F_r with F_j
join-irreducible critical, and an irreducible k-critical graph has >= 2k-1
vertices; 3-critical irreducible = odd cycles C_{2t+1}, t>=2. Kostochka-Yancey
(SRC-0011, SRC-0020 Theorem 6): e(F) >= KY_k(n), with equality iff F is k-Ore,
and non-Ore F has e(F) >= ((k+1)(k-2)n - y_k)/(2(k-1)). An exact-arithmetic
type enumerator lists every (a, c, factor types) whose minimum edge count meets
the leaf budget with n=|L| <= 21. A factor type is RESOLVED if all its graphs
are generated: odd cycles; KY-exact types (all k-Ore graphs, generated as
every DHGO composition of smaller k-Ore graphs with every edge, vertex and
split, deduplicated by isomorphism); types with <= 7 vertices (all graphs from
the NetworkX atlas filtered by criticality). Any type admitting a non-Ore
factor with >= 8 vertices is UNRESOLVED and listed with its (k,n,e) window;
no claim is made about it. For every resolved L, EVERY edge e and every a is
tested for the budget and omega(Lambda)<=8; surviving leaf graphs are
deduplicated by isomorphism.

## Decision and certificates

Each leaf graph: tools/s025_cover_anneal.py (seeds4201/4202, 30 s) for an
explicit positive split, independently checked (disjoint, union, NetworkX
planarity and stdlib rotation); then tools/s025_minor_cegar.py --lemmaC 5, cap
300 s, UNSAT accepted only with pinned CaDiCaL DRAT verified by pinned
drat-trim (tools/s025_certify.py) and tools/s025_check_minor_cert.py; a cap or
unverified UNSAT is UNKNOWN. S041's three leaf graphs are recomputed for a
uniform record (not new results). A portable stdlib checker regenerates the
type table and resolved graphs and verifies archive hashes.

## D077-style gate (fixed now; never lowered)

PROGRESS iff (A) a certified chi>=10 biplanar witness, or (B) a live leaf:
some Lambda certified biplanar by explicit checked layers with omega<=8, L
independently re-verified (10-a)-critical, leaf slack 6|Lambda|-12-e(Lambda)
>=1, reproduced by the separate checker, with a written account of how it
evades Lemma B/C. If (B), build >=1 composite K_a v Hajos(L1,L2) from live
leaves and decide it within caps. Otherwise PIVOT: record the certified
closure of the RESOLVED domain, list UNRESOLVED classes, park R3 apex search,
and queue S043 to R1 (exact layer-preserving order-3 class at order28) unless
the evidence then points to a better audited route.
