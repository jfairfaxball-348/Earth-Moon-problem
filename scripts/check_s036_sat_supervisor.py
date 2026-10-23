"""Real Windows controls for the S036 SAT scanner, supervisor and controller.

Disposable fixtures only: no scientific process, S035 artifact or retained
context is touched. Covers the S035 WATCHER_FAILURE repair (concurrent
replacement, exclusive locks, SAT during retry, permanent unreadability that
fails closed, cache commit only after reads, cross-block markers), supervisor
STOP/lease/loss paths, explicit underlying stop reasons, the two-slot
four-resident scheduler with per-turn metrics, soft throttling and pilot rearm.
"""
import copy
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
import s036_sat_scan as scan  # noqa: E402
import s036_sat_supervisor as sup  # noqa: E402
import s036_resident_controller as ctl  # noqa: E402
import s035_preserved_lifecycle as life  # noqa: E402
from check_s035_thread_repair import start as start_fixture, finish as finish_fixture  # noqa: E402

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
k32.CreateFileW.restype = wintypes.HANDLE
k32.WriteFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
k32.SetFilePointer.argtypes = [wintypes.HANDLE, wintypes.LONG, ctypes.c_void_p, wintypes.DWORD]
k32.CloseHandle.argtypes = [wintypes.HANDLE]
INVALID = wintypes.HANDLE(-1).value
SAT_LINE = b's SATISFIABLE\nv 1 -2 0\n'


class Exclusive:
    """Open a file with share mode 0 so every other open fails with a sharing violation."""
    def __init__(self, path, write=False):
        access = 0x80000000 | (0x40000000 if write else 0)
        self.handle = k32.CreateFileW(str(path), access, 0, None, 3, 0x80, None)
        if self.handle in (None, INVALID):
            raise ctypes.WinError(ctypes.get_last_error())

    def append(self, data):
        k32.SetFilePointer(self.handle, 0, None, 2)
        written = wintypes.DWORD()
        assert k32.WriteFile(self.handle, data, len(data), ctypes.byref(written), None) and written.value == len(data)

    def close(self):
        if self.handle:
            k32.CloseHandle(self.handle); self.handle = None


def replace_json(path, value):
    temp = Path(path).with_name(Path(path).name + f'.{threading.get_ident()}.{time.time_ns()}.tmp')
    temp.write_text(json.dumps(value))
    scan.retry(lambda: os.replace(temp, path), budget=5.0)


