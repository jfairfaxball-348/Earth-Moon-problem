# S033 — Samsung Galaxy S24 ARM64/Debian environment port and verification (FUTURE / UNEXECUTED)

Repository: https://github.com/jfairfaxball-348/Earth-Moon-problem
Owner override: D072 (2026-10-21). S033 is now the **PHONE ENVIRONMENT CONFIGURATION AND VALIDATION SESSION**. D071's planned parallel region-worker engineering and genuine solver campaign are postponed to S034. This amendment does not execute S033.

## Owner intent and invocation

The owner has successfully run Git, Claude Code and Codex CLI on a Samsung Galaxy S24 under Android -> Termux -> Debian Linux (proot-distro), including pushing commits to GitHub. The owner will do a **full clone of this repository** on the phone. The approximately 1.5 GB of tracked files is acceptable: do not insist on a sparse clone. Do not create a separate experiment repository, project or worktree.

Once the owner enters this cloned repo and says **"run next session"**, execute S033 directly under D047; no further permission phrase or confirmation is needed. The session focuses FIRST on adapting the *existing* solver to this environment, and ONLY AFTER successful setup/verification queues S034, which may begin the actual Earth–Moon solver work. Do not run S034 automatically. Keep the mathematics and all prior proof/certificate standards unchanged.

**Same repository and branch**: for this phone experiment the owner expressly requests no new session/development branch or PR. Do work locally on the checked-out 'main' branch; if clean, up to date and permitted by repository protection, commit and push normally to 'main' without force. This narrowly overrides older branch/PR-only workflow directions for mobile S033 and subsequent S034 mobile work; it does NOT override mathematical evidence checks. If main is protected or another writer changes it, stop and report rather than force, reset, or invent a branch. Do not discard local changes. All phone-specific changes must be reversible with normal Git history / 'git revert', with Windows laptop support preserved.

## Mandatory checks before touching solver code

1. Inspect actual local directory, git status/branch/remotes, current HEAD, live 'origin/main' and any uncommitted files; fetch carefully, never reset or overwrite. If not on main, describe the mismatch; do not silently switch while work is dirty.
2. Inspect actual 'uname -m' (expect aarch64), Debian/Termux/proot version, Python, GCC/G++, make, git, venv/pip, free RAM, CPU count and disk using commands such as 'nproc', 'free -h', 'df -h .', '/proc/meminfo'. Determine which system calls/process operations work inside unprivileged proot. Debian's 'root@localhost' is not privileged Android root.
3. Inspect existing repository materials: AGENTS.md, authoritative/STATE.json, START_HERE.md, NEXT_SESSION_PROMPT.md; D070 owner stop, D071 parallel directive, D072 phone directive, S032 closeout/progress and validation/S032/SUMMARY.json. Check actual source/build scripts before porting. Respect stopped S032 and all immutable archives.
4. Establish *phone-specific* conservative wall, memory, disk and thermal caps based on observed free resources. Historic S032 peak private memory was 2,774,176 KiB (about 2.65 GiB) on desktop; the old 11 GiB cap and 10 GiB disk reserve do not automatically fit a phone. Start with exactly ONE solver worker maximum. Avoid multi-hour background computations, battery drain and overheating in S033.
5. Explain Android screen locking/Doze/background termination and Termux wake-lock limitations. Do not depend on systemd, kernel namespaces, cgroups or unprivileged bubblewrap for solver correctness. Use the phone's actual permissions.

## Port the existing mathematical engine, not a substitute

Preserve S032's exact scientific formulation and proof discipline: 336,030 baseline clauses, 17,976 variables, the graph-prefix regions, original S11 alpha<=3 order-28/degree-11 search, and ALL 2,579,937 independently checked retained geometric clauses (189,309,949 uncompressed bytes, SHA256 6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177) from validation/S032/stopped/learned.lem.gz. Verify uncompressed hashes and source/input mapping before use. The original CaDiCaL private CDCL state was *not saved*; the learned geometric clauses are reusable evidence, not a continuation of private solver state. Keep OWNER_STOP, PAUSED and every unfinished region UNKNOWN.

