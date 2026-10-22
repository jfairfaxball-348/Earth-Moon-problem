# Independent Windows sharing fix review

Status: PASS. Reviewed watcher SHA256 is recorded in SHARING_FIX_REVIEW.json.
The previous FINAL_REVIEW and its source hashes are retained unchanged.

The change retries only transient PermissionError during JSON reads and atomic
replacement, for at most100 attempts with10ms between attempts. A complete
fsynced temporary file is retained while replacement is retried. Persistent
failure still raises into the existing preservation path; no lifecycle, SAT
priority, STOP or identity gate is bypassed.

Independent new temporary-file controls pass for fourth-attempt replacement,
fourth-attempt read, and exhaustion after100 attempts. On exhaustion, the old
target and the complete unpublished temporary JSON both survive. These controls
perform no process actions.

Read-only comparison of BEFORE_PILOT and AFTER_REFUSED_STARTUP confirms all four
native identities, CPU totals, counters, log lengths and geometric journal
lengths are identical. Every native remains stopped with zero sampled CPU, and
all eight legacy processes remain preserved. The refused startup did not run a
scientific pilot. The corrected source must be republished and its acceptance
hash updated before a fresh watcher-ready gate and actual bounded pilot.
