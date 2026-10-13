# S005 reproduction and trust

Preregistration: campaigns/CAM-0006.md and amendments, sessions/S005/PLAN.md.
Use the observed pinned .venv environment and native source/binary hashes
in ../S005_MANIFEST.json. Source/build provenance is in S004/README.md;
these existing native binaries were reused, not rebuilt in S005.

Run from repository root:

    .venv/Scripts/python.exe tools/s005_replay.py
    .venv/Scripts/python.exe tools/s005_search.py
    .venv/Scripts/python.exe tools/s005_search.py --zero-rest
    .venv/Scripts/python.exe tools/s005_search.py --one-first
    .venv/Scripts/python.exe tools/s005_independent.py
    .venv/Scripts/python.exe tools/s005_independent.py --row120
    .venv/Scripts/python.exe tools/s005_embeddings.py
    .venv/Scripts/python.exe tools/s005_bag_transfers.py
    .venv/Scripts/python.exe tools/s005_dense.py
    .venv/Scripts/python.exe tools/s005_compact.py
    .venv/Scripts/python.exe tools/s005_deficit_one.py
    .venv/Scripts/python.exe tools/s005_small.py
    .venv/Scripts/python.exe tools/s005_kempe.py
    .venv/Scripts/python.exe tools/check_s005_archives.py

Search driver skips already recorded targets. For a genuinely cold run,
use a clean clone plus scratch dependencies; do not delete existing evidence.
The interrupted row179 certificate retry used --one-first --resume, preserving
partial proof hash/status and regenerating before a fresh proof solve.

Full Cover exclusions: decompress search/PREFIX.cnf.gz and PREFIX.drat.gz
to scratch, copy the cut metadata beside PREFIX, run
tools/triangulation_cover.py check EDGEFILE PREFIX, verify raw proof and
CNF hashes against search_results.json, then drat-trim CNF PROOF -t 1200.
The original proof's hash/size and checked compact proof's raw/archive
hashes are distinct fields; use the **archive_raw_sha256** for the public proof.

The separate no-lex row120 CNF/proof uses independent_cover_search.py check
with its own cuts. It has no lex/excess constraint; row165's no-lex attempt
has UNKNOWN status and no public refutation. Positive controls alone do not
certify a universal encoder, whose written necessity proof remains a dependency.

Reduced dense proofs: regenerate tools/dense_face_cnf.py EDGEFILE OUTPUT.cnf
(--global for global mode). Verify CNF hash and decompress its retained DRAT.
If compacted, use archived_raw_sha256/archived_raw_bytes; original proof fields
are retained for provenance. Check drat-trim, using the same original CNF.
SAT_RELAXATION never means a planar split. Missing constraints are intentional.

D=1 relaxed formulas regenerate with deficit_one_cnf.encode(edges), emitted
as exact LF DIMACS by s004_certify.write_cnf. All current solve outcomes and
actual caps are in deficit_one/results.json, including failures/UNKNOWN.
The two controls are actual faces of explicit verified completion layers.

Indices are zero-based positions in survivors_alpha_ge3.json, following S004.
The cached reduced SAT models are independently decoded and clause/triangle
incidence checked by s005_model_audit.py. Their displayed layers are nonplanar;
positive models were not silently promoted.
Native logs preserve their exact observed bytes under .gitattributes, including
CRLF and checker progress carriage returns. Model archives carry matching raw
SHA-256 values; canonical LF CNF bytes and gzip proof bytes are separate.

Layer/rotation and chromatic obligations remain separate. No negative verdict
rests on a solver's UNSAT text. The small23v challenge is not presumed chi10;
if UNKNOWN it is not used as an obstruction. All accepted transfer maps are
injective and preserve every source edge, while failed searches are not
noncontainment theorems. No external formalisation or publication executed.
