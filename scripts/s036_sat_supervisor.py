"""Independent SAT-first supervisor for the S036 retained-RAM search.

Repairs the S035 WATCHER_FAILURE (PermissionError opening a concurrently
replaced ADOPTION.json, then a rescan that reused an advanced cache):

* every stat/open/hash/JSON read retries Windows sharing errors with bounded
  backoff (tools/s036_sat_scan.py); the scan cache commits only after a read;
* a file that stays unreadable past its exhaustion budget fails CLOSED: all
  registered identities are suspended first, then a complete rescan with a
  FRESH scanner runs, and the explicit reason is recorded in GUARD_PAUSE.json;
* SAT signals outrank every STOP, lease or failure path and are persisted
  before validation; validation failure never downgrades a SAT alert.

It never launches, resumes or terminates a process, and never writes inside
S035 artifacts (the historical campaign STOP is only re-latched if missing).
"""
import argparse
import os
from pathlib import Path
import shutil
import signal
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s036_sat_scan import Scanner, ScanUnavailable, retry, sha, read_text  # noqa: E402
import json  # noqa: E402

AREA = ROOT / 'artifacts/tmp/S035/campaign'
CONTROL = ROOT / 'artifacts/tmp/S036/control'
S035_SCIENTIFIC = ('campaign', 'benchmark-1', 'benchmark-2', 'benchmark-3', 'imported-s034',
                   'phase-diagnostic', 'phase-diagnostic-overlap-aborted',
                   'phase-diagnostic-input-rebase-failure')
S036_SCIENTIFIC = ('cold',)
FULL_SCAN_SECONDS = 30


def read(path, default=None):
    try:
        return json.loads(read_text(path))
    except FileNotFoundError:
        return {} if default is None else default


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.{time.time_ns()}.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=1)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    retry(lambda: os.replace(temp, path), budget=5.0)


def scientific_paths(area, control):
    """Every S035 scientific root, every S036 scientific root and S036 exit records."""
    for name in S035_SCIENTIFIC:
        directory = area.parent / name
        if directory.exists():
            yield from directory.rglob('*')
    for name in S036_SCIENTIFIC:
        directory = control.parent / name
        if directory.exists():
            yield from directory.rglob('*')
    yield from exit_records(control)


def exit_records(control):
    return [*control.glob('NATIVE_EXIT*.json'), control / 'TERMINAL.json', control / 'COLD_TERMINAL.json']


def fast_paths(control):
    adoption = read(control / 'ADOPTION.json')
    paths = [p for c in adoption.get('contexts', []) for p in Path(c['directory']).glob('*')]
    cold = read(control / 'COLD_SLOT.json')
    if cold.get('directory'):
        paths += list(Path(cold['directory']).glob('*'))
    return paths + exit_records(control)


def registered_identities(area, control, records):
    identities = []
    try:
        identities += [c['worker'] for c in read(control / 'ADOPTION.json').get('contexts', [])]
    except Exception as exc:
        records.append(dict(stage='ADOPTION_METADATA', error=repr(exc)))
    try:
        cold = read(control / 'COLD_SLOT.json')
        if cold.get('worker') and cold.get('state') == 'RUNNING':
            identities.append(cold['worker'])
    except Exception as exc:
        records.append(dict(stage='COLD_SLOT_METADATA', error=repr(exc)))
    registries = [(area / 'OWNER_PAUSE.json', 'FROZEN_PAUSE_METADATA')]
    if Path(area).resolve() == AREA.resolve():
        # The immutable committed registry is an independent fallback for the
        # real campaign only; PID plus creation time guards against reuse.
        registries.append((ROOT / 'validation/S035/pause/OWNER_PAUSE.json', 'COMMITTED_PAUSE_METADATA'))
    for path, stage in registries:
        try:
            identities += read(path).get('processes', [])
        except Exception as exc:
            records.append(dict(stage=stage, error=repr(exc)))
    return identities


