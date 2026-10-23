"""S036 fresh resident campaign: semantic recovery after loss of the S035 RAM identities.

The original S035 processes ended when the app that owned their process tree
closed (validation/S036/identity-loss). Their private CDCL is unrecoverable.
This controller starts NEW native processes (S036 diagnostic native, baseline
settings: congruence disabled, CaDiCaL default random walk) for the resident
regions 0, 7, 127, 255 from exact recipes: base + S032 seed + every S035
ledger-accepted audited geometric source + that region's S036 audited blocks.

Owner amendment 4 (23 October 2026, "raise the limits to whatever this machine
can handle ... recycle where needed"; validation/S036/MACHINE_LIMITS.json):
measured machine limits replace the original 5/6 GiB targets, all four residents
execute concurrently, and a resident is RECYCLED instead of halting the search
when it outgrows the per-solver threshold, when the residents outgrow their
target, or when available RAM stays low: it is stopped through its cooperative
stop file (natural exit 0), its new geometric clauses are independently
subdivision-audited into an immutable region block, and a new process for the
same region starts from the enlarged exact recipe. Recycling loses that region's
private CDCL only; it is never claimed as retained. Nothing is force-terminated.
SAT or exit 10 outranks everything; native UNSAT halts for a fresh standalone
DRAT and independent check and never closes a region here. Launch this
controller and the supervisor outside any application job (scripts/s036_launch.py).
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
import threading
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
LEDGER = ROOT / 'artifacts/tmp/S036/cold/LEDGER.json'
REGIONS = (0, 7, 127, 255)
SOURCES = ('tools/s036_sat_scan.py', 'scripts/s036_sat_supervisor.py', 'scripts/s036_resident_controller.py',
           'scripts/s036_fresh_campaign.py', 'tools/s035_preserved_lifecycle.py', 'scripts/s035_preserved_campaign.py',
           'tools/s035_sat_validation.py', 'tools/s035_windows.py')
GiB = 1024 ** 3
# Measured 23 October 2026 ~17:00 UTC: 15.71 GiB physical; ~6.4 GiB used outside the search
# (Claude app ~2.2 GiB plus ~0.5 GiB per running check-in session). Hard caps halt and
# preserve; the resident target and persistent low RAM recycle the largest resident.
MACHINE = dict(aggregate_private=8 * GiB, per_worker_private=3 * GiB, available_floor=int(1.25 * GiB),
               soft_private=7 * GiB, soft_available=2 * GiB, disk_reserve=8 * GiB,
               throttle_clear_seconds=120, throttle_clear_margin=int(0.25 * GiB))
ctl.LIMITS = dict(ctl.LIMITS, **MACHINE)
COLD_CEILING = int(7.75 * GiB)
ACTIVE_SLOTS = 4
ADMISSION = dict(reserve_bytes=2 * GiB, available_after_min=int(2.25 * GiB), loading_seconds=120)
RECYCLE = dict(worker_bytes=int(2.5 * GiB), cooldown_seconds=7200, low_ram_seconds=300, stop_wait_seconds=60)


def resource(area, control, contexts, registry, cache):
    """Resident resource gate with the registered cold band.

    If the resident target is crossed only because of a live cold solver, and the total
    stays within COLD_CEILING, every other check is re-evaluated with the target lifted
    to the ceiling. Above the ceiling, or if residents alone exceed the target, the
    target reason is returned so the caller asks the cold slot to yield or recycles.
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


def prepare_input(region, generation, fixture=None):
    """Heavy step (runs in a worker thread): new directory, exact input, INPUT.json."""
    from s035_engine import materialise
    if fixture:
        directory = Path(fixture['directory']) / f'gen-{generation}'
        directory.mkdir(parents=True, exist_ok=True)
        os.link(fixture['input'], directory / 'input.inst')
        meta = dict(fixture['meta'], generation=generation)
    else:
        directory = RESIDENT / f'region-{region:04d}' / uuid.uuid4().hex
        directory.mkdir(parents=True)
        cfg, value = recipe_for(region)
        digest = materialise(directory / 'input.inst', value, native=True)
        meta = dict(recipe=copy.deepcopy(value), input_sha256=digest, native=str(NATIVE), native_sha256=ctl.sha(NATIVE),
                    source_sha256=cfg['source_sha256'], resident=True, session='S036', region=region,
                    generation=generation, settings='baseline: congruence disabled, CaDiCaL default walk, no S036 options')
    atomic_json(directory / 'INPUT.json', meta)
    return dict(directory=directory, meta=meta)


