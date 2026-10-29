# S047 owner invocation and entry state

29 October 2026, about 23:20 UTC. In a cloud Claude Code conversation the
owner asked whether the lower bound could be reached "from working rather than
just looking for a counterexample", chose to explore "specifically the
contradiction one", and then instructed: "Yes, replace with new target, and do
run the session now here". Under D079 (docs/D079_S047_CONTRADICTION_ROUTE.md)
this supersedes the queued S047 calibration-gated mechanism trial (never
executed; text preserved in sessions/S046/S047_FUTURE_PROMPT.md) and, under
D047, invokes exactly the new S047 now. It does not invoke S048 or wake any
S035/S036/S045 control.

Executor: Claude Code on the web (cloud container), Linux 6.18 x86_64,
4 logical CPUs, 15 GiB RAM, Python 3.12.3 (PySAT 1.9.dev15, NetworkX 3.5,
NumPy 2.5.4; SciPy absent and not installed). Native CaDiCaL and drat-trim
built by scripts/cloud_setup.sh at artifacts/tmp/native/bin.

Entry reconciliation:

- local HEAD = fetched origin/main = 7fb60e1119fed86d61f44b95390ae5311b5a5344
  ("Reclaim redundant research scratch and record lossless recovery", the
  commit after S046 fe03d00); clean worktree on harness branch
  ccr-af80f6d5-2qearo, which equals main at entry.
- No python, cadical or drat-trim process running at entry. No automation
  exists or is created. Hosted CI status of 7fb60e1 was not queried in this
  container (no gh CLI): UNKNOWN, not PASS.
- Integration: AGENTS rule 12 makes the harness-assigned branch the cloud
  session branch; the harness forbids pushing elsewhere without permission.
  Ordinary non-force commits to ccr-af80f6d5-2qearo; merging to main is the
  owner's decision. This deviates from the recent "existing main" convention
  for environment reasons only.

Fresh full 271+K9 smoke on the D043 pinned cloud build: PASS, 271/271
chromatic rows verified with byte-matching CNFs, K9 CNF match and retained
proof verified, fresh CaDiCaL K9 proof verified; 70 s wall (verification cost,
not experimental budget). drat-trim sha256 bd6221fa...3e25 equals the D043
record; this CaDiCaL build hashes 905e60eb...954a (D043 recorded afa8b5b3...,
an unpinned compiler-output difference; the smoke reproduces all byte-level
inputs and proof checks). Receipt: validation/S047/SMOKE.json.

Status at entry: no certified chi>=10 biplanar witness; 9 <= chi_2 <= 12.
