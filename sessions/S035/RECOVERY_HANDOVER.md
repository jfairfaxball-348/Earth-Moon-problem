# S035 recovery handover

Do not restart automatically. Invoke S036 using the paired complete prompt.
Read validation/S035/closeout/PROCESS_SNAPSHOT.json and live thread identities;
RAM learning survives only while exact original suspended processes survive.
Do not use legacy STOP/recover, remove original STOP, resume helpers or kill
anything. Existing controller/watcher are gone; no continuous active guard is
claimed for this closed paused run. Recheck RAM/disk before any new work.

Portable semantic recovery: use scripts/restore_s035_preserved.py to restore
the existing base pause archive/dependencies into a NEW root with bounded
descriptors and explicit path rebasing. Consult its --help; the previous full
restore passed and must not be overwritten. Resolve base runtime.tar.xz from
committed verified parts with tools/s035_archive_parts.py; external S034 proof
bytes are validation/S034/campaign.tar.xz. Then overlay only files labelled
CLOSEOUT_DELTA in validation/S035/closeout/DELTA_INVENTORY.json from the adjacent
runtime-delta.tar.xz, checking each size/SHA256 and safe relative destination.
Delta storage labels BASE_PAUSE_ARCHIVE and EXTERNAL_S034_ARCHIVE refer to the
original exact-byte inventories, not to current live copies. Original pre-upgrade
container is retained locally; its expanded member bytes are in the base archive.
No lock/lease/PID file is runnable authority in a restored directory. Rebase
recipes without altering frozen originals. Never claim archive restores CDCL RAM.

DELTA_VERIFICATION.json records an actual fresh-root restoration and all changed
file hashes, not just archive readability. Base ARCHIVE_VERIFICATION.json and
resume/full-restore receipts remain immutable. New geometric journals have
PREFIX_AUDIT.json receipts; deduplicate/register immutable blocks before sharing.
This closeout does not edit historical REGIONS, resident context or certificate
ledgers. New S036 claims must be written into a separate execution ledger.
