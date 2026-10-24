# S040 CLOSED — D077 decision PIVOT, 24 October 2026

The registered solid-progress gate failed, so the decision is **PIVOT**: star/
patch/coordinated hill-climbing on the four-set objective is parked and S041
is queued as a comparative audit of genuinely different construction routes.
No chi>=10 witness; 9<=chi_2<=12 unchanged. S036 remains stopped; nine sorted
S11 prefixes UNKNOWN. S041 is FUTURE/UNEXECUTED and is not run here.

Gate evidence (PLAN.md, hashed before any objective value). Exact coordinated
neighborhoods at the S039 bests 82 (156 edges) and 79 (155): 216,582 and
119,281 scored states, zero strict improvements for singles and type0/1/2
pairs. Twelve matched unprotected arms (star/pair0/coord x two seeds x two
starts) all ended at their starts; protected arms reached 192 once. B1 fails
for all four coord arms (thresholds 41/39) and C fails (192>39).

What was learned (diagnostic, not constructive). tau=5/7 exactly; every
four-set already has a pair addable by an S039-legal single move, so the
opposite-layer occupancy that coordinated stars relax is not the bottleneck
(C2 only 2/5 pairs). Post-hoc, unrestricted single swaps improve by up to
31/19, but the hub pairs complete K9/K10 clusters: tau_safe=17/11 exactly and
that safe set still forms K9/K10; label-fixed alpha<=3 repairs contain K10.
Four-set minimisation at maximal density converges to near-K9 structure that
biplanarity forbids. Compatibility lemma CLM0133; exact neighborhoods CLM0134;
arms/gate CLM0135; diagnostics and K9 barrier CLM0136.

Checks. Fresh full271+K9 smoke PASS (11:56 UTC). Controls: S039 766/1045
singles reproduced; compatibility equals direct disjointness on14.6M pairs;
type decomposition for every pair; sphere checks. Independent chord-subset
replay with delta scoring and with OR masks matches both table hashes. All482
transitions, 24 saved records (sphere rotations, four-sets, colourings,
alpha), diagnostics certificates and nine malformed-certificate controls pass
in the portable stdlib checker. Every saved pair is <=9-colourable.

CPU: experiment315.15625 s, post-hoc31.90625 s; controls, replay and pair
checks separate; total far below7200. One experiment process; it finished at
12:15:17Z and nothing remains running. Unsearched, not excluded: coordinated
flips/patches, multi-star moves, degree2/>6 stars, other embeddings.

Reproduction from repository root (`.venv/Scripts/python.exe` on Windows):

1. Pinned EMP_CADICAL/EMP_DRAT_TRIM plus `scripts/cloud_smoke.py`: receipt
   validation/S040/SMOKE.json.
2. `scripts/check_s037_records.py`, `check_s038_records.py`,
   `check_s040_handoff.py`: frozen inherited replays.
3. Authoring scripts `check_s040_controls.py`, `tools/s040_experiment.py`,
   `validate_s040_pairs.py`, `posthoc_s040_swaps.py`, `posthoc_s040_repair.py`,
   `replay_s040_neighborhoods.py --delta`: finished and frozen; rerunning
   rewrites timing fields, so do not overwrite records merely to check them.
4. Read-only `scripts/check_s040_adversarial.py` and
   `scripts/check_s040_records.py`: portable stdlib replay, in CI.

MANIFEST.json pins new sources, session and scientific records; advancing
authority, catalogues, workflow and the manifest itself are excluded.
LOCAL_CHECKS.log records the local workflow, not hosted CI.

Entry main af53af4a85ad6207b22cd9f2220c52b7a2738036, tree
0c61efb288768dd53d216c63b8c62b0e5b6ab5e3, parent 7521e4e2fc78a8b3ca612d39265e2c6ddd8d75a4.
Entry hosted [run40091261553](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40091261553),
job120864239510: all26 steps success, clean local/remote match, no open PR.
One authored ordinary commit/push on main; the final SHA/tree/parent/remote and
actual hosted job are verified after publication and linked in the owner's
report; post-push receipt artifacts/tmp/S040/INTEGRATION.json (outside the
manifest). No PR/merge.

Next: S041 comparative audit (routes R1 symmetry-first, R2 graph-first then
exact split, R3 non-alpha structural compositions, optional R4), each with
sources, closed ranges, mechanism, certification path and a falsifiable first
experiment; S042 must carry its own D077-style gate. Full prompt identical in
authoritative/NEXT_SESSION_PROMPT.md and sessions/S040/S041_FUTURE_PROMPT.md.
