"""Run every 'run:' command of the hosted scaffold workflow locally; record outcomes."""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def commands():
    lines = (ROOT / '.github/workflows/scaffold.yml').read_text(encoding='utf-8').splitlines()
    out, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith('run: |'):
            i += 1
            while i < len(lines) and lines[i].startswith(' ' * 10):
                out.append(lines[i].strip())
                i += 1
            continue
        if s.startswith('run: '):
            out.append(s[5:])
        i += 1
    return out


def main():
    rows = []
    for cmd in commands():
        t = time.monotonic()
        run = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
        rows.append(dict(command=cmd, returncode=run.returncode, seconds=round(time.monotonic() - t, 1),
                         tail=(run.stdout + run.stderr)[-400:]))
        print(run.returncode, rows[-1]['seconds'], cmd, flush=True)
    ok = all(r['returncode'] == 0 for r in rows)
    (ROOT / 'artifacts/tmp/S046/LOCAL_CI.json').write_text(json.dumps(dict(status='PASS' if ok else 'FAIL', python=sys.version,
                                                                          steps=rows), indent=1) + '\n')
    print('LOCAL CI', 'PASS' if ok else 'FAIL')


if __name__ == '__main__':
    main()
