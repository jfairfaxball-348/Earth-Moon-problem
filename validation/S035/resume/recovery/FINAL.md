# S035 recovery byte verification: PASS

Full recovery completed in `C:\EM-S035-recovery-20261022T180328Z`; dependency files are in `C:\EM-S035-dependencies`.
Both roots were new. No existing recovery or live campaign directory was
overwritten, no original evidence was deleted, and no campaign process was
launched, resumed, suspended or terminated by this recovery work.

All eight runtime parts, their joined SHA256 and the local archive match
`bd2f8dbecc1d0558d9cb0110f3d205d7b65c405db830c61b7203fde312f09ab5`.
The original verifier passed all 12,969 archived objects. The corrected
bounded-handle writer then reconstructed and checked every original object,
including both raw and original gzip hashes with pinned zlib 1.3.1/level 1.
All 24,891 logical S035 files and all 95 referenced S034 raw proof files were
copied and hash-checked. The committed S034 archive was hash-checked and all
1,510 original files, including its raw proofs, were restored and checked.
All five dependency files and their archive hash passed. All 44 frozen pause
manifest files were rechecked unchanged after restoration. The local original
pre-upgrade container remains unchanged with its separately recorded SHA256.

The first stock restore exposed the Windows CRT descriptor limit. Its failure
log/report and partial fresh `C:\EM-S035-recovery` remain preserved. New
`scripts/restore_s035_preserved.py` closes each output handle after its current
chunk while retaining every original byte/hash gate. Both frozen recovery
sources remain unchanged. The 10,004-object regression, four exact gzip-member
checks, existing-root refusal, damaged-inventory rejection and corrupted-object
hash rejection passed.

Original absolute recipe paths remain provenance; no prefix was rebased and
no recovered executable was run. Future imports must register each old/new
prefix explicitly and verify each original file hash before using a rebased
path. The 131 current operational lock files were excluded. Three historical
lock member bytes remain only in the inert pre-upgrade expanded subtree.

At the static final check, free disk was 18,327,756,800 bytes
(17.07 GiB), above the 10 GiB reserve.
This is archive integrity and exact-byte recovery, not a scientific certificate
replay or a new mathematical result. See `REPORT.json`, `FINAL.json` and the
retained stage logs for commands, paths and failure provenance.
