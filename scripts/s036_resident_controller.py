"""S036 retained-RAM fair-turn controller for the four original S035 native contexts.

Adopts exactly the suspended S035 native identities for regions 0, 7, 127 and
255 under a separate S036 control directory. Only their original native
threads are resumed; legacy Python/conhost ancestors and classified
ntdll!TppWorkerThread helpers stay suspended. Nothing is launched, evicted,
duplicated or terminated; the historical S035 STOP, ledgers and RESUME_CONTROL
stay frozen and are only read.

Changes from the S035 preserved controller:
* registered S036 control directory and S036-pinned published acceptance;
* stop reasons carry the underlying supervisor cause (e.g. WATCHER_FAILURE)
  instead of a generic OWNER_OR_SUPERVISOR_PAUSE;
* a soft available-RAM dip THROTTLES (executing contexts paused, RAM kept)
  until it clears for a sustained interval, instead of ending the run; hard
  caps still preserve everything and exit;
* per-turn metrics (conflicts, decisions, propagations, geometric cuts, CPU,
  private memory, lemma bytes) are journalled for per-active-CPU-second rates;
* the storage budget counts S035 and S036 together and the optional bounded
  cold-diagnostic process is included in aggregate memory accounting.
Native UNSAT never closes a region here; a SAT/exit-10 outranks everything.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s035_windows import atomic_json, read_json, journal, locked, inhibit_sleep, directory_bytes  # noqa: E402
from s035_preserved_lifecycle import (LifecycleError, identity, checked, thread_counts,  # noqa: E402
                                      pause_identity, resume_identity, ProcessHandle, sample_identities)
import s035_thread_policy as thread_policy  # noqa: E402
import s035_preserved_campaign as s035  # noqa: E402

AREA = ROOT / 'artifacts/tmp/S035/campaign'
CONTROL = ROOT / 'artifacts/tmp/S036/control'
SOURCES = ('tools/s036_sat_scan.py', 'scripts/s036_sat_supervisor.py', 'scripts/s036_resident_controller.py',
           'tools/s035_preserved_lifecycle.py',
           'scripts/s035_preserved_campaign.py', 'tools/s035_thread_policy.py', 'tools/s035_sat_validation.py',
           'tools/s035_windows.py')
GiB = 1024 ** 3
LIMITS = dict(aggregate_private=6 * GiB, per_worker_private=2 * GiB, available_floor=2 * GiB,
              soft_private=5 * GiB, soft_available=2560 * 1024 ** 2, disk_reserve=10 * GiB,
              raw_proof_attempt=2 * GiB, campaign_bytes=40 * GiB, session_bytes=64 * GiB,
              throttle_clear_seconds=120, throttle_clear_margin=256 * 1024 ** 2)
LOGIC = re.compile(r'^c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)', re.M)
PROGRESS = re.compile(r'^c S032_PROGRESS seconds=([\d.]+) checks=(\d+) cuts=(\d+)', re.M)


def sha(path):
    return s035.sha(path)


def sources():
    return {name: sha(ROOT / name) for name in SOURCES}


def counters(directory):
    """Last logged native counters; these are logged values, not exact at-pause counts."""
    log = Path(directory) / 'native.log'
    with log.open('rb') as f:
        f.seek(max(0, f.seek(0, 2) - 16384))
        tail = f.read().decode(errors='replace')
    row = {}
    logic = LOGIC.findall(tail)
    progress = PROGRESS.findall(tail)
    if logic:
        row.update(conflicts=int(logic[-1][0]), decisions=int(logic[-1][1]), propagations=int(logic[-1][2]))
    if progress:
        row.update(native_wall_seconds=float(progress[-1][0]), checks=int(progress[-1][1]),
                   cuts=int(progress[-1][2]))
    lemma = Path(directory) / 'new-cuts.lem'
    row.update(native_log_bytes=log.stat().st_size, lemma_bytes=lemma.stat().st_size if lemma.exists() else 0)
    return row


def process_metrics(worker):
    p = checked(worker)
    clock, memory = p.cpu_times(), p.memory_info()
    return dict(cpu_seconds=clock.user + clock.system, private_bytes=memory.private, rss_bytes=memory.rss)


def plan(area, control):
    """Read only: verify frozen S035 identities and domain; policy from S036 control."""
    area = Path(area)
    paused = read_json(area / 'OWNER_PAUSE.json')
    frozen = paused['contexts']['contexts']
    current = read_json(area / 'RESIDENT_CONTEXTS.json')['contexts']
    if set(frozen) != {'0', '7', '127', '255'} or set(current) != set(frozen):
        raise LifecycleError('Unexpected resident membership; manual reconciliation required')
    policy = load_policy(control)
    contexts = []
    for key in sorted(frozen, key=int):
        context = frozen[key]
        if current[key]['worker'] != context['worker'] or current[key]['directory'] != context['directory']:
            raise LifecycleError('Frozen/current resident identity mismatch')
        checked(context['worker'])
        thread_policy.validate(context['worker'], policy, paused=True)
        contexts.append(dict(cell=context['cell'], worker=context['worker'], directory=context['directory'],
                             original_state=context['state'], original_turns=context.get('turns', 0), turns=0,
                             active_seconds=0.0, state='PAUSED',
                             quarantined_threads=policy['processes'][str(context['worker']['pid'])]['quarantined_threads']))
    if not (area / 'STOP').exists():
        raise LifecycleError('Historical STOP must remain latched')
    for record in paused['processes']:
        thread_policy.validate(record, policy, paused=True)
    ledger = read_json(area / 'REGIONS.json')
    unresolved = [row['id'] for row in ledger['cells'] if row['status'] != 'UNSAT_DRAT_VERIFIED']
    if unresolved != [0, 1, 3, 7, 15, 31, 63, 127, 255]:
        raise LifecycleError('Unexpected unresolved domain')
    if any(row.get('pending_proof') for row in ledger['cells']):
        raise LifecycleError('Unexpected pending proof requires reconciliation')
    return dict(status='PLAN_ONLY', contexts=contexts, original_processes=paused['processes'],
                historical_pause_sha256=sha(area / 'OWNER_PAUSE.json'),
                historical_regions_sha256=sha(area / 'REGIONS.json'), unresolved_ids=unresolved,
                proof_closed_regions=247, cold_ids=[1, 3, 15, 31, 63],
                legacy_control_policy='PERMANENTLY_SUSPENDED_STOP_LATCHED',
                deadline_policy='FRESH_MONOTONIC_ACTIVE_TURNS_NO_OVERALL_CUTOFF',
                verdict='UNKNOWN', whole_stratum_certified=False)


def load_policy(control):
    policy = read_json(Path(control) / 'THREAD_POLICY.json')
    if policy.get('status') != 'CLASSIFIED_HELPERS_REMAIN_SUSPENDED':
        raise LifecycleError('Thread policy has not passed classification')
    return policy


def watcher(control, stale_seconds=10):
    row = read_json(Path(control) / 'WATCHER.json')
    if row.get('status') != 'WATCHING' or not row.get('ready'):
        raise LifecycleError('Independent SAT supervisor is not ready: ' + str(row.get('status')))
    checked(row)
    if time.time() - row['updated_epoch'] > stale_seconds:
        raise LifecycleError('Independent SAT supervisor heartbeat is stale')
    if row.get('source_sha256') != sha(ROOT / 'scripts/s036_sat_supervisor.py'):
        raise LifecycleError('Independent SAT supervisor source mismatch')
    return {'pid': row['pid'], 'start_ticks': row['start_ticks']}


def published_acceptance(control):
    row = read_json(Path(control) / 'ACCEPTANCE.json')
    if row.get('status') != 'PASS' or row.get('source_sha256') != sources():
        raise LifecycleError('Published S036 lifecycle/SAT acceptance is absent or stale')
    if row.get('thread_policy_sha256') != sha(Path(control) / 'THREAD_POLICY.json'):
        raise LifecycleError('Thread quarantine policy differs from published acceptance')
    commit = row['published_commit']
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'],
                                     cwd=ROOT, text=True, timeout=60).split()[0]
    if remote != commit or subprocess.run(['git', 'merge-base', '--is-ancestor', commit, head],
                                          cwd=ROOT).returncode:
        raise LifecycleError('Acceptance commit is not verified remote main contained in HEAD')
    committed = subprocess.check_output(['git', 'show', f'{commit}:validation/S036/THREAD_POLICY.json'], cwd=ROOT)
    if hashlib.sha256(committed).hexdigest() != row['thread_policy_sha256']:
        raise LifecycleError('Thread policy was not published with acceptance sources')
    for name, digest in sources().items():
        data = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=ROOT)
        if hashlib.sha256(data).hexdigest() != digest:
            raise LifecycleError('Lifecycle/SAT source differs from published bytes: ' + name)
    return row


def stop_reason(area, control):
    """SAT outranks STOP; STOP carries the supervisor's explicit underlying cause."""
    if (Path(control) / 'SAT_ALERT.json').exists() or (Path(area) / 'SAT_ALERT.json').exists():
        return 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
    if (Path(control) / 'STOP').exists():
        guard = {}
        try:
            guard = read_json(Path(control) / 'GUARD_PAUSE.json') if (Path(control) / 'GUARD_PAUSE.json').exists() else {}
        except Exception:
            pass
        if (Path(control) / 'WATCHER_FAILURE.json').exists():
            return 'SUPERVISOR_PAUSE:' + str(guard.get('reason', 'WATCHER_FAILURE'))
        if guard.get('reason'):
            return 'SUPERVISOR_PAUSE:' + guard['reason']
        return 'OWNER_OR_CONTROLLER_STOP'
    if (Path(control) / 'WATCHER_FAILURE.json').exists():
        return 'SUPERVISOR_FAILURE_RECORDED'
    try:
        watcher(control)
    except LifecycleError as exc:
        return 'SUPERVISOR_UNAVAILABLE:' + str(exc)
    if not (Path(area) / 'STOP').exists():
        return 'HISTORICAL_STOP_UNLATCHED_UNSAFE'
    return None


