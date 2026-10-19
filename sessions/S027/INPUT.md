# S027 input — 2026-10-18

Live remote main 4d74c5f276a2a512b2588d3267a5496a7cba134b, tree
c439fe83c038b5627b9c53a3e05cb2ae65e4cd03, parents
96c9f3c9d482844a5c952d856132b99579b660bd and 2cd5c94999a817e384d346df6a08930b7591ae31
(PR #34 two-parent merge). Local HEAD equal; clean worktree; no open PRs; 57 remote
branches; latest main governance run 39155369381 success (Research scaffold checks)
and PR head run 39155308588 success. Hosted green jobs are not proofs.

Read: AGENTS.md, authoritative/STATE.json, START_HERE, SESSION_PROTOCOL, S026
CLOSEOUT/RESEARCH, research/S026_TWO_BRANCH_LEMMA.md, research/S026_CONTAINMENT_ENCODING.md,
CAM-0030/31, validation/S026/SUMMARY.json, validation/S026/source/SUMMARY.json and
FILTER_TRANSFERS.json.gz, filter-recovery/ candidate, local C5 checkpoints.

Frozen facts carried: 21/26 sum17 C5 classes certified NON-BIPLANAR; pending
C5[2,3,4,3,5], C5[2,4,3,4,4], C5[2,4,4,2,5], C5[3,3,3,4,4], C5[3,3,4,3,4]; all 2185
S026 source models excluded; P29-B14-0001 (28v,154e, alpha3, omega8) certified
NON-BIPLANAR and avoids all 26 sum17 C5 classes. Original271 NON-BIPLANAR.
No chi>=10 biplanar witness; 9<=chi_2<=12. D042 lower-only.

Entry smoke (before any science): local full scripts/cloud_smoke.py with pinned
artifacts/tmp/S004/cadical.exe (sha 120d2c53...) and drat-trim-mingw.exe
(sha 970caaea...): PASS, 271/271 chromatic CNF byte matches and DRAT verified;
K9 cover CNF regenerated/verified; fresh CaDiCaL K9 proof verified. The campaign
controller re-runs the full smoke itself as its first gated step.
