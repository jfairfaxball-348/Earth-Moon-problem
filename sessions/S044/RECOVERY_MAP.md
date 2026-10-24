# S044 recovery and re-entry map

All existing scientific records remain versioned and frozen. No old worker,
scheduler, autopilot or retained-RAM context is a permitted recovery path.
Private CDCL state was not durably saved by S043; its CNF and semantic cuts
are preserved. S036's historical clean stop remains authoritative.

| Purpose | Permanent location | Safe verification |
|---|---|---|
| Historical prefixes and planar prototypes | validation/S037 and sessions/S037 | scripts/check_s037_records.py |
| Patch and star evidence, explicit <=9 colourings | validation/S038, validation/S039 | check_s038_records.py; check_s040_handoff.py; check_s039_adversarial.py |
| Coordinated-move gate and K9/K10 diagnostics | validation/S040 | check_s040_adversarial.py; check_s040_records.py |
| Order-13 finite class and original apex decisions | validation/S041 | check_s041_adversarial.py; check_s041_records.py |
| Leaf type table, edge lists, archived DRAT | validation/S042 | check_s042_adversarial.py; check_s042_records.py |
| Exact Z3 encoding and all 20,000 cut subdivisions | validation/S043/BASE.cnf.gz, FINAL.cnf.gz, CUTS.jsonl.gz, ENCODING.json | check_s043_adversarial.py; check_s043_records.py |
| Current audit and scope correction | sessions/S044; validation/S044 | scripts/check_s044_records.py |

Run portable checks from the repository root with Python 3.12; they do not
start research. Use .venv/Scripts/python.exe on Windows. Read-only replay may
write its own console output; do not run experiment-authoring scripts against
frozen destinations. The S042 portable checker verifies hashes, receipts and
selected reconstruction; it does not freshly run all 97 DRAT checks. A full
replay requires pinned tools, fresh full smoke, deterministic regeneration and
scripts/archive_s042_certificates.py --verify, registered as a separate bounded
verification job. Local S042 CNF/lemma files are optional caches under
artifacts/tmp/S042/certificates_local; committed edge/proof archives and recipes
are the durable path.

Before any new research: obtain the owner's concrete choice, pin live main,
read current authority, register inputs and symmetry/completeness claims,
certificates and stopping criteria, run fresh cloud_smoke.py, and use new
session-specific output paths. The cloud scientific fallback is
scripts/cloud_setup.sh followed by full cloud_smoke.py in the SAME job;
docs/CLOUD_ENVIRONMENT.md and validation/S011/SUMMARY.json retain runner details.
Hosted scaffold success validates its actual checks; it is not a substitute
for a scientific proof certificate. Do not infer a research ETA from any
model, cut, rule or prefix count.
