"""S036 owner-directed clean stop and closeout evidence (24 October 2026).

Subcommands, run in order by the operator:
  sat-scan  final SAT-first scan of every S035/S036 scientific root and exit record
  stop      after the owner preservation pause: release the cold solver, end idle
            helpers, cooperatively stop each resident through its stop file
            (brief controlled resume; natural exit), audit its final geometric tail
  reaudit   independently re-check every S036 audited geometric block (bytes, SHA256,
            clause count, Kuratowski-subdivision check of every clause)
  manifest  inventory every preserved S036 runtime file (path, bytes, SHA256)
Nothing is force-terminated. A process that does not exit cooperatively is
re-suspended and reported as a blocker. Native UNSAT never closes a region here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'scripts')]
from s035_windows import atomic_json, read_json, journal, live_identity  # noqa: E402

S035 = ROOT / 'artifacts/tmp/S035'
S036 = ROOT / 'artifacts/tmp/S036'
CONTROL = S036 / 'control'
OUT = ROOT / 'validation/S036/closeout'
S035_SCIENTIFIC = ('campaign', 'benchmark-1', 'benchmark-2', 'benchmark-3', 'imported-s034', 'phase-diagnostic',
                   'phase-diagnostic-overlap-aborted', 'phase-diagnostic-input-rebase-failure')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=1) + '\n')


def sat_scan():
    from s036_sat_scan import Scanner
    scanner = Scanner(attempt_budget=5, exhaustion_seconds=0)
    roots = [S035 / n for n in S035_SCIENTIFIC] + [S036 / 'resident', S036 / 'cold', S036 / 'recovered']
    hits = []
    for root in roots:
        if root.exists():
            hits += scanner.inspect(root.rglob('*'), classify_controls=True, raise_unavailable=False)
    records = [*CONTROL.glob('NATIVE_EXIT*.json'), CONTROL / 'TERMINAL.json', CONTROL / 'COLD_TERMINAL.json',
               CONTROL / 'SAT_ALERT.json']
    hits += scanner.inspect([p for p in records if p.exists()], raise_unavailable=False)
    unsat = []
    for root in (S036 / 'resident', S036 / 'cold'):
        for log in root.rglob('native.log'):
            with log.open('rb') as f:
                f.seek(max(0, log.stat().st_size - 4096))
                if b's UNSATISFIABLE' in f.read():
                    unsat.append(str(log))
    value = dict(status='SAT_SIGNAL_REQUIRES_PROMINENT_REVIEW' if hits else 'NO_SAT_CANDIDATE_OR_EXIT10_FOUND',
                 scanned_files=scanner.scanned_files, roots=[str(r) for r in roots],
                 hits=[dict(path=str(p), sha256=sha(p)) for p in hits], unreadable=list(scanner.pending.values()),
                 native_unsat_logs=unsat, pending_proofs=bool(unsat),
                 control_files={p.name: p.exists() for p in records}, epoch=time.time(), verdict='UNKNOWN')
    write('SAT_FINAL_AUDIT.json', value)
    print(json.dumps({k: value[k] for k in ('status', 'scanned_files', 'hits', 'unreadable', 'native_unsat_logs')}))
    return value


def tail_counters(log):
    import re
    with Path(log).open('rb') as f:
        f.seek(max(0, Path(log).stat().st_size - 8192))
        text = f.read().decode(errors='replace')
    logic = re.findall(r'^c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)', text, re.M)
    progress = re.findall(r'^c S032_PROGRESS seconds=([\d.]+) checks=(\d+) cuts=(\d+)', text, re.M)
    row = dict(cooperative_stop_marker='c S036_COOPERATIVE_STOP' in text, unknown_marker='s UNKNOWN' in text,
               sat_marker='s SATISFIABLE' in text, unsat_marker='s UNSATISFIABLE' in text)
    if logic:
        row.update(conflicts=int(logic[-1][0]), decisions=int(logic[-1][1]), propagations=int(logic[-1][2]))
    if progress:
        row.update(native_wall_seconds=float(progress[-1][0]), cuts=int(progress[-1][2]))
    return row


def wait_gone(worker, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if not live_identity(worker['pid'], worker['start_ticks']):
            return True
        time.sleep(.5)
    return False


def end_idle_helper(script):
    """End an idle helper (cold runner / autopilot) that owns no solver child; never a solver."""
    import psutil
    ended = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = p.info['cmdline'] or []
            if p.info['name'] == 'python.exe' and any(str(x).endswith(script) for x in cmd):
                if any(k.name() == 'bipsat_s032.exe' for k in p.children(recursive=True)):
                    raise RuntimeError(f'{script} still owns a solver; not ending it')
                p.terminate(); p.wait(10); ended.append(p.pid)
        except psutil.NoSuchProcess:
            pass
    return ended


def remaining_python():
    """S036 campaign Python processes still alive, excluding this closeout process and its launcher."""
    import psutil
    me = psutil.Process(os.getpid())
    mine = {me.pid, me.ppid()}
    return [p.pid for p in psutil.process_iter(['name', 'cmdline'])
            if p.info['name'] == 'python.exe' and p.pid not in mine
            and any(str(x).endswith(('s036_fresh_campaign.py', 's036_sat_supervisor.py', 's036_cold_diagnostic.py',
                                     's036_autopilot.py', 's036_resident_controller.py')) for x in (p.info['cmdline'] or []))]


def verify():
    """Re-check the end state and finalise STOP_RECORD.json."""
    import psutil
    record = json.loads((OUT / 'STOP_RECORD.json').read_text(encoding='utf-8'))
    solvers = [p.pid for p in psutil.process_iter(['name']) if p.info['name'] == 'bipsat_s032.exe']
    python = remaining_python()
    record.update(remaining_solvers=solvers, remaining_s036_python=python, verified_epoch=time.time(),
                  status='CLEAN_STOPPED' if not solvers and not python
                  and all(r['status'] == 'EXITED_COOPERATIVELY' for r in record['residents']) else 'BLOCKED',
                  self_match_note='The first evaluation counted the closeout process itself; re-verified here.')
    write('STOP_RECORD.json', record)
    print(json.dumps(dict(status=record['status'], solvers=solvers, python=python)))


def stop():
    import s036_fresh_campaign as fresh
    from s035_preserved_lifecycle import pause_identity, resume_identity
    adoption = read_json(CONTROL / 'ADOPTION.json')
    controller, watcher = read_json(CONTROL / 'CONTROLLER.json'), read_json(CONTROL / 'WATCHER.json')
    assert (CONTROL / 'OWNER_PAUSE.json').exists() and adoption['status'] == 'PAUSED', 'owner pause first'
    for record in (controller, watcher):
        assert wait_gone(record, 120), 'controller/supervisor still alive'
    assert not (CONTROL / 'SAT_ALERT.json').exists() and not (CONTROL / 'TERMINAL.json').exists()
    record = dict(owner_pause_reason=adoption['reason'], pause_errors=adoption['pause_errors'], residents=[],
                  started_epoch=time.time())
    record['cold_solver'] = fresh.release_cold_solver(CONTROL)
    time.sleep(5)
    slot = read_json(CONTROL / 'COLD_SLOT.json')
    record['cold_slot_after_release'] = dict(state=slot.get('state'), last_returncode=slot.get('last_returncode'),
                                             last_directory=slot.get('last_directory'))
    record['ended_idle_cold_runner'] = end_idle_helper('s036_cold_diagnostic.py')
    record['ended_autopilot'] = end_idle_helper('s036_autopilot.py')
    for context in adoption['contexts']:
        worker, directory = context['worker'], Path(context['directory'])
        row = dict(cell=context['cell'], generation=context.get('generation', 0), worker=worker,
                   directory=str(directory), input_sha256=context['input_sha256'])
        if live_identity(worker['pid'], worker['start_ticks']):
            Path(context['stop_file']).touch()
            resume_identity(worker, pause_identity(worker), [])
            if not wait_gone(worker, 90):
                pause_identity(worker)
                row['status'] = 'BLOCKER_DID_NOT_EXIT_COOPERATIVELY_RESUSPENDED'
                record['residents'].append(row)
                continue
        row.update(status='EXITED_COOPERATIVELY', **tail_counters(directory / 'native.log'))
        if row.get('sat_marker'):
            row['status'] = 'SAT_SIGNAL_REQUIRES_PROMINENT_REVIEW'
        row['final_tail_audit'] = fresh.audit_block(context['cell'], str(directory))
        record['residents'].append(row)
    import psutil
    record['remaining_solvers'] = [p.pid for p in psutil.process_iter(['name']) if p.info['name'] == 'bipsat_s032.exe']
    record['remaining_s036_python'] = remaining_python()
    record.update(status='CLEAN_STOPPED' if not record['remaining_solvers'] and not record['remaining_s036_python']
                  and all(r['status'] == 'EXITED_COOPERATIVELY' for r in record['residents']) else 'BLOCKED',
                  private_cdcl_retained=False, finished_epoch=time.time(), forced_terminations_of_solvers=0)
    journal(CONTROL / 'JOURNAL.jsonl', 'closeout_clean_stop', status=record['status'],
            residents=[(r['cell'], r['status']) for r in record['residents']])
    write('STOP_RECORD.json', record)
    print(json.dumps(dict(status=record['status'], residents=[(r['cell'], r['status'], r.get('conflicts'),
                          r.get('final_tail_audit', {}).get('count')) for r in record['residents']],
                          cold=record['cold_solver'], solvers=record['remaining_solvers'])))
    return record


def blocks():
    """Every S036 audited geometric block (ledger plus all a-*.lem files under S036)."""
    seen = {}
    ledger = read_json(S036 / 'cold/LEDGER.json')
    for region, row in ledger['regions'].items():
        for key in ('audited_blocks', 'span_blocks', 'diagnostic_blocks', 'closeout_blocks'):
            for b in row.get(key, []):
                seen[b['path']] = dict(b, ledger_key=key, ledger_region=int(region))
    for path in S036.rglob('a-*.lem'):
        seen.setdefault(str(path), dict(path=str(path), ledger_key=None))
    # One record per physical file (ledger paths may be absolute or repository-relative).
    unique = {}
    for row in seen.values():
        key = str((Path(row['path']) if Path(row['path']).is_absolute() else ROOT / row['path']).resolve())
        if key not in unique or unique[key].get('ledger_key') is None:
            unique[key] = row
    return list(unique.values())


def reaudit():
    from s035_engine import subdivision
    pairs = read_json(S035 / 'campaign/CONFIG.json')['pairs']
    rows = []; total = 0; started = time.time()
    for b in sorted(blocks(), key=lambda r: r['path']):
        path = Path(b['path'])
        path = path if path.is_absolute() else ROOT / path
        if not path.exists():
            rows.append(dict(path=str(path), status='MISSING')); continue
        h = hashlib.sha256(); count = 0
        with path.open('rb') as f:
            for line in f:
                assert line.endswith(b'\n'), path
                xs = list(map(int, line.split()))
                assert xs.pop() == 0 and xs and len(xs) == len(set(xs))
                assert all(-2 * len(pairs) <= x < 0 for x in xs)
                assert len({(-x - 1) % 2 for x in xs}) == 1
                subdivision([tuple(pairs[(-x - 1) // 2]) for x in xs])
                h.update(line); count += 1
        ok = (b.get('sha256') in (None, h.hexdigest())) and (b.get('count') in (None, count))
        rows.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size, sha256=h.hexdigest(),
                         clauses=count, ledger_key=b.get('ledger_key'), region=b.get('ledger_region', b.get('region')),
                         kind=b.get('kind'), status='INDEPENDENT_SUBDIVISION_PASS' if ok else 'LEDGER_MISMATCH'))
        total += count
    value = dict(status='PASS' if all(r['status'] == 'INDEPENDENT_SUBDIVISION_PASS' for r in rows) else 'FAIL',
                 blocks=len(rows), clause_occurrences=total, seconds=round(time.time() - started, 1), rows=rows,
                 note='Occurrences across blocks are not globally unique clauses; S035 ledger-accepted sources '
                      'were audited in S035 and are hash-pinned in each recipe.')
    write('CUTS_AUDIT.json', value)
    print(json.dumps({k: value[k] for k in ('status', 'blocks', 'clause_occurrences', 'seconds')}))
    return value


def manifest():
    rows = []; total = 0
    for path in sorted(p for p in S036.rglob('*') if p.is_file()):
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix == '.lock':
            continue
        size = path.stat().st_size; total += size
        rows.append(dict(path=rel, bytes=size, sha256=sha(path)))
    value = dict(status='LOCAL_RUNTIME_ARTIFACTS_PRESERVED_IN_PLACE', root='artifacts/tmp/S036', files=len(rows),
                 bytes=total, rows=rows, epoch=time.time(),
                 note='Git-ignored runtime evidence kept in place; this manifest pins every file by SHA256.')
    write('PRESERVATION_MANIFEST.json', value)
    print(json.dumps(dict(files=len(rows), gib=round(total / 2**30, 2))))
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('sat-scan', 'stop', 'verify', 'reaudit', 'manifest'))
    args = parser.parse_args()
    dict(**{'sat-scan': sat_scan, 'stop': stop, 'verify': verify, 'reaudit': reaudit,
            'manifest': manifest})[args.action]()


if __name__ == '__main__':
    main()
