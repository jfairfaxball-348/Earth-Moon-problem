"""S036 autopilot: owner-authorised automatic recovery from operational pauses.

Owner, 24 October 2026: "the idea is autonomous working and solving ... fix whatever
you recommend and think is best and continue" and "I really want this to be just
hands off". The search previously stayed paused overnight after a safe operational
pause because every resume needed the owner.

Every 30 s this process checks the live S036 control state. When the search is
PAUSED for an OPERATIONAL reason it waits for the old controller and supervisor to
exit, then performs exactly the documented operator sequence: prepare-resume
(owner-authorised; cold solver released through its stop file), a fresh supervisor,
the controller with --resume (same resident identities, RAM kept), and the bounded
cold runner if none is alive. It never resumes after:
  * a SAT alert, a native return (TERMINAL.json) or any reason naming SAT/native return;
  * an owner pause (OWNER_PAUSE.json, or a stop reason not attributable to the system);
  * a supervisor scan failure whose fresh rescan was not clean.
At most RECOVERY_LIMIT recoveries in RECOVERY_WINDOW; beyond that it stops and leaves
the search paused for review. It never kills, suspends or force-terminates anything,
and never starts S037. All actions are journalled in artifacts/tmp/S036/control.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s035_windows import atomic_json, read_json, journal, live_identity, process_identity, locked  # noqa: E402

CONTROL = ROOT / 'artifacts/tmp/S036/control'
COLD = ROOT / 'artifacts/tmp/S036/cold'
STATE = ROOT / 'artifacts/tmp/S036/AUTOPILOT.json'
PYTHON = ROOT / '.venv/Scripts/python.exe'
RECOVERY_LIMIT = 6
RECOVERY_WINDOW = 6 * 3600
SETTLE_SECONDS = 60
RECOVERABLE = ('SUPERVISOR_PAUSE:ADOPTED_CONTROLLER_LEASE_EXPIRED', 'SUPERVISOR_PAUSE:ADOPTED_CONTROLLER_IDENTITY_LOST',
               'SUPERVISOR_UNAVAILABLE', 'SAFETY_AGGREGATE_PRIVATE_CAP', 'SAFETY_PER_WORKER_PRIVATE_CAP',
               'SAFETY_AVAILABLE_RAM_FLOOR', 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE',
               'SOFT_AVAILABLE_RAM_THROTTLE', 'RECYCLE_STOP_TIMEOUT', 'RECYCLE_AUDIT_FAILURE',
               'RESIDENT_PREPARATION_FAILURE', 'CONTROLLER_EXCEPTION', 'SUPERVISOR_PAUSE:WATCHER_SCAN_UNAVAILABLE',
               'SUPERVISOR_PAUSE:WATCHER_FAILURE', 'SUPERVISOR_FAILURE_RECORDED')
FORBIDDEN_WORDS = ('SAT', 'NATIVE_RETURN', 'TERMINAL')


def read(path, default=None):
    try:
        return read_json(path) if Path(path).exists() else (default if default is not None else {})
    except Exception:
        return default if default is not None else {}


def classify(control):
    """Return ('RUNNING'|'RECOVERABLE'|'BLOCKED', reason, detail)."""
    controller = read(control / 'CONTROLLER.json')
    adoption = read(control / 'ADOPTION.json')
    if (control / 'SAT_ALERT.json').exists() or (ROOT / 'artifacts/tmp/S035/campaign/SAT_ALERT.json').exists():
        return 'BLOCKED', 'SAT_ALERT_REQUIRES_PROMINENT_REVIEW', None
    if (control / 'TERMINAL.json').exists():
        return 'BLOCKED', 'NATIVE_RETURN_REQUIRES_REVIEW', None
    if (control / 'OWNER_PAUSE.json').exists():
        return 'BLOCKED', 'OWNER_PAUSE', None
    status = controller.get('status')
    alive = bool(controller.get('pid')) and live_identity(controller['pid'], controller.get('start_ticks', ''))
    if status in ('RUNNING', 'THROTTLED') and alive:
        return 'RUNNING', status, None
    if status in ('RUNNING', 'THROTTLED', None) and not alive:
        # Controller vanished without writing its halt; the supervisor pauses on lease
        # expiry. Once the supervisor has paused and exited, recovery may proceed.
        watcher = read(control / 'WATCHER.json')
        guard = read(control / 'GUARD_PAUSE.json')
        watcher_alive = bool(watcher.get('pid')) and live_identity(watcher['pid'], watcher.get('start_ticks', ''))
        if (not watcher_alive and str(guard.get('reason', '')).startswith('ADOPTED_CONTROLLER')
                and adoption.get('status') in ('RUNNING', 'THROTTLED')):
            return 'RECOVERABLE', 'SUPERVISOR_PAUSE:' + guard['reason'], dict(fix_adoption=True)
        return 'WAIT', 'CONTROLLER_LOST_AWAITING_SUPERVISOR_PAUSE', None
    reason = str(adoption.get('reason') or controller.get('reason') or '')
    if any(word in reason for word in FORBIDDEN_WORDS) and not reason.startswith('SUPERVISOR_PAUSE:WATCHER'):
        return 'BLOCKED', reason, None
    if adoption.get('pause_errors'):
        return 'BLOCKED', 'PAUSE_ERRORS_REQUIRE_REVIEW', adoption['pause_errors']
    watcher_failure = (control / 'WATCHER_FAILURE.json').exists()
    if watcher_failure:
        rescan = read(control / 'WATCHER_FAILURE_RESCAN.json')
        if not (rescan.get('sat_alert') is False and rescan.get('unreadable') == []):
            return 'BLOCKED', 'SUPERVISOR_FAILURE_RESCAN_NOT_CLEAN', rescan
    if reason.startswith(RECOVERABLE):
        return 'RECOVERABLE', reason, dict(watcher_failure=watcher_failure)
    return 'BLOCKED', 'UNCLASSIFIED_PAUSE_' + reason, None


def wait_for(predicate, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try:
            if predicate():
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def launch(*args):
    out = subprocess.run([str(PYTHON), str(ROOT / 'scripts/s036_launch.py'), *args], cwd=ROOT, capture_output=True,
                         text=True, timeout=180)
    if out.returncode:
        raise RuntimeError('launch failed: ' + out.stdout + out.stderr)
    return out.stdout.strip()


def cold_runner_alive():
    import psutil
    return any(p.info['name'] == 'python.exe' and any(str(x).endswith('s036_cold_diagnostic.py')
                                                      for x in (p.info['cmdline'] or []))
               for p in psutil.process_iter(['name', 'cmdline']))


def recover(control, reason, detail, state):
    import s036_fresh_campaign as fresh
    controller = read(control / 'CONTROLLER.json'); watcher = read(control / 'WATCHER.json')
    for record in (controller, watcher):
        if record.get('pid') and not wait_for(lambda r=record: not live_identity(r['pid'], r.get('start_ticks', '')), 120):
            raise RuntimeError('Previous controller/supervisor still alive; not recovering')
    if detail and detail.get('fix_adoption'):
        # The lost controller never wrote its halt record; record the supervisor's pause so the
        # standard verified prepare-resume (which re-checks every resident is suspended) applies.
        adoption = read(control / 'ADOPTION.json')
        adoption.update(status='PAUSED', reason=reason, pause_errors=[], exited_cells=[], executing_cells=[],
                        halt_written_by='autopilot_after_supervisor_pause')
        atomic_json(control / 'ADOPTION.json', adoption)
    plan = fresh.prepare_resume(control, owner_authorized=True,
                                watcher_failure_reviewed=bool(detail and detail.get('watcher_failure')))
    journal(control / 'JOURNAL.jsonl', 'autopilot_prepared_resume', reason=reason, history=plan['history'],
            cold_solver=plan['cold_solver'], requeued=plan['queued_regions'])
    launch('supervisor')
    if not wait_for(lambda: read(control / 'WATCHER.json').get('status') == 'WATCHING'
                    and not read(control / 'WATCHER.json').get('scanning'), 300):
        raise RuntimeError('Supervisor did not reach WATCHING')
    launch('fresh', '--resume')
    if not wait_for(lambda: read(control / 'CONTROLLER.json').get('status') in ('RUNNING', 'THROTTLED'), 300):
        raise RuntimeError('Controller did not reach RUNNING')
    cold = 'COLD_RUNNER_ALREADY_ALIVE'
    if not cold_runner_alive() and not (COLD / 'RUNNER.STOP').exists():
        launch('cold', 'campaign', '--regions', '1,3,15,31,63', '--budget', '360', '--span', '14400',
               '--max-wait', '604800')
        cold = 'COLD_RUNNER_RELAUNCHED'
    journal(control / 'JOURNAL.jsonl', 'autopilot_recovered', reason=reason, cold=cold,
            controller=read(control / 'CONTROLLER.json').get('pid'), watcher=read(control / 'WATCHER.json').get('pid'))
    return cold


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true', help='classify and report only')
    args = parser.parse_args()
    if args.once:
        print(json.dumps(classify(CONTROL), default=str)); return
    identity = dict(pid=os.getpid(), start_ticks=process_identity(os.getpid()))
    with locked(STATE.with_suffix('.lock'), blocking=False):
        state = read(STATE, dict(recoveries=[]))
        state.update(status='WATCHING', identity=identity, started_epoch=time.time())
        paused_since = None
        while True:
            try:
                kind, reason, detail = classify(CONTROL)
                now = time.time()
                state['recoveries'] = [r for r in state.get('recoveries', []) if now - r['epoch'] < RECOVERY_WINDOW]
                if kind == 'RUNNING' or kind == 'WAIT':
                    paused_since = None
                    state.update(status='WATCHING', last_kind=kind, last_reason=reason)
                elif kind == 'BLOCKED':
                    paused_since = None
                    state.update(status='BLOCKED_REVIEW_REQUIRED', last_kind=kind, last_reason=reason)
                else:
                    paused_since = paused_since or now
                    if now - paused_since < SETTLE_SECONDS:
                        state.update(status='SETTLING', last_reason=reason)
                    elif len(state['recoveries']) >= RECOVERY_LIMIT:
                        state.update(status='GAVE_UP_TOO_MANY_RECOVERIES', last_reason=reason)
                    else:
                        state.update(status='RECOVERING', last_reason=reason)
                        atomic_json(STATE, dict(state, updated_epoch=time.time()))
                        try:
                            cold = recover(CONTROL, reason, detail, state)
                            state['recoveries'].append(dict(epoch=time.time(), reason=reason, outcome='RECOVERED',
                                                            cold=cold))
                            state.update(status='WATCHING')
                        except Exception as exc:
                            state['recoveries'].append(dict(epoch=time.time(), reason=reason, outcome='FAILED',
                                                            error=repr(exc)))
                            journal(CONTROL / 'JOURNAL.jsonl', 'autopilot_recovery_failed', reason=reason,
                                    error=repr(exc), traceback=traceback.format_exc()[-1500:])
                            state.update(status='RECOVERY_FAILED_WILL_RETRY', last_error=repr(exc))
                        paused_since = None
                atomic_json(STATE, dict(state, updated_epoch=time.time()))
            except Exception as exc:
                state.update(status='AUTOPILOT_ERROR', last_error=repr(exc))
                try:
                    atomic_json(STATE, dict(state, updated_epoch=time.time()))
                except Exception:
                    pass
            time.sleep(30)


if __name__ == '__main__':
    main()
