"""Start the S036 supervisor or controller as a detached process with its own log.

Only these two registered entry points can be launched; nothing here resumes,
suspends or terminates a solver. Detachment lets them outlive the invoking
shell; their live identities are read from WATCHER.json / CONTROLLER.json.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / 'artifacts/tmp/S036/control'
ENTRIES = dict(supervisor=['scripts/s036_sat_supervisor.py'],
               controller=['scripts/s036_resident_controller.py', 'run'],
               cold=['scripts/s036_cold_diagnostic.py'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=sorted(ENTRIES))
    parser.add_argument('--pilot-seconds', type=float)
    args, extra = parser.parse_known_args()
    assert not extra or args.role == 'cold', 'Extra arguments are only passed to the bounded cold slot'
    command = [str(ROOT / '.venv/Scripts/python.exe'), *[str(ROOT / ENTRIES[args.role][0]), *ENTRIES[args.role][1:]],
               *extra]
    if args.pilot_seconds:
        assert args.role == 'controller'
        command += ['--pilot-seconds', str(args.pilot_seconds)]
    CONTROL.mkdir(parents=True, exist_ok=True)
    log = CONTROL / f'{args.role}-{time.strftime("%Y%m%dT%H%M%S")}.log'
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
    with log.open('ab') as out:
        try:
            p = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 creationflags=flags | 0x01000000)  # CREATE_BREAKAWAY_FROM_JOB
        except OSError:
            p = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 creationflags=flags)
    print(dict(role=args.role, launcher_pid=p.pid, log=str(log), command=command[1:]))


if __name__ == '__main__':
    sys.exit(main())
