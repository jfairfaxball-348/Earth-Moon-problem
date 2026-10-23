# S036 registered plan

1. Entry and SAT first (done before any process action): scripts/s036_entry_audit.py
   -> validation/S036/ENTRY.json, SAT_FIRST_AUDIT.json.
2. Repair the S035 WATCHER_FAILURE: tools/s036_sat_scan.py (bounded Windows
   sharing retries for stat/open/hash, cache commit only after a complete read,
   PENDING carry-over with fail-closed ScanUnavailable, SAT outranks
   unavailability), scripts/s036_sat_supervisor.py (preserve first, explicit
   reason + traceback, fresh complete rescan), scripts/s036_resident_controller.py
   (separate S036 control directory, explicit supervisor cause in stop reasons,
   soft-RAM throttle instead of exit, per-turn metrics, S035+S036 storage budget).
   Original S035 source bytes are unchanged; new files carry the repair.
3. Fresh Windows acceptance: full 271 + retained/fresh K9 smoke, real controls
   (validation/S036/SUPERVISOR_CONTROLS.json), S036 native controls, then
   publication to main and S036-pinned ACCEPTANCE before any resume.
4. Retained search: adopt contexts 0,7,127,255 by exact identity, 40 s same-process
   validation, rearm, unbounded 600 s fair turns in two slots, independent
   supervisor. Verify advancing counters and one full four-context rotation.
5. Per-region diagnostics: exit-1 attribution (validation/S036/EXIT1_ATTRIBUTION.json);
   registered cold option comparison on regions 1,3,15,31,63
   (validation/S036/DIAGNOSTIC_ARMS.json) through the bounded cold slot
   (validation/S036/COLD_CAPACITY_PLAN.json); adoption only by the registered rule;
   then fair cold rotation in bounded spans.
6. Two-hour check-ins after verified launch; independent supervision between them;
   never auto-restart paused work. Closeout installs identical S037 FUTURE prompts.

Hard limits: 6 GiB aggregate private, 2 GiB per worker, 2 GiB available floor,
10 GiB free disk, 2 GiB raw proof per attempt, 40 GiB campaign, 64 GiB S035+S036.
Native UNSAT needs fresh standalone DRAT plus independent checking; SAT outranks
everything. Baseline: 247/256 encoded regions proof-closed, nine UNKNOWN; S11
UNKNOWN; 9<=chi2<=12.
