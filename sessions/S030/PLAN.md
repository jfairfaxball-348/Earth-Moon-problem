# S030 preregistration — 2026-10-19

Owner: `run next session`; executor Codex desktop, local Windows workstation.
The S030 prompt explicitly permits the local pinned toolchain. Exactly S030.
Entry main 1e1fdc1985f125b5092fe1e2252a2767d8d8bc7a, tree
0d61e17ef478036e8680b68bdfe2b3f92a8232a7; PR38 has parents
742c1a19bac8cd7caf4c734d73fc76262c8ced29 and
7c60fa8b0d4201204cf059d6c34ac9fc90334be9. Hosted governance run
39239671991 / job118017161029 success. No open PR; historical branches retained.

Before science: full cloud_smoke.py with local pinned CaDiCaL/drat-trim,
external process-tree supervision, 2400 seconds and 11 GiB private commit.
FAIL blocks science. Record current binary/package hashes, never inherit PASS.

Written necessary conditions precede search. S11: delta=11, m=155/156;
S10: delta=10, m=140..156; S9: delta=9, m=126..156 (degree lower bounds).
H=complement is K4-free, max degree 27-delta, 222<=m(H)<=261;
the per-stratum windows above strengthen these. Delta>=9 is conditional on
SRC-0037; unconditional fallback retains delta<=8 as unsearched, not excluded.
The m=154 regular case remains separate until the external packet is replayed.

General labelled encoding, no clique-blow-up restriction: edge variables for
G and disjoint layer variables, alpha<=3 clauses on every four vertices,
degree/cardinality constraints and each layer <=78 edges. Exact planarity by
lazy Kuratowski clauses: forbid all edges of each returned nonplanar subgraph
in that layer. Independently validate each cut is nonplanar before use.
K9 clauses may be lazy; any further obstruction clause requires a checked map
and inherited certificate provenance. Triangle-free cuts require independently
checked triangle-free edge sets with >104 edges. Omission weakens a necessary
relaxation and cannot justify a negative promotion. SAT requires full controls
and independent witness validation. UNSAT requires a native checked DRAT proof
of the final formula, plus independently checked generation and cut ledger.

Symmetry: degree order nondecreasing with vertex 0 attaining the minimum,
and first present edge placed in layer 1. Both follow by relabelling/layer swap;
no unsupported canonical augmentation or heuristic blocking in a global proof.
If degree-order encoding is not independently validated, omit it entirely.

Feasibility: <=180 seconds of scientific pilot time, <=15% of registered
science budget 1500 seconds. Fetch paper59 packet/checker read-only; controls
C7[K4] (112-edge triangle-free cross set), retained 17-vertex alpha2 split if
available, and 18-vertex source theorem labelled inherited. Near25 alpha3
positive control optional construction bounded at 30 seconds, no assumed success.
Measure smaller analogous alpha constraints, then S11. Native solver cap for
S11 1200 seconds total, at most one heavy worker, 11 GiB process tree.
Stop on cap; S10/S9 remain NOT_RUN. Persist formula, cuts, solver log, hashes,
model if any, and UNKNOWN on caps/errors. No sampled slice is a whole stratum.
No speculative wall-time extrapolation from a different domain.

Independent replay uses a separate checker implementation for base semantics
and cut validity; native DRAT checker for UNSAT. A witness stops the search
for separate alpha, planarity embeddings and colouring verification.
No S031, outreach, publication or formalisation. Parked queues untouched.

## Pre-execution amendment for measured second stage

The initial general pilot will be stopped at about180s and retained separately;
it is generating mostly K9-containing models (six in123.6s), so weak one-clique
cuts spend most work rediscovering equivalent obstructions. Remaining global
S11 budget is <=1020s. Before the second run, add the proved independent-triple
anchor in RESEARCH, collect up to1000 distinct K9 clauses per model rather
than one, attempt bounded triangle-free cuts, and test certified library
obstructions only on K9-free candidates. No stratum or verdict changes.
Record source-v1 separately and preserve its stopped process receipt. The
new anchor is relabelling only; never assume a source-stated degree-sum lemma.

Second-stage refinement, registered before the final S11 segment: sort vertices
within3..13 and14..27 by their two adjacency bits to roots1,2. This is a
permutation within identical root0-neighborhood classes; hence every witness
still has a representative. Encode nondecreasing two-bit integers by forbidding
the six descending pairs. Retain the unsorted-anchor run separately at about
180s, audit all its cuts, then seed those globally valid cuts into the sorted
run. Final sorted cap <=800s, keeping pilot+unsorted+sorted <=1200s apart from
small process shutdown overhead. No label-specific empirical exclusion is used.
