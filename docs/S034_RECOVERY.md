# S034 results and Windows recovery

Read validation/S034/SUMMARY.json and sessions/S034/CLOSEOUT.md first. The
campaign stopped cleanly for disk reserve. No S035 or later computation ran.

The final manifest hashes the immutable entry evidence, final results and archive.
campaign.tar.xz is a lossless tar/xz stream: ordinary metadata lives under runtime/;
large DRAT proofs are interleaved1MiB chunks under proof-chunks/<file-id>/<offset>.
RUNTIME_INVENTORY.json maps original paths to byte sizes/SHA256 and proof IDs.
The archive also contains the identical inventory. This layout shares repeated
proof content efficiently without changing any proof bytes. archive_s034.py
stream-verified every original byte after compression. restore_s034.py is stdlib
and portable, rejects unsafe paths/overwrites and verifies every original file.

From the existing repo on Windows, using its pinned Python environment:

    python scripts/restore_s034.py --output artifacts/tmp/S035/imported-s034

This restores logs, exact recipes, checkpoints and accepted cut blocks, while
stream-verifying but omitting large DRAT files. Append --proofs only if the extra
~11.2GB is wanted. validation/S034/new-geometric.lem.gz separately contains all
93047 additions in recorded chronological block order. The original seed archive
is validation/S032/stopped/learned.lem.gz, with exact hash in the S035 prompt.

JSON absolute paths/PIDs/timestamps are provenance, not a live Windows config.
Import/rebase to the new root, verify each source/hash and clear live claim state;
retain the original archived certificates/recipes unchanged. Rebuild Windows
natives from pinned source, establish fresh deadlines/resource caps, independently
validate formulas/proofs for inherited closures, port POSIX lock/process controls,
and run fresh acceptance before science. Never execute the phone guardian config.
The16 closures concern encoded regions, not16 individual graph decisions.

Proof storage dominated the stop:95 files total11200738114 raw bytes. Do not
repeat this growth at multiple-worker scale. Apply audited lossless compression,
explicit budgets and recovery tests. Do not delete the sole copy of any evidence.
Private CDCL state was not saved. The old scheduled deadline has expired.

D044 fallback: ubuntu-24.04, pinned setup and full271+K9 smoke in the SAME job;
permanent validation/S011/SUMMARY.json and validation/S012 evidence. Historical
runs38623187997,38623722547,38624616691,38635879431 do not validate a fresh
Windows multiworker environment. Current hosted scaffold checks are governance.
