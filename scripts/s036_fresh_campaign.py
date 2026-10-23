"""S036 fresh resident campaign: semantic recovery after loss of the S035 RAM identities.

The original S035 processes ended when the app that owned their process tree
closed (validation/S036/identity-loss). Their private CDCL is unrecoverable.
This controller starts NEW native processes (S036 diagnostic native, baseline
settings: congruence disabled, CaDiCaL default random walk) for the resident
regions 0, 7, 127, 255 from exact recipes: base + S032 seed + every S035
ledger-accepted audited geometric source + that region's S036 audited blocks
(including the independently audited unshared tails of the lost contexts).

Residents are admitted one at a time through a measured memory gate, then kept
in RAM: two execute in fair 600 s turns, the rest are suspended with their
learning retained. Nothing is evicted, duplicated or force-terminated. SAT or
exit 10 outranks everything; native UNSAT halts for a fresh standalone DRAT and
independent check and never closes a region here. Launch this controller (and
the supervisor) outside any application job object (scripts/s036_launch.py --wmi).
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s035_windows import atomic_json, read_json, journal, locked, inhibit_sleep, process_identity  # noqa: E402
from s035_preserved_lifecycle import (LifecycleError, identity, checked, pause_identity,  # noqa: E402
                                      resume_identity, ProcessHandle, sample_identities)
import s035_preserved_campaign as s035  # noqa: E402
import s036_resident_controller as ctl  # noqa: E402

AREA = ROOT / 'artifacts/tmp/S035/campaign'
CONTROL = ROOT / 'artifacts/tmp/S036/control'
RESIDENT = ROOT / 'artifacts/tmp/S036/resident'
NATIVE = ROOT / 'artifacts/tmp/S036/native/bipsat_s032.exe'
REGIONS = (0, 7, 127, 255)
SOURCES = ('tools/s036_sat_scan.py', 'scripts/s036_sat_supervisor.py', 'scripts/s036_resident_controller.py',
           'scripts/s036_fresh_campaign.py', 'tools/s035_preserved_lifecycle.py', 'scripts/s035_preserved_campaign.py',
           'tools/s035_sat_validation.py', 'tools/s035_windows.py')
GiB = 1024 ** 3
ADMISSION = dict(reserve_bytes=int(1.5 * GiB), available_after_min=int(2.75 * GiB), loading_seconds=120)
# Owner-approved amendment 2 (validation/S036/COLD_CAPACITY_PLAN.json): the cold slot may
# occupy the band between the 5 GiB resident target and this ceiling; the 6 GiB aggregate
# hard cap is unchanged and residents alone remain bound by the 5 GiB target.
COLD_CEILING = int(5.75 * GiB)


def resource(area, control, contexts, registry, cache):
    """Resident resource gate with the registered cold band.

    If the 5 GiB target is crossed only because of a live cold solver, and the total
    stays within COLD_CEILING, every other check is re-evaluated with the target lifted
    to the ceiling. Above the ceiling, or if residents alone exceed 5 GiB, the target
    reason is returned so the caller asks the cold slot to yield (or halts).
    """
    hard, soft, sample = ctl.resource_reason(area, control, contexts, registry, cache)
    if hard != 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE' or not sample.get('cold_slot'):
        return hard, soft, sample
    try:
        cold_private = psutil.Process(sample['cold_slot']['pid']).memory_info().private
    except psutil.Error:
        cold_private = 0
    if sample['private'] - cold_private > ctl.LIMITS['soft_private'] or sample['private'] > COLD_CEILING:
        return hard, soft, sample
    saved = ctl.LIMITS
    ctl.LIMITS = dict(saved, soft_private=COLD_CEILING)
    try:
        hard, soft, sample = ctl.resource_reason(area, control, contexts, registry, cache)
    finally:
        ctl.LIMITS = saved
    sample['cold_band'] = True
    return hard, soft, sample


def sources():
    return {name: ctl.sha(ROOT / name) for name in SOURCES}


def published_acceptance(control):
    row = read_json(Path(control) / 'ACCEPTANCE_FRESH.json')
    if row.get('status') != 'PASS' or row.get('source_sha256') != sources():
        raise LifecycleError('Published S036 fresh-campaign acceptance is absent or stale')
    commit = row['published_commit']
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'],
                                     cwd=ROOT, text=True, timeout=60).split()[0]
    if remote != commit or subprocess.run(['git', 'merge-base', '--is-ancestor', commit, head], cwd=ROOT).returncode:
        raise LifecycleError('Fresh acceptance commit is not verified remote main contained in HEAD')
    for name, digest in sources().items():
        data = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=ROOT)
        if hashlib.sha256(data).hexdigest() != digest:
            raise LifecycleError('Fresh-campaign source differs from published bytes: ' + name)
    return row


def recipe_for(region):
    """Exact audited recipe; identical rule to the cold slot (S035 ledgers are read only)."""
    import s036_cold_diagnostic as cold
    return cold.recipe_for(region)


def launch(region, control, fixture=None):
    """Materialise the exact input and start one native; returns a context."""
    from s035_engine import materialise
    token = uuid.uuid4().hex
    directory = (fixture or {}).get('directory') or RESIDENT / f'region-{region:04d}' / token
    directory.mkdir(parents=True, exist_ok=True)
    if fixture:
        source, meta = fixture['input'], dict(fixture['meta'])
        if source != directory / 'input.inst':
            os.link(source, directory / 'input.inst')
    else:
        cfg, value = recipe_for(region)
        digest = materialise(directory / 'input.inst', value, native=True)
        meta = dict(recipe=copy.deepcopy(value), input_sha256=digest, native=str(NATIVE), native_sha256=ctl.sha(NATIVE),
                    source_sha256=cfg['source_sha256'], resident=True, session='S036', region=region,
                    settings='baseline: congruence disabled, CaDiCaL default walk, no S036 options')
    atomic_json(directory / 'INPUT.json', meta)
    stop = directory / 'COOPERATIVE_STOP'
    env = os.environ.copy()
    env.pop('EMP_S035_DISABLE_WALK', None); env.pop('EMP_S036_CADICAL_OPTIONS', None)
    env['EMP_S035_DISABLE_CONGRUENCE'] = '1'
    env['EMP_S036_STOP_FILE'] = str(stop)
    args = [str((fixture or {}).get('native', NATIVE)), str(directory / 'input.inst'), '--timeout', 'inf',
            '--lemmas', str(directory / 'new-cuts.lem')]
    with (directory / 'native.log').open('w') as log:
        p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
    worker = dict(pid=p.pid, start_ticks=process_identity(p.pid))
    context = dict(cell=region, worker=worker, directory=str(directory), input_sha256=meta['input_sha256'],
                   native_sha256=meta['native_sha256'], turns=0, active_seconds=0.0, state='LOADING',
                   launched_epoch=time.time(), stop_file=str(stop), sources=len(meta['recipe']['sources'])
                   if 'recipe' in meta else None)
    journal(control / 'JOURNAL.jsonl', 'fresh_resident_launched', cell=region, worker=worker,
            directory=str(directory), input_sha256=meta['input_sha256'])
    return context, p


def admission(control, contexts, registry, active):
    """Measured gate for one more resident; loads are staggered."""
    if any(time.time() - c['launched_epoch'] < ADMISSION['loading_seconds'] for c in contexts):
        return 'PREVIOUS_RESIDENT_STILL_LOADING'
    if len(active) >= 2:
        return 'NO_FREE_ACTIVE_SLOT'
    cold = ctl.cold_identity(control)
    sample = sample_identities(registry + [c['worker'] for c in contexts] + ([cold] if cold else []))
    if sample['private'] + ADMISSION['reserve_bytes'] > ctl.LIMITS['soft_private']:
        return f"AGGREGATE_PRIVATE {sample['private']}"
    if psutil.virtual_memory().available - ADMISSION['reserve_bytes'] < ADMISSION['available_after_min']:
        return f"AVAILABLE_RAM {psutil.virtual_memory().available}"
    return None


def terminal(control, contexts, handles):
    rows = []
    for context in contexts:
        code = handles[context['cell']].poll()
        if code is not None:
            rows.append(dict(cell=context['cell'], returncode=code, directory=context['directory'],
                             worker=context['worker'], input_sha256=context['input_sha256'],
                             native_sha256=context['native_sha256'],
                             status={10: 'SAT_SIGNAL_REQUIRES_PROMINENT_REVIEW',
                                     20: 'NATIVE_UNSAT_PENDING_FRESH_DRAT_AND_INDEPENDENT_CHECK'}.get(
                                         code, 'NATIVE_RETURN_REQUIRES_REVIEW')))
    if not rows:
        return None
    value = dict(status='NATIVE_RETURN_REQUIRES_REVIEW', results=rows, updated_epoch=time.time(), no_region_promoted=True)
    atomic_json(control / 'TERMINAL.json', value)
    if any(r['returncode'] == 10 for r in rows):
        atomic_json(control / 'SAT_ALERT.json', dict(**value, ordinary_UNKNOWN_forbidden=True,
                    review_status='SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'))
        return 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
    return 'NATIVE_RETURN_PRESERVED_PENDING_PROOF_OR_FAILURE_REVIEW'


RESUMABLE = ('SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE', 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED',
             'SOFT_AVAILABLE_RAM_THROTTLE', 'SUPERVISOR_PAUSE:OWNER_OR_CONTROLLER_STOP', 'OWNER_OR_CONTROLLER_STOP')
KEEP_ON_ARCHIVE = {'history', 'CONTROLLER.lock', 'MUTATION.lock', 'WATCHER.lock', 'ACCEPTANCE_FRESH.json',
                   'COLD_SLOT.json'}


def prepare_resume(control):
    """Operator step: verify a cleanly paused fresh campaign and archive its controls.

    Never resumes a process. Refuses after SAT, native return, supervisor failure,
    pause errors, a live previous controller/supervisor or any resident that is not
    alive with every thread suspended. Writes RESUME_PLAN.json for `run --resume`.
    """
    control = Path(control).resolve()
    if (control / 'SAT_ALERT.json').exists() or (control / 'TERMINAL.json').exists():
        raise LifecycleError('SAT or native return requires review; no resume')
    if (control / 'WATCHER_FAILURE.json').exists():
        raise LifecycleError('Supervisor failure recorded; manual review required')
    previous = read_json(control / 'ADOPTION.json')
    if (previous.get('mode') != 'FRESH_SEMANTIC_RECOVERY_RESIDENTS' or previous.get('status') != 'PAUSED'
            or previous.get('pause_errors') or previous.get('exited_cells') or previous.get('reason') not in RESUMABLE):
        raise LifecycleError('Previous fresh campaign is not cleanly paused for a resumable reason')
    for record in (previous['controller'], previous['watcher']):
        try:
            checked(record)
        except LifecycleError:
            continue
        raise LifecycleError('Previous controller/supervisor has not exited')
    for context in previous['contexts']:
        rows = life_counts(context['worker'])
        context.update(threads=rows, state='PAUSED')
    history = control / 'history' / (str(time.time_ns()) + '-fresh-resume-' + uuid.uuid4().hex[:6])
    history.mkdir(parents=True)
    moved = []
    for path in list(control.iterdir()):
        if path.name in KEEP_ON_ARCHIVE:
            continue
        path.rename(history / path.name); moved.append(path.name)
    plan = dict(status='RESUME_PLAN_VERIFIED_NO_PROCESS_RESUMED', previous_reason=previous['reason'],
                history=str(history), moved=moved, contexts=previous['contexts'],
                queued_regions=previous.get('queued_regions', []), epoch=time.time())
    atomic_json(control / 'RESUME_PLAN.json', plan)
    journal(control / 'JOURNAL.jsonl', 'fresh_resume_prepared', history=str(history),
            cells=[c['cell'] for c in previous['contexts']], no_process_resumed=True)
    return plan


def life_counts(worker):
    """Suspend every current thread of OUR resident (idempotent) and return exact counts.

    Suspended processes can acquire idle OS thread-pool workers (as in S035); for
    processes this campaign launched they are suspended with the rest, never left running.
    Raises if the process no longer survives.
    """
    return pause_identity(worker)


def run(area, control, regions=REGIONS, pilot_seconds=None, fixture=None, resume=False):
    area, control = Path(area).resolve(), Path(control).resolve()
    if fixture is None:
        if control != CONTROL.resolve():
            raise LifecycleError('Fresh campaign uses the registered S036 control directory')
        published_acceptance(control)
    if resume:
        plan = read_json(control / 'RESUME_PLAN.json')
        if plan.get('status') != 'RESUME_PLAN_VERIFIED_NO_PROCESS_RESUMED' or (control / 'ADOPTION.json').exists():
            raise LifecycleError('Resume requires a verified RESUME_PLAN and archived previous adoption')
    elif (control / 'ADOPTION.json').exists():
        raise LifecycleError('Archive the previous S036 control state before a fresh campaign')
    supervisor = ctl.watcher(control)
    reason = ctl.stop_reason(area, control)
    if reason:
        raise LifecycleError('A preservation stop/SAT alert is latched: ' + reason)
    controller = identity(os.getpid())
    registry = [controller, supervisor]
    contexts, handles, queue = [], {}, list(regions)
    if resume:
        queue = list(plan['queued_regions'])
        for context in plan['contexts']:
            context.update(threads=life_counts(context['worker']), state='PAUSED')
            context.pop('turn_start_metrics', None)
            handles[context['cell']] = ProcessHandle(context['worker'])
            contexts.append(context)
        (control / 'RESUME_PLAN.json').rename(control / f'RESUME_PLAN-used-{time.time_ns()}.json')
        journal(control / 'JOURNAL.jsonl', 'fresh_resume_adopted', cells=[c['cell'] for c in contexts],
                same_identities=True)
    cold_yield_since = None
    active_started, turn_start, cache = {}, {}, {}
    throttle = dict(active=False, clear_since=None, events=0)
    adoption = dict(status='PREPARING', session='S036', mode='FRESH_SEMANTIC_RECOVERY_RESIDENTS', controller=controller,
                    watcher=supervisor, created_epoch=time.time(), epoch=time.time(), contexts=contexts,
                    source_sha256=sources(), lease_seconds=10, limits=ctl.LIMITS, admission=ADMISSION,
                    queued_regions=queue, private_cdcl_of_lost_contexts='UNRECOVERABLE_NOT_CLAIMED')
    atomic_json(control / 'ADOPTION.json', adoption)
    errors = []
    reason = 'CONTROLLER_EXCEPTION'
    started = time.monotonic()
    end = started + pilot_seconds if pilot_seconds else float('inf')
    quantum = min(600, pilot_seconds / 4) if pilot_seconds else 600
    with locked(control / 'CONTROLLER.lock', blocking=False):
        previous = {sig: signal.signal(sig, lambda s, f: (control / 'STOP').touch())
                    for sig in (signal.SIGINT, signal.SIGTERM)}
        inhibited = False

        def end_turn(context, now, why):
            key = context['cell']
            with locked(control / 'MUTATION.lock'):
                context['threads'] = pause_identity(context['worker'])
            context['active_seconds'] += now - active_started.pop(key)
            context['state'] = 'PAUSED'
            metrics = dict(cell=key, turn=context['turns'], why=why, wall_seconds=now - turn_start.pop(key),
                           **ctl.process_metrics(context['worker']), **ctl.counters(context['directory']))
            start_row = context.pop('turn_start_metrics', {})
            for name in ('cpu_seconds', 'conflicts', 'decisions', 'propagations', 'cuts', 'lemma_bytes'):
                if name in metrics and name in start_row:
                    metrics['delta_' + name] = metrics[name] - start_row[name]
            journal(control / 'JOURNAL.jsonl', 'fair_turn_paused', cell=key, worker=context['worker'],
                    active_seconds=context['active_seconds'], why=why)
            journal(control / 'METRICS.jsonl', 'turn_metrics', **metrics)
        try:
            inhibit_sleep(True); inhibited = True
            while True:
                reason = terminal(control, contexts, handles) or ctl.stop_reason(area, control)
                if reason:
                    break
                now = time.monotonic()
                for context in contexts:
                    if context['cell'] in active_started and now - active_started[context['cell']] >= quantum:
                        end_turn(context, now, 'FAIR_TURN_QUANTUM')
                if now >= end:
                    reason = 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED'
                    break
                hard, soft, sample = resource(area, control, contexts,
                                              registry + [c['worker'] for c in contexts], cache)
                if hard == 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE' and sample.get('cold_slot'):
                    # The cold slot always yields first: request its cooperative stop
                    # and give it up to 60 s before treating the target as binding.
                    cold_yield_since = cold_yield_since or time.monotonic()
                    if time.monotonic() - cold_yield_since < 60:
                        try:
                            Path(read_json(control / 'COLD_SLOT.json')['stop_file']).touch()
                        except Exception as exc:
                            journal(control / 'JOURNAL.jsonl', 'cold_yield_request_failed', error=repr(exc))
                        if not adoption.get('cold_yield_requested_epoch') or \
                                time.time() - adoption['cold_yield_requested_epoch'] > 60:
                            adoption['cold_yield_requested_epoch'] = time.time()
                            journal(control / 'JOURNAL.jsonl', 'cold_slot_yield_requested', private=sample['private'])
                        hard = None
                elif not sample.get('cold_slot'):
                    cold_yield_since = None
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
                    if sample['available'] >= ctl.LIMITS['soft_available'] + ctl.LIMITS['throttle_clear_margin']:
                        throttle['clear_since'] = throttle['clear_since'] or time.monotonic()
                        if time.monotonic() - throttle['clear_since'] >= ctl.LIMITS['throttle_clear_seconds']:
                            throttle.update(active=False, clear_since=None)
                            journal(control / 'JOURNAL.jsonl', 'soft_throttle_cleared',
                                    available=sample['available'], private=sample['private'])
                    else:
                        throttle['clear_since'] = None
                if not throttle['active']:
                    # Admit the next queued resident only through the measured gate.
                    if queue:
                        why = admission(control, contexts, registry, active_started)
                        adoption['admission_blocked'] = why
                        if why is None:
                            with locked(control / 'MUTATION.lock'):
                                if ctl.stop_reason(area, control):
                                    continue
                                region = queue.pop(0)
                                context, process = launch(region, control, (fixture or {}).get(region))
                            handles[region] = ProcessHandle(context['worker'])
                            contexts.append(context)
                            context.update(state='RUNNING', turns=1, turn_start_metrics={})
                            active_started[region] = turn_start[region] = time.monotonic()
                            atomic_json(control / 'ADOPTION.json', adoption)
                    choices = sorted((c for c in contexts if c['cell'] not in active_started),
                                     key=lambda c: (c['active_seconds'], c['turns'], c['cell']))
                    for context in choices[:max(0, 2 - len(active_started))]:
                        with locked(control / 'MUTATION.lock'):
                            if ctl.stop_reason(area, control):
                                break
                            context['turn_start_metrics'] = dict(**ctl.process_metrics(context['worker']),
                                                                 **ctl.counters(context['directory']))
                            # Own processes: re-inventory (idempotent) so threads the
                            # process created itself are resumed with exact counts.
                            rows = pause_identity(context['worker'])
                            resume_identity(context['worker'], rows, [])
                            if ctl.stop_reason(area, control):
                                context['threads'] = pause_identity(context['worker'])
                                break
                        active_started[context['cell']] = turn_start[context['cell']] = time.monotonic()
                        context.update(state='RUNNING', turns=context['turns'] + 1)
                        journal(control / 'JOURNAL.jsonl', 'same_identity_resumed', cell=context['cell'],
                                worker=context['worker'], turn=context['turns'])
                status = 'THROTTLED' if throttle['active'] else 'RUNNING'
                adoption.update(status=status, updated_epoch=time.time(), sample=sample, resource_cache=cache,
                                executing_cells=sorted(active_started), throttle=throttle, queued_regions=queue)
                atomic_json(control / 'ADOPTION.json', adoption)
                atomic_json(control / 'CONTROLLER.json', dict(status=status, **controller, updated_epoch=time.time(),
                            executing_cells=sorted(active_started), lease_seconds=10, verdict='UNKNOWN',
                            throttle=throttle, mode='FRESH_SEMANTIC_RECOVERY_RESIDENTS'))
                time.sleep(.2)
        except BaseException as exc:
            reason = 'CONTROLLER_EXCEPTION_' + repr(exc)
            raise
        finally:
            try:
                if inhibited:
                    inhibit_sleep(False)
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
                detected = terminal(control, contexts, handles) if contexts else None
                if detected:
                    reason = detected
            finally:
                if (control / 'SAT_ALERT.json').exists() or (area / 'SAT_ALERT.json').exists():
                    reason = 'SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW'
                now = time.monotonic()
                for context in contexts:
                    if context['cell'] in active_started:
                        context['active_seconds'] += now - active_started[context['cell']]
                exited = {c['cell'] for c in contexts if handles[c['cell']].poll() is not None}
                live = [c for c in contexts if c['cell'] not in exited]
                try:
                    errors = s035.halt_all(control, dict(adoption, contexts=live), reason) if live else []
                    adoption.update(status='PAUSED', reason=reason, pause_errors=errors, updated_epoch=time.time(),
                                    exited_cells=sorted(exited), executing_cells=[])
                    atomic_json(control / 'ADOPTION.json', adoption)
                    atomic_json(control / 'CONTROLLER.json', dict(status='PAUSED', reason=reason, **controller,
                                updated_epoch=time.time(), pause_errors=errors, verdict='UNKNOWN'))
                finally:
                    for handle in handles.values():
                        handle.close()
    print(json.dumps(dict(status='PAUSED', reason=reason, pause_errors=errors, no_region_promoted=True)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'status', 'pause', 'prepare-resume'))
    parser.add_argument('--pilot-seconds', type=float)
    parser.add_argument('--resume', action='store_true', help='adopt the residents named in RESUME_PLAN.json')
    args = parser.parse_args()
    if args.action == 'status':
        print(json.dumps(read_json(CONTROL / 'ADOPTION.json'), indent=1))
    elif args.action == 'prepare-resume':
        plan = prepare_resume(CONTROL)
        print(json.dumps({k: plan[k] for k in ('status', 'previous_reason', 'history', 'queued_regions')}, indent=1))
    elif args.action == 'pause':
        (CONTROL / 'STOP').touch(); print('Preservation pause requested; residents will be suspended, not terminated.')
    else:
        if args.pilot_seconds is not None and not 0 < args.pilot_seconds <= 120:
            raise LifecycleError('Pilot must be between zero and 120 seconds')
        run(AREA, CONTROL, pilot_seconds=args.pilot_seconds, resume=args.resume)


if __name__ == '__main__':
    main()
