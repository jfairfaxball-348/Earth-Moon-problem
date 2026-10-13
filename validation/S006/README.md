# S006 reproduction and trust

Only CAM-0007 and its prospective amendments define the finite domains. Use the pinned .venv and reused S004 native binaries; environment.json records observed versions, source pins and actual SHA256 values. No native build or external Lean development was executed.

From repository root:

    .venv/Scripts/python.exe tools/s006_evidence.py entry
    .venv/Scripts/python.exe tools/s006_run.py replay
    .venv/Scripts/python.exe tools/s006_run.py search
    .venv/Scripts/python.exe tools/s006_run.py search --larger-one
    .venv/Scripts/python.exe tools/s006_chromatic.py
    .venv/Scripts/python.exe tools/s006_chromatic.py --larger-one
    .venv/Scripts/python.exe tools/s006_upper.py
    .venv/Scripts/python.exe tools/check_s006_archives.py
    .venv/Scripts/python.exe scripts/check_scaffold.py
    .venv/Scripts/python.exe -m unittest discover -s tests -v

Evidence capture entry is intended before a new session commit; its assertions expect main to be the merged PR#5 snapshot. Replaying that command later may fail because live main changed. Archived ENTRY_EVIDENCE is the observed entry, not a promise that main stays there. Outgoing live capture uses tools/s006_evidence.py exit PR_NUMBER after actual merge and writes ignored artifacts/tmp/S006/LIVE_EXIT_EVIDENCE.json. Never invent outgoing SHA inside its own commit.

Cold baseline replays K9, row165 biplanarity, row165 bag proof, all271 proper ten-colourings/CNF/proof hashes and all25 full S005 archived compact refutations. It also regenerates and hash-audits S005 redundant independent/reduced archives; those redundant proofs are not all freshly replayed. Twenty-three fresh positive controls are actual planar splits checked separately. The adapted baseline script changes only output directories and retains its exact bytes in ignored scratch; its SHA is in the manifest. Failed controls block new acceptance.

Each search target has graph6, positive bag weights, explicit labels0..n-1, edge file/hash and deficit. For any accepted refutation, decompress search/cover-rowI.cnf.gz and the certificate.archive DRAT to ignored scratch; verify CNF, raw proof and archive SHA256 values from search_results.json. Copy the cut metadata beside the scratch prefix; run tools/triangulation_cover.py check EDGEFILE PREFIX and then drat-trim-mingw.exe PREFIX.cnf PREFIX.drat -t1200 (separate arguments '-t','1200'). The Windows solver itself does not accept -t; all solver caps are external. Native text-DRAT proof, compact extraction and fresh compact check are distinct stages. The retained public proof may be compact; use archive_raw_sha256, not the original proof_sha256. Logs preserve observed native bytes.

Amendment C's larger_one domain has separate larger_targets/larger_search_results files; it starts only after all nine original D=1 exclusions are checked. Chromatic results replay all19 archived lower proofs and directly inspect all upper colourings, separately from biplanarity. The original running search driver was loaded before the prospective larger-lane and counter repair. driver_versions.json distinguishes a reconstruction from exact tool patches (not an observed launch hash) and a later actual file snapshot; no launch-time hash is invented. The mathematical Cover generator and native tools did not change. The final corrected driver reproduces the same formulas and accepted certificates; two consecutive final UNKNOWNs stop a lane. Any actual cap/provenance limitations are retained in ADVERSARIAL/CLOSEOUT.

Hash/CNF audit is reproducibility, not a formally verified encoder. The mathematical necessity proof is research/S004_TRIANGULATION_COVER.md and CLM-0028, permitting completion overlap and noninput edges for any registered deficit. Lex uses checked automorphisms and one common primary order. Actual positive needs both independently checked planar layers and a fresh lower chromatic proof; a SAT relaxation or unverified UNSAT never supplies a verdict.

Gallai_controls.json and palette_trap.json store explicit labelled edges/layers/colourings. tools/s006_upper.py verifies those fixed examples with LR and separate sphere rotations. The all-order forest theorem has a complete hand proof in research/S006_CRITICAL_DENSITY.md; nine equality controls are not its proof. The palette trap has chi8 and external degree1, hence not12-critical. Source-stated Gallai/list/DP facts keep their actual dependencies and access grades. No full graph census, universal colouring improvement, novelty, external review or formal certification implied.
