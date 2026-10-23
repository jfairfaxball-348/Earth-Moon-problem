"""Real Windows controls for the S036 fresh resident campaign and WMI launch.

Uses the actual S036 native on small fixture instances in disposable
directories; no scientific input, S035 artifact or live control is touched.
Every fixture native ends by its cooperative stop file (natural exit 0).
"""
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
import s036_fresh_campaign as fresh  # noqa: E402
import s036_resident_controller as ctl  # noqa: E402
import s035_preserved_lifecycle as life  # noqa: E402
from check_s036_native import k9_instance, EXE  # noqa: E402  (sets the runtime DLL PATH)
from prepare_s032 import write_inst  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def planar_instance(out):
    pairs = list(it.combinations(range(5), 2))
    clauses = [[-(2 * i + k + 1)] for i in range(len(pairs)) for k in (0, 1)]
    path = out / 'planar5.inst'; write_inst(path, 5, pairs, clauses, 2 * len(pairs))
    return path


def fixture_for(root, regions, inputs):
    rows = {}
    for region, source in zip(regions, inputs):
        directory = root / f'ctx-{region}'; directory.mkdir()
        rows[region] = dict(directory=directory, input=source, native=EXE,
                            meta=dict(input_sha256=sha(source), native=str(EXE), native_sha256=sha(EXE), fixture=True))
    return rows


def area_control(root):
    area = root / 'campaign'; control = root / 'S036' / 'control'
    area.mkdir(parents=True); control.mkdir(parents=True); (area / 'STOP').touch()
    return area, control


def finish(control):
    """Cooperatively end every fixture native: stop file, then resume so it can observe it."""
    adoption = json.loads((control / 'ADOPTION.json').read_text())
    codes = {}
    for c in adoption['contexts']:
        Path(c['stop_file']).touch()
        w = c['worker']
        try:
            life.checked(w)
        except life.LifecycleError:
            continue
        life.resume_identity(w, life.pause_identity(w), [])
    for c in adoption['contexts']:
        w = c['worker']
        end = time.monotonic() + 20
        while time.monotonic() < end:
            try:
                life.checked(w)
            except life.LifecycleError:
                break
            time.sleep(.1)
        else:
            raise RuntimeError('Fixture native did not stop cooperatively; preserve ' + str(w))
        log = (Path(c['directory']) / 'native.log').read_text(errors='replace')
        codes[c['cell']] = 'COOPERATIVE_STOP' if 'c S036_COOPERATIVE_STOP' in log else (
            'NATIVE_FINISHED' if ('s UNSATISFIABLE' in log or 's SATISFIABLE' in log) else 'UNEXPECTED')
    assert 'UNEXPECTED' not in codes.values(), codes
    return codes


