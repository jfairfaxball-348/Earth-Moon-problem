# S025 CLOSEOUT — 2026-10-16

## Mathematical verdict
- **No χ≥10 biplanar witness.** Classical 9 ≤ χ₂ ≤ 12 is unchanged.
- **The original 271 exactly-χ10 clique blow-up corpus is ENTIRELY NON-BIPLANAR** (CLM-0094).
  - 52 rows were certified in S004–S009.
  - All 219/219 formerly UNKNOWN rows, row148 included (edge sha 4f8dab6c…), contain a DRAT-certified non-biplanar 17-vertex C5 clique blow-up under an explicit injective vertex map. Every obstruction edge is checked to be a row edge.
  - The only imported dependency is K9 having thickness 3: classical (SRC-0014), with a programme DRAT re-verified in this session's smoke.
  - The D051/D054 original-219 priority is discharged by complete decision (D058).
- **C5 threshold.**
  - All 262 K9-free C5[a] with Σaᵢ ≤ 16 are biplanar (explicit checked splits).
  - 18/26 Σaᵢ=17 classes are DRAT-certified non-biplanar.
  - Still UNKNOWN (heuristic defect 1 only): C5[2,3,4,3,5], C5[2,3,5,2,5], C5[2,3,5,3,4], C5[2,4,3,3,5], C5[2,4,3,4,4], C5[2,4,4,2,5], C5[3,3,3,4,4], C5[3,3,4,3,4].
  - The iff-classification (biplanar ⇔ aᵢ+aᵢ₊₁ ≤ 8 and Σ ≤ 16) is pending those classes.
- **New tools.**
  - Complete two-sphere-triangulation SAT (CLM-0089): validated but too weak (F070).
  - Flip-annealing cover oracle: row148 best 4 uncovered, against a historical 6.
  - K9-minor Lemma B/C CEGAR (CLM-0090/0091) with clause re-justification, byte-exact CNF regeneration and drat-trim.
- **Arm A** (weighted-independence chromatic certificates over triangulation pairs, heuristic): α≤3 reached n=24, α≤4 reached n=32, and W=3 total-28 minima are ≥8. No χ≥10.

## Certified C5 obstructions (native CaDiCaL sha 120d2c53bf14…, drat-trim sha 970caaea97a1…)
| graph | CEGAR s | Kuratowski lemmas | CNF clauses (all justified) | native solve s | drat-trim s | DRAT bytes | CNF sha256 |
|---|---|---|---|---|---|---|---|
| C5[1,1,7,1,7] | 75.1 | 9947 | 41217 | 4.0 | 0.56 | 367614 | e26d1fee6a09c2a0… |
| C5[1,2,6,1,7] | 46.4 | 5614 | 35098 | 0.32 | 11.41 | 223303 | 8e1160c51506cc8a… |
| C5[1,2,6,2,6] | 101.7 | 13394 | 49150 | 7.86 | 0.86 | 702868 | 568f84ef567fa6fe… |
| C5[1,3,5,1,7] | 53.0 | 6481 | 39718 | 1.13 | 0.76 | 233947 | 6713841aca1b7fb6… |
| C5[1,3,5,2,6] | 118.3 | 19329 | 58087 | 20.69 | 7.91 | 3264400 | b1571858325e24bf… |
| C5[1,3,5,3,5] | 206.2 | 43238 | 113472 | 25.66 | 7.83 | 7078121 | 5c7fe6f97f3f3bda… |
| C5[1,4,4,1,7] | 42.6 | 6462 | 40678 | 1.93 | 4.87 | 485784 | 7a5bf438d7372fd8… |
| C5[1,4,4,2,6] | 101.3 | 21535 | 64304 | 17.12 | 2.11 | 3360258 | eacea3b6b9aeac80… |
| C5[1,4,4,3,5] | 226.4 | 56245 | 134700 | 7.9 | 14.98 | 12593417 | bafba90bb4c94390… |
| C5[1,4,4,4,4] | 259.1 | 75873 | 180439 | 14.97 | 16.17 | 14568450 | 2c81a1c79547f803… |
| C5[1,5,3,2,6] | 85.1 | 20642 | 63445 | 8.22 | 3.33 | 3776743 | 865c52be6c63a707… |
| C5[1,5,3,3,5] | 139.9 | 41722 | 106643 | 28.86 | 42.88 | 5642470 | 65e063b59faa4d85… |
| C5[1,6,2,2,6] | 50.8 | 13459 | 48615 | 17.58 | 2.09 | 2894641 | e0c03612b5c49010… |
| C5[2,2,5,3,5] | 1808.3 | 244008 | 508249 | 142.36 | 274.34 | 134331668 | 68fcb3a1637a12fc… |
| C5[2,3,4,2,6] | 402.9 | 78941 | 186439 | 4.43 | 7.96 | 25997776 | c4e235ddee9c1a2f… |
| C5[2,3,4,4,4] | 2392.3 | 329308 | 683997 | 188.07 | 375.78 | 151758731 | 790da5faa6e2bb8e… |
| C5[2,5,2,6,2] | 551.3 | 73298 | 171521 | 11.62 | 17.85 | 12667212 | 0c91fe373b77347c… |
| C5[3,3,3,3,5] | 1474.2 | 260471 | 551117 | 87.56 | 144.4 | 76570732 | 08fcf19bc9502faa… |

Full records, gzipped lemma JSON (rebuilds the CNF byte-for-byte) and gzipped DRAT proofs are in validation/S025/certs and validation/S025/C5_CERTIFICATES.json.

## Environment and integrity
- The owner said "you are running locally now", so S025 ran on the owner's Windows 11 workstation (16 threads, 16 GiB), Python 3.12.10, python-sat 1.9.dev15, networkx 3.5.
- The full scripts/cloud_smoke.py **PASS** ran before any science: 271/271 chromatic DRAT, 271/271 CNF byte matches, retained K9 verified, fresh CaDiCaL K9 proof verified. The first attempt failed before any check on a relative native path.
- No GitHub Actions science run and no WIP branch.
- Resource deviation F071: RAM oversubscription killed several exact runs and one certification batch. All are recorded NOT_COMPLETED, and nothing was inferred from them.

## Integration
- One isolated authored commit on session/S025-c5-obstructions-corpus-closure, from entry main b8733f8 (tree 24dda2c, parents f66f0e7 + 2027da4, PR #30).
- Ordinary PR and non-force two-parent merge. The actual SHAs, tree and hosted checks are read back live after merge and reported to the owner. This frozen file does not predict them.

## Next
S026 FUTURE/UNEXECUTED: obstruction-aware χ≥10 candidate generation, plus finishing the remaining Σ=17 C5 classes. The prompt is byte-identical at authoritative/NEXT_SESSION_PROMPT.md and sessions/S025/S026_FUTURE_PROMPT.md. No Lean, Palomar, arXiv, paper or outreach.

## Integration reconciliation — 2026-10-18

The owner requested reconciliation of the local/remote handoff. The original local commit8fda361 was not on remote main; PR31 separately advanced main to6883520 with an older queued S025 directive. A one-commit reconciliation transplants the completed S025 results onto that main while preserving both execution and directive provenance. Two omitted compressed proofs were recovered byte-for-byte against original certificate digests, and three source files restored to their original manifest byte hashes after Git CRLF normalization. This is packaging/governance only; no new search/native proof replay/smoke or S026 execution. Original observed results, limits and failures remain unchanged. Full receipt: docs/S025_INTEGRATION_RECONCILIATION.md and validation/S025/INTEGRATION_MANIFEST.json. Outgoing PR/main identities are independently read after commit; no guessed hashes here.
