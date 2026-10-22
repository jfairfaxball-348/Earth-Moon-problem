"""S034 one-worker overnight campaign, durable guardian, status and STOP."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s026_supervision import atomic_json, journal
from s034_regions import (create, ledger, process_identity, recover, report, sha, stop_group, utc, time_left)
from s034_engine import Campaign

DEFAULT = ROOT/'artifacts/tmp/S034/campaign'
DEADLINE = '2026-10-22T06:00:00+00:00'


def initialise(area, deadline):
    gate = ROOT/'artifacts/tmp/S034'
    smoke = json.loads((gate/'SMOKE.json').read_text())
    controls = json.loads((gate/'NATIVE_CONTROLS.json').read_text())
    audit = json.loads((gate/'INPUT_AUDIT.json').read_text())
    scheduler = json.loads((gate/'SCHEDULER_CONTROLS.json').read_text())
    assert smoke['verdict'] == 'PASS'
    assert smoke['chromatic_rows_verified'] == smoke['chromatic_cnf_byte_matches'] == 271
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    assert controls['exhaustive_n5_fixed_graphs'] == 1024 and controls['positive24'] == controls['K33'] == 'PASS'
    assert scheduler['status'] == 'PASS' and scheduler['native_sha256'] == controls['native_sha256']
    for name, digest in scheduler['source_sha256'].items():
        assert sha(ROOT/name) == digest, 'Scheduler source changed after controls'
    assert audit['status'] == 'PASS' and audit['independently_checked_native_clauses'] == 2579937
    assert audit['base_clauses'] == 336030 and audit['variables'] == 17976
    native = gate/'native/bipsat_s034'
    assert sha(native) == controls['native_sha256']
    assert 'EMP_ABSOLUTE_DEADLINE' in (gate/'native/bipsat_s032.cpp').read_text()
    data = ROOT/'artifacts/tmp/S032'
    mapping = json.loads((data/'INPUTS.json').read_text())
    for name, digest in mapping['sha256'].items():
        assert sha(data/name) == digest
    base = data/'base.cnf'
    seed = data/'campaign/learned.lem'
    assert sha(seed) == audit['lemma_sha256'] == '6e6d88e19e3526117b1a01ea0a7f818ec7c8f950e3c379fdb380d096b10c7177'
    m = len(mapping['pairs'])
    variables = list(range(2*m+1, 3*m+1))
    units = {}
    with base.open() as source:
        assert next(source).split() == ['p', 'cnf', '17976', '336030']
        for line in source:
            cs = list(map(int, line.split()))
            if len(cs) == 2 and abs(cs[0]) in variables:
                v, b = abs(cs[0]), cs[0] > 0
                assert v not in units or units[v] == b
                units[v] = b
    deadline = datetime.fromisoformat(deadline).timestamp()
    assert deadline > time.time()
    names = ['scripts/s034_campaign.py', 'scripts/build_s034_native.py', 'scripts/verify_s034.py',
             'scripts/audit_s034_inputs.py', 'scripts/check_s034_scheduler.py',
             'tools/s034_regions.py', 'tools/s034_engine.py', 'tools/s032_subdivision.hpp',
             'scripts/audit_s033_fast.py', 'tools/s026_supervision.py']
    config = dict(session='S034', scientific=True, root=str(ROOT), deadline=deadline,
                  deadline_uk='2026-10-22T07:00:00+01:00', n=28, pairs=mapping['pairs'],
                  variables=17976, graph_variables=variables, graph_units=units,
                  edge_low=155, edge_high=156, bits=8, base=str(base), base_clauses=336030,
                  base_sha256=sha(base), mapping_sha256=sha(data/'INPUTS.json'),
                  seed=dict(path=str(seed), sha256=audit['lemma_sha256'], count=2579937),
                  native=str(native), native_sha256=sha(native),
                  cadical=str(ROOT/'artifacts/tmp/native/bin/cadical'),
                  checker=str(ROOT/'artifacts/tmp/native/bin/drat-trim'),
                  workers=1, concurrency_increase_validated=False,
                  min_visit_seconds=120, max_visit_seconds=1800,
                  rss_cap_kib=1048576, available_floor_kib=384*1024,
                  disk_reserve_bytes=4*1024**3, temperature_cap_c=45,
                  thermal_limitation='No readable temperature/PSI sensors at entry; no thermal guarantee',
                  source_sha256={name: sha(ROOT/name) for name in names})
    config['cadical_sha256'] = sha(config['cadical'])
    config['checker_sha256'] = sha(config['checker'])
    config['deadline_monotonic'] = time.monotonic()+deadline-time.time()
    create(area, config)
    print(json.dumps(report(area), indent=2))


def guardian(area):
    area = Path(area).resolve()
    config = json.loads((area/'CONFIG.json').read_text())
    if config.get('scientific'):
        for name, digest in config['source_sha256'].items():
            assert sha(ROOT/name) == digest, 'Scientific source gate mismatch'
        assert sha(config['native']) == config['native_sha256']
    with (area/'GUARDIAN.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with (area/'CONTROLLER.lock').open('a') as controller_lock:
            fcntl.flock(controller_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            recover(area)
        interrupted = []
        def handler(signum, frame):
            interrupted.append(signum)
            (area/'STOP').touch()
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, handler)
        try:
            os.nice(10)
            nice = True
        except OSError:
            nice = False
        restarts = []
        child = None
        reason = None
        try:
            while time_left(config) > 0 and not interrupted and not (area/'STOP').exists():
                recover(area)
                env = os.environ.copy()
                env['S034_GUARDIAN_PID'] = str(os.getpid())
                with (area/'controller-process.log').open('a') as log:
                    child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'controller',
                                              '--directory', str(area)], env=env, stdout=log,
                                             stderr=subprocess.STDOUT, start_new_session=True)
                identity = dict(pid=child.pid, start_ticks=process_identity(child.pid))
                journal(area/'JOURNAL.jsonl', 'controller_started', **identity)
                next_heartbeat = 0
                while child.poll() is None:
                    remaining = time_left(config)
                    if time.time() >= next_heartbeat:
                        atomic_json(area/'GUARDIAN.json', dict(status='RUNNING', pid=os.getpid(),
                            start_ticks=process_identity(os.getpid()), controller=identity,
                            deadline=config['deadline'], updated_utc=utc(), restarts=len(restarts),
                            lower_priority_requested=nice, verdict='UNKNOWN'))
                        next_heartbeat = time.time()+10
                    if remaining <= 0 or interrupted or (area/'STOP').exists():
                        reason = 'DEADLINE' if remaining <= 0 else 'OWNER_STOP'
                        # Stop every identified native/proof group, independent of the controller.
                        with ledger(area) as data:
                            for cell in data['cells']:
                                if cell['claim']:
                                    stop_group(cell['claim'].get('worker'))
                        try:
                            child.send_signal(signal.SIGTERM)
                            child.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            stop_group(identity); child.wait()
                        break
                    time.sleep(min(1, max(.01, remaining)))
                state = json.loads((area/'CONTROLLER.json').read_text())
                why = state.get('reason')
                if reason or why == 'DEADLINE' or why and (why.startswith('SAFETY_') or why in
                        ('OWNER_STOP', 'OWNER_OR_GUARDIAN_STOP', 'PROOF_CHECK_FAILURE', 'PROOF_PROCESS_FAILURE',
                         'UNEXPECTED_NATIVE_EXIT', 'CONTROLLER_WORKER_ERROR')):
                    reason = reason or why
                    break
                restarts = [t for t in restarts if time.time()-t < 900]
                restarts.append(time.time())
                journal(area/'JOURNAL.jsonl', 'controller_restart', returncode=child.returncode, count=len(restarts))
                if len(restarts) >= 3:
                    reason = 'UNSTABLE_REPEATED_CONTROLLER_CRASH'
                    break
                time.sleep(min(2, max(0, config['deadline']-time.time())))
            reason = reason or ('DEADLINE' if time_left(config) <= 0 else 'OWNER_STOP')
        finally:
            if child is not None and child.poll() is None:
                try:
                    child.send_signal(signal.SIGTERM); child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    stop_group(dict(pid=child.pid, start_ticks=process_identity(child.pid))); child.wait()
            recover(area)
            value = dict(status='STOPPED', reason=reason, deadline=config['deadline'], stopped_utc=utc(),
                         verdict='UNKNOWN', whole_stratum_certified=False)
            atomic_json(area/'GUARDIAN.json', value)
            atomic_json(area/'STOPPED.json', {**value, 'progress': report(area)})
            journal(area/'JOURNAL.jsonl', 'guardian_stopped', reason=reason)
            print(json.dumps(value), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'guard', 'controller', 'status', 'stop', 'recover'])
    parser.add_argument('--directory', type=Path, default=DEFAULT)
    parser.add_argument('--deadline', default=DEADLINE)
    args = parser.parse_args()
    area = args.directory.resolve()
    if args.action == 'init':
        initialise(area, args.deadline)
    elif args.action == 'status':
        print(json.dumps(report(area), indent=2))
    elif args.action == 'stop':
        (area/'STOP').touch()
        print('STOP requested; regions remain UNKNOWN unless independently proof-closed')
    elif args.action == 'recover':
        with (area/'CONTROLLER.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            recover(area)
    elif args.action == 'controller':
        assert os.environ.get('S034_GUARDIAN_PID'), 'Internal action: start the durable guard instead'
        Campaign(area).run()
    else:
        guardian(area)


if __name__ == '__main__':
    main()
