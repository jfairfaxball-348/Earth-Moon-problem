# S039 CLOSED — bounded vertex-star research, 24 October 2026

Star relocations escape the two S038 basins, producing best82/79 independent
four-sets at156/155 edges. Every saved graph has a proper<=9-colouring, so
there is no chi>=10 witness;9<=chi_2<=12 unchanged. S036 remains stopped and
nine sorted S11 prefixes UNKNOWN. S040 FUTURE/UNEXECUTED is not run here.

Exact selected degree3..6 neighborhoods have766/1045 distinct effects, minima
83/116 and4/5 strict improvements from the91/123 starts. Independent chord-subset
and polygon-splitting enumeration matches all1811 effects. The star lemma
preserves edge count and quad deficit, including a genuine77-edge layer.
Eight matched patch/star arms give best91/123 for patches versus82/79 with
stars; ceilings/seeds/inputs agree, actual CPU differs. Two seeds do not prove
statistical superiority. Best155 score79 has alpha exactly4; best156 score82
has an independent5-set. Those distinctions do not change their9-colourability.

The Sulanke K6-join-C5 core is independently verified exactly9-chromatic with
26/24 planar edges. Old retained-core extensions through17 stay closed. Four
order28 seeds preserve it. Pure coning into paired tri/quad faces always allows
a9-colouring extension (<=8 earlier neighbors), so it is a calibration family.
Protected non-insertion searches yield best193/210 at156/155; separate explicit
9-colourings prove their exact chi9. No exhaustive core-extension claim.

All22 saved layer records (including duplicates), all762 search transitions and
four17-insertion seeds independently replay. Sphere rotations, simplicity,
disjointness, exact counts, all20475 four-sets and colourings check.110 sampled
moves cover ordinary/quad stars and targets inside/outside the hole. Eight
malformed certificate controls are rejected. No SAT-negative claim or colouring
SAT attempt occurred. Claims CLM0129..0132; related method source SRC0061.

Experimental CPU79.71875s, saved classification1s separate, controls2.140625s
and replay separate, below7200s. Every experimental arm finished at its finite
plateau; no process/scheduler remains from this session. No frozen S036/S037/
S038 artifact/source changed. Degree2/>6, nonsimple links, simultaneous opposite-
layer relocations and other embeddings remain unsearched, not excluded.

Reproduction from repository root (`.venv/Scripts/python.exe` on Windows):

1. Pinned EMP_CADICAL/EMP_DRAT_TRIM plus `scripts/cloud_smoke.py`: fresh271+K9
   PASS; receipt validation/S039/SMOKE.json,24Oct11:05:35 UTC.
2. `scripts/check_s037_records.py` and `scripts/check_s038_records.py`: frozen
   inherited sources/evidence replays, also verified in the full local workflow.
3. Authoring scripts `check_s039_controls.py`, `tools/s039_experiment.py`,
   `replay_s039_stars.py`, `validate_s039_pairs.py`: already finished and frozen;
   do not overwrite records merely to check them, as timings would differ.
4. Read-only `scripts/check_s039_adversarial.py` and
   `scripts/check_s039_records.py`: complete portable stdlib replay, in CI.

MANIFEST.json pins new sources/session/scientific records; advancing authority,
catalogues/workflow and manifest itself are excluded. Frozen imported helpers
are pinned and rechecked by preceding session manifests. LOCAL_CHECKS.log
records the complete local workflow, not hosted CI or a fresh science run.

Entry main af422b1bf68402f4eb072c82c9012cecc57d4202, tree
9ee7c27a78e87cab3704854d5e9cd5b8df5e76f6, parent f8f18621e5b556320a9a4132a7650cda17797e79.
Entry hosted [run40088018936](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40088018936),
job120854812683: all25 steps success, clean local/remote match, no open PR.
One authored ordinary commit/push on main; final SHA/tree/parent/remote and
actual hosted jobs are independently verified after publication and linked in
the owner's report. The post-push local receipt is artifacts/tmp/S039/
INTEGRATION.json, outside the manifest to avoid self-reference; no PR/merge.

Recommended S040: diagnose the remaining independent-four-set hypergraphs and
test atomic stars in both layers, permitting provisional conflicts only when
the other move removes the conflicting edge. Start from the improved79/82
pairs; compare against S039 stars with matched caps and retain a small protected-
core arm. This changes compatibility, not just runtime. It is a prospective
experiment, with no guaranteed improvement. Full prompt identical in
authoritative/NEXT_SESSION_PROMPT.md and sessions/S039/S040_FUTURE_PROMPT.md;
print it with verified integration links and stop before execution.

GitHub Actions science fallback: `scripts/cloud_setup.sh` then full same-job
`scripts/cloud_smoke.py` on Ubuntu with pinned tools and archived artifacts.
Permanent runner evidence: validation/S011/SUMMARY.json and
docs/CLOUD_ENVIRONMENT.md. Scaffold checks do not replace fresh smoke.
