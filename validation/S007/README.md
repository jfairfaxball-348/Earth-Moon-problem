# S007 reproduction and trust

CAM-0008 and prospective amendments A-D are the exact registration. From repo root with pinned .venv/native S004 tools:

    .venv/Scripts/python.exe tools/s007_run.py replay
    .venv/Scripts/python.exe tools/s007_static_controls.py
    .venv/Scripts/python.exe tools/s007_spare.py
    .venv/Scripts/python.exe tools/s007_run.py search
    .venv/Scripts/python.exe tools/s007_global.py
    .venv/Scripts/python.exe tools/s007_upper.py
    .venv/Scripts/python.exe tools/s007_heavy_cegar.py
    .venv/Scripts/python.exe tools/check_s007_archives.py
    .venv/Scripts/python.exe scripts/check_scaffold.py
    .venv/Scripts/python.exe -m unittest discover -s tests -v

Do not exceed two computing workers; heavy/global/full lanes have distinct registered caps/stops. Native provenance in environment.json and S004 README. Cold baseline checks40 full archived proofs and K9/row165/bag;271 chromatic archive/hash/colour checks are not fresh proof replay of all271. Four selected targets have fresh lower proof checks.

StrongCover adds necessary subsets/K5 cuts to old Cover and a provedD<=2 distinct-face consequence; do not enable that last consequence atD>=3. Any new full negative archive decompresses CNF/proof/cuts to scratch and regenerates with tools/s007_cover.py check EDGEFILE PREFIX, then drat-trim PREFIX.cnf PREFIX.drat. Compare original/retained raw and gzip hashes separately. Same-numbered source rows retain exact labels.

GlobalD2 SAT logs contain every native auxiliary assignment. tools/check_s007_archives.py cold-regenerates and verifies every clause, then direct face/multiplicity counts; .model.json retains projections. These models have no layer/planarity converse. D2 controls on actual42-vertex completions and23 pinned StrongCover completions are separate finite controls, not a proof by testing.

Heavy local graph splits/colourings/rotations are in heavy_search.json and heavy_cegar_result.json. Exactchi7/8 is elementary from the exhibited clique plus proper colouring, neverchi>=10. Kuratowski partial CNF/lemmas, if retained, have independently checked structures and cold regeneration but require a checked complete DRAT refutation to yield a negative. A partial RUNNING/UNKNOWN record is not a proof. Compressed lemma JSON may be decompressed to scratch beside the CNF for tools/check_cegar_certificate.py; canonical LF byte regeneration is a separate recorded check.

Observed prelaunch driver hashes are permanent. The replay_driver_snapshot was restored against the actually observed hash after a temporary helper insertion; initialglobal path-type failure preceded target solves and has a separate launch hash. No reconstructed hash is labelled as observed at launch. Source/native hashes remained fixed. Final manifest hashes staged Git bytes, with raw Windows hashes separately where needed; manifest excludes itself. Outgoing integration is independently observed after commit, never anticipated in frozen records.

Shared published premises, Python/PySAT and native checker trust remain; no Lean/external universal review/source-archive execution/novelty guarantee. Headline9..12 unchanged; onlyS007 executed.
