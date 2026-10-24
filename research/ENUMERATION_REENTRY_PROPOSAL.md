# Proposal: return to proof-producing solver enumeration

24 October 2026. Owner direction: return to an optimised enumeration search
on graph domains without a known resolution after checking prior art.
This is a concrete proposal, not execution of S045 or a restart of S036.
No solver, controller, scheduler or experiment was started in preparing it.
The previous PAUSE recommendation should not be read as a rejection of exact
enumeration. The recent construction heuristics and selected families failed;
the unrestricted search domains remain unresolved.

## Owner-selected direction: 50 vertices

Owner follow-up selects the larger-order direction, with 50 vertices as the
concrete proposal. This supersedes the earlier preference below for a
smaller-order comparative pilot. It does not start a numbered session.

The proposed domain is finite simple graphs G on V={0,...,49}, represented
by disjoint planar edge sets E1,E2 with G=(V,E1 union E2). Seek chi(G)>=10
directly; do not carry forward alpha<=3, minimum degree 11, the old sorted
prefixes, or a prescribed symmetry. Additional restrictions would define
explicit subfamilies and need separate justification.

| Planning quantity | Value |
|---|---:|
| Possible vertex pairs | 1225 |
| Maximum edges in either planar layer | 144 |
| Maximum edges in the union | 288 |
| Maximum average degree of the union | 11.52 |
| Two-layer edge-selection Boolean variables before auxiliaries | 2450 |
| Standard nine-colouring vertex/colour variables before auxiliaries | 450 |

The edge bounds follow from 3n-6 per planar layer; these are upper bounds,
not a requirement to attain 288 union edges. More vertices allow different
global constraints while planarity keeps the graph sparse. These variable
counts are not runtime estimates: planarity, symmetry and learned clauses
can dominate the actual encoding and search.

### Proposed solver loop

1. Generate a candidate pair of planar layers, reusing the retained native
   partial-planarity machinery only after validating its new 50-vertex
   encoding. Alternatively use a separately registered generator that
   maintains planarity by construction. No old campaign process is resumed.
2. Test the union for a proper nine-colouring using a separate SAT instance.
3. If a colouring c exists, add the clause

       OR { g_uv : u<v and c(u)=c(v) },

   where g_uv means that uv is present in the union. Every graph requiring
   ten colours must contain an edge inside at least one class of c;
   otherwise c also colours that graph. Thus this clause discards a whole
   family of nine-colourable graphs, rather than just the current graph.
   Record each colouring partition and independently verify its clause;
   colour-label permutations give the same partition. This is a proposed
   counterexample-guided synthesis loop, not a novelty or performance claim.
4. If the colouring test returns UNSAT, retain UNKNOWN until a standalone
   proof checker verifies the non-nine-colourability certificate. Independently
   check both planar embeddings, simplicity and edge disjointness. Find and
   check a proper ten-colouring if claiming chi=10; non-nine alone gives
   chi>=10. Preserve the explicit graph and certificates immediately.

At 50 vertices, alpha<=5 would also suffice, since ceil(50/5)=10. It is an
optional restricted route, not a mandatory filter: alpha>=6 does not imply
nine-colourability. Avoid explicitly imposing all 15,890,700 six-set clauses
as the default encoding. Direct colouring tests retain candidates that the
counting shortcut would miss.

Adding isolated vertices to a known nine-chromatic graph cannot help.
Low-degree additions that each see at most eight earlier neighbours also
preserve nine-colourability by greedy extension. A useful larger graph must
introduce constraints that defeat every nine-colouring. If a successful
50-vertex graph contains a smaller ten-chromatic core, retain that success;
do not require all 50 vertices to be critical without declaring the narrower
domain.

The first experiment should be a preregistered bounded pilot measuring
candidate generation, colouring-test cost, growth of verified colouring
clauses, and durable output. No claim of exhaustive feasibility, speedup or
time-to-witness is justified yet. A capped search remains UNKNOWN. A complete
negative requires a checked certificate for the precisely registered domain,
including independent justification of all externally supplied clauses.

### Prior-art boundary for this proposal

On 24 October 2026 the inspected primary Szeider source establishes the
small-independence result alpha<=2, not an exclusion of arbitrary 50-vertex
biplanar ten-chromatic graphs. Its introduction also states m<=6n-12.
https://arxiv.org/html/2609.28102v1

