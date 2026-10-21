# Debian/Termux ARM64 use

Work in the full existing clone on main. Keep Termux foreground, disable its
battery optimization if desired, and optionally run `termux-wake-lock` in
Termux before entering Debian. A wake lock does not prevent Android low-memory
kills or guarantee execution through Doze. Debian root in proot is not Android
root. No systemd, namespaces, cgroups or bubblewrap are needed by the solver.
Use `exit` from Debian to return to Termux, then `termux-wake-unlock`.

Install `git gcc g++ make python3 python3-venv` using Debian apt. Run:

```
bash scripts/cloud_setup.sh
git clone https://github.com/seanstock/bipsat2 artifacts/tmp/S033/bipsat2
git -C artifacts/tmp/S033/bipsat2 checkout --detach ab6e472b7ef4ab7dca1d12c8907b3c74399d3828
.venv/bin/python scripts/build_s033_native.py
.venv/bin/python scripts/cloud_smoke.py
mkdir -p artifacts/tmp/S033
cp artifacts/tmp/cloud_smoke/RESULT.json artifacts/tmp/S033/SMOKE.json
.venv/bin/python scripts/check_s033_phone.py
.venv/bin/python scripts/audit_s033_inputs.py
.venv/bin/python scripts/check_s033_lifecycle.py
.venv/bin/python scripts/check_s033_diagnostic.py
```

The clone command is for first setup only; never overwrite an existing checkout.
Builds default to one compiler process (`EMP_BUILD_JOBS` explicitly overrides).
Native outputs go to S033, leaving archived Windows binaries unchanged.

`python3 scripts/s033_phone.py status` is read-only and starts no solver.
`python3 scripts/s033_phone.py stop` requests STOP. The controller observes it
within its polling cycle, terminates the native process group and records UNKNOWN.
`python3 scripts/s033_phone.py recover` obtains the exclusive controller lock,
checks saved process identity and terminates an orphan before recording UNKNOWN.
An unexpected controller kill leaves RUNNING on disk until recovery; this is
not proof or success. Never infer UNSAT from a timeout, signal or log fragment.

Only short diagnostics are supported by this command, for example after controls:

```
.venv/bin/python scripts/s033_phone.py run --input artifacts/tmp/S033/controls-v2/K9.inst --seconds 5
```

One worker; native wall cap 1..30 seconds; external cap adds two seconds;
1 GiB observed tree RSS; 4 GiB disk reserve. Missing RSS stops execution.
RSS can double-count shared pages; it is not private memory. No thermal sensors
are exposed on this phone, so no thermal/throttling guarantee is made. Stop if
hot. Check `free -h`, `df -h .`, `/proc/meminfo`, `uname -m` before later work.
No unattended multi-hour campaign is authorized in S033.

All native outcomes remain candidates/UNKNOWN in the diagnostic supervisor.
Scientific readiness additionally requires full 271/271 CNF and DRAT smoke,
retained and fresh K9, native controls, independently validated archived rules
and exact input mapping, and STOP/signal/kill recovery tests. SAT needs independent
graph certification; exact-region UNSAT needs standalone checked DRAT and domain
audit. Retained geometric clauses do not preserve private CDCL state.

Rollback phone compatibility with ordinary `git revert` of the S033 commit(s),
reviewing conflicts with subsequent work. Do not reset or discard later changes.