def cold_identity(control):
    try:
        row = read_json(Path(control) / 'COLD_SLOT.json') if (Path(control) / 'COLD_SLOT.json').exists() else {}
    except Exception:
        return None
    if row.get('state') == 'RUNNING' and row.get('worker'):
        try:
            checked(row['worker'])
            return row['worker']
        except LifecycleError:
            return None
    return None


def resource_reason(area, control, contexts, registry, cache):
    """Return (hard_reason, soft_reason, sample). Hard reasons halt; soft throttles."""
    cold = cold_identity(control)
    sample = sample_identities(registry + ([cold] if cold else []))
    available = psutil.virtual_memory().available
    sample.update(available=available, cold_slot=cold)
    if sample['private'] > LIMITS['aggregate_private']:
        return 'SAFETY_AGGREGATE_PRIVATE_CAP', None, sample
    if available < LIMITS['available_floor']:
        return 'SAFETY_AVAILABLE_RAM_FLOOR', None, sample
    if sample['private'] > LIMITS['soft_private']:
        return 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE', None, sample
    if shutil.disk_usage(ROOT).free < LIMITS['disk_reserve']:
        return 'SAFETY_DISK_RESERVE', None, sample
    for context in contexts:
        if checked(context['worker']).memory_info().private > LIMITS['per_worker_private']:
            return 'SAFETY_PER_WORKER_PRIVATE_CAP', None, sample
    now = time.monotonic()
    if now - cache.get('sampled', -1e9) >= 60:
        cache.update(sampled=now, campaign_bytes=directory_bytes(area),
                     session_bytes=directory_bytes(ROOT / 'artifacts/tmp/S035') + directory_bytes(ROOT / 'artifacts/tmp/S036'))
        cache['proof_cap'] = any(p.stat().st_size > LIMITS['raw_proof_attempt']
                                 for root in (area / 'attempts', ROOT / 'artifacts/tmp/S036/cold')
                                 if root.exists() for p in root.rglob('proof.drat'))
    if cache['campaign_bytes'] > LIMITS['campaign_bytes']:
        return 'SAFETY_CAMPAIGN_DISK_CAP', None, sample
    if cache['session_bytes'] > LIMITS['session_bytes']:
        return 'SAFETY_S035_S036_DISK_CAP', None, sample
    if cache['proof_cap']:
        return 'SAFETY_RAW_PROOF_ATTEMPT_CAP', None, sample
    if available < LIMITS['soft_available']:
        return None, 'SOFT_AVAILABLE_RAM_THROTTLE', sample
    return None, None, sample


