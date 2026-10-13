# S004 research outcome — 2026-10-13

**OPEN: 9 <= chi_2 <= 12 unchanged.** No biplanar chi>=10 construction,
universal improved colouring theorem or full resolution.

All 271 alpha>=3 survivors are now exactly 10-chromatic: 542 checked
bag/vertex DRAT refutations and 271 proper 10-colourings; bag proofs retained.
One full 22v/119e survivor (source index 165) is excluded by a regenerated
triangulation-cover CNF and two checked solver refutations. A compact core
proof was rechecked and retained. Subgraph transfer excluded only itself;
270 remain UNKNOWN. All 159 source-corpus apices are excluded (147 Euler,
8 codegree, 4 K9), correcting S003's missed K8 filter/source SHA.

Two full fixed-base k=8 samples agree with S003, not a full census check.
New completion-face oracle calibrated by K9 and 102 positive controls.
A separate no-lex incidence encoder found a non-planar relaxed SAT model;
it did not independently reproduce the full-survivor exclusion.
All 16 C5 maximal/child targets remain locally UNKNOWN after face/packing
runs; a 600 s short-link retry also UNKNOWN. Counting gives 297 feasible
orbits and 13 maximal patterns, not a biplanarity classification.

A checked 4-chromatic biplanar double-wheel graph defeats every single
Kempe swap for one rainbow 11-colouring of its deletion (D=533); no critical
or multi-swap theorem follows. apex(C5[K3]) is exactly 9-chromatic, verified
by colouring and alpha/join lower proof; its biplanarity remains UNKNOWN.

Details: research/S004_FRONTIER.md, S004_TRIANGULATION_COVER.md,
S004_KEMPE_LOCK.md; validation/S004_MANIFEST.json; CAM-0005 amendments.
Claims CLM-0026..0033. No novelty guarantee, external certificate replay,
Lean, publication or outreach.