- Reuse the pinned Linux CaDiCaL, drat-trim and Python setup in scripts/cloud_setup.sh and the native evidence harness in scripts/cloud_smoke.py. Install required Debian aarch64 compiler, Python and build dependencies. Adapt optional package issues, compiling from source where necessary, without weakening pinned source correctness.
- Port scripts/build_s032_native.py and build_s032_progress_native.py (or introduce narrowly scoped portable equivalents in THIS repository) from x86_64 LLVM-MinGW, Windows .exe, '<io.h>', '_commit', '-lpsapi' to true Linux/aarch64 native build. Preserve pinned upstream bipsat2 source, CaDiCaL and the planar graph library, independent subdivision guard, exact input/output semantics and telemetry. Never replace the real solver with an unrelated general SAT script or a dummy benchmark. Keep Windows desktop builds working and archived binaries untouched.
- Port the Windows-only supervision elements in scripts/run_s032_native.py and scripts/s032_coverage.py, including 'ctypes.windll', CREATE_NEW_PROCESS_GROUP, CREATE_NO_WINDOW and 'windows_tree_bytes', to safe POSIX/proot process-group stop/cleanup, RSS monitoring, time/disk caps and atomic progress files. Reuse tools/s026_supervision.py where feasible. Detect insufficient /proc visibility rather than inventing trustworthy memory readings. Do not allow interruptions/crashes to mark a region UNSAT.
- Keep layer and auxiliary variables existential, exact disjoint regions/assumptions, correct input hashes and independent DRAT verification. SAT is at most a candidate requiring independent graph/planarity/chromatic witness certification. Solver UNSAT only closes an exact encoded region after standalone CaDiCaL DRAT production and independent drat-trim verification plus domain audit. A cap, relaxation SAT or crash stays UNKNOWN. All original S032 documents, binary hashes and certificates remain frozen.

## S033 acceptance, controls and deliverables

A. Add a concise in-repository phone setup/usage guide, repeatable ARM64 build commands, environment diagnostics, read-only progress/status command and safe explicit STOP. Ensure owner can use these from Debian/Termux and knows how to get back to Termux.

B. Actually compile the native bipsat2 solver on aarch64 and test small fixed planar/nonplanar inputs, K33, the existing positive24 test, and appropriate n=5 exhaustive/backtracking/independent subdivision controls (all 1,024 n=5 instances where feasible). Native free K9 if time-capped remains UNKNOWN; never call it PASS.

C. Before declaring **scientific readiness**, run the COMPLETE original '271/271' CNF byte-identity + independent DRAT acceptance, retained and fresh K9 via '.venv/bin/python scripts/cloud_smoke.py' on this phone. Its full PASS is required. Partial smoke is diagnostic only; a failure blocks scientific computation. Record realized architecture, package versions, source SHA256 and new platform-dependent executable hashes.

D. Execute a deliberately short, registered, bounded native diagnostic on a proof-backed test input using the REAL ported bipsat2 binary. Report wall/CPU time, measured RSS, disk and any obtainable thermal/throttle readings. Exercise graceful STOP, signals, and unexpected kill/restart recovery. Do not run a long search or claim mathematical progress in S033.

E. Record an explicit mobile verdict: 'PHONE_READY_VALIDATED' only when pinned native build, full smoke, controls and stop/recovery pass; otherwise 'PHONE_PARTIAL' or 'PHONE_NOT_READY' with precise blockers. No new mathematical witness, bound or stratum closure is implied. Maintain classical 9 <= chi_2 <= 12, S11 m155/156 UNKNOWN and S10/S9/S8 NOT_RUN. Include safe resource caps and rollback instructions ('git revert' the S033 compatibility commit(s) without discarding later work). Keep full desktop support.

F. Finish S033 with working tested code when possible, logs/manifests, concise state update and a COMPLETE S034 queued prompt both in authoritative/NEXT_SESSION_PROMPT.md and a session-local S034 future prompt. Print the full S034 prompt at closeout. Do not start S034 without a new owner invocation. Use direct non-force main commits only if permitted and safe; otherwise retain local work and explain the push block.

## S034 (FUTURE / UNEXECUTED) — requirements for complete handover

S034 must be a REAL SOLVER session using the validated phone environment, not another environmental design session. If S033's acceptance failed, S034 must first fix those exact blockers; never start uncertified science.

Carry forward all *unexecuted* D071 parallel-region engineering: exact partition of the authorised 256 graph-presence regions; correct region assumptions and hashes; unique per-cell claim and proof status; atomic and collision-free controller/worker manifests; robust stop/recovery; read-only observable progress; dynamic independent worker scheduling and separately checked DRAT closures; full small controls, same-environment 271+K9 acceptance, and honest UNKNOWN handling.

On the phone **initially run ONE worker**, with a practical owner-approved finite wall/memory/disk/thermal budget and an actual chosen unresolved S11 region/input. Only attempt a second worker after measured sufficient thermal, disk and RAM headroom and concurrency tests. For desktop runs retain the D071 plan to benchmark 1/2/3 workers (four only if safely justified); do not apply its 11 GiB allowance to the phone. No automatic unattended hours-long run. Keep original mathematics, all certificates and Windows/laptop paths, and allow ordinary Git-history rollback of phone-specific changes. Continue toward the D042 target: one independently certified biplanar graph with chromatic number >=10, without any premature claim.

This prompt is **the queue for S033**. It is not an execution record. S034 remains unexecuted until owner invocation after S033.
