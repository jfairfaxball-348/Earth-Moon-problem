# Cloud execution environment (decision D043)

From S011 onward, sessions run in Claude Code cloud sessions (ephemeral Linux containers), not on the Windows machine used for S001–S010. This file is the binding environment reference. It changes infrastructure only; no mathematical status changes.

## Automatic setup

`.claude/settings.json` registers `.claude/hooks/session-start.sh`, which runs `scripts/cloud_setup.sh` synchronously at session start in cloud sessions (`CLAUDE_CODE_REMOTE=true`). The script is idempotent and can be run by hand on any Linux machine:

```
bash scripts/cloud_setup.sh
```

It:

1. creates `.venv` with Python 3.12 (falling back to `python3`), and installs the pinned packages `python-sat==1.9.dev15` and `networkx==3.5`, plus `numpy==2.5.4` and `pymupdf==1.26.6` when available (census/figure tools only);
2. builds the S004-pinned native tools from source with the Linux `configure/make` route that validation/S004/README.md names:
   CaDiCaL `c60730422e758ef1cebe7aeddf2dda31c996bf04` (3.0.1) and drat-trim `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (`gcc -O2`), into `artifacts/tmp/native/bin/`;
3. links the legacy Windows paths that S004–S010 scripts hard-code, `artifacts/tmp/S004/cadical.exe` and `artifacts/tmp/S004/drat-trim-mingw.exe`, to the Linux builds, so preserved scientific scripts are NOT edited;
4. writes `artifacts/tmp/native/ENVIRONMENT.json` (platform, Python, package versions, compiler, source pins, binary SHA-256, CPUs, memory) and `artifacts/tmp/native/setup.log`.

The hook also exports `PATH` (venv and native bin first), `EMP_CADICAL` and `EMP_DRAT_TRIM` for the session. Use `.venv/bin/python` where historical READMEs say `.venv/Scripts/python.exe`. `artifacts/tmp/` and `.venv/` are gitignored and never committed.

## Mandatory entry acceptance check

Before any scientific computation, every cloud session runs:

```
.venv/bin/python scripts/cloud_smoke.py
```

It regenerates all 271 S004 non-9-colourability CNFs and requires each to match its recorded SHA-256, checks each retained DRAT proof with the Linux drat-trim, regenerates and checks the K9 non-biplanarity control in a fresh process, and checks a fresh CaDiCaL K9 proof. It writes `artifacts/tmp/cloud_smoke/RESULT.json`. A FAIL blocks scientific computation until explained. A PASS is an environment check, not new mathematics. Record its verdict, counts and the ENVIRONMENT.json binary hashes in the session manifest.

D043 validation (2026-10-14, Linux 6.18 x86_64, glibc 2.39, Python 3.12.3, gcc 13.3.0): PASS. 271/271 chromatic proofs verified with 271/271 CNF byte matches against the Windows records; K9 CNF byte match and retained DRAT verified; fresh CaDiCaL K9 solve (exit 20, ~25 s) with proof verified. Observed binary SHA-256: cadical `afa8b5b3777b45c6723634ad8b30cb0a65246f9621a28269389cb99296dfc7c1`, drat-trim `bd6221fa417e0fdf8881ffc93782954f18cc2a3bdea26c4dd8a07beec7923e25`. Binary hashes depend on the container compiler; a later container may differ and must record its own.

## Differences from the S001–S010 Windows environment

- **New environment, not byte reproduction.** Linux binaries differ from the pinned Windows `cadical.exe`/`drat-trim-mingw.exe` hashes. Acceptance rests on independently checked DRAT/LRAT proofs and regenerated input hashes, never on binary identity. Historical Windows records stay as they are.
- **CaDiCaL `-t` works on Linux.** The Windows "no `-t`" limitation (F025) does not apply; still enforce registered wall caps externally.
- `tools/export_pysat_drat.py` has a Windows-only `fflush` branch; on Linux it is skipped by design.
- **Process isolation still applies.** Importing `s008_tree` patches `CardEnc` globally (F045); sequential Cover and totalizer/tree generators must run in separate fresh processes.

## Resource limits

The observed container has 4 CPUs, about 15.7 GiB RAM and a fixed writable disk allowance (about 29 GB free at D043; `df` "Avail" is the allowance). Preregister workers to fit: at most one heavy solver/checker worker with a 12 GiB memory cap, or two workers with a 6 GiB cap each. Delete large scratch files (CNFs, uncompressed proofs) once their hashes and compressed archives are recorded. Never store uncompressed proofs in `validation/`.

## Persistence and long runs

Containers are ephemeral and are reclaimed after inactivity; anything not pushed is lost. Therefore:

- run long searches in the background with registered caps, checkpoint result JSON under `artifacts/tmp/`, and keep campaigns sized to finish within an active session;
- if a session must pause mid-campaign, push a backup snapshot to a separate `wip/S###-…` branch. Backup branches are never merged and never count as the session commit; the session's single authored commit is still made on the session branch;
- a lost container leaves its unfinished targets UNKNOWN/NOT_RUN, never negative.

## Git and GitHub in the cloud

- The cloud harness assigns the session branch (for example `ccr-…`). It is the session's isolated branch. At the start of each numbered session, reset it to live main (`git fetch origin main && git checkout -B <branch> origin/main`) so the PR carries exactly one authored session commit, and record the actual branch name in STATE.
- Create the PR, read checks and merge through the GitHub tools available in the session (non-force, merge-commit method only, never squash or rebase). Then verify the merge commit's two parents, tree identity with the branch head, and the actual post-merge workflow run.
- Hosted "Research scaffold checks" are governance checks only.

## Verified alternative when Claude cloud checkout/hook is absent (decision D044, S011)

An assistant/runtime without access to a checked-out clone or hooked Linux .venv **must not execute scientific searches there**. In S011 we created preregistered, never-merged GitHub Actions WIP branches which checkout the actual repository on `ubuntu-24.04`, run `bash scripts/cloud_setup.sh` and the full `.venv/bin/python scripts/cloud_smoke.py` **within each job before research**, run one bounded research process, and upload logs, exact sources/input/native SHA256 and results as Actions artifacts. This avoids claiming nonexistent local hooks. GitHub-hosted four-core Linux runner had about15GiB RAM. D043 acceptance was PASS across 271/271 archived chromatic native proofs and CNF byte matches, K9 and fresh K9 native proof in each S011 research job; run-specific binary SHA256 differed even between runners, which is expected and must be recorded, not equated.

Concrete workflows: `.github/workflows/s011-research.yml` (CAM0012 run38623187997); `s011-sparsify.yml` (CAM0013 run38623722547); `s011-edge-critical.yml` (CAM0014 run38624616691); `s011-preserve-certificates.yml` (permanent certificate packaging run38625149681). Full indices/artifact digests and native SHA256 in `validation/S011/SUMMARY.json`. The complete 863 proven colour-deletion witnesses are permanently saved as `validation/S011/edge_critical_witnesses.json.gz`; Actions ZIP artifacts are temporary and are NOT the only accepted preservation medium. WIP branches are backup/execution only and NEVER merged. For future sessions, preregister a **new** job and repeat full same-job smoke; don't reuse an old PASS as a new runner's environment acceptance. Maintain no more than one heavy worker at12GiB or two6GiB, registered time/memory caps and branch hygiene. Continue to prefer cloud hook when actually present.
