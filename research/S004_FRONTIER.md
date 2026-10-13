# S004 finite construction frontier

Headline unchanged: no certified biplanar graph with chi>=10; no universal
upper-bound improvement. This is a finite candidate exclusion and audit.

## 271 exact chromatic certificates (CLM-0026)

The exact S003 alpha>=3 list was independently rechecked against F1/F2/F3.
For every row, the bag CNF expresses nine sets of independent base bags,
with bag i appearing at least w_i times. This is equivalent to a proper
9-colouring: adjacent bags cannot share a colour and a clique bag needs
w_i different colours. The vertex CNF is a separate plain colouring
encoding of the explicitly expanded graph, with a maximum clique's colours
fixed by a global colour permutation. Both were refuted with independently
checked DRAT proofs for each of the 271 rows. Each vertex 10-colouring was
decoded and checked on every edge. Thus chi=10 exactly; this is not a
claim of biplanarity. Proof hashes and upper colourings are in
validation/S004/chi10_results.json; compressed bag proofs are retained.

## Independent census samples (CLM-0030)

Each of two preregistered 8-vertex bases was checked through all 8^8 positive
vectors: GsUPOK has kept=485, 458 colourable, 19 F3-excluded, 8 survivors;
GrEKGc has kept=71, 61 colourable, 0 F3-excluded, 10 survivors. Chunked plain
enumeration, independent MIS-cover colouring and triangle branching agree
with main-tool reruns and S003's stored vectors, including explicit
isomorphism handling of the main relabelling. The other 7440 true-twin-free
order-8 bases were not independently checked, nor was k=9 enumerated.

## C5 classification attempt (CLM-0031 is counting only)

Full 8^5 positive-weight enumeration with all full-bag F1/F2/F3 filters and
10 dihedral images gives 297 feasible orbits and 13 maximal ones. The
ordered 13 maximal patterns and three one-step children of [2,6,2,6,2]
were tested with the new face-cover oracle (120 s nominal each, hard cap
130 s) and constructive planar-edge packing (30 s each, seed 4004).
All 16 ended UNKNOWN in both routes. A 600 s short-link retry on [2,6,2,6,2]
also ended UNKNOWN (608.516 s observed). These shorter new-encoding runs
do not supersede S003's longer Kuratowski timeouts or create negative
certificates. They give no classification theorem and no frontier closure.

## One checked full survivor exclusion (CLM-0032)

The preregistered first minimum-order row is source index 165:
G|fH_K[4,2,2,2,2,2,2,6], n=22, m=119, D=1. Its input edges and metadata
are retained in validation/S004/targets/full-min-survivor.edges and
full_survivor_target.json. The face search returned UNSAT after 11
iterations and 773 well-formed cuts (163.875 s). The regenerated final
CNF has 82537 variables and 169777 clauses. An initial 60 s fresh proof
solve timed out, so no negative result was accepted then.

After explicit preregistration of a 600 s retry, standalone CaDiCaL 3.0.1
refuted that CNF and drat-trim VERIFIED its 509916970-byte text DRAT proof.
A second bundled Cadical153 solve with the repaired C-runtime export also
produced a drat-trim VERIFIED proof (416906985 bytes). Exact hashes/times
and checker logs are retained. A compact core DRAT proof was extracted
from the bundled-solver proof and rechecked against the full original CNF;
that 129950618-byte certificate is retained compressed, with both raw and
archive hashes. Original solver proof hashes and reproduction commands are
retained. CNF regeneration is raw byte identical.

Consequently this fixed 10-chromatic graph is not biplanar. This does not
prove thickness exactly three. A separately written incidence encoder
without lex/excess constraints provided an additional challenge. It found
a relaxed SAT model: layer 0 is non-planar with four bad links, and layer 1
is non-planar/disconnected. It did not independently reproduce the negative
verdict. Its ten positive controls passed; the first generator's proof and
checked refutations remain the evidence, with this limitation explicit.

Capacity-respecting bag maps into all 271 survivors were searched and every
positive map was expanded to an injective vertex map checked on every
obstruction edge. Only the obstruction itself was excluded this way.
Other failed bag searches do not rule out more general subgraph embeddings.
The remaining **270** listed alpha>=3 survivors still have UNKNOWN
biplanarity in this programme. No universal conclusion or novelty claim.

## Chromatic scope of the remaining apex calibration (CLM-0033)

C5[K3] has independence number two, so 15 vertices force at least eight
colours. An explicit proper eight-colouring is checked; its universal apex
needs exactly one additional colour. Thus apex(C5[K3]) is nine-chromatic.
Its biplanarity remains UNKNOWN after the registered face run; a positive
split would be another chi=9 example, not a headline lower-bound advance.