def start_native(region, prepared, control, generation, native=NATIVE):
    """Fast step: start one native on a prepared input; returns (context, process)."""
    directory, meta = Path(prepared['directory']), prepared['meta']
    stop = directory / 'COOPERATIVE_STOP'
    env = os.environ.copy()
    env.pop('EMP_S035_DISABLE_WALK', None); env.pop('EMP_S036_CADICAL_OPTIONS', None)
    env['EMP_S035_DISABLE_CONGRUENCE'] = '1'
    env['EMP_S036_STOP_FILE'] = str(stop)
    args = [str(native), str(directory / 'input.inst'), '--timeout', 'inf', '--lemmas', str(directory / 'new-cuts.lem')]
    with (directory / 'native.log').open('w') as log:
        p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
    worker = dict(pid=p.pid, start_ticks=process_identity(p.pid))
    context = dict(cell=region, worker=worker, directory=str(directory), input_sha256=meta['input_sha256'],
                   native_sha256=meta['native_sha256'], turns=0, active_seconds=0.0, state='LOADING',
                   launched_epoch=time.time(), stop_file=str(stop), generation=generation,
                   sources=len(meta['recipe']['sources']) if 'recipe' in meta else None)
    journal(control / 'JOURNAL.jsonl', 'fresh_resident_launched', cell=region, worker=worker,
            directory=str(directory), input_sha256=meta['input_sha256'], generation=generation)
    return context, p


def pairs_of(directory):
    meta = read_json(Path(directory) / 'INPUT.json')
    return meta['recipe']['pairs'] if 'recipe' in meta else meta['pairs']


