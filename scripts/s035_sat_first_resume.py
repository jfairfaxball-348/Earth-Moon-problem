"""External SAT-first guard for identity-aware S035 RAM recovery.

This guard never launches, resumes or terminates a worker. Historical paused
sources remain unchanged. SAT signals survive STOP and validator failures.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
SCIENTIFIC = ('campaign', 'benchmark-1', 'benchmark-2', 'benchmark-3',
              'imported-s034', 'phase-diagnostic', 'phase-diagnostic-overlap-aborted',
              'phase-diagnostic-input-rebase-failure')
SAT = re.compile(rb'^\s*s SATISFIABLE\s*$', re.M)
EXIT10 = re.compile(rb'"(?:returncode|exitcode|exit_code)"\s*:\s*10\b')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {} if default is None else default


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+f'.{os.getpid()}.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=1)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)


class Scanner:
    """Cache immutable prefixes; rescan changed files without retaining logs."""
    def __init__(self):
        self.seen = {}
        self.scanned_files = 0
        self.controls = []

    def inspect(self, paths, classify_controls=False):
        hits = []
        for path in paths:
            path = Path(path)
            if not path.is_file() or path.suffix.lower() not in ('.log', '.json', '.jsonl'):
                continue
            # Never read our own alerts/evidence as new discoveries.
            if path.name in ('SAT_ALERT.json', 'WATCHER.json') or 'SAT_EVENTS' in path.parts:
                continue
            try:
                st = path.stat()
            except FileNotFoundError:
                continue
            old = self.seen.get(str(path))
            signature = (st.st_size, st.st_mtime_ns)
            if old == signature:
                continue
            self.seen[str(path)] = signature
            self.scanned_files += 1
            candidate = 'CANDIDATE' in path.name.upper()
            found = candidate
            # Log appends can be read from the prior EOF, including overlap.
            start = max(0, old[0]-512) if old and st.st_size > old[0] and path.suffix == '.log' else 0
            with path.open('rb') as f:
                f.seek(start); tail = b''
                for block in iter(lambda: f.read(1024*1024), b''):
                    data = tail+block
                    if SAT.search(data) or EXIT10.search(data):
                        found = True; break
                    tail = data[-512:]
            if found:
                item = dict(path=str(path), sha256=sha(path), candidate_file=candidate)
                # The imported historical control directory is explicitly a
                # control; a scientific path is never excused by its contents.
                imported_control = classify_controls and 'imported-s034' in path.parts and any('control' in p.lower() for p in path.parts[path.parts.index('imported-s034')+1:-1])
                if imported_control:
                    self.controls.append(item)
                else:
                    hits.append(path)
        return hits


def scientific_paths(area):
    # Cover every scientific root, rather than relying on one attempt layout.
    if area.name == 'campaign':
        for name in SCIENTIFIC:
            directory = area.parent/name
            if directory.exists():
                yield from directory.rglob('*')
    else:
        yield from area.rglob('*')


def pause_all(area, control, reason):
    """Pause exact identities idempotently; do not call legacy STOP/recover."""
    from s035_preserved_lifecycle import pause_identity
    from s035_windows import locked
    records = []
    for path in (area/'STOP', control/'STOP'):
        try:
            path.touch()
        except Exception as exc:
            records.append(dict(stage='STOP_LATCH', path=str(path), error=repr(exc)))
    identities = []
    # The new controller observes the latched STOP and releases its Windows
    # sleep inhibition in finally. Its resume mutations use the same lock.
    try:
        adoption = read(control/'ADOPTION.json')
        identities += [c['worker'] for c in adoption.get('contexts', [])]
    except Exception as exc:
        records.append(dict(stage='ADOPTION_METADATA', error=repr(exc)))
    try:
        identities += read(area/'OWNER_PAUSE.json').get('processes', [])
    except Exception as exc:
        records.append(dict(stage='FROZEN_PAUSE_METADATA', error=repr(exc)))
    if area.resolve() == (ROOT/'artifacts/tmp/S035/campaign').resolve():
        # The immutable committed pause registry is an independent fallback
        # if live metadata is damaged. PID plus creation-time guards reuse.
        try:
            identities += read(ROOT/'validation/S035/pause/OWNER_PAUSE.json')['processes']
        except Exception as exc:
            records.append(dict(stage='COMMITTED_PAUSE_METADATA', error=repr(exc)))
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
        with locked(control/'MUTATION.lock'):
            suspend_registered()
    except Exception as exc:
        records.append(dict(stage='MUTATION_LOCK', error=repr(exc)))
        # If a disk/lock failure blocks coordination, preservation still has
        # to attempt OS suspension; no forced termination is permitted.
        seen.clear()
        suspend_registered()
    # Original STOP stays latched throughout adoption. This new STOP is the
    # live control request; neither is ever removed by this supervisor.
    try:
        write(control/'GUARD_PAUSE.json', dict(reason=reason, epoch=time.time(), processes=records))
    except Exception as exc:
        records.append(dict(stage='PAUSE_RECORD', error=repr(exc)))
    return records


def preserve(path, event, inventory):
    path = Path(path)
    if not path.is_file():
        inventory.append(dict(path=str(path), missing=True)); return
    digest = sha(path); target = event/'objects'/digest
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(path, target)
    assert sha(target) == digest
    inventory.append(dict(path=str(path), sha256=digest, bytes=path.stat().st_size,
                          object=str(target)))


def handle(area, control, hits, validator=None):
    """Persist signal first, then pause, preserve and independently validate."""
    area = Path(area); control = Path(control)
    previous = read(area/'SAT_ALERT.json')
    alert = dict(status='SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW', epoch=time.time(),
                 paths=[str(p) for p in hits], ordinary_UNKNOWN_forbidden=True,
                 mathematical_headline_promoted=False, verification=[], preserved=[])
    if previous:
        alert['previous_alert'] = previous
    try:
        write(area/'SAT_ALERT.json', alert)
        write(control/'SAT_ALERT.json', alert)
    except Exception as exc:
        alert['initial_alert_write_error'] = repr(exc)
    finally:
        # OS preservation must still happen if the disk cannot accept a new
        # alert. Under the registered reserve both alert writes precede it.
        alert['paused'] = pause_all(area, control, 'SAT_SIGNAL_REQUIRES_REVIEW')
    event = control/'SAT_EVENTS'/str(time.time_ns())
    event.mkdir(parents=True)
    try:
        cfg = read(area/'CONFIG.json')
        for path in (area/'CONFIG.json', area/'REGIONS.json', area/'RESIDENT_CONTEXTS.json',
                     control/'ADOPTION.json', Path(__file__)):
            preserve(path, event, alert['preserved'])
        for name in cfg.get('source_sha256', {}):
            preserve(ROOT/name, event, alert['preserved'])
        preserve(cfg.get('native', area/'MISSING_NATIVE'), event, alert['preserved'])
        directories = {Path(p).parent for p in hits}
        terminal = read(control/'TERMINAL.json')
        directories.update(Path(r['directory']) for r in terminal.get('results', []) if r.get('returncode') == 10)
        for hit in hits:
            preserve(hit, event, alert['preserved'])
        for directory in sorted(directories):
            for name in ('native.log', 'native-RESULT.json', 'RESULT.json', 'INPUT.json',
                         'CANDIDATE.json', 'SAT_FIRST_CANDIDATE.json', 'input.inst', 'new-cuts.lem'):
                path = directory/name
                if path.exists():
                    preserve(path, event, alert['preserved'])
            source = directory/'input.inst'
            recipe = read(directory/'INPUT.json').get('recipe')
            # Resident recipes acquire later shared deltas; only immutable
            # INPUT.json binds the actual input of this native process.
            try:
                if recipe:
                    for p in [recipe['base'], *[s['path'] for s in recipe['sources']]]:
                        preserve(p, event, alert['preserved'])
                if not source.exists():
                    if not recipe:
                        raise ValueError('Exact native input/recipe unavailable; signal retained')
                    from s035_engine import materialise
                    source = event/('input-'+directory.name+'.inst')
                    materialise(source, recipe, native=True)
                    preserve(source, event, alert['preserved'])
                if validator is None:
                    from s035_sat_validation import validate_candidate
                    validator = validate_candidate
                target = event/('candidate-'+directory.name+'.json')
                validator(cfg, source, directory/'native.log', target, recipe=recipe)
                alert['verification'].append(dict(directory=str(directory),
                    status='POTENTIALLY_VALID_WITNESS_PENDING_FULL_DOMAIN_REVIEW', candidate=str(target)))
            except Exception as exc:
                alert['verification'].append(dict(directory=str(directory),
                    status='SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED', error=repr(exc)))
    except Exception as exc:
        alert['preservation_error'] = repr(exc)
    write(event/'MANIFEST.json', alert)
    write(area/'SAT_ALERT.json', alert); write(control/'SAT_ALERT.json', alert)
    print('SAT ALERT: campaign paused; prominent independent review required. '+str(area/'SAT_ALERT.json'), flush=True)
    return alert


def lease_issue(control):
    from s035_windows import live_identity
    adoption = read(control/'ADOPTION.json')
    if not adoption.get('controller'):
        return None
    # A newly published adoption has a short grace period for the first lease.
    ident = adoption['controller']
    if not live_identity(ident['pid'], ident['start_ticks']):
        return 'ADOPTED_CONTROLLER_IDENTITY_LOST'
    state = read(control/'CONTROLLER.json')
    stamp = state.get('updated_epoch', adoption.get('epoch', adoption.get('created_epoch', 0)))
    if time.time()-stamp > 5:
        return 'ADOPTED_CONTROLLER_LEASE_EXPIRED'
    return None


def pause_and_rescan(area, control, scanner, reason, validator=None):
    """Freeze writers first, then catch a SAT emitted concurrently with STOP."""
    pause_all(area, control, reason)
    hits = scanner.inspect(scientific_paths(area), classify_controls=True)
    hits += scanner.inspect([*control.glob('NATIVE_EXIT*.json'), control/'TERMINAL.json'])
    if hits:
        return handle(area, control, hits, validator=validator)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT/'artifacts/tmp/S035/campaign')
    parser.add_argument('--control-directory', type=Path)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    area = args.directory.resolve(); control = (args.control_directory or area/'RESUME_CONTROL').resolve()
    control.mkdir(parents=True, exist_ok=True)
    from s035_windows import live_identity, process_identity, locked
    scanner = Scanner(); last_full = 0; stopped = []
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.append(signum))
    with locked(control/'WATCHER.lock', blocking=False):
        identity = dict(pid=os.getpid(), start_ticks=process_identity(os.getpid()))
        source_hash = sha(Path(__file__))
        try:
            while True:
                now = time.time()
                full = now-last_full >= 30
                if full:
                    paths = scientific_paths(area); last_full = now
                else:
                    adoption = read(control/'ADOPTION.json')
                    paths = [p for c in adoption.get('contexts', []) for p in Path(c['directory']).glob('*')]
                hits = scanner.inspect(paths, classify_controls=True)
                # Native exit codes are collected through retained Windows
                # handles, even though their old Python parents stay paused.
                hits += scanner.inspect([*control.glob('NATIVE_EXIT*.json'), control/'TERMINAL.json'])
                if hits:
                    handle(area, control, hits)
                    write(control/'WATCHER.json', dict(**identity, status='SAT_ALERT', ready=False,
                        updated_epoch=time.time(), source_sha256=source_hash))
                    return
                if args.once:
                    if (area/'SAT_ALERT.json').exists():
                        print('Existing SAT ALERT requires prominent review. '+str(area/'SAT_ALERT.json'))
                        return
                    write(control/'SAT_AUDIT.json', dict(status='NO_SCIENTIFIC_SAT_OR_CANDIDATE_FOUND',
                        scanned_files=scanner.scanned_files, classified_control_hits=scanner.controls,
                        hits=[], epoch=time.time(), scientific_roots=SCIENTIFIC))
                    print('No SAT signal in all scientific roots; no process action taken.'); return
                issue = lease_issue(control)
                if issue or stopped or (control/'STOP').exists():
                    alert = pause_and_rescan(area, control, scanner, issue or 'WATCHER_OR_OWNER_STOP')
                    write(control/'WATCHER.json', dict(**identity, status='SAT_ALERT' if alert else 'PAUSED', ready=False,
                        updated_epoch=time.time(), source_sha256=source_hash))
                    return
                if (area/'SAT_ALERT.json').exists():
                    pause_all(area, control, 'EXISTING_SAT_ALERT'); return
                write(control/'WATCHER.json', dict(**identity, status='WATCHING', ready=True,
                    updated_epoch=time.time(), last_full_scan_epoch=last_full,
                    scanned_files=scanner.scanned_files, source_sha256=source_hash))
                time.sleep(.2)
        except BaseException as exc:
            try:
                pause_and_rescan(area, control, scanner, 'WATCHER_FAILURE')
            except BaseException as recovery_error:
                write(control/'WATCHER_RECOVERY_FAILURE.json', dict(error=repr(recovery_error), epoch=time.time()))
            write(control/'WATCHER_FAILURE.json', dict(error=repr(exc), epoch=time.time()))
            raise


if __name__ == '__main__':
    main()
