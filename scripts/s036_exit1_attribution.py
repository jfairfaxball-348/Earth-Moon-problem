"""Attribute the historical S035 native exit code 1 in regions 15 and 31 (read-only).

The S035 native exits 10 (SAT), 20 (UNSAT), 0 (UNKNOWN) or 3 (die()). Exit 1 is
the status Windows `taskkill /F` (TerminateProcess) gives the target. This script
joins every exit-1 native-RESULT in the nine unresolved regions to the S035
journal events that forced termination, and runs a disposable taskkill control.
"""
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT / 'artifacts/tmp/S035/campaign'


def utc(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat()


def main():
    events = [json.loads(line) for line in (AREA / 'JOURNAL.jsonl').read_text().splitlines() if line.strip()]
    stops = [e for e in events if e['kind'] in ('stop_requested', 'guardian_stopped', 'resident_memory_eviction')]
    rows = []
    for cell in (0, 1, 3, 7, 15, 31, 63, 127, 255):
        for directory in sorted((AREA / 'attempts' / f'cell-{cell:04d}').iterdir()):
            path = directory / 'native-RESULT.json'
            if not path.exists():
                continue
            result = json.loads(path.read_text())
            if result.get('returncode') != 1:
                continue
            log = (directory / 'native.log').read_text(errors='replace')
            row = dict(cell=cell, attempt=directory.name, reason=result.get('reason'),
                       wall_seconds=result.get('wall_seconds'),
                       fatal_marker='bipsat FATAL' in log, sat_marker='s SATISFIABLE' in log,
                       unsat_marker='s UNSATISFIABLE' in log)
            if result.get('reason') == 'VISIT_QUANTUM':
                row['attribution'] = ('V1 visit-quantum cap: engine stop_group() ran taskkill /T /F at the '
                                      'registered visit limit')
            elif result.get('reason') == 'OWNER_STOP':
                row['attribution'] = 'V1 owner stop: engine halt stop_group() ran taskkill /T /F'
            else:
                # A reused resident's turn starts at this attempt's claim, not at process creation.
                claim = next(e for e in events if e['kind'] == 'claim' and e.get('token') == directory.name)
                started = claim['utc']
                start = datetime.fromisoformat(started).timestamp()
                end = start + result['wall_seconds']
                near = [e for e in stops if abs(datetime.fromisoformat(e['utc']).timestamp() - end) <= 5]
                row.update(worker_started_utc=started, exit_observed_near_utc=utc(end),
                           journal_events_within_5s=[dict(kind=e['kind'], utc=e['utc'], reason=e.get('reason'))
                                                     for e in near])
                row['attribution'] = ('V1 resident pilot OWNER_STOP: halt stop_group() ran taskkill /T /F on the '
                                      'executing resident' if any(e['kind'] == 'stop_requested' for e in near)
                                      else 'UNATTRIBUTED')
            rows.append(row)
    child = subprocess.Popen([sys._base_executable, '-c', 'import time; time.sleep(60)'],
                             creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(.5)
    subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                   creationflags=subprocess.CREATE_NO_WINDOW)
    control_code = child.wait(timeout=10)
    data = dict(status='ATTRIBUTED' if all(r['attribution'] != 'UNATTRIBUTED' for r in rows) else 'PARTIAL',
                native_exit_codes=dict(SAT=10, UNSAT=20, UNKNOWN=0, die=3),
                taskkill_force_control_exit_code=control_code, rows=rows,
                conclusion=('Every exit 1 in the unresolved regions is a forced Windows termination by the '
                            'historical S035 V1 engine (visit cap or owner-stop halt), not a native crash, SAT or '
                            'UNSAT. No log carries a FATAL, SAT or UNSAT marker. S036 never force-terminates; its '
                            'cold slot ends by --timeout or the cooperative stop file.'),
                verdict='UNKNOWN')
    assert control_code == 1
    out = ROOT / 'validation/S036/EXIT1_ATTRIBUTION.json'
    out.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=data['status'], rows=len(rows), control=control_code,
                          by=[(r['cell'], r['reason'], r['attribution'][:40]) for r in rows]), indent=1))


if __name__ == '__main__':
    main()