def halt_all(control, adoption, reason):
    try:
        cold = read_json(Path(control) / 'COLD_SLOT.json') if (Path(control) / 'COLD_SLOT.json').exists() else {}
        if cold.get('stop_file'):
            Path(cold['stop_file']).touch()
    except Exception:
        pass
    return s035.halt_all(control, adoption, reason)


def run(area, control, pilot_seconds=None):
    if pilot_seconds is not None and not 0 < pilot_seconds <= 120:
        raise LifecycleError('Pilot must be between zero and 120 seconds')
    area, control = Path(area).resolve(), Path(control).resolve()
    if control != CONTROL.resolve() and not os.environ.get('EMP_S036_FIXTURE'):
        raise LifecycleError('Scientific adoption uses the registered S036 control directory')
    published_acceptance(control)
    adoption = plan(area, control)
    contexts = adoption['contexts']
    s035.input_gates(area, contexts)
    supervisor = watcher(control)
    if stop_reason(area, control):
        raise LifecycleError('A preservation stop/SAT alert is latched: ' + stop_reason(area, control))
    handles = []
    reason = 'CONTROLLER_EXCEPTION'
    active_started = {}
    turn_start = {}
    cache = {}
    controller = identity(os.getpid())
    registry = [*adoption['original_processes'], controller, supervisor]
    adoption.update(status='PREPARING', controller=controller, watcher=supervisor, created_epoch=time.time(),
                    epoch=time.time(), source_sha256=sources(), control_directory=str(control), lease_seconds=10,
                    session='S036', limits=LIMITS,
                    adoption_mode='SAME_PROCESS_NO_NEW_WORKERS_NO_PROOFS_NO_COLD_ADMISSIONS')
    throttle = dict(active=False, clear_since=None, events=0)
    errors = []
    with locked(control / 'CONTROLLER.lock', blocking=False):
        try:
            for context in contexts:
                handles.append(ProcessHandle(context['worker']))
                context['threads'] = thread_counts(context['worker'])
            hard, soft, initial_sample = resource_reason(area, control, contexts, registry, cache)
            if hard or soft:
                raise LifecycleError(hard or soft)
            adoption.update(status='ARMED', updated_epoch=time.time(), sample=initial_sample)
            atomic_json(control / 'ADOPTION.json', adoption)
            started = time.monotonic()
            end = started + pilot_seconds if pilot_seconds else float('inf')
            quantum = min(600, pilot_seconds / 4) if pilot_seconds else 600
            inhibited = False

            def request_pause(signum, frame):
                (control / 'STOP').touch()
            previous = {sig: signal.signal(sig, request_pause) for sig in (signal.SIGINT, signal.SIGTERM)}

            def end_turn(context, now, why):
                key = context['cell']
                with locked(control / 'MUTATION.lock'):
                    context['threads'] = pause_identity(context['worker'])
                context['active_seconds'] += now - active_started.pop(key)
                context['state'] = 'PAUSED'
                metrics = dict(cell=key, turn=context['turns'], why=why,
                               wall_seconds=now - turn_start.pop(key), **process_metrics(context['worker']),
                               **counters(context['directory']))
                start_row = context.pop('turn_start_metrics', {})
                for name in ('cpu_seconds', 'conflicts', 'decisions', 'propagations', 'cuts', 'lemma_bytes'):
                    if name in metrics and name in start_row:
                        metrics['delta_' + name] = metrics[name] - start_row[name]
                journal(control / 'JOURNAL.jsonl', 'fair_turn_paused', cell=key, worker=context['worker'],
                        active_seconds=context['active_seconds'], why=why)
                journal(control / 'METRICS.jsonl', 'turn_metrics', **metrics)
            try:
                inhibit_sleep(True)
                inhibited = True
                while True:
                    reason = s035.terminal(control, contexts, handles) or stop_reason(area, control)
                    if reason:
                        break
                    native_pids = {row['worker']['pid'] for row in contexts}
                    policy = load_policy(control)
                    for record in adoption['original_processes']:
                        thread_policy.validate(record, policy, paused=record['pid'] not in native_pids)
                    now = time.monotonic()
                    for context in contexts:
                        if context['cell'] in active_started and now - active_started[context['cell']] >= quantum:
                            end_turn(context, now, 'FAIR_TURN_QUANTUM')
                    if now >= end:
                        reason = 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED'
                        break
                    hard, soft, sample = resource_reason(area, control, contexts, registry, cache)
                    if hard:
                        reason = hard
                        break
                    if soft:
                        if not throttle['active']:
                            throttle.update(active=True, events=throttle['events'] + 1, since=time.time(), reason=soft)
                            for context in contexts:
                                if context['cell'] in active_started:
                                    end_turn(context, time.monotonic(), soft)
                            journal(control / 'JOURNAL.jsonl', 'soft_throttle_started', reason=soft,
                                    available=sample['available'], private=sample['private'])
                        throttle['clear_since'] = None
                    elif throttle['active']:
                        if sample['available'] >= LIMITS['soft_available'] + LIMITS['throttle_clear_margin']:
                            throttle['clear_since'] = throttle['clear_since'] or time.monotonic()
                            if time.monotonic() - throttle['clear_since'] >= LIMITS['throttle_clear_seconds']:
                                throttle.update(active=False, clear_since=None)
                                journal(control / 'JOURNAL.jsonl', 'soft_throttle_cleared',
                                        available=sample['available'], private=sample['private'])
                        else:
                            throttle['clear_since'] = None
                    if not throttle['active']:
                        choices = sorted((row for row in contexts if row['cell'] not in active_started),
                                         key=lambda row: (row['active_seconds'], row['turns'], row['cell']))
                        for context in choices[:max(0, 2 - len(active_started))]:
                            with locked(control / 'MUTATION.lock'):
                                if stop_reason(area, control):
                                    break
                                context['turn_start_metrics'] = dict(**process_metrics(context['worker']),
                                                                     **counters(context['directory']))
                                resume_identity(context['worker'], context['threads'], context['quarantined_threads'])
                                if stop_reason(area, control):
                                    context['threads'] = pause_identity(context['worker'])
                                    break
                            active_started[context['cell']] = turn_start[context['cell']] = time.monotonic()
                            context.update(state='RUNNING', turns=context['turns'] + 1)
                            journal(control / 'JOURNAL.jsonl', 'same_identity_resumed', cell=context['cell'],
                                    worker=context['worker'], turn=context['turns'])
                    status = 'THROTTLED' if throttle['active'] else 'RUNNING'
                    adoption.update(status=status, updated_epoch=time.time(), sample=sample, resource_cache=cache,
                                    executing_cells=sorted(active_started), throttle=throttle)
                    atomic_json(control / 'ADOPTION.json', adoption)
                    atomic_json(control / 'CONTROLLER.json', dict(status=status, **controller,
                                updated_epoch=time.time(), executing_cells=sorted(active_started), lease_seconds=10,
                                historical_stop_latched=True, verdict='UNKNOWN', throttle=throttle))
                    time.sleep(.2)
            finally:
                if inhibited:
                    inhibit_sleep(False)
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
        except BaseException as exc:
            reason = 'CONTROLLER_EXCEPTION_' + repr(exc)
            raise
        finally:
            try:
                detected = s035.terminal(control, contexts, handles)
                if detected:
                    reason = detected
            finally:
                for handle in handles:
                    try:
                        if handle.poll() == 10:
                            reason = 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
                    except Exception:
                        pass
                if (control / 'SAT_ALERT.json').exists() or (area / 'SAT_ALERT.json').exists():
                    reason = 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
                now = time.monotonic()
                for context in contexts:
                    if context['cell'] in active_started:
                        context['active_seconds'] += now - active_started[context['cell']]
                try:
                    errors = halt_all(control, adoption, reason)
                    atomic_json(control / 'CONTROLLER.json', dict(status='PAUSED', reason=reason, **controller,
                                updated_epoch=time.time(), pause_errors=errors, verdict='UNKNOWN'))
                finally:
                    for handle in handles:
                        handle.close()
    print(json.dumps(dict(status='PAUSED', reason=reason, pause_errors=errors,
                          original_stop_latched=(area / 'STOP').exists(), no_region_promoted=True)))


