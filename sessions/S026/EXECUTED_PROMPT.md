# S026 — obstruction-aware χ≥10 candidate generation with the S025 exact engine (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem

## Invocation and binding scope
- The owner's next "run next session", or a submission of this S026 prompt or its link, authorises exactly S026 under D047. No second confirmation is needed. STOP before S027.
- D042 remains lower-bound-only: exhibit a finite simple biplanar graph of chromatic number ≥10 with all independent proof checks.
- Do NOT work on universal upper bounds, Lean, Palomar, arXiv, manuscripts or outside correspondence.
- S025 settled the D051/D054 original-219 queue. The whole fixed 271-row exactly-χ10 clique blow-up corpus is certified NON-BIPLANAR, so that priority is discharged (D058).
- S026 may therefore choose new candidate sources within D042. It must justify each arm quantitatively and preregister caps before running.

## Integration handoff note (2026-10-18)
S025 local source commit8fda361 and PR31 main6883520 diverged. Read docs/S025_INTEGRATION_RECONCILIATION.md and validation/S025/INTEGRATION_MANIFEST.json, then obtain the final ordinary PR/two-parent merge/checks live. Both authority histories and the actual S025 execution prompt are preserved. Two omitted proof archives are restored against recorded compressed/raw digests; targeted .gitattributes preserve three recovered original tool byte hashes. No new scientific computation was performed during reconciliation and no S026 local-run permission is inferred.

## Read-first frozen S025 facts and integrity
Independently pin live main (commit, tree, S025 PR and two-parent merge), workflows/checks, open PRs, branches and rulesets. Read:
- AGENTS.md, STATE.json, START_HERE, SESSION_PROTOCOL, CERTIFICATE_POLICY, CLOUD_ENVIRONMENT;
- research/S025_C5_OBSTRUCTIONS_CORPUS_CLOSURE.md;
- sessions/S025/{RESEARCH,ADVERSARIAL,PRIOR_ART,CLOSEOUT,MANIFEST.json};
- campaigns CAM-0027..0029;
- validation/S025 (C5_CERTIFICATES.json, TRANSFER_271.json, ARM_A_FRONTIER.json, SMOKE.json, ENVIRONMENT.json).

S025 key facts:
1. **Lemma B/C (CLM-0090/0091).** Cross-layer K9-minor contraction lemmas, valid given K9's thickness 3.
2. **Exact engine.** `tools/s025_minor_cegar.py --lemmaC 5` (Kuratowski CEGAR plus Lemma-C clauses) refuted 17-vertex C5 clique blow-ups in 43–2400 s. Plain Kuratowski CEGAR and the complete triangulation-cover SAT encoding were too weak; K9 cover was UNKNOWN at 600 s.
3. **Verification of every refutation.**
   - `tools/s025_check_minor_cert.py` re-justifies every CNF clause.
   - `tools/s025_regen_cnf.py` rebuilds the CNF byte-for-byte from the gzipped lemma JSON.
   - drat-trim VERIFIED native CaDiCaL proofs.
4. **C5 threshold.** C5[a₁..a₅] (all aᵢ≥1) is biplanar for all 262 K9-free classes with Σaᵢ≤16, each with an explicit checked split. The Σaᵢ=17 classes listed as certified in C5_CERTIFICATES.json are non-biplanar. The other 8 Σaᵢ=17 classes are UNKNOWN: 3 are CEGAR-UNSAT with DRAT not completed and 5 are NOT_COMPLETED; all had annealing defect 1 (heuristic). The full iff-classification is pending those classes.
5. **Corpus closure.** All 219 former UNKNOWN rows, row148 included, contain a certified C5 obstruction under explicit checked vertex maps. The corpus is 271/271 NON-BIPLANAR. This is not a χ₂ statement.
6. **Positive oracle.** `tools/s025_cover_anneal.py` (triangulation-pair flips). Arm A weighted-independence annealing, heuristic best minima only:
   - α≤3 biplanar graphs reached n=24; n=25..28 bottomed at 1, 4, 13, 35;
   - W=3 total weight 28 stayed at ≥8 bad sets;
   - α≤4 reached n=32.
7. **Environment.** S025 ran on the owner's local Windows workstation with the S004-pinned native binaries after a full 271+K9 smoke PASS. Peak concurrency exhausted RAM (F071); respect one heavy ≤12 GiB worker and keep the total under 12 GiB.

Classical 9 ≤ χ₂ ≤ 12 is unchanged.

## Arm 1 — finish and harden the C5 classification (bounded)
- DRAT-certify the three CEGAR-UNSAT classes C5[2,4,3,3,5], C5[2,3,5,2,5] and C5[2,3,5,3,4]. Run the S025 engine on the five NOT_COMPLETED classes C5[2,3,4,3,5], C5[2,4,3,4,4], C5[2,4,4,2,5], C5[3,3,3,4,4] and C5[3,3,4,3,4]. Work serially, one heavy worker, cap 4 h each.
- Certify each with clause re-justification, byte regeneration and drat-trim.
- If all are certified, record the classification theorem with its exact dependency on K9.
- Attempt, but do not require, a hand proof of the Σaᵢ≥17 direction from Lemma C. A partial hand argument is not a theorem.

## Arm 2 — obstruction-aware candidate source (main research arm)
Design and preregister ONE source of explicitly ≥10-chromatic candidates that provably avoids:
- K9;
- every certified C5 obstruction as a subgraph;
- S013/S014/S023 closed families.

Examples:
- clique blow-ups of 9–11-vertex bases filtered by the new obstructions;
- weighted/partial blow-ups whose bags are not cliques;
- permuted-layer unions T ∪ σ(T) checked for χ_f > 9.

For each candidate:
- exact χ ≥ 10 by checked no-9 DRAT, or an elementary weighted-independence certificate;
- biplanarity by annealer (positive) and minor-CEGAR (negative), with full certification.

Report counts generated/filtered/decided, and stop at preregistered caps. Generalise Lemma C carefully (other certified non-biplanar minor targets, or two non-singleton branch sets) ONLY with a hand proof and an extended clause checker. Any new lemma family must pass K9/J1/C5 controls.

## Arm 3 (optional, light) — chromatic-pressure frontier
Extend the weighted-independence annealing only if a structural reason is given (e.g. χ_f-targeted weights from LP duals). Do not repeat S025 configurations.

## Environment and reporting
- If running locally: full scripts/cloud_smoke.py with absolute native paths before science.
- Otherwise: Claude cloud hook, or D044 never-merged WIP GitHub Actions with same-job setup and full smoke.
- Record package, native and source SHA256, seeds, caps, wall time and memory, exact attempted counts, and independent checker verdicts.
- One heavy ≤12 GiB worker at a time; no RAM oversubscription.
- Distinguish heuristic, exact finite, SOURCE_STATED and formally certified results.

## S026 closeout contract
- Write sessions/S026/{INPUT,PLAN,RESEARCH,ADVERSARIAL,PRIOR_ART,CLOSEOUT,MANIFEST.json,OWNER_INVOCATION,EXECUTED_PROMPT}, paired catalogue claim/source entries, campaign/decision/failure/phase/session records and a truthful STATE.
- Write a COMPLETE S027 FUTURE/UNEXECUTED prompt, byte-identical at authoritative/NEXT_SESSION_PROMPT.md and sessions/S026/S027_FUTURE_PROMPT.md.
- One isolated authored commit, ordinary PR, non-force TWO-parent merge; independently verify main, tree, parents and hosted checks.
- The final user report MUST include the full S027 prompt verbatim and verified GitHub links. STOP before S027.
