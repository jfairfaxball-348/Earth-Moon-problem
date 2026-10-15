# D051 — restore all 219 fixed χ=10 sources as priority of S015 (governance only)

**Date:** 2026-10-15. **Owner:** "yes, we should check those 219 just in case before we move on. Install that as the next session - why did they stop working? I know we have moved to cloud and container sessions but you can use github actions to run CL stuff? Is it explicitly only something that can be done locally?"

This owner message explicitly requests rewriting the **queued** S015 handover; it does **NOT** invoke S015 research now. D047 means their NEXT instruction to run S015 (or "Run next session") will authorise one complete S015. Historical S014 proof/readouts and previous S015 prompt remain in S014's merged commit Git history. The revised file authoritative/NEXT_SESSION_PROMPT.md and sessions/S014/S015_FUTURE_PROMPT.md are kept byte-identical.

## Verified why / remote execution

- The 271 graphs are already verified exact χ=10. 52 have certified NONBIPLANAR, 219 are **BIPLANARITY_UNKNOWN**; canonical 219 fixed row IDs are validation/S010/SUMMARY.json remaining_unknown_indices (not all graphs on some given order). Deciding biplanarity of ONE would meet D042 χ₂≥10, provided original no9 proofs cold replay and both layers certified.
- S011 GitHub Actions CAM0012 on 2026-10-14 run38623187997 job116055647178: all219 received two deterministic greedy split attempts (438 total) and 25 one-edge-repair cases; found zero full splits. Best row156 n24 m128 had 11 unplaced edges; this proves NO negative biplanarity. S011 then switched to edge-critical/del-and-repair constructions because the modest initial heuristic gave no positives, NOT because all 219 were ruled out. S012–S014 worked on other construction families (S012 194,896 swaps, S013 Sulanke ≤17, S014 retained-H 18v K7/K7-e analytic), leaving 219 unchanged.
- D043 local hook/cloud setup is a requirement for trust in numerical science **on that local runner**, NOT a requirement to run locally. D044 explicitly permits and ALREADY DEMONSTRATED GitHub Actions fallback. Successful previous jobs ran ubuntu-24.04 with `bash scripts/cloud_setup.sh`, same-job `.venv/bin/python scripts/cloud_smoke.py` (271 exact source DRAT/CNF and K9 control), then real bounded research, with results/hashes/logs. Sample GH workflows .github/workflows/s011-research.yml, s011-sparsify.yml, s011-edge-critical.yml and S013 workflow. S014 did no science solely because it did not stage this fallback, despite D044 allowing it. This was execution/prioritisation, not an unavoidable tool limitation.
- No S015 computational run or reclassification is performed by this D051 prompt amendment. ALL 219 remain UNKNOWN.

## Binding next-session priority

1. On invocation, use GitHub Actions proactively if hooked checkout absent (no second approval needed beyond owner invoking S015). Register and PUSH never-merged WIP code/workflow, obtain real hosted runs/artifacts, enforce full same-job cold smoke; do not pretend a previous job's smoke is current.
2. Progressively give ALL 219 new actual coverage (not another two-seed replay), then exact focused escalation of best candidates. Preserve per-row attempted/unknown/proved distinctions, reproducibility and bounded resources; no claim that running 219 heuristics exhausts the space.
3. A complete valid 2-planar split on ONE existing exact10 graph is a decisive positive lower-bound advance after cold certification. Negative requires exhaustive proof-checked sound necessary condition; timeout/solver UNKNOWN does not exclude.
4. Do not allow secondary new-construction agenda to displace these 219 until the owner explicitly pivots or an accepted lower-bound witness is found. If still unresolved after a resource-bounded campaign, carry the same unresolved roster and next concrete techniques into S016 rather than dropping them.

The environment remains 4-core/~15 GiB hosted with a 12 GiB single-worker maximum, registered timeout and artifact retention constraints per docs/CLOUD_ENVIRONMENT.md. Research and funding budgets are finite; no promise that each of 219 can be mathematically classified within one run.