The inspected rStation paper 22 discusses fractional/counting limitations;
it is an unrefereed source, and its fractional-colouring conjecture is not
an established exclusion. Searching direct non-nine-colourability avoids
requiring n/alpha>9. Before production, freeze a fresh admission matrix for
the actual selected subfamilies; this proposal does not guarantee novelty
or that all prior art has been inspected.
https://rstation.ai/problems/earth_moon/papers/22

## Earlier comparison of vertex counts and structures

Owner follow-up: consider a different number or arrangement of vertices.
The programme requires a biplanar graph needing at least ten colours, not
28 vertices, minimum degree 11, or a prescribed symmetry. These were search
choices. Compare the following domains before committing to another S11 run:

| Domain to screen against current prior art | What changes | How ten colours would be proved |
|---|---|---|
| Still-open classes at orders 21..27 | Fewer vertices; remove the order-28 restriction | Direct checked non-9-colourability; alpha<=3 alone gives no ten-colour guarantee here |
| Order 28 with minimum degree 9 or 10 | Different degree profiles from all nine old S11 regions; allow the full admissible edge range | Alpha<=3 suffices, together with checked planar layers |
| Order 37 with alpha<=4, or other selected larger orders | Permit larger independent sets and new structures | 37/4>9 supplies a counting lower bound; other choices may need direct non-9 proofs |
| Retained order-28 S11 slice | Optimise the old domain for comparison, without assuming it is the best destination | Alpha<=3 plus checked planar layers |

These are domains for prior-art admission and bounded comparative pilots,
not claims that every listed class is currently open or computationally easy.
The 21..27 range must first exclude any orders/classes already settled by
the order-by-order literature. The 37-vertex option also requires a specific
prior-art check; no absence-of-prior-search claim is made.

Why 28 was selected previously: chi(G)>=ceil(n/alpha(G)), so n=28 is the
first order where alpha<=3 alone forces ten colours. This is a sufficient
certificate, not a necessary shape of a ten-chromatic graph. At n=27,
alpha<=3 guarantees only nine colours as a lower bound; chi=10 could still
hold and would need a stronger certificate. Conversely increasing n above
28 while keeping alpha<=3 does not avoid the old existence question: any
28-vertex induced subgraph would itself be a qualifying witness. Allowing
alpha=4 or using direct colouring constraints makes a genuine change.

Here arrangement means changing adjacency, degree structure and/or the
two-layer edge partition. Different coordinates or vertex labels alone do
not change the abstract graph or its chromatic number. Search need not
restrict the graph to a selected symmetric family.

The earlier recommendation was a pilot comparing admitted smaller-order/direct-colouring cases and
the untouched order-28 degree-9/10 strata against the optimised S11 baseline.
Do not assume larger order helps just because it provides more choices.
Choose production from measured feasibility and information gain. Count-based
routes, including 37/4, still carry the conjectural fractional-colouring risk;
direct non-9 searches allow colour demand not detected by n/alpha.

## Retained S11 baseline option

The earlier proposed baseline uses finite simple graphs G on 28 labelled vertices satisfying
alpha(G)<=3, minimum degree exactly 11, and m in {155,156}, together with
an edge-disjoint two-planar-layer decomposition. This is the unresolved S11
slice in the repository. A witness has chi>=ceil(28/3)=10. A negative settles
only the registered slice; it does not settle all minimum degrees or EMP.
The smaller minimum-degree strata remain separate potential future work.

## A concrete partition to benchmark

Write d(v)=11+e(v), e(v)>=0. The handshaking identity gives

    sum_v e(v) = 2m - 28*11 = 2 or 4.

The partitions of these small excesses give exactly seven degree multisets:

| Edges | Degrees above 11 | Remaining degree-11 vertices |
|---|---|---:|
| 155 | 13 | 27 |
| 155 | 12,12 | 26 |
| 156 | 15 | 27 |
| 156 | 14,12 | 26 |
| 156 | 13,13 | 26 |
| 156 | 13,12,12 | 25 |
| 156 | 12,12,12,12 | 24 |

These patterns are already implicit in the old formula. Explicitly encoding
and partitioning them may strengthen propagation and produce smaller proof
jobs; no speedup, novelty or closure is claimed before benchmarking.
Regenerate the encoding in a new session directory. Combining degree order,
root-neighbour anchoring and the old sorted-type constraints needs a written
soundness proof. Do not simply pin high-degree labels on top of the old
anchors: those permutations need not preserve one another.