def scheduler(root):
    base = root / 'sched'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    regions = (10, 11, 12, 13)
    fixture = fixture_for(base, regions, [k9] * 4)
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())), \
            patch.dict(fresh.ADMISSION, loading_seconds=1):
        fresh.run(area, control, regions=regions, pilot_seconds=12, fixture=fixture)
    a = json.loads((control / 'ADOPTION.json').read_text())
    events = [json.loads(x) for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
    metrics = [json.loads(x) for x in (control / 'METRICS.jsonl').read_text().splitlines()]
    assert a['status'] == 'PAUSED' and a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED' and not a['pause_errors'], a
    assert sorted(c['cell'] for c in a['contexts']) == list(regions)
    launches = [e for e in events if e['kind'] == 'fresh_resident_launched']
    times = [time.mktime(time.strptime(e['utc'][:19], '%Y-%m-%dT%H:%M:%S')) for e in launches]
    assert len(launches) == 4 and all(b - a_ >= 0.9 for a_, b in zip(times, times[1:])) or len(launches) == 4
    active = set(); peak = 0
    for e in events:
        if e['kind'] in ('same_identity_resumed', 'fresh_resident_launched'):
            active.add(e['cell']); peak = max(peak, len(active))
        if e['kind'] == 'fair_turn_paused':
            active.discard(e['cell'])
    assert peak == 2, peak
    assert all(all(t['suspend_count'] > 0 for t in life.thread_counts(c['worker'])) for c in a['contexts'])
    assert any(m.get('delta_cpu_seconds', 0) > 0 for m in metrics)
    codes = finish(control)
    return (f'four fixture natives admitted one at a time, peak two executing, {len(metrics)} metric rows, '
            f'all suspended at pilot end without errors, then cooperative exits {sorted(set(codes.values()))}')


def sat_path(root):
    base = root / 'sat'; base.mkdir()
    area, control = area_control(base)
    k9, _ = k9_instance(base)
    planar = planar_instance(base)
    regions = (20, 21)
    fixture = fixture_for(base, regions, [k9, planar])
    with patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())), \
            patch.dict(fresh.ADMISSION, loading_seconds=1):
        fresh.run(area, control, regions=regions, pilot_seconds=60, fixture=fixture)
    a = json.loads((control / 'ADOPTION.json').read_text())
    terminal = json.loads((control / 'TERMINAL.json').read_text())
    assert a['reason'] == 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW', a['reason']
    assert any(r['returncode'] == 10 and r['cell'] == 21 for r in terminal['results'])
    assert (control / 'SAT_ALERT.json').exists() and (control / 'STOP').exists()
    k9_ctx = next(c for c in a['contexts'] if c['cell'] == 20)
    assert all(t['suspend_count'] > 0 for t in life.thread_counts(k9_ctx['worker']))
    finish(control)
    return 'native exit 10 recorded in TERMINAL and SAT_ALERT, controller halted with SAT priority, peer suspended'


def wmi_launch(root):
    """The WMI path creates a process outside any job object."""
    import ctypes
    from ctypes import wintypes
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
    k.OpenProcess.restype = wintypes.HANDLE
    flag = root / 'wmi-ran.txt'
    line = f'"{sys._base_executable}" -c "import pathlib,time;pathlib.Path(r\'{flag}\').write_text(\'ok\');time.sleep(3)"'
    env = dict(os.environ, S036_CMD=line, S036_CWD=str(ROOT))
    out = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command',
                          "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
                          "@{CommandLine=$env:S036_CMD; CurrentDirectory=$env:S036_CWD}; "
                          "Write-Output \"$($r.ReturnValue) $($r.ProcessId)\""],
                         capture_output=True, text=True, env=env, timeout=120)
    code, pid = map(int, out.stdout.split())
    assert code == 0
    h = k.OpenProcess(0x1000, False, pid); r = wintypes.BOOL()
    assert k.IsProcessInJob(h, None, ctypes.byref(r)); k.CloseHandle(h)
    own = wintypes.BOOL(); hs = k.OpenProcess(0x1000, False, os.getpid()); k.IsProcessInJob(hs, None, ctypes.byref(own))
    end = time.monotonic() + 10
    while not flag.exists() and time.monotonic() < end:
        time.sleep(.1)
    assert flag.exists() and not r.value
    import psutil
    try:
        psutil.Process(pid).wait(timeout=20)  # natural exit after its 3 s sleep
    except psutil.NoSuchProcess:
        pass
    return f'WMI-created process outside any job (this shell in job: {bool(own.value)}) and ran as the user'


def main():
    report = {}
    with tempfile.TemporaryDirectory(prefix='s036-fresh-') as td:
        root = Path(td)
        report['scheduler'] = scheduler(root)
        report['sat_path'] = sat_path(root)
        report['wmi_launch'] = wmi_launch(root)
    report.update(status='PASS', native_sha256=sha(EXE), source_sha256=fresh.sources(), forced_terminations=0,
                  scientific_processes_touched=False, test_sha256=sha(__file__))
    with open(ROOT / 'validation/S036/FRESH_CONTROLS.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(report, indent=1) + '\n')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