def pause_all(area, control, reason, detail=None):
    """Suspend every registered exact identity idempotently; never terminate."""
    from s035_preserved_lifecycle import pause_identity
    from s035_windows import locked
    records = []
    try:
        (control / 'STOP').touch()
    except Exception as exc:
        records.append(dict(stage='S036_STOP_LATCH', error=repr(exc)))
    if not (area / 'STOP').exists():
        try:
            (area / 'STOP').touch()
            records.append(dict(stage='HISTORICAL_STOP_RELATCHED'))
        except Exception as exc:
            records.append(dict(stage='HISTORICAL_STOP_LATCH', error=repr(exc)))
    # The cold runner obeys this cooperative stop as well as the S036 STOP.
    cold = {}
    try:
        cold = read(control / 'COLD_SLOT.json')
        if cold.get('stop_file'):
            Path(cold['stop_file']).touch()
    except Exception as exc:
        records.append(dict(stage='COLD_COOPERATIVE_STOP', error=repr(exc)))
    identities = registered_identities(area, control, records)
    seen = set()

    def suspend_registered():
        for identity in identities:
            try:
                key = (identity['pid'], identity['start_ticks'])
                if key in seen or identity['pid'] == os.getpid():
                    continue
                seen.add(key)
                records.append(dict(identity=identity, pause=pause_identity(identity)))
            except Exception as exc:
                records.append(dict(identity=identity, error=repr(exc)))
    try:
        with locked(control / 'MUTATION.lock'):
            suspend_registered()
    except Exception as exc:
        records.append(dict(stage='MUTATION_LOCK', error=repr(exc)))
        seen.clear()
        suspend_registered()
    try:
        write(control / 'GUARD_PAUSE.json', dict(reason=reason, detail=detail, epoch=time.time(),
                                                 processes=records))
    except Exception as exc:
        records.append(dict(stage='PAUSE_RECORD', error=repr(exc)))
    return records


def preserve(path, event, inventory):
    path = Path(path)
    if not path.is_file():
        inventory.append(dict(path=str(path), missing=True)); return
    try:
        digest = sha(path); target = event / 'objects' / digest
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            retry(lambda: shutil.copyfile(path, target), budget=10.0)
        assert sha(target) == digest
        inventory.append(dict(path=str(path), sha256=digest, bytes=path.stat().st_size, object=str(target)))
    except Exception as exc:
        inventory.append(dict(path=str(path), error=repr(exc)))


def candidate_config(cfg, directory):
    """Cold diagnostics run the S036 native; bind validation to that exact executable."""
    meta = read(Path(directory) / 'INPUT.json')
    if meta.get('native') and meta.get('native_sha256'):
        cfg = dict(cfg, native=meta['native'], native_sha256=meta['native_sha256'])
    return cfg


