"""Start an S036 supervisor, controller or cold slot as an independent process with its own log.

Default launch uses WMI Win32_Process.Create, so the process (and every solver
it starts) is outside any application's job object: closing Claude Code,
ChatGPT/Codex or a terminal cannot end the search. (S035's retained processes
were lost exactly that way; a control showed CREATE_BREAKAWAY_FROM_JOB does not
leave the Claude Code job.) Only registered entry points can be launched;
nothing here resumes, suspends or terminates a solver. Live identities are read
from WATCHER.json / CONTROLLER.json / COLD_SLOT.json.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'artifacts/tmp/S036/control'
ENTRIES = dict(supervisor=['scripts/s036_sat_supervisor.py'],
               controller=['scripts/s036_resident_controller.py', 'run'],
               fresh=['scripts/s036_fresh_campaign.py', 'run'],
               cold=['scripts/s036_cold_diagnostic.py'],
               autopilot=['scripts/s036_autopilot.py'])


def quote(arg):
    return '"' + str(arg) + '"'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=sorted(ENTRIES))
    parser.add_argument('--pilot-seconds', type=float)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--no-wmi', action='store_true', help='child of this shell (inherits its job object)')
    args, extra = parser.parse_known_args()
    assert not extra or args.role == 'cold', 'Extra arguments are only passed to the bounded cold slot'
    command = [str(ROOT / '.venv/Scripts/python.exe'), str(ROOT / ENTRIES[args.role][0]), *ENTRIES[args.role][1:], *extra]
    if args.pilot_seconds:
        assert args.role in ('controller', 'fresh')
        command += ['--pilot-seconds', str(args.pilot_seconds)]
    if args.resume:
        assert args.role == 'fresh', '--resume re-adopts a prepared fresh campaign only'
        command += ['--resume']
    CONTROL.mkdir(parents=True, exist_ok=True)
    # Long-lived helpers that outlive a pause (cold runner, autopilot) log outside the
    # control directory, which prepare-resume archives while their logs are still open.
    logs = CONTROL if args.role in ('supervisor', 'controller', 'fresh') else CONTROL.parent / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    log = logs / f'{args.role}-{time.strftime("%Y%m%dT%H%M%S")}.log'
    if args.no_wmi:
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        with log.open('ab') as out:
            p = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 creationflags=flags)
        print(dict(role=args.role, launcher_pid=p.pid, log=str(log), wmi=False)); return
    line = 'cmd.exe /d /s /c "' + ' '.join(quote(a) for a in command) + ' >> ' + quote(log) + ' 2>&1"'
    env = dict(os.environ, S036_CMD=line, S036_CWD=str(ROOT))
    script = ("$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
              "-Arguments @{CommandLine=$env:S036_CMD; CurrentDirectory=$env:S036_CWD}; "
              "Write-Output \"$($r.ReturnValue) $($r.ProcessId)\"")
    out = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True,
                         text=True, env=env, timeout=120)
    fields = out.stdout.strip().split()
    if out.returncode or len(fields) != 2 or fields[0] != '0':
        raise SystemExit('WMI launch failed: ' + out.stdout + out.stderr)
    print(dict(role=args.role, wmi_cmd_pid=int(fields[1]), log=str(log), wmi=True, command=command[1:]))


if __name__ == '__main__':
    sys.exit(main())
