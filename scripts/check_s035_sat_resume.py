"""SAT guard controls, including real interruption; never use campaign workers."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
import s035_sat_first_resume as guard


def portable():
    with tempfile.TemporaryDirectory() as temporary:
        area = Path(temporary)/'campaign'; area.mkdir()
        paths = []
        for name in guard.SCIENTIFIC:
            p = area.parent/name/'attempts/cell-0000/token'; p.mkdir(parents=True, exist_ok=True)
            log = p/'native.log'; log.write_text('c active\n')
            paths.append(log)
        scanner = guard.Scanner()
        assert scanner.inspect(guard.scientific_paths(area)) == []
        for p in paths:
            with p.open('a') as f:
                f.write('s SATISFIABLE\nv 1 -2 0\n')
        assert set(scanner.inspect(guard.scientific_paths(area))) == set(paths)
        assert scanner.inspect(guard.scientific_paths(area)) == []
        # Exit10 takes precedence even with an UNKNOWN/STOP result.
        result = paths[0].with_name('another-RESULT.json')
        result.write_text('{"status":"UNKNOWN","reason":"OWNER_STOP","returncode":10}')
        candidate = paths[1].with_name('SAT_FIRST_CANDIDATE.json'); candidate.write_text('{}')
        assert set(scanner.inspect([result, candidate])) == {result, candidate}
        # Log truncation and replacement cannot hide a signal.
        same = paths[2]; same.write_text('s SATISFIABLE\n')
        assert scanner.inspect([same]) == [same]
        control = area/'RESUME_CONTROL'; control.mkdir()
        (area/'CONFIG.json').write_text('{}')
        def fail(*args, **kwargs):
            assert json.loads((area/'SAT_ALERT.json').read_text())['ordinary_UNKNOWN_forbidden']
            raise ValueError('Intentional rejected assignment')
        with patch.object(guard, 'pause_all', return_value=[]):
            alert = guard.handle(area, control, [paths[0]], validator=fail)
        assert alert['ordinary_UNKNOWN_forbidden']
        assert alert['verification'][0]['status'] == 'SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED'
        assert (area/'SAT_ALERT.json').exists() and (control/'SAT_ALERT.json').exists()
        assert any(Path(row.get('path', '')).name == 'native.log' for row in alert['preserved'])
        late_area = Path(temporary)/'race/campaign'; late_area.mkdir(parents=True)
        late_control = late_area/'RESUME_CONTROL'; late_control.mkdir()
        late_dir = late_area/'attempts/cell-0000/token'; late_dir.mkdir(parents=True)
        late_log = late_dir/'native.log'; late_log.write_text('c active\n')
        (late_area/'CONFIG.json').write_text('{}')
        late_scanner = guard.Scanner()
        assert late_scanner.inspect([late_log]) == []
        def pause_then_signal(*args):
            late_log.write_text('s SATISFIABLE\nv 1 0\n')
            return []
        with patch.object(guard, 'pause_all', side_effect=pause_then_signal):
            late_alert = guard.pause_and_rescan(late_area, late_control, late_scanner, 'OWNER_STOP', validator=fail)
        assert late_alert['ordinary_UNKNOWN_forbidden']
        assert (late_area/'SAT_ALERT.json').exists()
    return dict(all_scientific_roots=True, append_and_replacement=True,
                exit10_stop_race=True, alternate_candidate_name=True,
                alert_precedes_validation_failure=True, original_log_preserved=True,
                final_pause_scan_catches_late_SAT=True)


def windows():
    import psutil
    from s035_preserved_lifecycle import identity, pause_identity, resume_identity, checked
    # This worker observes a file and exits cooperatively after the test; it is
    # unrelated to all scientific identities and never calls a solver.
    with tempfile.TemporaryDirectory() as temporary:
        area = Path(temporary)/'campaign'; area.mkdir()
        control = area/'RESUME_CONTROL'; control.mkdir()
        directory = area/'attempts/cell-0000/test'; directory.mkdir(parents=True)
        done = area/'COOPERATIVE_EXIT'
        code = 'import pathlib,time,sys;p=pathlib.Path(sys.argv[1]);\nwhile not p.exists(): time.sleep(.01)\nsys.exit(0)'
        child = subprocess.Popen([sys._base_executable, '-c', code, str(done)], creationflags=subprocess.CREATE_NO_WINDOW)
        record = identity(child.pid)
        try:
            time.sleep(.2)
            # One extra count mimics an already parked original process.
            pause_identity(record)
            psutil.Process(child.pid).suspend()
            (control/'ADOPTION.json').write_text(json.dumps(dict(contexts=[dict(cell=0,directory=str(directory),worker=record)])))
            (area/'CONFIG.json').write_text('{}')
            (area/'OWNER_PAUSE.json').write_text('{"processes":[]}')
            threads = pause_identity(record); resume_identity(record, threads)
            (directory/'native.log').write_text('s SATISFIABLE\nv 1 0\n')
            (directory/'native-RESULT.json').write_text('{"reason":"OWNER_STOP","returncode":10}')
            (directory/'input.inst').write_text('intentionally invalid fixture input')
            def invalid(*args, **kwargs):
                raise ValueError('Intentional validator rejection during interruption')
            alert = guard.handle(area, control, [directory/'native.log'], validator=invalid)
            assert checked(record).status() == psutil.STATUS_STOPPED
            before = checked(record).cpu_times()
            time.sleep(.2)
            after = checked(record).cpu_times()
            assert (after.user+after.system)-(before.user+before.system) < .03
            assert alert['verification'][0]['status'] == 'SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED'
            assert (control/'STOP').exists() and (area/'STOP').exists()
            assert (directory/'native.log').read_text().startswith('s SATISFIABLE')
            assert any(Path(v.get('path','')).name == 'input.inst' for v in alert['preserved'])
            # Mutable adoption metadata must not block the independent frozen
            # identity registry from preserving a still-running worker.
            resume_identity(record, pause_identity(record))
            (control/'ADOPTION.json').write_text('{malformed')
            (area/'OWNER_PAUSE.json').write_text(json.dumps(dict(processes=[record])))
            recovered = guard.pause_all(area, control, 'MALFORMED_ADOPTION_CONTROL')
            assert checked(record).status() == psutil.STATUS_STOPPED
            assert any(r.get('stage') == 'ADOPTION_METADATA' for r in recovered)
            done.touch()
            resume_identity(record, pause_identity(record))
            assert child.wait(timeout=5) == 0
        finally:
            if child.poll() is None:
                done.touch()
                try:
                    if checked(record).status() == psutil.STATUS_STOPPED:
                        resume_identity(record, pause_identity(record))
                    child.wait(timeout=5)
                except Exception as exc:
                    raise RuntimeError('Control remains alive; preserve identity '+str(record)) from exc
    # Run the actual independent guard against a fresh fixture, with a stale
    # controller lease and then an owner STOP. It must suspend and exit itself.
    for cause in ('STALE_CONTROLLER', 'CONTROLLER_LOST', 'OWNER_STOP'):
        with tempfile.TemporaryDirectory() as temporary:
            area = Path(temporary)/'campaign'; area.mkdir()
            control = area/'RESUME_CONTROL'; control.mkdir()
            directory = area/'attempts/cell-0000/test'; directory.mkdir(parents=True)
            (directory/'native.log').write_text('c active fixture\n')
            done = area/'COOPERATIVE_EXIT'
            child = subprocess.Popen([sys._base_executable, '-c', code, str(done)], creationflags=subprocess.CREATE_NO_WINDOW)
            record = identity(child.pid); time.sleep(.2)
            (area/'OWNER_PAUSE.json').write_text('{"processes":[]}')
            controller = identity(os.getpid())
            if cause == 'CONTROLLER_LOST':
                expired = subprocess.Popen([sys._base_executable, '-c', 'import time; time.sleep(.1)'],
                                           creationflags=subprocess.CREATE_NO_WINDOW)
                controller = identity(expired.pid)
                assert expired.wait(timeout=5) == 0
            (control/'ADOPTION.json').write_text(json.dumps(dict(controller=controller, epoch=time.time()-10,
                contexts=[dict(cell=0,directory=str(directory),worker=record)])))
            (control/'CONTROLLER.json').write_text(json.dumps(dict(updated_epoch=time.time()-(10 if cause=='STALE_CONTROLLER' else 0))))
            if cause == 'OWNER_STOP':
                (control/'STOP').touch()
            supervisor = subprocess.Popen([sys.executable, str(ROOT/'scripts/s035_sat_first_resume.py'),
                '--directory', str(area), '--control-directory', str(control)], creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                assert supervisor.wait(timeout=10) == 0, supervisor.stderr.read().decode()
                assert checked(record).status() == psutil.STATUS_STOPPED
                state = json.loads((control/'WATCHER.json').read_text())
                assert state['status'] == 'PAUSED' and not state['ready']
                paused = json.loads((control/'GUARD_PAUSE.json').read_text())
                assert paused['reason'] == {'STALE_CONTROLLER':'ADOPTED_CONTROLLER_LEASE_EXPIRED',
                    'CONTROLLER_LOST':'ADOPTED_CONTROLLER_IDENTITY_LOST', 'OWNER_STOP':'WATCHER_OR_OWNER_STOP'}[cause]
            finally:
                (control/'STOP').touch()
                if supervisor.poll() is None:
                    supervisor.wait(timeout=10)
                done.touch()
                if checked(record).status() == psutil.STATUS_STOPPED:
                    resume_identity(record, pause_identity(record))
                assert child.wait(timeout=5) == 0
    return dict(real_candidate_interrupt=True, paused_cpu_zero=True, validation_failure_keeps_alert=True,
                STOP_race=True, malformed_adoption_preserves_worker=True,
                stale_controller_guard=True, controller_loss_guard=True, owner_stop_guard=True,
                nonforcing_natural_exit=True, original_campaign_untouched=True)


if __name__ == '__main__':
    report = dict(status='PASS', portable=portable())
    if os.name == 'nt':
        report['windows'] = windows()
        out = ROOT/'validation/S035/resume/SAT_CONTROLS.json'
        guard.write(out, report)
    print(json.dumps(report, indent=1))