def handle(area, control, hits, validator=None):
    """Persist the signal, pause everything, preserve evidence, then validate."""
    area = Path(area); control = Path(control)
    previous = read(control / 'SAT_ALERT.json')
    alert = dict(status='SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW', epoch=time.time(),
                 paths=[str(p) for p in hits], ordinary_UNKNOWN_forbidden=True,
                 mathematical_headline_promoted=False, verification=[], preserved=[])
    if previous:
        alert['previous_alert'] = previous
    try:
        write(control / 'SAT_ALERT.json', alert)
    except Exception as exc:
        alert['initial_alert_write_error'] = repr(exc)
    finally:
        alert['paused'] = pause_all(area, control, 'SAT_SIGNAL_REQUIRES_REVIEW')
    event = control / 'SAT_EVENTS' / str(time.time_ns())
    event.mkdir(parents=True)
    try:
        cfg = read(area / 'CONFIG.json')
        for path in (area / 'CONFIG.json', area / 'REGIONS.json', area / 'RESIDENT_CONTEXTS.json',
                     control / 'ADOPTION.json', control / 'COLD_SLOT.json', Path(__file__),
                     ROOT / 'tools/s036_sat_scan.py'):
            preserve(path, event, alert['preserved'])
        for name in cfg.get('source_sha256', {}):
            preserve(ROOT / name, event, alert['preserved'])
        preserve(cfg.get('native', area / 'MISSING_NATIVE'), event, alert['preserved'])
        directories = {Path(p).parent for p in hits}
        for name in ('TERMINAL.json', 'COLD_TERMINAL.json'):
            terminal = read(control / name)
            directories.update(Path(r['directory']) for r in terminal.get('results', []) if r.get('returncode') == 10)
        for hit in hits:
            preserve(hit, event, alert['preserved'])
        for directory in sorted(directories):
            for name in ('native.log', 'native-RESULT.json', 'RESULT.json', 'INPUT.json', 'CANDIDATE.json',
                         'SAT_FIRST_CANDIDATE.json', 'input.inst', 'new-cuts.lem'):
                if (directory / name).exists():
                    preserve(directory / name, event, alert['preserved'])
            try:
                meta = read(directory / 'INPUT.json')
                recipe = meta.get('recipe')
                local = candidate_config(cfg, directory)
                preserve(local.get('native', area / 'MISSING_NATIVE'), event, alert['preserved'])
                if recipe:
                    for p in [recipe['base'], *[s['path'] for s in recipe['sources']]]:
                        preserve(p, event, alert['preserved'])
                source = directory / 'input.inst'
                if not source.exists():
                    if not recipe:
                        raise ValueError('Exact native input/recipe unavailable; signal retained')
                    from s035_engine import materialise
                    source = event / ('input-' + directory.name + '.inst')
                    materialise(source, recipe, native=True)
                    preserve(source, event, alert['preserved'])
                if validator is None:
                    from s035_sat_validation import validate_candidate
                    validator = validate_candidate
                target = event / ('candidate-' + directory.name + '.json')
                validator(local, source, directory / 'native.log', target, recipe=recipe)
                alert['verification'].append(dict(directory=str(directory),
                    status='POTENTIALLY_VALID_WITNESS_PENDING_FULL_DOMAIN_REVIEW', candidate=str(target)))
            except Exception as exc:
                alert['verification'].append(dict(directory=str(directory),
                    status='SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED', error=repr(exc)))
    except Exception as exc:
        alert['preservation_error'] = repr(exc)
    write(event / 'MANIFEST.json', alert)
    write(control / 'SAT_ALERT.json', alert)
    print('SAT ALERT: S036 search paused; prominent independent review required. ' +
          str(control / 'SAT_ALERT.json'), flush=True)
    return alert


def lease_issue(control, stale_seconds=10):
    from s035_windows import live_identity
    adoption = read(control / 'ADOPTION.json')
    if not adoption.get('controller'):
        return None
    ident = adoption['controller']
    if not live_identity(ident['pid'], ident['start_ticks']):
        return 'ADOPTED_CONTROLLER_IDENTITY_LOST'
    state = read(control / 'CONTROLLER.json')
    stamp = state.get('updated_epoch', adoption.get('epoch', adoption.get('created_epoch', 0)))
    if time.time() - stamp > stale_seconds:
        return 'ADOPTED_CONTROLLER_LEASE_EXPIRED'
    return None


