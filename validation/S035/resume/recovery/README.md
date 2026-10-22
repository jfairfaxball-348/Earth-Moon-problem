# S035 preservation-only recovery verification

`REPORT.json` records the current result and exact commands. A result of
`IN_PROGRESS_PRESERVATION_ONLY` is incomplete; only a final
`PASS_ALL_ARCHIVE_BYTES_AND_FRESH_FULL_RESTORE` confirms full restoration.
The logs retain the archive verifier and restore output.

This work verifies hashes and reconstructs original file bytes. It does not
replay scientific certificates, close any region, launch a solver, alter STOP,
or resume/suspend/terminate any campaign identity. Original evidence stays in
place. The original pre-upgrade container has a separate hash receipt in
`PREUPGRADE_ORIGINAL.json`.

The full restore uses a new recovery directory and a separate new dependencies
root. Restored JSON retains original absolute paths as provenance. No prefix
rebasing or execution from these roots was performed. The restore includes all
95 hash-pinned S034 raw proof references through `restore_s034.py --proofs`.
Pinned zlib 1.3.1 reconstructs the original gzip envelopes and deflate bytes.

The first full restore failed on the Windows CRT file descriptor limit because
the frozen object writer kept one handle open per object. Its report, log and
partial new directory are preserved. `scripts/restore_s035_preserved.py` adapts
only that writer, closing each destination after its current chunk and keeping
the same complete hash and byte checks. Both frozen recovery source files stay
unchanged and are hash-checked before the adapter runs. The 10,004-object
regression and exact gzip member checks are recorded in `STREAM_CONTROL.json`.

The 131 current operational lock files are excluded by the original inventory.
Three historical lock members from the pre-upgrade container remain as inert
evidence only under `pre-resident-runtime-expanded/campaign/`; they are not
installed in the restored campaign directory and must never be treated as live
locks or used to invoke a historical controller.

Reproduce only into fresh paths:

```powershell
.venv/Scripts/python.exe validation/S035/resume/recovery/verify_recovery.py
```

The harness verifies all eight parts, their joined SHA256, the local archive,
the 44-file pause manifest, every archived object, every restored logical file,
the S034 archive and raw proofs, and every dependency byte. It refuses a full
restore without enough space for all copies and a 10 GiB reserve.
