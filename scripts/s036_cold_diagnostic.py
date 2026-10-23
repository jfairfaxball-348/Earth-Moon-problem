"""S036 bounded cold slot: registered option diagnostics and fair cold rotation.

At most one cold native process runs, beside (never instead of) the two retained
fair-turn slots. It is admitted only through the registered capacity gate
(validation/S036/COLD_CAPACITY_PLAN.json), ends by natural --timeout or by the
cooperative stop file, and is registered in the S036 control directory so the
independent SAT supervisor suspends it on any alert. Nothing is force-killed.

Per region one immutable input (base + S032 seed + every S035 ledger-accepted
audited geometric source + S036 audited cold cuts for that region + region
assumptions) is materialised once; all arms read identical bytes. New geometric
clauses are independently subdivision-audited before any reuse. Native UNSAT is
recorded as pending a fresh standalone DRAT proof and independent check; it never
closes a region here. SAT/exit 10 stops the runner and is left to the
supervisor's prominent SAT path (two independent channels: log and exit record).
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s035_windows import atomic_json, read_json, journal, live_identity, process_identity  # noqa: E402

AREA = ROOT / 'artifacts/tmp/S035/campaign'
CONTROL = ROOT / 'artifacts/tmp/S036/control'
COLD = ROOT / 'artifacts/tmp/S036/cold'
NATIVE = ROOT / 'artifacts/tmp/S036/native/bipsat_s032.exe'
ARMS = ROOT / 'validation/S036/DIAGNOSTIC_ARMS.json'
PLAN = ROOT / 'validation/S036/COLD_CAPACITY_PLAN.json'
GiB = 1024 ** 3
COLD_REGIONS = (1, 3, 15, 31, 63)
LOGIC = re.compile(r'^c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)', re.M)
PROGRESS = re.compile(r'^c S032_PROGRESS seconds=([\d.]+) checks=(\d+) cuts=(\d+)', re.M)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def ledger_path():
    return COLD / 'LEDGER.json'


def load_ledger():
    return read_json(ledger_path()) if ledger_path().exists() else dict(regions={}, verdict='UNKNOWN')


def recipe_for(region):
    """Exact recipe; only audited sources. S035 ledgers are read, never written."""
    from s035_engine import recipe
    cfg = read_json(AREA / 'CONFIG.json')
    regions = read_json(AREA / 'REGIONS.json')
    cell = regions['cells'][region]
    assert cell['id'] == region and cell['status'] != 'UNSAT_DRAT_VERIFIED'
    shared = [row for row in regions['accepted_cuts'] if row.get('audit') in (None, 'INDEPENDENT_SUBDIVISION_PASS')]
    extra = load_ledger()['regions'].get(str(region), {}).get('audited_blocks', [])
    return cfg, recipe(cfg, shared + extra, cell['assumptions'])


def gates(admission=False, cold_private=0):
    """Return None when the cold slot may run, else the registered yield reason."""
    plan = read_json(PLAN)['admission_gate']
    if (CONTROL / 'STOP').exists():
        return 'S036_STOP_LATCHED'
    if (CONTROL / 'SAT_ALERT.json').exists() or (AREA / 'SAT_ALERT.json').exists():
        return 'SAT_ALERT_PRESENT'
    try:
        controller = read_json(CONTROL / 'CONTROLLER.json')
        watcher = read_json(CONTROL / 'WATCHER.json')
    except Exception as exc:
        return 'CONTROL_METADATA_UNAVAILABLE:' + repr(exc)
    if controller.get('status') != 'RUNNING' or time.time() - controller.get('updated_epoch', 0) > 10:
        return 'CONTROLLER_NOT_RUNNING:' + str(controller.get('status'))
    if watcher.get('status') != 'WATCHING' or time.time() - watcher.get('updated_epoch', 0) > plan['supervisor_heartbeat_max_age_seconds']:
        return 'SUPERVISOR_NOT_WATCHING'
    adoption = read_json(CONTROL / 'ADOPTION.json')
    # Sample the registered retained/legacy identities plus controller and
    # supervisor directly; the controller's own sample may already include the
    # cold process, so it must not be added to cold_private twice.
    from s035_preserved_lifecycle import sample_identities
    registry = read_json(AREA / 'OWNER_PAUSE.json')['processes'] + [adoption['controller'], adoption['watcher']]
    try:
        private = sample_identities(registry)['private']
    except Exception as exc:
        return 'IDENTITY_SAMPLE_UNAVAILABLE:' + repr(exc)
    available = psutil.virtual_memory().available
    if admission:
        if available < plan['available_ram_bytes_min']:
            return f'ADMISSION_AVAILABLE_RAM {available}'
        if private + plan['admission_reserve_bytes'] > plan['aggregate_private_after_admission_max']:
            return f'ADMISSION_AGGREGATE_PRIVATE {private}'
        if shutil.disk_usage(ROOT).free < plan['free_disk_min_bytes']:
            return 'ADMISSION_DISK'
    else:
        if available < int(2.75 * GiB):
            return f'YIELD_AVAILABLE_RAM {available}'
        if private + cold_private > 5 * GiB:
            return f'YIELD_AGGREGATE_PRIVATE {private + cold_private}'
        if cold_private > 1.5 * GiB:
            return f'YIELD_COLD_PRIVATE {cold_private}'
        if shutil.disk_usage(ROOT).free < 10 * GiB:
            return 'YIELD_DISK_RESERVE'
    return None


def materialise_region(region):
    from s035_engine import materialise
    cfg, value = recipe_for(region)
    directory = COLD / f'region-{region:04d}'
    directory.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:16]
    source = directory / f'input-{key}.inst'
    meta_path = directory / f'input-{key}.json'
    if source.exists() and meta_path.exists() and sha(source) == read_json(meta_path)['input_sha256']:
        return source, read_json(meta_path)
    digest = materialise(source, value, native=True)
    meta = dict(recipe=copy.deepcopy(value), input_sha256=digest, native=str(NATIVE), native_sha256=sha(NATIVE),
                source_sha256=cfg['source_sha256'], resident=False, session='S036', region=region,
                recipe_key=key)
    atomic_json(meta_path, meta)
    return source, meta


def parse(log):
    text = Path(log).read_text(errors='replace')
    logic = [tuple(map(int, m)) for m in LOGIC.findall(text)]
    progress = [(float(a), int(b), int(c)) for a, b, c in PROGRESS.findall(text)]
    return text, logic, progress


def run_arm(region, arm, source, meta, budget, purpose):
    token = uuid.uuid4().hex
    directory = COLD / f'region-{region:04d}' / f'{purpose}-{arm["name"]}-{token[:8]}'
    directory.mkdir(parents=True)
    os.link(source, directory / 'input.inst')
    atomic_json(directory / 'INPUT.json', dict(meta, arm=arm, purpose=purpose, budget_wall_seconds=budget))
    stop = directory / 'COOPERATIVE_STOP'
    env = os.environ.copy()
    env.pop('EMP_S035_DISABLE_WALK', None)
    env['EMP_S035_DISABLE_CONGRUENCE'] = '1'
    env['EMP_S036_STOP_FILE'] = str(stop)
    if arm['options']:
        env['EMP_S036_CADICAL_OPTIONS'] = arm['options']
    else:
        env.pop('EMP_S036_CADICAL_OPTIONS', None)
    args = [str(NATIVE), str(directory / 'input.inst'), '--timeout', str(budget),
            '--lemmas', str(directory / 'new-cuts.lem')]
    samples = []
    yield_reason = None
    with (directory / 'native.log').open('w') as log:
        p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
    worker = dict(pid=p.pid, start_ticks=process_identity(p.pid))
    atomic_json(CONTROL / 'COLD_SLOT.json', dict(state='RUNNING', worker=worker, directory=str(directory),
                stop_file=str(stop), region=region, arm=arm['name'], purpose=purpose, started_epoch=time.time(),
                budget_wall_seconds=budget, runner=dict(pid=os.getpid(), start_ticks=process_identity(os.getpid()))))
    journal(COLD / 'JOURNAL.jsonl', 'cold_started', region=region, arm=arm['name'], purpose=purpose, worker=worker,
            directory=str(directory), input_sha256=meta['input_sha256'])
    proc = psutil.Process(p.pid)
    peak = 0
    first_progress = None
    started = time.monotonic()
    try:
        while p.poll() is None:
            try:
                clock, memory = proc.cpu_times(), proc.memory_info()
                cpu = clock.user + clock.system
                peak = max(peak, memory.private)
                samples.append(dict(t=time.monotonic() - started, cpu=cpu, private=memory.private,
                                    available=psutil.virtual_memory().available))
                if first_progress is None and (directory / 'native.log').stat().st_size:
                    _, logic, progress = parse(directory / 'native.log')
                    if progress and logic:
                        first_progress = dict(t=samples[-1]['t'], cpu=cpu, conflicts=logic[-1][0],
                                              decisions=logic[-1][1], propagations=logic[-1][2],
                                              cuts=progress[-1][2])
            except psutil.Error:
                pass
            if yield_reason is None:
                reason = gates(cold_private=samples[-1]['private'] if samples else 0)
                if reason:
                    yield_reason = reason
                    stop.touch()
                    journal(COLD / 'JOURNAL.jsonl', 'cold_yield_requested', region=region, arm=arm['name'],
                            reason=reason)
            time.sleep(1)
    finally:
        code = p.wait()
        atomic_json(CONTROL / 'COLD_SLOT.json', dict(state='IDLE', last_worker=worker, last_directory=str(directory),
                    last_returncode=code, updated_epoch=time.time()))
    text, logic, progress = parse(directory / 'native.log')
    final_cpu = samples[-1]['cpu'] if samples else None
    result = dict(region=region, arm=arm['name'], options=arm['options'], purpose=purpose, returncode=code,
                  worker=worker, yield_reason=yield_reason, cooperative_stop='c S036_COOPERATIVE_STOP' in text,
                  wall_seconds=time.monotonic() - started, final_cpu_seconds_sampled=final_cpu,
                  peak_private_bytes=peak, input_sha256=meta['input_sha256'], native_sha256=meta['native_sha256'],
                  first_progress=first_progress, verdict='UNKNOWN')
    if logic:
        result.update(final_conflicts=logic[-1][0], final_decisions=logic[-1][1], final_propagations=logic[-1][2])
    if progress:
        result['final_cuts'] = progress[-1][2]
    if first_progress and logic and progress and final_cpu and final_cpu > first_progress['cpu']:
        cpu = final_cpu - first_progress['cpu']
        result['window_cpu_seconds'] = cpu
        for name, value in (('conflicts', logic[-1][0]), ('decisions', logic[-1][1]),
                            ('propagations', logic[-1][2]), ('cuts', progress[-1][2])):
            result[name + '_per_cpu_second'] = (value - first_progress[name]) / cpu
    # Flat-counter pathology: a >=60 s stretch of progress lines with unchanged conflicts.
    flat = 0.0
    pairs = list(zip(progress, logic))
    for (p0, l0), (p1, l1) in zip(pairs, pairs[1:]):
        flat = flat + (p1[0] - p0[0]) if l1[0] == l0[0] else 0.0
        result['flat_counter_pathology'] = result.get('flat_counter_pathology', False) or flat >= 60
    result.setdefault('flat_counter_pathology', False)
    status = {0: 'NATIVE_UNKNOWN', 10: 'SAT_SIGNAL_REQUIRES_PROMINENT_REVIEW',
              20: 'NATIVE_UNSAT_PENDING_FRESH_DRAT_AND_INDEPENDENT_CHECK'}.get(code, 'NATIVE_FAILURE_REQUIRES_REVIEW')
    result['status'] = status
    atomic_json(directory / 'native-RESULT.json', result)
    if code != 0:
        rows = read_json(CONTROL / 'COLD_TERMINAL.json').get('results', []) if (CONTROL / 'COLD_TERMINAL.json').exists() else []
        rows.append(dict(region=region, directory=str(directory), returncode=code, status=status, worker=worker))
        atomic_json(CONTROL / 'COLD_TERMINAL.json', dict(results=rows, no_region_promoted=True, updated_epoch=time.time()))
    result['audit'] = audit_cuts(region, directory)
    atomic_json(directory / 'native-RESULT.json', result)
    journal(COLD / 'JOURNAL.jsonl', 'cold_finished', **{k: v for k, v in result.items() if k != 'audit'},
            audited=result['audit'].get('count'))
    if code == 20:
        with_ledger(lambda data: data['regions'].setdefault(str(region), {}).setdefault('pending_proofs', []).append(
            dict(directory=str(directory), recipe_key=meta['recipe_key'], status=status)))
    if code == 0:
        # UNKNOWN: the exact input is reproducible from INPUT.json; release this hard link.
        (directory / 'input.inst').unlink()
    return result


def with_ledger(update):
    data = load_ledger()
    update(data)
    atomic_json(ledger_path(), data)
    return data


def audit_cuts(region, directory):
    """Independently subdivision-check every complete new clause before reuse."""
    from s035_engine import subdivision
    cfg = read_json(AREA / 'CONFIG.json')
    source = Path(directory) / 'new-cuts.lem'
    if not source.exists() or not source.stat().st_size:
        return dict(count=0)
    pairs = cfg['pairs']
    h = hashlib.sha256(); count = 0
    temp = Path(directory) / 'audit.part'
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
    target = Path(directory) / ('a-' + h.hexdigest()[:16] + '.lem')
    os.replace(temp, target)
    row = dict(path=str(target), count=count, sha256=h.hexdigest(), audit='INDEPENDENT_SUBDIVISION_PASS',
               n=cfg['n'], origin=str(source), region=region, session='S036')
    atomic_json(target.with_suffix('.audit.json'), row)
    with_ledger(lambda data: data['regions'].setdefault(str(region), {}).setdefault('audited_blocks', []).append(row))
    return row


TERMINAL_GATES = ('S036_STOP_LATCHED', 'SAT_ALERT_PRESENT', 'CONTROLLER_NOT_RUNNING:PAUSED')


def wait_admission(max_wait):
    """Wait for the measured admission gate; stop at once on STOP, SAT or a paused controller."""
    end = time.monotonic() + max_wait
    while True:
        reason = gates(admission=True)
        if reason is None:
            return None
        if reason.startswith(TERMINAL_GATES) or time.monotonic() >= end:
            return reason
        time.sleep(30)


def summary_path():
    return COLD / 'DIAGNOSTIC_SUMMARY.json'


def diagnose(regions, arm_names, budget, max_wait, max_yields=6):
    """Each arm counts only when it runs its full budget; a yielded attempt is retried later."""
    arms = [a for a in read_json(ARMS)['arms'] if not arm_names or a['name'] in arm_names]
    summary = read_json(summary_path())['rows'] if summary_path().exists() else []
    done = {(r['region'], r['arm']) for r in summary if r.get('purpose') == 'diag' and r.get('returncode') == 0
            and not r.get('yield_reason')}
    for region in regions:
        todo = [a for a in arms if (region, a['name']) not in done]
        if not todo:
            continue
        source, meta = materialise_region(region)
        journal(COLD / 'JOURNAL.jsonl', 'cold_region_input', region=region, input_sha256=meta['input_sha256'],
                recipe_key=meta['recipe_key'], sources=len(meta['recipe']['sources']))
        for arm in todo:
            yields = 0
            while True:
                reason = wait_admission(max_wait)
                if reason:
                    summary.append(dict(region=region, arm=arm['name'], status='NOT_ADMITTED', reason=reason,
                                        epoch=time.time()))
                    atomic_json(summary_path(), dict(rows=summary, verdict='UNKNOWN', updated_epoch=time.time()))
                    journal(COLD / 'JOURNAL.jsonl', 'cold_not_admitted', region=region, arm=arm['name'], reason=reason)
                    return summary
                result = run_arm(region, arm, source, meta, budget, 'diag')
                result['counted'] = result['returncode'] == 0 and not result['yield_reason']
                summary.append(result)
                atomic_json(summary_path(), dict(rows=summary, verdict='UNKNOWN', updated_epoch=time.time()))
                if result['returncode'] != 0:
                    return summary
                if result['counted']:
                    break
                yields += 1
                if yields >= max_yields:
                    journal(COLD / 'JOURNAL.jsonl', 'cold_arm_abandoned_after_yields', region=region,
                            arm=arm['name'], yields=yields)
                    return summary
                time.sleep(120)
        source.unlink()
    return summary


def adopt(summary):
    """Apply the pre-registered adoption rule (validation/S036/DIAGNOSTIC_ARMS.json) mechanically."""
    registered = read_json(ARMS)
    counted = [r for r in summary if r.get('purpose') == 'diag' and r.get('counted')]
    regions = {}
    for region in COLD_REGIONS:
        rows = {r['arm']: r for r in counted if r['region'] == region}
        base = rows.get('baseline')
        decision = dict(arm='baseline', reason='baseline kept')
        if base is None or 'conflicts_per_cpu_second' not in base:
            decision['reason'] = 'baseline arm missing or unmeasured; baseline kept'
        else:
            qualified = []
            for name, row in rows.items():
                if name == 'baseline':
                    continue
                checks = dict(exit_by_timeout=row['returncode'] == 0 and not row.get('yield_reason'),
                              no_pathology=not row.get('flat_counter_pathology'),
                              memory=row.get('peak_private_bytes', 1 << 62) <= 1.5 * GiB,
                              conflicts=row.get('conflicts_per_cpu_second', 0) >= 1.5 * base['conflicts_per_cpu_second'],
                              cuts=row.get('cuts_per_cpu_second', 0) >= 0.75 * base.get('cuts_per_cpu_second', 0))
                decision.setdefault('checks', {})[name] = checks
                if all(checks.values()):
                    qualified.append((row['conflicts_per_cpu_second'], name))
            if qualified:
                best = max(qualified)
                decision.update(arm=best[1], reason='registered rule satisfied (highest conflicts/CPU-s among qualifiers)')
        decision['measured_arms'] = sorted(rows)
        regions[str(region)] = decision
    value = dict(status='ADOPTION_BY_REGISTERED_RULE', rule=registered['adoption_rule'], regions=regions,
                 interpretation_limits=registered['interpretation_limits'], epoch=time.time())
    atomic_json(COLD / 'ARM_ADOPTION.json', value)
    journal(COLD / 'JOURNAL.jsonl', 'cold_arm_adoption', regions={k: v['arm'] for k, v in regions.items()})
    return value


def adopted_arm(region):
    arms = {a['name']: a for a in read_json(ARMS)['arms']}
    adoption = read_json(COLD / 'ARM_ADOPTION.json') if (COLD / 'ARM_ADOPTION.json').exists() else {}
    return arms[adoption.get('regions', {}).get(str(region), {}).get('arm', 'baseline')]


def rotate(span, max_wait):
    """Fair round-robin over cold regions; each span ends naturally or cooperatively."""
    state_path = COLD / 'ROTATION.json'
    state = read_json(state_path) if state_path.exists() else dict(next_index=0, spans=[])
    while True:
        region = COLD_REGIONS[state['next_index'] % len(COLD_REGIONS)]
        reason = wait_admission(max_wait)
        if reason:
            journal(COLD / 'JOURNAL.jsonl', 'cold_rotation_stopped', reason=reason)
            return state
        source, meta = materialise_region(region)
        result = run_arm(region, adopted_arm(region), source, meta, span, 'span')
        source.unlink()
        state['spans'].append({k: result.get(k) for k in ('region', 'arm', 'returncode', 'yield_reason', 'wall_seconds',
                                                          'final_conflicts', 'final_cuts', 'peak_private_bytes')})
        if result['returncode'] != 0:
            atomic_json(state_path, state)
            return state
        # A span that yielded early is resumed later for the same region (semantic
        # cuts kept); only a span that ran its full budget advances the rotation.
        if not result['yield_reason']:
            state['next_index'] += 1
        atomic_json(state_path, state)
        if result['yield_reason']:
            time.sleep(120)


def campaign(regions, budget, span, max_wait):
    """Finish registered diagnostics, adopt by the registered rule, then rotate fairly."""
    arms = read_json(ARMS)['arms']
    summary = diagnose(regions, [], budget, max_wait)
    done = {(r['region'], r['arm']) for r in summary if r.get('purpose') == 'diag' and r.get('counted')}
    missing = [(g, a['name']) for g in regions for a in arms if (g, a['name']) not in done]
    if missing:
        journal(COLD / 'JOURNAL.jsonl', 'cold_campaign_stopped_before_adoption', missing=len(missing))
        return dict(status='DIAGNOSTICS_INCOMPLETE', missing=missing)
    adoption = adopt(summary)
    state = rotate(span, max_wait)
    return dict(status='ROTATION_STOPPED', adoption={k: v['arm'] for k, v in adoption['regions'].items()},
                spans=len(state['spans']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('diagnose', 'rotate', 'campaign', 'status'))
    parser.add_argument('--regions', default='1,3,15,31,63')
    parser.add_argument('--arms', default='')
    parser.add_argument('--budget', type=float, default=360)
    parser.add_argument('--span', type=float, default=14400)
    parser.add_argument('--max-wait', type=float, default=600)
    args = parser.parse_args()
    COLD.mkdir(parents=True, exist_ok=True)
    regions = [int(x) for x in args.regions.split(',') if x]
    assert set(regions) <= set(COLD_REGIONS), 'Cold slot runs cold regions only'
    if args.action == 'status':
        print(json.dumps(dict(slot=read_json(CONTROL / 'COLD_SLOT.json') if (CONTROL / 'COLD_SLOT.json').exists() else None,
                              ledger=load_ledger()), indent=1)); return
    lock = COLD / 'RUNNER.lock'
    from s035_windows import locked
    # campaign queues behind any runner already holding the slot; at most one
    # cold native process can exist because every run_arm happens under this lock.
    with locked(lock, blocking=args.action == 'campaign'):
        if args.action == 'campaign':
            print(json.dumps(campaign(regions, args.budget, args.span, args.max_wait), indent=1))
        elif args.action == 'diagnose':
            rows = diagnose(regions, [a for a in args.arms.split(',') if a], args.budget, args.max_wait)
            print(json.dumps([{k: r.get(k) for k in ('region', 'arm', 'returncode', 'status', 'yield_reason',
                                                      'conflicts_per_cpu_second', 'cuts_per_cpu_second',
                                                      'peak_private_bytes')} for r in rows], indent=1))
        elif args.action == 'rotate':
            print(json.dumps(rotate(args.span, args.max_wait), indent=1))


if __name__ == '__main__':
    main()
