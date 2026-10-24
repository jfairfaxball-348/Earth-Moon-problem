# S037 CLOSED — bounded structural reset, 24 October 2026

No certified 10-chromatic biplanar witness; 9<=chi_2<=12. Nine S11 sorted
prefixes remain UNKNOWN. S036 remains CLEAN_STOPPED; frozen files and archives
were preserved. S038 is FUTURE/UNEXECUTED, not run.

- CLM-0123 proves all 247 historical closed prefixes follow from sorting alone.
  Frozen mapping/formula hashes, exact type truth tables, full-eleven-position
  extension counts and all historical certificate IDs were independently checked.
  The 96.5% figure was symmetry bookkeeping, not proximity to completion.
- Explicit planar-pair prototypes cover both 78+78 and 78+77 densities. Best
  results: 91 and 125 independent four-sets. Nineteen saved records (with
  duplicates) have independently checked planar rotation certificates, all
  20475 four-set checks and explicit <=9-colourings. None is a chi>=10 witness.
- The 91-state is a strict single-flip trap: 43 admissible flips all yield >=93.
  Two 155-edge fixed splits cannot add a disjoint edge to their second layer;
  446 explicit K5/K3,3 subdivision certificates cover all possible additions.
  This is not a claim about alternative repartitionings or other graphs.
- Fixed-first-layer hitting has explicit 77/78-edge solutions covering all
  4821 independent four-sets, but their second layers are nonplanar. Four
  fixed-template exact permutation arms capped UNKNOWN without improvement.
- Experimental CPU: 44.625s; nonextension certificate generation: 15.5625s;
  total 60.1875s, plus separately recorded full smoke and short controls/checks.
  Registered finite/plateau limits ended the experiments; no unattended worker,
  scheduled restart, S036 restart, new branch or PR.

Reproduction (Windows `.venv/Scripts/python.exe`, portable `python` where noted):

1. Set EMP_CADICAL and EMP_DRAT_TRIM to pinned native executables and run
   `scripts/cloud_smoke.py`: fresh full 271/271 + retained/fresh K9 PASS.
2. `tools/s037_symmetry.py`: independent exact nine-pattern audit PASS.
3. `scripts/check_s037_controls.py`: 613 legal-flip controls, J1 positive,
   objective comparison, corruption and nonplanarity controls PASS.
4. `tools/s037_pairs.py --cpu-per-arm 40 --steps 15000 --arms 12`, then
   `tools/s037_permutation.py`, `tools/s037_guided.py`, `tools/s037_hitting.py`.
5. `scripts/analyse_s037_structure.py`,
   `scripts/certify_s037_nonextension.py`, `tools/s037_check_pair.py`.
6. `python scripts/check_s037_records.py`: portable stdlib independent evidence
   replay, also installed in hosted scaffold CI. MANIFEST.json pins exact bytes.
   Re-running authoring scripts changes timing fields; use the record checker
   to verify frozen evidence without overwriting it.

Entry main 8e67c193bd09278872fba69a0106a92ce824a85f (tree
70dead44f17e4b770f413515f2ef4ec5b3f90d65), direct child of verified S036 closeout
d972b7832b92c48f2cc920f1f181160e0d2a82e1. Entry scaffold run
[40084389706](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40084389706),
job 120844214068, all inspected steps SUCCESS. This is governance, not science.
Publication uses an ordinary non-force push on existing main; final commit,
remote tree/parent and actual hosted job are checked after publication and
reported with immutable links to the owner. Local post-publication receipt:
artifacts/tmp/S037/INTEGRATION.json (outside frozen evidence to avoid self-hash
cycles). No PR/merge applies under S037's existing-main instruction.

Recommendation: bounded coordinated face-patch repair from the saved 91/125
states, explicitly retaining nonextendible 77-edge layers. Full next prompt:
`authoritative/NEXT_SESSION_PROMPT.md`, identical to
`sessions/S037/S038_FUTURE_PROMPT.md`. No automatic S038 execution.

Actions scientific fallback: `scripts/cloud_setup.sh` then full
`scripts/cloud_smoke.py` in the SAME job on Ubuntu, with pinned tools and finite
CPU caps; archive immutable sources, inputs, controls and certificates.
Historical runner evidence is in validation/S011/SUMMARY.json and
docs/CLOUD_ENVIRONMENT.md; it does not substitute for fresh acceptance.