def rearm_pilot(area, control):
    """Archive a successful bounded pilot's S036 controls; never resume OS work."""
    area, control = Path(area).resolve(), Path(control).resolve()
    published_acceptance(control)
    if (area / 'SAT_ALERT.json').exists() or (control / 'SAT_ALERT.json').exists():
        raise LifecycleError('SAT discovery requires review; pilot rearm forbidden')
    previous = read_json(control / 'ADOPTION.json')
    if (previous.get('status') != 'PAUSED' or previous.get('pause_errors') or
            previous.get('reason') != 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED'):
        raise LifecycleError('Only a successfully paused bounded pilot may be rearmed')
    if (control / 'WATCHER_FAILURE.json').exists():
        raise LifecycleError('A supervisor failure is recorded; manual review required')
    planned = plan(area, control)
    if {row['cell']: row['worker'] for row in planned['contexts']} != {
            row['cell']: row['worker'] for row in previous['contexts']}:
        raise LifecycleError('Pilot/frozen process identities differ')
    for record in (previous['controller'], previous['watcher']):
        try:
            checked(record)
        except LifecycleError:
            continue
        raise LifecycleError('Previous adoption controller/supervisor has not exited')
    if not (control / 'STOP').exists():
        raise LifecycleError("Successful pilot's S036 STOP is missing")
    with locked(control / 'CONTROLLER.lock', blocking=False):
        with locked(control / 'MUTATION.lock', blocking=False):
            policy = load_policy(control)
            for context in previous['contexts']:
                actual = thread_policy.validate(context['worker'], policy, paused=True)
                old_ids = thread_policy.keys(context['threads'])
                retained = [r for r in actual if (r['tid'], r['created_ticks']) in old_ids]
                if sorted(retained, key=lambda r: r['tid']) != sorted(context['threads'], key=lambda r: r['tid']):
                    raise LifecycleError('Pilot suspended thread counts changed')
            history = control / 'history' / (str(time.time_ns()) + '-' + uuid.uuid4().hex[:8])
            history.mkdir(parents=True)
            moved = []
            retained = {'ACCEPTANCE.json', 'JOURNAL.jsonl', 'METRICS.jsonl', 'CONTROLLER.lock', 'MUTATION.lock',
                        'WATCHER.lock', 'history', 'STOP', 'THREAD_POLICY.json', 'COLD_SLOT.json', 'COLD_TERMINAL.json'}
            for path in list(control.iterdir()):
                if path.name in retained:
                    continue
                target = history / path.name
                if not path.resolve().is_relative_to(control) or not target.resolve().is_relative_to(history):
                    raise LifecycleError('Unexpected rearm path')
                path.rename(target)
                moved.append(path.name)
            (control / 'STOP').rename(history / 'STOP')
            moved.append('STOP')
            atomic_json(history / 'REARM.json', dict(status='SUCCESSFUL_PILOT_ARCHIVED_NO_WORK_RESUMED',
                        moved=moved, previous_controller=previous['controller'],
                        previous_watcher=previous['watcher'], original_stop_latched=True))
            journal(control / 'JOURNAL.jsonl', 'successful_pilot_rearmed', history=str(history),
                    original_stop_latched=True, no_process_resumed=True)
    print(json.dumps(dict(status='REARMED_NO_PROCESS_RESUMED', history=str(history))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'run', 'pause', 'status', 'rearm-pilot'))
    parser.add_argument('--directory', type=Path, default=AREA)
    parser.add_argument('--control-directory', type=Path, default=CONTROL)
    parser.add_argument('--pilot-seconds', type=float)
    args = parser.parse_args()
    area, control = args.directory.resolve(), args.control_directory.resolve()
    if args.action == 'plan':
        print(json.dumps(plan(area, control), indent=1))
    elif args.action == 'status':
        print(json.dumps(read_json(control / 'ADOPTION.json'), indent=1))
    elif args.action == 'pause':
        (control / 'STOP').touch()
        print('Preservation pause requested; native identities will be suspended.')
    elif args.action == 'rearm-pilot':
        rearm_pilot(area, control)
    else:
        run(area, control, args.pilot_seconds)


if __name__ == '__main__':
    main()
