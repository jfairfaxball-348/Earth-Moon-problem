# S046 closeout

S046 CLOSED, decision PIVOT / INCONCLUSIVE, 25 October 2026. Invoked by the
owner's "run next session" under D047 (prompt sessions/S045/S046_FUTURE_PROMPT.md,
sha256 f4c202cd…8452, unchanged). Executor: Claude Code desktop
(claude-opus-5-5) on the owner's Windows laptop. No witness; 9<=chi_2<=12.

Preregistration validation/S046/REGISTRATION.json was written at 08:56:27 UTC
before any experiment; fresh full 271+K9 smoke PASS (validation/S046/SMOKE.json).
Experimental use 1428.7 CPU s / 1352.5 wall s excluding in-slice audits
(raw 1552.5 / 1476.3 including them) against the 1800/3600 ceiling
(validation/S046/BUDGET.json).

Findings:

1. Saved S045 candidates are mainly easy. Exact census of all 642381 records:
   640299 (99.676%) have an empty 9-core, so they are 8-degenerate and
   explicitly 9-colourable; no record has minimum degree 9; zero labelled
   duplicate unions. All 300 stratified sample records have explicit checked
   colourings with at most 8 colours. 78% of S045 recycle-phase wall time was
   preparation plus audit (86% in the last eight slices).
2. Reductions written and checked: a chi>=10 biplanar graph contains a
   biplanar 10-critical subgraph (minimum degree 9, connected, no cut vertex,
   K9-free, 9n/2 <= m <= 6n-12). Core order n is a separate domain from
   "at most n". Lex-leader rows plus first-pair layer rule are sound
   (written proof; exhaustive controls at n=4,5,6). Positive control: the core
   plus symmetry search rediscovered K6 v C5 at n=11, k=8 in 5 s.
3. Matched pilots (orders 24/28/32/40/50 x baseline, core, core+symmetry,
   60 s each): no arm passed the registered targeting criterion. Every
   analysed candidate (300) had a checked colouring with at most 8 colours;
   core filtering lowered clique numbers and throughput; static symmetry
   breaking produced nothing at n=40, 50.
4. Post-hoc calibration A1 (registered after E3, k=8): K6 v C5 found at n=11
   only; no 9-chromatic graph in 40 s at any order 13–24, including the
   baseline domain at n=15/20 where padded K6 v C5 certainly lies.

Decision: no domain or design is selected. E4 checkpoint repair and
operational acceptance were conditional and NOT RUN. Long runs of unguided
colouring-feedback generation are not supported by the evidence. No finite
domain was excluded; every native run ended by its time cap (no UNSAT at k=9).
S045's 50-vertex domain is not recommended as a target.

Next: S047 calibration-gated mechanism trial (seeded generation and
co-certificate amplification against the k=8 ladder; bounded k=9 pilot only
if a mechanism qualifies; otherwise PAUSE recommended), FUTURE/UNEXECUTED.
Full prompt byte-identical in authoritative/NEXT_SESSION_PROMPT.md and
sessions/S046/S047_FUTURE_PROMPT.md. The owner may instead pause.

Evidence: sessions/S046/{INPUT,PLAN,RESEARCH,ADVERSARIAL,PRIOR_ART}.md;
validation/S046 (registration, amendment, smoke, controls, diagnostics,
pilots, calibration, certificates, runtime manifest, budget, MANIFEST).
Portable check: python scripts/check_s046_records.py (add --native locally to
re-run drat-trim on the 8 archived DRAT certificates). Frozen pre-S046 checks
replay against exact entry authority bytes via scripts/s046_replay_history.py.
Before publication every run step of .github/workflows/scaffold.yml passed
locally (38/38, validation/S046/LOCAL_CI.json); that is not a hosted result.

Integration: existing main, ordinary non-force commit/push, no branch/PR.
Entry main 5f56fdf14b88eef9b77f549679c35a1e59a5b106, tree
150651489c2f1afae044f9d82461cf23c7cf0d79, parent
a55d0d00ce5eb620df941ee19650e3a2d804639e, entry hosted run 40176540308
success. The final commit and its hosted run are verified after publication
and reported to the owner; artifacts/tmp/S046/FINAL_INTEGRATION.json records
them locally. No S047, automation, Lean, publication, outreach or S035/S036/
S045 resumption was performed.
