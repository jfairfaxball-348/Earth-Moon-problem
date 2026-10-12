# Candidate and proof certificates

Canonical 10–12 chromatic construction schema: JSON with num_vertices, edges_part1, edges_part2, coloring (length N), chromatic_number, plus provenance and optional embedding and proof certificate manifests.

Required checks:
1. finite simple labelled graph: all endpoints valid, no loops/duplicates and no overlap between E1 and E2;
2. independent planarity verification for both layers, ideally combinatorial rotation-system witnesses independently rechecked via Euler characteristic;
3. k entries represent exactly k colours; each edge has differently coloured endpoints;
4. no proper (k−1)-colouring: mathematical proof or proof-producing SAT CNF mapping with independently checked UNSAT LRAT/DRAT trace; a timeout/UNSAT console line/solver's unverified assertion is insufficient;
5. independent cold re-check and canonical SHA-256 hash; full reproduction instructions and exact environment.

**Gate:** preliminary script tools/check_submission.py checks 1 and 3 and, if NetworkX installed, provides an exploratory layer planarity check. It **does not** certify item 4 and cannot establish χ=k, even when it exits successfully. Formal Lean result is a later separate gate.

For universal theorems, use a complete written proof checked against arbitrary n, both layers, the entire graph class and all exceptional base cases. Finite SAT exhaustion without a universal completeness reduction is not a theorem about χ₂.
