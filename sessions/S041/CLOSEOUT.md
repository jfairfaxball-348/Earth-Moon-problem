# S041 CLOSED — comparative route audit, 24 October 2026

S041 audited four construction routes under registered criteria and ran four
small exact probes. Ranking: R3 non-alpha joins/apex first, R1 symmetry-first
second, R2 graph-first third, R4 S11 cells parked. S042 is queued as a certified
apex-leaf census with its own D077-style gate; it is FUTURE/UNEXECUTED. No
chi>=10 witness; 9<=chi_2<=12. S036 stopped; nine sorted S11 prefixes UNKNOWN.

Findings (all exact for the stated finite classes):
- CLM0137: a layer-preserving automorphism of odd prime order of a 156-edge
  order28 biplanar pair has order 3 (one fixed vertex) or 13 (two fixed
  vertices); orders 5,7,11,17,19,23 are impossible.
- CLM0138: the whole order-13 class is decided: 50600 certified candidate
  layers, 156 planar, 3510 valid pairs, none with alpha<=3; best 767
  independent four-sets (local search reached 79).
- CLM0139: counting (conditional on Kostochka-Yancey) excludes Mycielski-type
  constructions and every chi10 join except K1vH9, K2vH8, K3vH7 with
  omega(H)<=8-a; Hajos junctions cost one apex edge.
- CLM0140: the apex leaf graphs of Sulanke, K3vHajos(K6,K6) and
  K2vHajos(K7,K7) are not biplanar (Lemma-B/C CEGAR, pinned DRAT, every clause
  justified); hence every apex-over-Hajos composite using these leaves fails.

Why R3 first: its chi>=10 is certified by construction and does not require
chi_f>9, which rStation's conjecture F9 would make impossible for all counting
routes (R1, R2, R4 and S025-S040). Its risk is that K9-minor lemmas, which
killed every leaf tested, kill all leaves; S042 measures exactly that.

Checks: fresh full271+K9 smoke PASS (12:32 UTC); frozen S037/S038/S040 replays
PASS. Portable stdlib checker regenerates all order-13 orbits and candidates,
re-verifies every certificate and pair count, the counting facts, the Sulanke
control split, regenerated leaf graphs and archived certificate hashes;
adversarial script rejects nine malformed certificates. Probe CPU about 921 s
of the registered 1800 s; one process at a time; nothing remains running.

Reproduction from repository root (`.venv/Scripts/python.exe` on Windows):
1. Pinned EMP_CADICAL/EMP_DRAT_TRIM plus `scripts/cloud_smoke.py` (receipt
   validation/S041/SMOKE.json).
2. Frozen replays: check_s037/s038 records, check_s040_handoff, check_s040_*.
3. Finished probes (do not rerun to check): `tools/s041_probes.py`,
   `tools/s041_p3.py`, `tools/s041_p4.py p4`, `scripts/archive_s041_certificates.py`.
4. Read-only `scripts/check_s041_adversarial.py`, `scripts/check_s041_records.py`
   (stdlib, CI). DRAT and clause justification are archived local receipts.

Entry main 77a9f5e61732cc805160a489b213ca10b0686c38, tree
16497f46a9ca14de244e9ae3fd79ffb86578c028, parent af53af4a85ad6207b22cd9f2220c52b7a2738036.
Entry hosted [run40094055875](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40094055875),
job120872508137: all27 steps success. One ordinary commit/push on main; final
SHA/tree/parent and the hosted job are verified after publication (receipt
artifacts/tmp/S041/INTEGRATION.json, outside the manifest). No PR/merge.

Next: S042 apex-leaf census (prompt identical in authoritative/
NEXT_SESSION_PROMPT.md and sessions/S041/S042_FUTURE_PROMPT.md).
