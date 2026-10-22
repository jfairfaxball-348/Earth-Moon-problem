# S035 continuation recovery failures retained

The first full restore failed after8,188 created objects with Windows
`OSError: [Errno 24] Too many open files`. The frozen verifier retained every
object output handle until archive EOF. The failed new root
`C:\EM-S035-recovery` remains intact; recovery/FIRST_ATTEMPT.json and
FIRST_ATTEMPT_restore_all.log preserve the exact failure. The new bounded-handle
adapter keeps the frozen restore/verifier bytes unchanged and passes10,004-object,
gzip reconstruction, existing-root and corruption-rejection controls. The next
attempt uses a separate new directory.

One fresh watcher fixture initially started through the Windows venv Python
redirector and hit a startup thread/status race while pausing. Its exact fixture
identity was8592/create1792691722.431854, unrelated to the scientific identities.
The fixture was cooperatively recovered through its own exit file and exited0;
no force termination occurred. New fixtures use sys._base_executable and wait
for startup. The lifecycle primitive now stabilises the suspended thread set
before returning. The final real interruption and lifecycle controls pass.

The first published recovery-control manifest hashed one local CRLF test script,
while Git committed its LF-normalized bytes. Hosted run39828526770 failed this
integrity gate; no science had resumed. Ordinary follow-up commit
e9a4f4e3bf1584c4bce919badb833c07240f7af0 corrects the manifest to the exact
published bytes. Hosted run39828616279/job119998471179 passes. The four
controlling/validation source hashes reviewed for adoption were unaffected.

An early independent review incorrectly described the old watcher glob as one
level too deep. Rechecking confirmed it matches the actual cell/token/file
layout; that statement was corrected before publication. The actual scan gaps
were other scientific roots, candidate/result variants and race/failure handling.

No failure changed a graph verdict, certificate, encoded closure or headline.

The first live startup attempt preceded the watcher's readiness record; the
controller refused it before opening/resuming native contexts. A second attempt
met a Windows reader-sharing PermissionError in the watcher's atomic status
replacement. Its safety path suspended identities idempotently and latched only
the new control STOP. BEFORE_PILOT vs AFTER_REFUSED_STARTUP shows identical native
CPU/counters/log/journal bytes. All failed control files and logs are preserved
in startup-refused/ and the original separate runtime directory. Read/replace
retries and real concurrent-reader controls passed before ordinary publication
0922b7c and the successful actual pilot. The halted adoption status also now
clears its current executing_cells list; per-context paused states and OS CPU
were already correct in the original successful pilot.