def scanner_controls(root):
    results = []
    # Concurrent replacement: the exact S035 failure class, at high rate.
    target = root / 'replaced.json'; replace_json(target, dict(n=0))
    stop = threading.Event(); errors = []

    def writer():
        n = 0
        while not stop.is_set():
            n += 1
            try:
                replace_json(target, dict(n=n))
            except BaseException as exc:
                errors.append(repr(exc))
    threads = [threading.Thread(target=writer) for _ in range(3)]
    [t.start() for t in threads]
    s = scan.Scanner(attempt_budget=2.0, exhaustion_seconds=5.0)
    reads = 0; end = time.monotonic() + 6
    try:
        while time.monotonic() < end:
            s.seen.clear()
            assert s.inspect([target]) == []
            reads += 1
    finally:
        stop.set(); [t.join(5) for t in threads]
    assert not errors and not s.pending, (errors, s.pending)
    replace_json(target, dict(returncode=10))
    assert s.inspect([target]) == [target]
    results.append(f'{reads} full reads during 3-writer atomic replacement: no failure; retried {s.retried_reads}')
    # Exclusive lock released within the attempt budget: SAT found after retry.
    log = root / 'locked-native.log'; log.write_bytes(b'c active\n')
    s = scan.Scanner(attempt_budget=3.0, exhaustion_seconds=10.0)
    assert s.inspect([log]) == []
    lock = Exclusive(log, write=True); lock.append(SAT_LINE)
    timer = threading.Timer(1.0, lock.close); timer.start()
    began = time.monotonic(); hits = s.inspect([log]); waited = time.monotonic() - began
    timer.join()
    assert hits == [log] and s.retried_reads >= 1 and waited >= .8, (hits, s.retried_reads, waited)
    results.append(f'SAT written under exclusive lock detected after {waited:.2f}s of bounded retries')
    # Permanent unreadability: pending, cache not advanced, then fail closed.
    log2 = root / 'permanent-native.log'; log2.write_bytes(b'c active\n')
    s = scan.Scanner(attempt_budget=.3, exhaustion_seconds=1.0)
    assert s.inspect([log2]) == []
    lock = Exclusive(log2, write=True); lock.append(SAT_LINE)
    try:
        assert s.inspect([log2]) == [] and str(log2) in s.pending
        assert s.seen[str(log2)][0] == len(b'c active\n'), 'cache advanced before a successful read'
        time.sleep(1.1)
        try:
            s.inspect([log2]); raise AssertionError('exhausted scan did not fail closed')
        except scan.ScanUnavailable as exc:
            assert exc.failures and exc.failures[0]['path'] == str(log2)
        # Another file's SAT still outranks the unavailable one.
        other = root / 'other-native.log'; other.write_bytes(SAT_LINE)
        assert s.inspect([log2, other]) == [other]
    finally:
        lock.close()
    assert s.inspect([log2]) == [log2]
    results.append('permanent lock: PENDING without cache advance, ScanUnavailable after budget, '
                   'concurrent SAT still returned, SAT found after release')
    # Cross-block marker, append overlap, truncation and replacement.
    big = root / 'cross-native.log'
    big.write_bytes(b'c ' + b'x' * (scan.BLOCK - 8) + b'\ns SATI' + b'SFIABLE\n')
    assert scan.Scanner().inspect([big]) == [big]
    app = root / 'append-native.log'; app.write_bytes(b'c line\n' * 1000)
    s = scan.Scanner(); assert s.inspect([app]) == []
    with app.open('ab') as f:
        f.write(b's SATIS')
    assert s.inspect([app]) == []
    with app.open('ab') as f:
        f.write(b'FIABLE\n')
    assert s.inspect([app]) == [app]
    trunc = root / 'trunc-native.log'; trunc.write_bytes(b'c line\n' * 100)
    s = scan.Scanner(); assert s.inspect([trunc]) == []
    trunc.write_bytes(SAT_LINE)
    assert s.inspect([trunc]) == [trunc]
    exit10 = root / 'x-RESULT.json'; exit10.write_text('{"reason":"OWNER_STOP","returncode":10}')
    cand = root / 'SAT_FIRST_CANDIDATE.json'; cand.write_text('{}')
    assert set(scan.Scanner().inspect([exit10, cand])) == {exit10, cand}
    results.append('cross-block marker, split append, truncation, exit10 JSON and candidate names detected')
    return results


def fixture_area(root):
    area = root / 'campaign'; control = root / 'S036' / 'control'
    (area / 'attempts/cell-0000/tok').mkdir(parents=True); control.mkdir(parents=True)
    (area / 'STOP').touch()
    (area / 'OWNER_PAUSE.json').write_text('{"processes":[]}')
    (area / 'CONFIG.json').write_text('{}')
    directory = area / 'attempts/cell-0000/tok'
    (directory / 'native.log').write_bytes(b'c active fixture\n')
    return area, control, directory


