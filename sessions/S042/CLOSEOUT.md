# S042 CLOSED — apex-leaf census, D077-style decision PIVOT, 24 October 2026

The registered gate failed (no witness, no live leaf), so the decision is
PIVOT: R3 apex-over-Hajos search is parked and S043 is queued as the exact
order-3 layer-symmetric class at order 28 (route R1). No chi>=10 witness;
9<=chi_2<=12. S036 stopped; nine sorted S11 prefixes UNKNOWN. S043 is
FUTURE/UNEXECUTED and is not run here.

Results. Exact type reduction (CLM0142): with |L|<=21, 45 leaf types meet the
budget, 15 resolved, 30 named UNRESOLVED non-Ore windows. Generation: 23514
(a, L, e) choices, 97 non-isomorphic leaf graphs (CLM0143), from C5, 6-Ore/11,
7-Ore/19 and, as PARTIAL results, 7-Ore/13. All 97 are certified non-biplanar
by Lemma-B/C K9-minor CEGAR with pinned DRAT and full clause justification, in
at most 4.1 s each. By the leaf lemma (CLM0141) every K_avH with H a Hajos
composite having a leaf in the resolved types is non-biplanar, a=1,2,3.

Learning. In every case the obstruction is the cross-layer K9 minor, never a
Kuratowski subdivision: dense joins that generate chromatic number collide with
K9 minors once an apex is added. The only open R3 room is non-Ore near-extremal
critical graphs (and DHGO vertex-split operands) that no available source
lists.

Checks. Fresh full271+K9 smoke PASS; frozen S037/S038/S040/S041 replays PASS.
Independent stdlib type table; independent VF2 replay of all leaf graphs;
byte-identical CNF regeneration and drat-trim re-verification of every
committed DRAT proof; portable stdlib checker for hashes, receipts, type table
and small families. Experimental CPU 2671.4 s of 3600.

Archive policy: edges and DRAT proofs committed (28 MB); CNF and lemma files
(234 MB) kept in artifacts/tmp/S042/certificates_local and pinned by SHA-256,
regenerable with `scripts/archive_s042_certificates.py --verify`.

Reproduction from repository root (`.venv/Scripts/python.exe` on Windows):
1. Pinned EMP_CADICAL/EMP_DRAT_TRIM plus `scripts/cloud_smoke.py`.
2. Frozen replays: check_s037/s038 records, check_s040_handoff,
   check_s040_records, check_s041_records.
3. Finished experiment (do not rerun to check): `tools/s042_census.py`.
4. Local verification: `scripts/replay_s042_leaves.py`,
   `scripts/archive_s042_certificates.py --verify`.
5. Read-only portable `scripts/check_s042_records.py` (stdlib, CI).

Entry main ef06ec59a6f545e146b00f18101c3da03da545c5, tree
e5aa9358f657b9f95b1aa3b65821a65d9e057cfc, parent 77a9f5e61732cc805160a489b213ca10b0686c38.
Entry hosted [run40097274698](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40097274698),
job120882047086: all28 steps success. One ordinary commit/push on main; final
SHA/tree/parent and hosted job verified after publication (receipt
artifacts/tmp/S042/INTEGRATION.json). No PR/merge.

Next: S043 (prompt identical in authoritative/NEXT_SESSION_PROMPT.md and
sessions/S042/S043_FUTURE_PROMPT.md).
