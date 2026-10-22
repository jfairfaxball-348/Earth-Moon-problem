# S035 â€” SAT-first resumption and nine-region diagnostic (OWNER INVOCATION REQUIRED)

This prompt resumes S035 only when the owner explicitly supplies it for execution.
S035 is PAUSED, not completed. S036 and all later sessions are not authorised.
Use this existing repository/main; no new project, branch, PR or force push.

1. Read AGENTS.md, authoritative/STATE.json, sessions/S035/PAUSE.md,
   NINE_REGION_DIAGNOSTIC.md, RESIDENT_UPGRADE_PLAN.md and validation/S035/pause/.
   Reconcile remote main, actual hosted jobs and local edits. Do not automatically
   launch or recover a guardian. The prior guardian/controller JSON says RUNNING
   because it is frozen: OWNER_PAUSE.json and authoritative PAUSED take priority.

2. SAT FIRST: inspect SAT_AUDIT.json and rescan all native logs, exit-code10
   results and candidate files. Run scripts/s035_sat_first_watch.py --once.
   Any SAT signal takes precedence over UNKNOWN, stop reasons and ordinary
   progress. Preserve the complete assignment, exact input/recipe, logs, sources
   and hashes; suspend the campaign immediately and independently validate CNF,
   both planar layers, disjoint union, alpha<=3, order28, degree/edge domain and
   a proper colouring. Report a potentially valid witness prominently. Difficulty
   alone implies neither SAT nor UNSAT. Do not promote before full domain review.

3. Use scripts/s035_pause_status.py. Twelve original processes were suspended,
   not killed; four native contexts retain RAM CDCL only while their PID/create
   identities survive. STOP remains latched. NEVER blindly remove STOP, resume
   the old guardian or call legacy recover: legacy STOP/recover uses taskkill /F.
   The native has no cooperative exit handler. Resolve this lifecycle blocker and
   validate a non-forcing pause/exit path on small controls before heavy work.
   A same-process RAM resume also requires explicit identity-aware handling of
   suspend counts, frozen wall deadlines and queued claims; no safe one-command
   RAM resume is currently supplied. Do not discard it to simplify recovery.

4. Durable semantic recovery: verify every runtime.tar.xz part and joined SHA,
   then python scripts/archive_s035_pause.py --verify. Use python scripts/restore_s035_pause.py --output C:\EM-S035-recovery
   to restore original objects and logical paths into a NEW directory. The
   script never launches a worker and verifies all restored hashes. Restore referenced
   S034 raw proof files with scripts/restore_s034.py --output <new-dir> --proofs
   from the committed, hash-verified validation/S034/campaign.tar.xz. Never
   overwrite live suspended work. Restore dependencies.tar.xz into a NEW root using DEPENDENCIES.json
   hashes for S032 base/seed, Windows checker and required runtime DLLs. Rebase only registered prefixes with hash checks.
   Restore gzip containers with pinned zlib1.3.1/level1; all original compressed
   and raw proof hashes were checked. The original pre-resident gzip container
   remains local; all its member bytes are independently stored in the pause
   archive. Operational live lock bytes are excluded and never copied to recovery.

5. Exact unresolved IDs: 0,1,3,7,15,31,63,127,255. All UNKNOWN; no pending UNSAT
   proofs or verification backlog at pause. RAM contexts: 0,7,127,255. Cold queue:
   1,3,15,31,63. Historical private_cdcl_retained flags on cold rows are stale;
   use the actual resident context map. Keep 247 independently proof-closed encoded
   regions. Standalone fresh DRAT plus independent checker gates every new closure.

6. Before any new heavy computation, commit/push diagnostic and SAT/lifecycle
   improvements and verify remote main. Run the SAT-first supervisor outside the
   guardian tree BEFORE future workers, preserving prominent SAT_ALERT.json even
   if validation fails. Test candidate interruption, validation failure and STOP
   races; do not rely solely on successful native return handling. Use targeted
   comparisons per region; avoid identical capped proof regeneration or blind
   restarts. Keep congruence disabled and random walk default unless a registered
   comparison justifies change. Four resident admissions including reservations,
   two executing slots, 600s fair turns; no repeated cache churn.

7. Retain 6GiB aggregate/2GiB per-worker private caps, 2GiB RAM floor,
   10GiB disk reserve, 2GiB raw-proof attempt cap and 40GiB campaign/64GiB S035
   budgets. Soft resident targets:5GiB/2.5GiB available RAM. Thermal unavailable.
   Respect fresh owner runtime instructions. Keep all checkpoints and evidence.
   S11 remains UNKNOWN;9<=chi2<=12. Encoded region closures are not graph or whole
   stratum exclusions. Preserve parked/publication/outreach/Lean gates.
