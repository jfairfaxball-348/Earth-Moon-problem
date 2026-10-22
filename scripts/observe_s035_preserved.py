"""Read-only S035 identity/CPU/telemetry observation; never control a process."""
import argparse
import json
from pathlib import Path
import re
import sys
import time
import psutil

ROOT = Path(__file__).resolve().parents[1]
LOGIC = re.compile(r'^c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)', re.M)


def snapshot(area):
    paused = json.loads((area/'OWNER_PAUSE.json').read_text())
    native = paused['contexts']['contexts']
    rows = []
    for key, context in sorted(native.items(), key=lambda pair: int(pair[0])):
        identity = context['worker']; process = psutil.Process(identity['pid'])
        same = str(process.create_time()) == identity['start_ticks']
        if not same:
            raise RuntimeError('Native identity changed: '+key)
        clock = process.cpu_times(); mem = process.memory_info()
        log = Path(context['directory'])/'native.log'
        with log.open('rb') as source:
            source.seek(max(0, log.stat().st_size-1024*1024))
            text = source.read().decode(errors='replace')
        counters = LOGIC.findall(text)
        rows.append(dict(cell=int(key), worker=identity, status=process.status(),
            cpu_seconds=clock.user+clock.system, private_bytes=mem.private,
            counters=dict(zip(('conflicts','decisions','propagations'), map(int,counters[-1]))) if counters else None,
            log_bytes=log.stat().st_size,
            geometric_journal_bytes=(Path(context['directory'])/'new-cuts.lem').stat().st_size))
    before = {row['cell']: row['cpu_seconds'] for row in rows}
    time.sleep(.25)
    for row in rows:
        process = psutil.Process(row['worker']['pid'])
        if str(process.create_time()) != row['worker']['start_ticks']:
            raise RuntimeError('Native identity changed during CPU sample')
        clock = process.cpu_times()
        row['sample_cpu_delta'] = clock.user+clock.system-before[row['cell']]
    other = []
    for identity in paused['processes']:
        if identity['pid'] in {r['worker']['pid'] for r in rows}:
            continue
        process = psutil.Process(identity['pid'])
        other.append(dict(pid=identity['pid'], same_identity=str(process.create_time())==identity['start_ticks'],
                          status=process.status()))
    return dict(epoch=time.time(), native=rows, legacy=other,
        all_legacy_preserved=all(r['same_identity'] and r['status']==psutil.STATUS_STOPPED for r in other),
        all_native_paused=all(r['status']==psutil.STATUS_STOPPED and r['sample_cpu_delta']==0 for r in rows),
        thermal='UNAVAILABLE', verdict='UNKNOWN', whole_stratum_certified=False)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=ROOT/'artifacts/tmp/S035/campaign')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); result=snapshot(args.directory)
    text=json.dumps(result,indent=1)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text)
    print(text)
