"""Read-only S036 status: live identities, leases, turns, counters and resources.

Never resumes, suspends, launches or terminates anything. Optional --sample N
measures CPU and counter deltas over N seconds for the executing contexts.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
import psutil  # noqa: E402
from s036_resident_controller import counters, CONTROL, AREA  # noqa: E402
from s035_windows import live_identity, read_json  # noqa: E402


def snapshot():
    a = read_json(CONTROL / 'ADOPTION.json')
    rows = []
    for c in a['contexts']:
        w = c['worker']
        row = dict(cell=c['cell'], state=c['state'], turns=c['turns'], active_seconds=round(c['active_seconds'], 1),
                   alive=live_identity(w['pid'], w['start_ticks']))
        if row['alive']:
            p = psutil.Process(w['pid']); t = p.cpu_times()
            row.update(cpu=t.user + t.system, private_mib=p.memory_info().private // 2**20)
        row.update(counters(c['directory']))
        rows.append(row)
    return a, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', type=float, default=0)
    args = parser.parse_args()
    a, before = snapshot()
    controller = read_json(CONTROL / 'CONTROLLER.json'); watcher = read_json(CONTROL / 'WATCHER.json')
    out = dict(utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), adoption_status=a['status'],
               reason=a.get('reason'), executing=a.get('executing_cells'),
               controller=dict(status=controller.get('status'), pid=controller.get('pid'),
                               alive=live_identity(controller.get('pid', 0), controller.get('start_ticks', '')),
                               lease_age=round(time.time() - controller.get('updated_epoch', 0), 1)),
               watcher=dict(status=watcher.get('status'), pid=watcher.get('pid'),
                            alive=live_identity(watcher.get('pid', 0), watcher.get('start_ticks', '')),
                            heartbeat_age=round(time.time() - watcher.get('updated_epoch', 0), 1),
                            retried_reads=watcher.get('retried_reads'), pending=len(watcher.get('pending', []))),
               sat_alert=(CONTROL / 'SAT_ALERT.json').exists(), stop=(CONTROL / 'STOP').exists(),
               historical_stop=(AREA / 'STOP').exists(), throttle=a.get('throttle'),
               available_gib=round(psutil.virtual_memory().available / 2**30, 2),
               aggregate_private_gib=round(a.get('sample', {}).get('private', 0) / 2**30, 2),
               free_disk_gib=round(shutil.disk_usage(ROOT).free / 2**30, 2), contexts=before,
               cold_slot=read_json(CONTROL / 'COLD_SLOT.json') if (CONTROL / 'COLD_SLOT.json').exists() else None)
    if args.sample:
        time.sleep(args.sample)
        _, after = snapshot()
        out['sample_seconds'] = args.sample
        out['deltas'] = [dict(cell=b['cell'], cpu=round(x.get('cpu', 0) - b.get('cpu', 0), 2),
                              conflicts=x.get('conflicts', 0) - b.get('conflicts', 0),
                              decisions=x.get('decisions', 0) - b.get('decisions', 0),
                              cuts=x.get('cuts', 0) - b.get('cuts', 0)) for b, x in zip(before, after)]
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