def simple_worker(done):
    code = 'import pathlib,time,sys;p=pathlib.Path(sys.argv[1])\nwhile not p.exists(): time.sleep(.01)\nsys.exit(0)'
    child = subprocess.Popen([sys._base_executable, '-c', code, str(done)], creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(.2)
    return child, life.identity(child.pid)


def release(child, record, done):
    done.touch()
    try:
        if child.poll() is None:
            rows = life.thread_state(record)
            if any(r['suspend_count'] for r in rows):
                life.resume_identity(record, life.pause_identity(record))
        assert child.wait(timeout=10) == 0
    except Exception as exc:
        raise RuntimeError('Fixture worker left alive; preserve ' + str(record)) from exc


def start_supervisor(area, control, *extra):
    return subprocess.Popen([sys.executable, str(ROOT / 'scripts/s036_sat_supervisor.py'), '--directory', str(area),
                             '--control-directory', str(control), *extra], creationflags=subprocess.CREATE_NO_WINDOW,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def wait_for(predicate, seconds, what):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try:
            if predicate():
                return
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            pass
        time.sleep(.05)
    raise AssertionError('Timeout waiting for ' + what)


def watcher_state(control):
    return json.loads((control / 'WATCHER.json').read_text())


def suspended(record):
    return all(r['suspend_count'] >= 1 for r in life.thread_state(record))


def supervisor_controls(root):
    results = []
    for case in ('STRESS_THEN_OWNER_STOP', 'PERMANENT_LOCK_FAILS_CLOSED', 'SAT_DURING_RETRY',
                 'STALE_CONTROLLER', 'CONTROLLER_LOST'):
        base = root / case.lower(); base.mkdir()
        area, control, directory = fixture_area(base)
        done = base / 'DONE'; child, record = simple_worker(done)
        controller = life.identity(os.getpid())
        if case == 'CONTROLLER_LOST':
            gone = subprocess.Popen([sys._base_executable, '-c', 'pass'], creationflags=subprocess.CREATE_NO_WINDOW)
            controller = life.identity(gone.pid); gone.wait(5)
        adoption = dict(controller=controller, epoch=time.time(),
                        contexts=[dict(cell=0, directory=str(directory), worker=record)])
        replace_json(control / 'ADOPTION.json', adoption)
        replace_json(control / 'CONTROLLER.json', dict(updated_epoch=time.time() - (60 if case == 'STALE_CONTROLLER' else 0)))
        stop = threading.Event(); errors = []

        def lease():
            n = 0
            while not stop.is_set():
                n += 1
                try:
                    replace_json(control / 'ADOPTION.json', dict(adoption, n=n))
                    replace_json(control / 'CONTROLLER.json', dict(updated_epoch=time.time()))
                    replace_json(directory / 'WORKER.json', dict(n=n, verdict='UNKNOWN'))
                except BaseException as exc:
                    errors.append(repr(exc))
                time.sleep(.002)
        lease_thread = None
        if case not in ('STALE_CONTROLLER', 'CONTROLLER_LOST'):
            lease_thread = threading.Thread(target=lease); lease_thread.start()
        lock = None
        extra = ['--full-scan-seconds', '1']
        if case == 'PERMANENT_LOCK_FAILS_CLOSED':
            extra += ['--exhaustion-seconds', '2']
        supervisor = start_supervisor(area, control, *extra)
        try:
            if case == 'STRESS_THEN_OWNER_STOP':
                wait_for(lambda: watcher_state(control)['status'] == 'WATCHING', 20, 'watching')
                time.sleep(10)  # ~10 full scans while three files are replaced every few ms
                state = watcher_state(control)
                assert supervisor.poll() is None and state['status'] == 'WATCHING', state
                (control / 'STOP').touch()
                assert supervisor.wait(timeout=30) == 0, supervisor.stderr.read().decode()
                assert watcher_state(control)['status'] == 'PAUSED'
                guard = json.loads((control / 'GUARD_PAUSE.json').read_text())
                assert guard['reason'] == 'OWNER_OR_CONTROLLER_STOP' and suspended(record)
                assert ctl.stop_reason(area, control) == 'SUPERVISOR_PAUSE:OWNER_OR_CONTROLLER_STOP'
                results.append(f'10s of full/fast scans during continuous replacement: WATCHING, then owner STOP '
                               f'paused the worker; retried reads {state["retried_reads"]}')
            elif case == 'PERMANENT_LOCK_FAILS_CLOSED':
                wait_for(lambda: watcher_state(control)['status'] == 'WATCHING', 20, 'watching')
                lock = Exclusive(directory / 'native.log', write=True); lock.append(b'c still running\n')
                code = supervisor.wait(timeout=40)
                assert code != 0
                failure = json.loads((control / 'WATCHER_FAILURE.json').read_text())
                guard = json.loads((control / 'GUARD_PAUSE.json').read_text())
                assert failure['reason'] == guard['reason'] == 'WATCHER_SCAN_UNAVAILABLE', (failure, guard)
                assert 'ScanUnavailable' in failure['traceback'] and suspended(record)
                assert (control / 'STOP').exists() and watcher_state(control)['status'] == 'FAILED_CLOSED'
                rescan = json.loads((control / 'WATCHER_FAILURE_RESCAN.json').read_text())
                assert any(row['path'] == str(directory / 'native.log') for row in rescan['unreadable'])
                assert ctl.stop_reason(area, control) == 'SUPERVISOR_PAUSE:WATCHER_SCAN_UNAVAILABLE'
                results.append('permanent exclusive lock: worker suspended first, explicit WATCHER_SCAN_UNAVAILABLE '
                               'with traceback, fresh rescan lists the unreadable file, controller reports the cause')
            elif case == 'SAT_DURING_RETRY':
                wait_for(lambda: watcher_state(control)['status'] == 'WATCHING', 20, 'watching')
                time.sleep(1.5)
                lock = Exclusive(directory / 'native.log', write=True); lock.append(SAT_LINE)
                threading.Timer(1.2, lock.close).start()
                assert supervisor.wait(timeout=60) == 0, supervisor.stderr.read().decode()
                state = watcher_state(control)
                alert = json.loads((control / 'SAT_ALERT.json').read_text())
                assert state['status'] == 'SAT_ALERT' and state['retried_reads'] >= 1, state
                assert alert['ordinary_UNKNOWN_forbidden'] and suspended(record)
                assert alert['verification'][0]['status'] == 'SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED'
                assert ctl.stop_reason(area, control) == 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
                results.append('SAT appended under an exclusive lock: bounded retry, SAT_ALERT before validation, '
                               'worker suspended, rejected fixture validation kept the alert')
            else:
                assert supervisor.wait(timeout=30) == 0, supervisor.stderr.read().decode()
                guard = json.loads((control / 'GUARD_PAUSE.json').read_text())
                expected = dict(STALE_CONTROLLER='ADOPTED_CONTROLLER_LEASE_EXPIRED',
                                CONTROLLER_LOST='ADOPTED_CONTROLLER_IDENTITY_LOST')[case]
                assert guard['reason'] == expected and suspended(record), guard
                results.append(f'{case.lower()}: supervisor paused the worker with {expected}')
            assert not errors, errors[:3]
        finally:
            stop.set()
            if lease_thread:
                lease_thread.join(5)
            if lock:
                lock.close()
            if supervisor.poll() is None:
                (control / 'STOP').touch(); supervisor.wait(timeout=30)
            release(child, record, done)
    # Late SAT racing the final pause is caught by the fresh final rescan.
    base = root / 'late'; base.mkdir(); area, control, directory = fixture_area(base)
    with patch.object(sup, 'pause_all', side_effect=lambda *a, **k: (directory / 'native.log').write_bytes(SAT_LINE) or []):
        sup.pause_all(area, control, 'OWNER_OR_CONTROLLER_STOP')
        alert, unreadable = sup.final_rescan(area, control, validator=lambda *a, **k: (_ for _ in ()).throw(ValueError('x')))
    assert alert and alert['ordinary_UNKNOWN_forbidden'] and not unreadable
    results.append('late SAT after the final pause caught by the fresh complete rescan')
    return results


def controller_controls(root):
    results = []
    os.environ['EMP_S036_FIXTURE'] = '1'
    for case in ('PILOT_SCHEDULER', 'THROTTLE', 'SUPERVISOR_CAUSE'):
        base = root / ('ctl-' + case.lower()); base.mkdir()
        area = base / 'campaign'; control = base / 'S036' / 'control'; control.mkdir(parents=True); area.mkdir()
        (area / 'STOP').touch()
        fixtures = [start_fixture(base / f'slot-{i}') for i in range(4)]
        contexts = []; policy = dict(status='CLASSIFIED_HELPERS_REMAIN_SUSPENDED', processes={})
        try:
            for i, f in enumerate(fixtures):
                (f['directory'] / 'native.log').write_text(
                    'c S032_PROGRESS seconds=1.0 checks=1 cuts=1 model_checks=0 check_seconds=0\n'
                    f'c S032_LOGIC conflicts={i} decisions={i} propagations={i}\n')
                w = f['worker']
                contexts.append(dict(cell=i, worker=w, directory=str(f['directory']), turns=0, active_seconds=0,
                                     state='PAUSED', quarantined_threads=f['quarantine'], input_sha256='fixture',
                                     native_sha256='fixture'))
                policy['processes'][str(w['pid'])] = dict(start_ticks=w['start_ticks'], kind='NATIVE_ORIGINAL_THREAD_ONLY',
                                                         threads=f['rows'], quarantined_threads=f['quarantine'])
            (control / 'THREAD_POLICY.json').write_text(json.dumps(policy))
            planned = dict(contexts=contexts, original_processes=[f['worker'] for f in fixtures])
            calls = dict(n=0)
            real_resource = ctl.resource_reason

            def resource(area_, control_, contexts_, registry, cache):
                calls['n'] += 1
                hard, soft, sample = real_resource(area_, control_, contexts_, registry, cache)
                if case == 'THROTTLE' and 5 <= calls['n'] <= 12:
                    return None, 'SOFT_AVAILABLE_RAM_THROTTLE', dict(sample, available=0)
                return None, None, dict(sample, available=10 * ctl.GiB)
            limits = dict(ctl.LIMITS, throttle_clear_seconds=1)
            stopper = None
            if case == 'SUPERVISOR_CAUSE':
                def cause():
                    time.sleep(3)
                    (control / 'GUARD_PAUSE.json').write_text(json.dumps(dict(reason='WATCHER_SCAN_UNAVAILABLE')))
                    (control / 'STOP').touch()
                stopper = threading.Thread(target=cause); stopper.start()
            with patch.object(ctl, 'published_acceptance', lambda c: {}), \
                    patch.object(ctl, 'plan', lambda a, c: copy.deepcopy(planned)), \
                    patch.object(ctl.s035, 'input_gates', lambda *a: {}), \
                    patch.object(ctl, 'watcher', lambda c, stale_seconds=10: life.identity(os.getpid())), \
                    patch.object(ctl, 'resource_reason', resource), patch.object(ctl, 'LIMITS', limits):
                ctl.run(area, control, pilot_seconds=8)
            if stopper:
                stopper.join()
            a = json.loads((control / 'ADOPTION.json').read_text())
            events = [json.loads(x) for x in (control / 'JOURNAL.jsonl').read_text().splitlines()]
            metrics = [json.loads(x) for x in (control / 'METRICS.jsonl').read_text().splitlines()] \
                if (control / 'METRICS.jsonl').exists() else []
            assert not a['pause_errors'] and (control / 'STOP').exists() and (area / 'STOP').exists()
            assert all(all(t['suspend_count'] > 0 for t in life.thread_counts(f['worker'])) for f in fixtures)
            if case == 'PILOT_SCHEDULER':
                active = set(); peak = 0
                for e in events:
                    if e['kind'] == 'same_identity_resumed':
                        active.add(e['cell']); peak = max(peak, len(active))
                    if e['kind'] == 'fair_turn_paused':
                        active.discard(e['cell'])
                assert peak == 2 and all(c['turns'] >= 2 for c in a['contexts']), (peak, [c['turns'] for c in a['contexts']])
                assert a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED'
                assert metrics and all('delta_cpu_seconds' in m and m['delta_cpu_seconds'] > 0 for m in metrics), metrics[:2]
                # Successful pilot rearm archives S036 controls; nothing resumes.
                a['controller'] = dict(pid=2147483000, start_ticks='0'); a['watcher'] = dict(pid=2147483001, start_ticks='0')
                (control / 'ADOPTION.json').write_text(json.dumps(a))
                with patch.object(ctl, 'published_acceptance', lambda c: {}), \
                        patch.object(ctl, 'plan', lambda ar, c: copy.deepcopy(planned)):
                    ctl.rearm_pilot(area, control)
                assert not (control / 'STOP').exists() and (area / 'STOP').exists()
                assert all(all(t['suspend_count'] > 0 for t in life.thread_counts(f['worker'])) for f in fixtures)
                results.append(f'four-resident/two-slot pilot: peak 2, turns {[c["turns"] for c in a["contexts"]]}, '
                               f'{len(metrics)} metric rows with CPU deltas; rearm archived controls without resume')
            elif case == 'THROTTLE':
                kinds = [e['kind'] for e in events]
                assert 'soft_throttle_started' in kinds and 'soft_throttle_cleared' in kinds, kinds
                started = kinds.index('soft_throttle_started'); cleared = kinds.index('soft_throttle_cleared')
                assert 'same_identity_resumed' not in kinds[started:cleared]
                assert any(m['why'] == 'SOFT_AVAILABLE_RAM_THROTTLE' for m in metrics)
                assert a['reason'] == 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED'
                results.append('soft RAM dip throttled (executing turns paused, no resumes) and cleared after the '
                               'sustained interval without ending the run')
            else:
                assert a['reason'] == 'SUPERVISOR_PAUSE:WATCHER_SCAN_UNAVAILABLE', a['reason']
                results.append('controller halt reason carries the supervisor cause SUPERVISOR_PAUSE:WATCHER_SCAN_UNAVAILABLE')
        finally:
            for f in fixtures:
                if f['p'].poll() is None:
                    finish_fixture(f)
    os.environ.pop('EMP_S036_FIXTURE', None)
    return results


def main():
    report = dict(status='RUNNING')
    with tempfile.TemporaryDirectory(prefix='s036-controls-') as td:
        root = Path(td)
        (root / 'scan').mkdir()
        report['scanner'] = scanner_controls(root / 'scan')
        report['supervisor'] = supervisor_controls(root)
        report['controller'] = controller_controls(root)
    report.update(status='PASS', scientific_processes_touched=False, forced_terminations=0,
                  source_sha256=ctl.sources(),
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT / 'validation/S036/SUPERVISOR_CONTROLS.json').write_text(json.dumps(report, indent=1) + '\n',
                                                                   encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
