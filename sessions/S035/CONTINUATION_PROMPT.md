# S035 — inspect the live sustained continuation (S036 NOT AUTHORISED)

Owner already authorised S035 continuation. Read AGENTS.md, authoritative/STATE.json,
sessions/S035/RESUMED_RUNNING.md and THREAD_REPAIR.md before acting. Do not launch
a duplicate controller or solver. This is the same S035, not a completed session.

1. Read actual RESUME_CONTROL/ADOPTION.json, CONTROLLER.json and WATCHER.json under
   artifacts/tmp/S035/campaign. Verify PID/create times, heartbeat freshness, CPU,
   memory/disk safeguards, immutable input/native/source hashes and actual state.
   Healthy RUNNING uses two executing slots, four retained regions0,7,127,255 and
   fair600s turns without an overall time cutoff. Cold1,3,15,31,63 remain queued.

2. Exact original solver threads alone may resume. Classified Windows thread-pool
   helpers remain quarantined and all legacy processes stay frozen. Never blindly
   admit new threads, rearm a paused controller, remove original STOP, run legacy
   recover/STOP, kill/evict/replace RAM contexts, duplicate workers or start S036.
   A paused/failing live registry overrides this historical running snapshot;
   diagnose and preserve first. Use the published thread policy and acceptance.

3. SAT takes absolute priority. Preserve assignment, exact input/recipe, logs,
   sources and hashes; suspend surviving identities non-forcing; validate with
   tools/s035_sat_validation.py. Report a potentially valid witness prominently.
   Failed validation stays SAT review. Native UNSAT requires fresh standalone DRAT
   and independent checking; no fresh heavy proof generation is authorised here.

4. Keep6GiB aggregate/2GiB per worker,2GiB RAM floor,10GiB disk reserve,2GiB raw
   proof and40GiB campaign/64GiB total S035 budgets. Soft pressure preserves RAM;
   no thermal guarantee. Preserve new complete geometric prefixes for independent
   audit before sharing/promoting them. Keep all original archives/checkpoints.

5.247 encoded regions remain proof-closed; nine remain UNKNOWN. Encoded closures
   are not graph exclusions or whole-stratum proof. S11 UNKNOWN;9<=chi2<=12.
   Publication/outreach/Lean gates stay separate. Existing main, ordinary non-force
   commits/pushes; no new branch/project/PR. Preserve immutable pause and recovery
   manifests using their archived exact source bytes. Keep this prompt identical
   to sessions/S035/CONTINUATION_PROMPT.md. The scheduled check-ins completed and
   their heartbeat stays paused; do not add hourly notifications without request.