Partition difficult patterns further by certified structural types or SAT
cubes, with a checked cover of the parent domain. Keep splitting adaptive;
avoid treating the old nine prefixes as nine suitably sized jobs. The 247
historical forbidden prefixes followed sorting alone, so they did not remove
most of the substantive graph search space.

## Solver work to compare

1. Reconstruct a cold baseline with the retained native CaDiCaL and checked
   partial-planarity propagator. Do not wake old S036 processes or controls.
2. Compare an explicit-degree-pattern encoding against that baseline on the
   same bounded inputs and resources. Check whether smaller proof jobs can
   actually finish; retain UNKNOWN for every unfinished job.
3. Test proof-producing symmetry reduction, stronger certified obstruction
   filters and a graph-first enumeration/fixed-graph-decision alternative.
   Use the existing Lemma-B/C decision tools where their hypotheses apply.
   Any generator over optional graph edges needs fresh conditional-clause
   justification; fixed-graph cuts cannot be transferred blindly.
4. Reuse independently audited geometric cuts after exact variable-map
   validation, deduplication and selective loading. Archive the full source
   pool. Do not import private CDCL state or assumption-dependent clauses as
   unconditional global facts. Fewer loaded cuts can be sound but weaker;
   the memory/runtime tradeoff must be measured.

A candidate graph is not resolved by rejecting one attempted split. Prove
non-biplanarity across every split before adding a graph-blocking clause.
Canonical graph enumeration must have a checked completeness argument and
sound symmetry clauses; a casual isomorphism filter is insufficient for an
exhaustive negative. A joint SAT decision of an entire work unit can instead
close it directly, without explicitly listing every graph.

## Prior-art admission

Maintain a dated matrix of the precise vertex/degree/edge/symmetry conditions
for every prospective work unit: known excluded, known positive, unresolved
in inspected sources, or source access insufficient. Skip known exclusions;
do not call a domain globally open merely because a local job timed out.

Fresh primary inspection on 24 October 2026: Szeider's arXiv:2609.28102v1
Section 7 still identifies the order-28 K4-free-complement question and notes
the potential but unknown feasibility of transferring its enumeration method.
It closes the independence-at-most-two route, not the S11 target above.
https://arxiv.org/html/2609.28102v1#S7

The 2026 rStation order-bound/regular-endpoint material is narrower: the
eleven-regular order-28 case has 154 edges and is not one of these seven
patterns. Direct refreshes of posts 152/155 and paper 59 failed in this pass;
post 146 also needs a fresh check. Their exact current statements and any
supplements must be obtained before admitting a production unit. An absence
of an inspected closure is not a guarantee about all prior art.

The established solver approach and encoding alternatives are credited to
Kirchweger–Scheucher–Szeider, SAT-Based Generation of Planar Graphs (2023),
and the retained bipsat2 implementation (SRC-0055).
https://doi.org/10.4230/LIPIcs.SAT.2023.14

## Acceptance, budget and outputs

First a fresh full 271+K9 smoke, small exhaustive/corruption controls,
encoding and partition validation, then a preregistered serial optimisation
benchmark. A proposed first budget is 1800 cumulative CPU seconds for the
benchmark, one worker, an externally enforced 3 GiB private-memory cap,
at least 1.5 GiB available RAM and a 10 GiB disk reserve. Re-measure the
machine before fixing production limits; this document does not launch or
authorise an unattended run. Benchmark counts/limits must be finalised before
results, not fitted afterwards. No forced termination of old campaign state.

Continue production only with a demonstrated operational gain and an explicit
resource plan. Keep stable work IDs, inputs, hashes, a disjoint-cover map,
audited cuts, cooperative stops and proof/export paths. Save each completed
certificate immediately. Prefer manageable units with durable finished proofs
over a handful of permanently unresolved giant jobs.

Report three outcomes separately: a checked biplanar witness; a work unit
excluded by standalone DRAT plus independent clause justification; or UNKNOWN.
Report completed units with their exact definitions, not a percentage of
graphs unless projected counting is independently established. Cut counts,
conflicts and runtime are diagnostics, not mathematical coverage or an ETA.

For this proposed enumeration campaign, checked closure of a substantive
registered unit is useful negative progress. It is not a chi>=10 construction
or a retroactive change to the old S040/S042/S043 gates. A new future prompt
should state this distinction explicitly and replace the pause-only plan
before any research run begins. The programme target remains D042.
