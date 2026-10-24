# S038 CLOSED — bounded planar face-patch research, 24 October 2026

No certified10-chromatic biplanar witness.9<=chi_2<=12 unchanged; nine S11
prefixes UNKNOWN. S036 remains stopped. S039 is FUTURE/UNEXECUTED, not run.

The requested prototype is implemented for genuine78+78 and78+77 layers.
It preserves embeddings by exact polygon filling and supports atomic patches
in both layers. Controls, independent exact neighborhoods and every search
transition pass portable stdlib replay. Frozen S037 evidence is unchanged.

- Original91/125 states have no strict improvement in tested one-layer disk
  supports1..4 or joint splits1+1,1+2,2+1,2+2. These are selected fixed-embedding
  families, not all planar moves, embeddings, paths or graphs.
- Independent removed-edge/chord-subset enumeration matches all28039 family
  records (overlap across families). The disk-filling lemma and necessary
  four-set coverage filter are proved directly; no novelty claimed.
- Twelve matched capped arms give best91/123 at156/155 edges. Both single and
  patch methods reach123; patches cost more CPU with no best-score advantage
  in three seeds. Four coupled arms give no improvement at original starts.
- Twenty-two saved layer records, including duplicates, have independent sphere
  rotations, explicit<=9-colourings, counts/disjointness/simplicity checks and
  all20475 four-set checks. Both saved123 states have8-colourings.
- All1736 search transitions are independently replayed, including patch
  boundaries, noncrossing fillings, atomic disjointness and exact scores.
- Experimental CPU101.09375s; fresh full271+K9 acceptance, controls and replay
  recorded separately. All experiments stopped at registered finite/plateau
  limits. No autonomous worker, scheduler or old campaign restart.

Reproduction with `.venv/Scripts/python.exe` on Windows, `python` for portable
checks (run from repository root):

1. Set EMP_CADICAL/EMP_DRAT_TRIM to the pinned native tools and run
   `scripts/cloud_smoke.py`: fresh271/271, retained and fresh K9 PASS.
2. `scripts/check_s037_records.py`: frozen inherited evidence PASS.
3. `scripts/check_s038_controls.py`: polygon4..8 exact counts,80 sampled moves,
   direct scores and malformed/crossing controls PASS.
4. `tools/s038_experiment.py`, `tools/s038_coupled.py`, `tools/s038_radius4.py`:
   author bounded experiment records. Do not rerun against frozen destinations
   just to verify; timings would change.
5. `scripts/replay_s038_neighborhoods.py`, `scripts/replay_s038_coupled.py`,
   `scripts/replay_s038_radius4.py`: independent finite replays.
6. `scripts/validate_s038_pairs.py`: explicit pair/rotation/colour authoring.
7. `scripts/check_s038_records.py`: read-only full portable replay, also in CI.

MANIFEST.json pins the scientific/session records and sources. Exact bests are
in validation/S038/arms/155-3800-patch.json and155-3801-single.json (123), with
the156 best retained from S037. Authority/catalogues distinguish these
finite computational results from the still-open headline objective.

Entry main f8f18621e5b556320a9a4132a7650cda17797e79, tree
6fa290b1db05cff34ef9db6199b110b498a38dd4; prior S037 source/parent verified.
Entry hosted [run40086242706](https://github.com/jfairfaxball-348/Earth-Moon-problem/actions/runs/40086242706),
job120849656724, all24 steps SUCCESS; no open PR at entry. Final publication is
one ordinary non-force push on existing main, with commit/tree/parent and actual
hosted results verified afterward and immutable links in the owner's report.
Local post-push receipt: artifacts/tmp/S038/INTEGRATION.json, outside frozen
evidence to avoid a self-referential commit hash. No PR/merge under this prompt.

Next recommendation: change the move/seed representation rather than continue
boundary-only radius expansion on two weak seeds. The full S039 prompt is
installed identically in authoritative/NEXT_SESSION_PROMPT.md and
sessions/S038/S039_FUTURE_PROMPT.md. It proposes interior-vertex star relocation
and a bounded audit of seeds retaining a certified nine-chromatic core. Neither
is executed here or promised to succeed; older closed Sulanke extension ranges
must be checked first.

GitHub Actions scientific fallback: scripts/cloud_setup.sh then full same-job
scripts/cloud_smoke.py on Ubuntu with pinned tools, registered finite limits,
and permanently archived sources/inputs/certificates. Permanent historical
runner receipts: validation/S011/SUMMARY.json and docs/CLOUD_ENVIRONMENT.md.
Scaffold success alone does not establish fresh scientific acceptance.
