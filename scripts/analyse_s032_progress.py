"""Read-only diagnostics for the existing S032 worker; no ETA or coverage claim."""
import argparse
from collections import deque
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import time

ROOT = Path(__file__).resolve().parents[1]
NATIVE = re.compile(r'checks=(\d+) cuts=(\d+) model_checks=(\d+) check_seconds=([\d.]+)')


def stamp(value):
    return datetime.fromisoformat(value).timestamp()


def native(value):
    match = NATIVE.search(value or '')
    if not match:
        return None
    a, b, c, d = match.groups()
    return dict(checks=int(a), cuts=int(b), model_checks=int(c), check_seconds=float(d))


def history(path):
    """Bounded-memory stream of the immutable-at-entry journal prefix."""
    remaining = path.stat().st_size
    previous = None
    active = quiet = longest = 0.0
    gaps = []
    recent = deque()
    first = last = None
    with path.open('rb') as f:
        while remaining:
            line = f.readline(min(remaining, 1024 * 1024))
            remaining -= len(line)
            if not line or not line.endswith(b'\n'):
                break
            row = json.loads(line)
            counts = native(row.get('native_progress'))
            if row.get('kind') != 'heartbeat' or counts is None:
                continue
            point = dict(utc=row['utc'], **counts)
            if first is None:
                first = point
            if previous is not None:
                dt = stamp(point['utc']) - stamp(previous['utc'])
                if 0 <= dt <= 90:
                    active += dt
                    quiet = quiet + dt if point['cuts'] == previous['cuts'] else 0.0
                    longest = max(longest, quiet)
                elif dt > 90:
                    gaps.append(dict(start=previous['utc'], end=point['utc'], seconds=dt))
            point['observed_interval_seconds'] = active
            recent.append(point)
            while len(recent) > 1 and active - recent[1]['observed_interval_seconds'] > 7200:
                recent.popleft()
            previous = last = point
    windows = {}
    if last:
        for seconds in [3600, 7200]:
            baseline = next((p for p in recent if active-p['observed_interval_seconds'] <= seconds), last)
            elapsed = active - baseline['observed_interval_seconds']
            windows[str(seconds)] = dict(observed_seconds=elapsed,
                new_checks=last['checks']-baseline['checks'],
                new_rules=last['cuts']-baseline['cuts'],
                rules_per_observed_hour=((last['cuts']-baseline['cuts'])*3600/elapsed if elapsed else None))
    return dict(first=first, latest=last, observed_interval_seconds=active,
                unobserved_gaps=gaps, current_no_new_geometric_rule_observed_seconds=quiet,
                longest_no_new_geometric_rule_observed_seconds=longest, windows=windows)


def process(pid):
    """Query-only handle. Never request write, suspend or terminate access."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return dict(pid=pid, query_error=ctypes.get_last_error())
    try:
        values = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *[ctypes.byref(v) for v in values]):
            return dict(pid=pid, query_error=ctypes.get_last_error())
        numbers = [(v.dwHighDateTime << 32) | v.dwLowDateTime for v in values]
        return dict(pid=pid, creation_filetime=numbers[0], exit_filetime=numbers[1],
                    cpu_seconds=(numbers[2]+numbers[3])/10_000_000)
    finally:
        kernel.CloseHandle(handle)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sample-seconds', type=float, default=5)
    ap.add_argument('--out', type=Path, default=ROOT/'artifacts/tmp/S032/analysis')
    args = ap.parse_args()
    assert 0 <= args.sample_seconds <= 30
    area = ROOT/'artifacts/tmp/S032/campaign'
    controller = json.loads((area/'CONTROLLER.json').read_text())
    progress = json.loads((area/'PROGRESS.json').read_text())
    checkpoint = json.loads((area/'CHECKPOINT.json').read_text())
    pids = [controller['pid'], controller['worker_pid']]
    before = [process(pid) for pid in pids]
    start = time.monotonic()
    time.sleep(args.sample_seconds)
    after = [process(pid) for pid in pids]
    elapsed = time.monotonic()-start
    for a, b in zip(before, after):
        if 'cpu_seconds' in a and 'cpu_seconds' in b:
            b['same_process_across_sample'] = a['creation_filetime'] == b['creation_filetime']
            b['sample_cpu_seconds'] = b['cpu_seconds']-a['cpu_seconds']
            b['sample_one_core_utilisation'] = b['sample_cpu_seconds']/elapsed
    hashes = {p: sha(ROOT/p) == value for key in ['source_sha256', 'runtime_sha256']
              for p, value in controller[key].items()}
    now = datetime.now(timezone.utc)
    report = dict(observed_utc=now.isoformat(), verdict='UNKNOWN',
        controller_status=controller['status'], process_sample_seconds=elapsed,
        processes=after, source_runtime_hashes_match=all(hashes.values()), hash_checks=hashes,
        native_input_hashes_match=(sha(ROOT/'artifacts/tmp/S032/native/bipsat_s032.exe') == controller['native_sha256']
            and sha(ROOT/'artifacts/tmp/S032/S11.inst') == controller['input_sha256']),
        progress=progress, checkpoint=checkpoint,
        checkpoint_age_seconds=now.timestamp()-stamp(checkpoint['updated_utc']),
        result_exists=(area/'RESULT.json').exists(), free_disk_bytes=shutil.disk_usage(ROOT).free,
        history=history(area/'JOURNAL.jsonl'),
        limitations=['No total-work counter, coverage percentage, completion probability or ETA.',
            'Quiet geometric counters do not measure internal logical progress or prove a hang.',
            'Intervals over90s are unobserved gaps, not automatically sleep.',
            'Process CPU is cumulative; journal window rates exclude unobserved gaps.',
            'Live CDCL conflicts, decisions and internal learned clauses are not exposed.',
            'This analyser does not stop, suspend, modify or launch a solver.'])
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out/now.strftime('%Y%m%dT%H%M%S%fZ')
    target.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    h = report['history']
    latest = h['latest'] or {}
    recent = h['windows'].get('3600', {})
    text = (f"# S032 read-only progress report\n\nObserved: {now.isoformat()}\n\n"
            f"Controller: {controller['status']}; mathematical verdict: UNKNOWN.\n\n"
            f"Native CPU hours: {after[-1].get('cpu_seconds', 0)/3600:.2f}. "
            f"CPU seconds during {elapsed:.1f}s sample: {after[-1].get('sample_cpu_seconds', 'unavailable')}.\n\n"
            f"Partial checks: {latest.get('checks', 'unavailable'):,}; "
            f"new campaign geometric rules: {latest.get('cuts', 'unavailable'):,}; "
            f"complete model checks: {latest.get('model_checks', 'unavailable')}.\n\n"
            f"Recent observed window: {recent.get('observed_seconds', 0)/3600:.2f} hours, "
            f"{recent.get('new_checks', 0):,} new checks and "
            f"{recent.get('new_rules', 0):,} new geometric rules. "
            f"Unobserved gaps are excluded from this window.\n\n"
            f"Longest quiet geometric stretch: {h['longest_no_new_geometric_rule_observed_seconds']/3600:.2f} observed hours. "
            f"Current stretch: {h['current_no_new_geometric_rule_observed_seconds']/3600:.2f} observed hours.\n\n"
            + '\n'.join('- '+line for line in report['limitations'])+'\n')
    target.with_suffix('.md').write_text(text, encoding='utf-8')
    print(json.dumps(dict(report=str(target.with_suffix('.json')), processes=after,
                         history=h, source_runtime_hashes_match=report['source_runtime_hashes_match'])))


if __name__ == '__main__':
    main()
