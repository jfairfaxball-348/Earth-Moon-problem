# S040 post-hoc addendum — registered before running, 24 October 2026

Written after the registered experiment finished. It CANNOT change the D077
decision, which is fixed by PLAN.md criteria (A)-(C) on the registered arms.
Explanatory learning only, not constructive progress and not a new arm.

1. POSTHOC_SWAPS.json (already run, disclosed as post-hoc): exact four-set
change of every unrestricted single union-edge swap, no planarity/layer/move
constraint, with direct recount controls.

2. Label-fixed alpha<=3 repair at the two inputs. Add the registered exact
hitting set T (|T|=tau) to the union U; choose a maximum set D of original
union edges to delete such that every one of the20475 four-sets still contains
a kept pair (RC2 MaxSAT; the result is checked by direct enumeration). If
|D| >= |U|+tau-156 the output is an explicit alpha<=3 graph on the same labels
with <=156 edges at edit distance |T|+|D| from a checked biplanar pair; by
counting it has chi>=10. Report clique number, degrees and K9 containment.
It proves NOTHING about biplanarity: no split is searched here, and any such
graph is only a candidate for a future exact biplanarity decision (S041 audit).
CPU is reported separately and included in the 7200 s total.

3. Registered after item2 showed both repairs contain K10 (before running this
item). At the two inputs and the protected best, for every useful absent pair
f: whether U+f contains K9 (exact clique search, NetworkX cross-check), with
four-set incidence. Report the incidence share carried by K9-completing pairs,
and the K9-safe hitting number tau_safe (hitting set restricted to pairs f with
U+f K9-free; RC2, checked, packing lower bound over safe pairs), plus whether
U plus that set is jointly K9-free. Proves only these finite labelled facts.
