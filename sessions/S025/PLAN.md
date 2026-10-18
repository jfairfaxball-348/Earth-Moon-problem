# S025 PLAN and measured execution

Scope justification: the queued prompt asks for two arms, A (chromatic pressure) and B (global row148). Both stay inside D042 (lower bound only). Arm B *is* the D051/D054 original-219 priority, attacked through row148. No broader rescope was taken.

1. **Entry.** Pin live main b8733f8 (tree 24dda2c, parents f66f0e7 + 2027da4, PR #30). No open PRs, no rulesets; main governance run 38863687297 succeeded (governance only). Read AGENTS/STATE/START_HERE/SESSION_PROTOCOL/CLOUD_ENVIRONMENT, the S023/S024 research files and the failure ledger. *Done.*
2. **Environment.** The owner said to run locally. Use the S004-pinned Windows native CaDiCaL and drat-trim with the project .venv. Run the full scripts/cloud_smoke.py (271 CNF byte matches + DRAT, retained and fresh K9) before any science. *Done: PASS. A first attempt failed before any check on a relative-path issue.*
3. **Arm B, required implementation.**
   - Build the complete two-sphere-triangulation SAT encoding with lazy LINK/CONN cuts and an independent decoder.
   - Controls: K8/J1/J2/K9P3 positive, K9 negative.
   - Stop gate: if the K9 control is not decided within 600 s, treat the encoding as validated-complete but too weak, and change method. *Gate triggered: K9 UNKNOWN at 600 s.*
4. **Arm B, method pivot (in-session decision, recorded in D058).**
   a. Flip-annealing positive oracle over triangulation pairs. Controls: J1, J2, K9P3 split; K9 never reaches 0.
   b. Row148: five seeds of 120–900 s.
   c. Greedy obstruction descent.
   d. C5 classification: all 297 filter-feasible orbits, 2 seeds × 60 s.
   e. Exact refutation with Kuratowski CEGAR + K9-minor lemmas. Every CNF clause independently re-justified; native DRAT checked by drat-trim.
   f. Transfer by explicitly checked subgraph maps to all 271 rows.
   - Stop criterion: every UNKNOWN row settled by a certified obstruction, or caps reached.
5. **Arm A.**
   - Retire the overlap objective.
   - Weighted-independence annealer as a chromatic-certificate objective: α≤2 calibration (n=14–18), α≤3 (n=22–28), weighted total 28, α≤4 (n=30–37); 900–1800 s per configuration. Exploratory, not preregistered before S025.
   - Any zero at n+k ≥ 28 (W=3) or n ≥ 37 (W=4) is re-checked by the elementary brute-force checker, then given a proper 10-colouring.
6. **Closeout.** Ledgers, claims and sources, STATE, the S026 prompt, one authored commit, PR, two-parent merge and live verification.

**Resources.** Preregistered: one heavy worker ≤12 GiB plus light annealing workers. *Actual:* at peak about 14 concurrent Python processes, and free RAM fell to about 1 GiB. Several exact runs then died (one MemoryError; others vanished without output) and one certification batch hit a MemoryError. This is a recorded deviation (sessions/S025/ADVERSARIAL.md, F071). No certified result depends on a failed run.