def final_rescan(area, control, validator=None):
    """Complete rescan with a fresh cache; unreadable files are recorded, not skipped silently."""
    scanner = Scanner(attempt_budget=5.0, exhaustion_seconds=0)
    hits = scanner.inspect(scientific_paths(area, control), classify_controls=True, raise_unavailable=False)
    unreadable = list(scanner.pending.values())
    if hits:
        return handle(area, control, hits, validator=validator), unreadable
    return None, unreadable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=AREA)
    parser.add_argument('--control-directory', type=Path, default=CONTROL)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--exhaustion-seconds', type=float, default=30.0)
    parser.add_argument('--full-scan-seconds', type=float, default=FULL_SCAN_SECONDS)
    args = parser.parse_args()
    area = args.directory.resolve(); control = args.control_directory.resolve()
    control.mkdir(parents=True, exist_ok=True)
    from s035_windows import process_identity, locked
    stopped = []
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.append(signum))
    identity = dict(pid=os.getpid(), start_ticks=process_identity(os.getpid()))
    source_hash = sha(Path(__file__)); scan_hash = sha(ROOT / 'tools/s036_sat_scan.py')
    state = dict(last_full=0.0)

    def heartbeat(status='WATCHING', ready=True, **extra):
        write(control / 'WATCHER.json', dict(**identity, status=status, ready=ready, updated_epoch=time.time(),
              last_full_scan_epoch=state['last_full'], scanned_files=scanner.scanned_files,
              retried_reads=scanner.retried_reads, pending=list(scanner.pending.values()),
              source_sha256=source_hash, scan_sha256=scan_hash, **extra))
    scanner = Scanner(attempt_budget=2.0, exhaustion_seconds=args.exhaustion_seconds,
                      heartbeat=lambda: heartbeat(scanning=True))
    with locked(control / 'WATCHER.lock', blocking=False):
        try:
            while True:
                now = time.time()
                if now - state['last_full'] >= args.full_scan_seconds:
                    paths = scientific_paths(area, control); full = True
                else:
                    paths = fast_paths(control); full = False
                hits = scanner.inspect(paths, classify_controls=True)
                if full:
                    state['last_full'] = now
                if hits:
                    handle(area, control, hits)
                    heartbeat('SAT_ALERT', False)
                    return
                if args.once:
                    if (control / 'SAT_ALERT.json').exists():
                        print('Existing SAT ALERT requires prominent review. ' + str(control / 'SAT_ALERT.json'))
                        return
                    write(control / 'SAT_AUDIT.json', dict(status='NO_SCIENTIFIC_SAT_OR_CANDIDATE_FOUND',
                        scanned_files=scanner.scanned_files, classified_control_hits=scanner.controls,
                        hits=[], epoch=time.time(), scientific_roots=[*S035_SCIENTIFIC, *S036_SCIENTIFIC]))
                    print('No SAT signal in all scientific roots; no process action taken.'); return
                issue = lease_issue(control)
                if issue or stopped or (control / 'STOP').exists():
                    reason = issue or ('SUPERVISOR_SIGNAL' if stopped else 'OWNER_OR_CONTROLLER_STOP')
                    pause_all(area, control, reason)
                    alert, unreadable = final_rescan(area, control)
                    heartbeat('SAT_ALERT' if alert else 'PAUSED', False, pause_reason=reason,
                              final_rescan_unreadable=unreadable)
                    return
                if (control / 'SAT_ALERT.json').exists():
                    pause_all(area, control, 'EXISTING_SAT_ALERT')
                    heartbeat('SAT_ALERT', False)
                    return
                heartbeat()
                time.sleep(.2)
        except BaseException as exc:
            # Fail closed: preserve first (no scan dependency), record the
            # explicit cause and traceback, then a complete fresh rescan.
            reason = 'WATCHER_SCAN_UNAVAILABLE' if isinstance(exc, ScanUnavailable) else 'WATCHER_FAILURE'
            detail = dict(error=repr(exc), traceback=traceback.format_exc(),
                          failures=getattr(exc, 'failures', None))
            try:
                pause_all(area, control, reason, detail)
            finally:
                write(control / 'WATCHER_FAILURE.json', dict(reason=reason, epoch=time.time(), **detail))
            try:
                alert, unreadable = final_rescan(area, control)
                write(control / 'WATCHER_FAILURE_RESCAN.json', dict(sat_alert=bool(alert), unreadable=unreadable,
                                                                    epoch=time.time()))
            except BaseException as recovery_error:
                write(control / 'WATCHER_RECOVERY_FAILURE.json', dict(error=repr(recovery_error),
                      traceback=traceback.format_exc(), epoch=time.time()))
            try:
                heartbeat('FAILED_CLOSED', False, failure_reason=reason)
            except BaseException:
                pass
            raise


if __name__ == '__main__':
    main()