def audit_block(region, directory, ledger_path=LEDGER):
    """Independently subdivision-audit a stopped resident's complete new clauses (worker thread)."""
    from s035_engine import subdivision
    directory = Path(directory)
    source = directory / 'new-cuts.lem'
    if not source.exists() or not source.stat().st_size:
        return dict(count=0)
    pairs = pairs_of(directory)
    h = hashlib.sha256(); count = 0
    temp = directory / 'recycle-audit.part'
    with source.open('rb') as f, temp.open('wb') as dest:
        for line in f:
            if not line.endswith(b'\n'):
                break
            xs = list(map(int, line.split()))
            assert xs.pop() == 0 and xs and len(xs) == len(set(xs))
            assert all(-2 * len(pairs) <= x < 0 for x in xs)
            assert len({(-x - 1) % 2 for x in xs}) == 1
            subdivision([tuple(pairs[(-x - 1) // 2]) for x in xs])
            dest.write(line); h.update(line); count += 1
        dest.flush(); os.fsync(dest.fileno())
    if not count:
        temp.unlink()
        return dict(count=0)
    target = directory / ('a-' + h.hexdigest()[:16] + '.lem')
    os.replace(temp, target)
    row = dict(path=str(target), count=count, sha256=h.hexdigest(), audit='INDEPENDENT_SUBDIVISION_PASS',
               n=1 + max(max(p) for p in pairs), origin=str(source), region=region, session='S036',
               kind='RECYCLED_RESIDENT_GEOMETRIC_JOURNAL')
    atomic_json(target.with_suffix('.audit.json'), row)
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with locked(ledger_path.with_suffix('.lock')):
        data = read_json(ledger_path) if ledger_path.exists() else dict(regions={}, verdict='UNKNOWN')
        blocks = data['regions'].setdefault(str(region), {}).setdefault('audited_blocks', [])
        if not any(b['sha256'] == row['sha256'] for b in blocks):
            blocks.append(row)
        atomic_json(ledger_path, data)
    return row


class Worker(threading.Thread):
    """Run one heavy function off the control loop so leases and heartbeats stay fresh."""
    def __init__(self, fn, *args, **kwargs):
        super().__init__(daemon=True)
        self.fn, self.args, self.kwargs = fn, args, kwargs
        self.result = self.error = None

    def run(self):
        try:
            self.result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            self.error = exc


def admission(control, contexts, registry, active):
    """Measured gate for one more resident; loads are staggered."""
    if any(time.time() - c['launched_epoch'] < ADMISSION['loading_seconds'] for c in contexts):
        return 'PREVIOUS_RESIDENT_STILL_LOADING'
    if len(active) >= ACTIVE_SLOTS:
        return 'NO_FREE_ACTIVE_SLOT'
    cold = ctl.cold_identity(control)
    sample = sample_identities(registry + [c['worker'] for c in contexts] + ([cold] if cold else []))
    if sample['private'] + ADMISSION['reserve_bytes'] > ctl.LIMITS['soft_private']:
        return f"AGGREGATE_PRIVATE {sample['private']}"
    if psutil.virtual_memory().available - ADMISSION['reserve_bytes'] < ADMISSION['available_after_min']:
        return f"AVAILABLE_RAM {psutil.virtual_memory().available}"
    return None


def terminal(control, contexts, handles):
    """Unexpected native returns. A recycling resident's exit 0 is expected and excluded."""
    rows = []
    for context in contexts:
        code = handles[context['cell']].poll()
        if code is None or (context.get('state') == 'RECYCLING' and code == 0):
            continue
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


def private_of(context):
    try:
        return psutil.Process(context['worker']['pid']).memory_info().private
    except psutil.Error:
        return 0


def recycle_candidate(contexts, minimum=0):
    """Largest resident past its cooldown and at or above `minimum` private bytes."""
    now = time.time()
    rows = [(private_of(c), c['cell'], c) for c in contexts
            if c.get('state') not in ('RECYCLING', 'LOADING')
            and now - c.get('launched_epoch', 0) >= RECYCLE['cooldown_seconds']]
    rows = [r for r in rows if r[0] >= minimum]
    return max(rows, key=lambda r: (r[0], r[1]))[2] if rows else None


RESUMABLE = ('SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE', 'BOUNDED_PILOT_COMPLETE_RAM_PRESERVED',
             'SOFT_AVAILABLE_RAM_THROTTLE', 'SUPERVISOR_PAUSE:OWNER_OR_CONTROLLER_STOP', 'OWNER_OR_CONTROLLER_STOP')
# Hard-cap preservation pauses resume only with explicit owner authorisation.
OWNER_RESUMABLE = ('SAFETY_AGGREGATE_PRIVATE_CAP', 'SAFETY_PER_WORKER_PRIVATE_CAP', 'SAFETY_AVAILABLE_RAM_FLOOR',
                   'RECYCLE_STOP_TIMEOUT')
KEEP_ON_ARCHIVE = {'history', 'CONTROLLER.lock', 'MUTATION.lock', 'WATCHER.lock', 'ACCEPTANCE_FRESH.json',
                   'COLD_SLOT.json'}


def release_cold_solver(control, wait=60):
    """Operator step: a cold solver suspended by a preservation pause is let exit cooperatively."""
    path = Path(control) / 'COLD_SLOT.json'
    slot = read_json(path) if path.exists() else {}
    if slot.get('state') != 'RUNNING' or not slot.get('worker'):
        return None
    try:
        checked(slot['worker'])
    except LifecycleError:
        return 'COLD_SOLVER_ALREADY_GONE'
    Path(slot['stop_file']).touch()
    resume_identity(slot['worker'], pause_identity(slot['worker']), [])
    end = time.monotonic() + wait
    while time.monotonic() < end:
        try:
            checked(slot['worker'])
        except LifecycleError:
            journal(Path(control) / 'JOURNAL.jsonl', 'cold_solver_released_for_cooperative_exit', worker=slot['worker'])
            return 'COLD_SOLVER_EXITED_COOPERATIVELY'
        time.sleep(.5)
    pause_identity(slot['worker'])
    raise LifecycleError('Cold solver did not stop cooperatively; preserved suspended')


def prepare_resume(control, owner_authorized=False, ledger_path=LEDGER):
    """Operator step: verify a cleanly paused fresh campaign and archive its controls.

    Never resumes a resident. Refuses after SAT, native return, supervisor failure,
    pause errors, a live previous controller/supervisor or any resident that is not
    alive with every thread suspended. Residents that had already exited cooperatively
    while being recycled are audited now and queued for relaunch.
    """
    control = Path(control).resolve()
    if (control / 'SAT_ALERT.json').exists() or (control / 'TERMINAL.json').exists():
        raise LifecycleError('SAT or native return requires review; no resume')
    if (control / 'WATCHER_FAILURE.json').exists():
        raise LifecycleError('Supervisor failure recorded; manual review required')
    previous = read_json(control / 'ADOPTION.json')
    allowed = RESUMABLE + (OWNER_RESUMABLE if owner_authorized else ())
    recycled = {row['cell']: row for row in previous.get('recycled_exits', [])}
    if (previous.get('mode') != 'FRESH_SEMANTIC_RECOVERY_RESIDENTS' or previous.get('status') != 'PAUSED'
            or previous.get('pause_errors') or set(previous.get('exited_cells', [])) - set(recycled)
            or previous.get('reason') not in allowed):
        raise LifecycleError('Previous fresh campaign is not cleanly paused for a resumable reason')
    for record in (previous['controller'], previous['watcher']):
        try:
            checked(record)
        except LifecycleError:
            continue
        raise LifecycleError('Previous controller/supervisor has not exited')
    released = release_cold_solver(control)
    live = []
    for context in previous['contexts']:
        if context['cell'] in recycled:
            if not recycled[context['cell']].get('audited'):
                audit_block(context['cell'], context['directory'], ledger_path)
            continue
        context.update(threads=life_counts(context['worker']), state='PAUSED')
        live.append(context)
    history = control / 'history' / (str(time.time_ns()) + '-fresh-resume-' + uuid.uuid4().hex[:6])
    history.mkdir(parents=True)
    moved = []
    for path in list(control.iterdir()):
        if path.name in KEEP_ON_ARCHIVE:
            continue
        path.rename(history / path.name); moved.append(path.name)
    plan = dict(status='RESUME_PLAN_VERIFIED_NO_PROCESS_RESUMED', previous_reason=previous['reason'],
                owner_authorized=owner_authorized, history=str(history), moved=moved, contexts=live,
                queued_regions=sorted(recycled) + list(previous.get('queued_regions', [])),
                generations=previous.get('generations', {}), cold_solver=released, epoch=time.time())
    atomic_json(control / 'RESUME_PLAN.json', plan)
    journal(control / 'JOURNAL.jsonl', 'fresh_resume_prepared', history=str(history),
            cells=[c['cell'] for c in live], requeued=sorted(recycled), owner_authorized=owner_authorized,
            no_process_resumed=True)
    return plan


def life_counts(worker):
    """Suspend every current thread of OUR resident (idempotent) and return exact counts.

    Suspended processes can acquire idle OS thread-pool workers (as in S035); for
    processes this campaign launched they are suspended with the rest, never left running.
    Raises if the process no longer survives.
    """
    return pause_identity(worker)


def run(area, control, regions=REGIONS, pilot_seconds=None, fixture=None, resume=False, ledger_path=LEDGER):
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
    generations = {}
    if resume:
        queue = list(plan['queued_regions'])
        generations = {int(k): v for k, v in plan.get('generations', {}).items()}
        for context in plan['contexts']:
            context.update(threads=life_counts(context['worker']), state='PAUSED')
            context.pop('turn_start_metrics', None)
            context.setdefault('generation', generations.get(context['cell'], 0))
            handles[context['cell']] = ProcessHandle(context['worker'])
            contexts.append(context)
        (control / 'RESUME_PLAN.json').rename(control / f'RESUME_PLAN-used-{time.time_ns()}.json')
        journal(control / 'JOURNAL.jsonl', 'fresh_resume_adopted', cells=[c['cell'] for c in contexts],
                requeued=queue, same_identities=True)
    for context in contexts:
        generations[context['cell']] = max(generations.get(context['cell'], 0), context.get('generation', 0))
    cold_yield_since = None
    recycle = preparing = None
    recycled_exits = []
    low_ram_last = 0.0
    active_started, turn_start, cache = {}, {}, {}
    throttle = dict(active=False, clear_since=None, events=0)
    adoption = dict(status='PREPARING', session='S036', mode='FRESH_SEMANTIC_RECOVERY_RESIDENTS', controller=controller,
                    watcher=supervisor, created_epoch=time.time(), epoch=time.time(), contexts=contexts,
                    source_sha256=sources(), lease_seconds=10, limits=ctl.LIMITS, admission=ADMISSION,
                    recycle_policy=RECYCLE, active_slots=ACTIVE_SLOTS, cold_ceiling=COLD_CEILING,
                    queued_regions=queue, generations=generations, recycled_exits=recycled_exits,
                    private_cdcl_of_lost_contexts='UNRECOVERABLE_NOT_CLAIMED')
    atomic_json(control / 'ADOPTION.json', adoption)
    errors = []
    reason = 'CONTROLLER_EXCEPTION'
    started = time.monotonic()
    end = started + pilot_seconds if pilot_seconds else float('inf')
    quantum = min(600, pilot_seconds / 4) if pilot_seconds else 600
    next_release_check = 0.0
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
                           generation=context.get('generation', 0),
                           **ctl.process_metrics(context['worker']), **ctl.counters(context['directory']))
            start_row = context.pop('turn_start_metrics', {})
            for name in ('cpu_seconds', 'conflicts', 'decisions', 'propagations', 'cuts', 'lemma_bytes'):
                if name in metrics and name in start_row:
                    metrics['delta_' + name] = metrics[name] - start_row[name]
            journal(control / 'JOURNAL.jsonl', 'fair_turn_paused', cell=key, worker=context['worker'],
                    active_seconds=context['active_seconds'], why=why)
            journal(control / 'METRICS.jsonl', 'turn_metrics', **metrics)

        def start_recycle(context, why):
            """Stop one resident through its cooperative stop file; never a forced termination."""
            if context['cell'] in active_started:
                end_turn(context, time.monotonic(), 'RECYCLE_' + why)
            before = dict(private_bytes=private_of(context), **ctl.counters(context['directory']))
            with locked(control / 'MUTATION.lock'):
                Path(context['stop_file']).touch()
                resume_identity(context['worker'], pause_identity(context['worker']), [])
            context['state'] = 'RECYCLING'
            journal(control / 'JOURNAL.jsonl', 'resident_recycle_started', cell=context['cell'], why=why,
                    worker=context['worker'], generation=context.get('generation', 0), **before)
            return dict(context=context, phase='STOPPING', started=time.monotonic(), why=why, before=before)
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
                # A recycling resident may already have exited: it is excluded from the
                # identity sample and per-worker checks (its exit code is polled separately).
                present = [c for c in contexts if c.get('state') != 'RECYCLING']
                hard, soft, sample = resource(area, control, present,
                                              registry + [c['worker'] for c in present], cache)
                busy = recycle is not None or preparing is not None
                if hard == 'SOFT_RESIDENT_CACHE_TARGET_PRESERVATION_PAUSE':
                    if sample.get('cold_slot'):
                        # The cold slot always yields first: request its cooperative stop
                        # and give it up to 60 s before the target is treated as binding.
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
                    elif busy:
                        hard = None  # a recycle/relaunch in progress is already reducing residency
                    else:
                        candidate = recycle_candidate(contexts)
                        if candidate is not None:
                            recycle = start_recycle(candidate, 'RESIDENT_TARGET')
                            hard = None
                if not sample.get('cold_slot'):
                    cold_yield_since = None
                if hard:
                    reason = hard
                    break
                if recycle is None and preparing is None:
                    candidate = recycle_candidate(contexts, minimum=RECYCLE['worker_bytes'])
                    if candidate is not None:
                        recycle = start_recycle(candidate, 'PER_WORKER')
                if soft:
                    if not throttle['active']:
                        throttle.update(active=True, events=throttle['events'] + 1, since=time.time(), reason=soft,
                                        since_monotonic=time.monotonic())
                        for context in contexts:
                            if context['cell'] in active_started:
                                end_turn(context, time.monotonic(), soft)
                        journal(control / 'JOURNAL.jsonl', 'soft_throttle_started', reason=soft,
                                available=sample['available'], private=sample['private'])
                    throttle['clear_since'] = None
                    # Persistent low RAM sheds the largest resident (one at a time).
                    if (recycle is None and preparing is None
                            and time.monotonic() - throttle['since_monotonic'] >= RECYCLE['low_ram_seconds']
                            and time.monotonic() - low_ram_last >= RECYCLE['low_ram_seconds']):
                        candidate = recycle_candidate(contexts)
                        if candidate is not None:
                            recycle = start_recycle(candidate, 'LOW_AVAILABLE_RAM')
                            low_ram_last = time.monotonic()
                elif throttle['active']:
                    if sample['available'] >= ctl.LIMITS['soft_available'] + ctl.LIMITS['throttle_clear_margin']:
                        throttle['clear_since'] = throttle['clear_since'] or time.monotonic()
                        if time.monotonic() - throttle['clear_since'] >= ctl.LIMITS['throttle_clear_seconds']:
                            throttle.update(active=False, clear_since=None)
                            journal(control / 'JOURNAL.jsonl', 'soft_throttle_cleared',
                                    available=sample['available'], private=sample['private'])
                    else:
                        throttle['clear_since'] = None
                # Recycling progress: cooperative exit, then an off-loop independent audit.
                if recycle is not None:
                    context = recycle['context']
                    code = handles[context['cell']].poll()
                    if recycle['phase'] == 'STOPPING':
                        if code == 0:
                            recycle.update(phase='AUDITING', worker=Worker(audit_block, context['cell'],
                                                                           context['directory'], ledger_path))
                            recycle['worker'].start()
                        elif code is None and time.monotonic() - recycle['started'] > RECYCLE['stop_wait_seconds']:
                            with locked(control / 'MUTATION.lock'):
                                context['threads'] = pause_identity(context['worker'])
                            context['state'] = 'PAUSED'
                            reason = 'RECYCLE_STOP_TIMEOUT'
                            break
                    elif recycle['phase'] == 'AUDITING' and not recycle['worker'].is_alive():
                        if recycle['worker'].error is not None:
                            reason = 'RECYCLE_AUDIT_FAILURE_' + repr(recycle['worker'].error)
                            recycled_exits.append(dict(cell=context['cell'], directory=context['directory'],
                                                       audited=False))
                            break
                        block = recycle['worker'].result
                        contexts.remove(context)
                        handles.pop(context['cell']).close()
                        queue.insert(0, context['cell'])
                        journal(control / 'JOURNAL.jsonl', 'resident_recycled', cell=context['cell'],
                                why=recycle['why'], generation=context.get('generation', 0), worker=context['worker'],
                                audited_clauses=block.get('count', 0), block=block.get('sha256'),
                                private_cdcl_retained=False, **recycle['before'])
                        recycle = None
                if not throttle['active']:
                    # Prepare (off-loop) and then start the next queued resident through the gate.
                    if preparing is None and recycle is None and queue:
                        why = admission(control, contexts, registry, active_started)
                        adoption['admission_blocked'] = why
                        if why is None:
                            region = queue.pop(0)
                            generation = generations.get(region, -1) + 1 if region in generations else 0
                            preparing = dict(region=region, generation=generation,
                                             worker=Worker(prepare_input, region, generation,
                                                           (fixture or {}).get(region)))
                            preparing['worker'].start()
                    if preparing is not None and not preparing['worker'].is_alive():
                        if preparing['worker'].error is not None:
                            reason = 'RESIDENT_PREPARATION_FAILURE_' + repr(preparing['worker'].error)
                            queue.insert(0, preparing['region'])
                            break
                        with locked(control / 'MUTATION.lock'):
                            if ctl.stop_reason(area, control):
                                queue.insert(0, preparing['region']); preparing = None
                                continue
                            region, generation = preparing['region'], preparing['generation']
                            context, process = start_native(region, preparing['worker'].result, control, generation,
                                                            (fixture or {}).get(region, {}).get('native', NATIVE))
                        handles[region] = ProcessHandle(context['worker'])
                        contexts.append(context)
                        generations[region] = generation
                        context.update(state='RUNNING', turns=1, turn_start_metrics={})
                        active_started[region] = turn_start[region] = time.monotonic()
                        preparing = None
                    choices = sorted((c for c in contexts if c['cell'] not in active_started
                                      and c.get('state') != 'RECYCLING'),
                                     key=lambda c: (c['active_seconds'], c['turns'], c['cell']))
                    for context in choices[:max(0, ACTIVE_SLOTS - len(active_started))]:
                        with locked(control / 'MUTATION.lock'):
                            if ctl.stop_reason(area, control):
                                break
                            context['turn_start_metrics'] = dict(**ctl.process_metrics(context['worker']),
                                                                 **ctl.counters(context['directory']))
                            # Own processes: re-inventory (idempotent) so threads the
                            # process created itself are resumed with exact counts.
                            resume_identity(context['worker'], pause_identity(context['worker']), [])
                            if ctl.stop_reason(area, control):
                                context['threads'] = pause_identity(context['worker'])
                                break
                        active_started[context['cell']] = turn_start[context['cell']] = time.monotonic()
                        context.update(state='RUNNING', turns=context['turns'] + 1)
                        journal(control / 'JOURNAL.jsonl', 'same_identity_resumed', cell=context['cell'],
                                worker=context['worker'], turn=context['turns'])
                # Release a loaded resident's input copy (the exact recipe stays in INPUT.json).
                if fixture is None and time.monotonic() >= next_release_check:
                    next_release_check = time.monotonic() + 30
                    for context in contexts:
                        inp = Path(context['directory']) / 'input.inst'
                        if context.get('input_released') or not inp.exists():
                            continue
                        with (Path(context['directory']) / 'native.log').open('rb') as log:
                            if b'c S032_PROGRESS' in log.read(65536):
                                inp.unlink(); context['input_released'] = True
                                journal(control / 'JOURNAL.jsonl', 'resident_input_released', cell=context['cell'],
                                        input_sha256=context['input_sha256'])
                status = 'THROTTLED' if throttle['active'] else 'RUNNING'
                adoption.update(status=status, updated_epoch=time.time(), sample=sample, resource_cache=cache,
                                executing_cells=sorted(active_started), throttle=throttle, queued_regions=queue,
                                generations=generations,
                                recycling=recycle and dict(cell=recycle['context']['cell'], phase=recycle['phase'],
                                                           why=recycle['why']),
                                preparing=preparing and dict(region=preparing['region'],
                                                             generation=preparing['generation']))
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
                for context in contexts:
                    # A resident that finished its cooperative recycle exit is re-queued at resume.
                    if (context['cell'] in exited and context.get('state') == 'RECYCLING'
                            and handles[context['cell']].poll() == 0
                            and not any(r['cell'] == context['cell'] for r in recycled_exits)):
                        recycled_exits.append(dict(cell=context['cell'], directory=context['directory'],
                                                   audited=False))
                live = [c for c in contexts if c['cell'] not in exited]
                try:
                    errors = s035.halt_all(control, dict(adoption, contexts=live), reason) if live else []
                    adoption.update(status='PAUSED', reason=reason, pause_errors=errors, updated_epoch=time.time(),
                                    exited_cells=sorted(exited), executing_cells=[], recycled_exits=recycled_exits,
                                    generations=generations, queued_regions=queue)
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
    parser.add_argument('--owner-authorized', action='store_true',
                        help='prepare-resume after a hard-cap preservation pause (owner decision only)')
    args = parser.parse_args()
    if args.action == 'status':
        print(json.dumps(read_json(CONTROL / 'ADOPTION.json'), indent=1))
    elif args.action == 'prepare-resume':
        plan = prepare_resume(CONTROL, owner_authorized=args.owner_authorized)
        print(json.dumps({k: plan[k] for k in ('status', 'previous_reason', 'owner_authorized', 'history',
                                               'queued_regions', 'cold_solver')}, indent=1))
    elif args.action == 'pause':
        (CONTROL / 'STOP').touch(); print('Preservation pause requested; residents will be suspended, not terminated.')
    else:
        if args.pilot_seconds is not None and not 0 < args.pilot_seconds <= 120:
            raise LifecycleError('Pilot must be between zero and 120 seconds')
        run(AREA, CONTROL, pilot_seconds=args.pilot_seconds, resume=args.resume)


if __name__ == '__main__':
    main()
