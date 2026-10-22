"""S035 Windows multiworker campaign, durable guardian, status and STOP."""
import argparse
from datetime import datetime, timezone

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
from s035_windows import read_json, locked, inhibit_sleep, tree_sample, atomic_json, journal, memory_available
import shutil

from s035_regions import (create, ledger, process_identity, recover, report, sha, stop_group, utc, time_left)
from s035_resident_engine import Campaign, recover

DEFAULT = ROOT/'artifacts/tmp/S035/campaign'
DEADLINE = None


def guardian(area):
    area = Path(area).resolve()
    config = json.loads((area/'CONFIG.json').read_text())
    if config.get('scientific'):
        for name, digest in config['source_sha256'].items():
            assert sha(ROOT/name) == digest, 'Scientific source gate mismatch'
        assert sha(config['native']) == config['native_sha256']
    with locked(area/'GUARDIAN.lock', blocking=False):
        with locked(area/'CONTROLLER.lock', blocking=False):
            recover(area)
        interrupted = []
        def handler(signum, frame):
            interrupted.append(signum)
            (area/'STOP').touch()
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, handler)
        try:
            import psutil
            psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            nice = True
        except OSError:
            nice = False
        restarts = []
        child = None
        reason = None
        inhibit_sleep(True)
        try:
            while time_left(config) > 0 and not interrupted and not (area/'STOP').exists():
                recover(area)
                env = os.environ.copy()
                env['S035_GUARDIAN_PID'] = str(os.getpid())
                env['S035_GUARDIAN_START'] = process_identity(os.getpid())
                with (area/'controller-process.log').open('a') as log:
                    child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'controller',
                                              '--directory', str(area)], env=env, stdout=log,
                                             stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
                identity = dict(pid=child.pid, start_ticks=process_identity(child.pid))
                child_started=time.time()
                journal(area/'JOURNAL.jsonl', 'controller_started', **identity)
                next_heartbeat = 0
                while child.poll() is None:
                    remaining = time_left(config)
                    sample = tree_sample(os.getpid())
                    unsafe = None
                    if sample['private'] > config['rss_cap_kib']*1024: unsafe='SAFETY_AGGREGATE_PRIVATE_CAP'
                    if memory_available() < config['available_floor_kib']: unsafe='SAFETY_LOW_MEMORY_PRESSURE'
                    if shutil.disk_usage(ROOT).free < config['disk_reserve_bytes']: unsafe='SAFETY_DISK_RESERVE'
                    if (area/'CONTROLLER.json').exists() and time.time()-max(child_started,(area/'CONTROLLER.json').stat().st_mtime) > 120:
                        unsafe='SAFETY_STALE_CONTROLLER'
                    if unsafe:
                        reason=unsafe
                        (area/'STOP').touch()
                    if time.time() >= next_heartbeat:
                        atomic_json(area/'GUARDIAN.json', dict(status='RUNNING', pid=os.getpid(),
                            start_ticks=process_identity(os.getpid()), controller=identity,
                            deadline=config['deadline'], updated_utc=utc(), restarts=len(restarts),
                            lower_priority_requested=nice, sleep_inhibition=True, sample=tree_sample(os.getpid()), thermal='UNAVAILABLE', verdict='UNKNOWN'))
                        next_heartbeat = time.time()+10
                    if remaining <= 0 or interrupted or (area/'STOP').exists():
                        reason = reason or ('DEADLINE' if remaining <= 0 else 'OWNER_STOP')
                        # Stop every identified native/proof group, independent of the controller.
                        with ledger(area) as data:
                            for cell in data['cells']:
                                if cell['claim']:
                                    stop_group(cell['claim'].get('worker'))
                        try:
                            (area/'STOP').touch()
                            child.wait(timeout=15)
                        except subprocess.TimeoutExpired:
                            stop_group(identity); child.wait()
                        break
                    time.sleep(min(1, max(.01, remaining)))
                state = read_json(area/'CONTROLLER.json')
                why = state.get('reason')
                if reason or why == 'DEADLINE' or why and (why.startswith('SAFETY_') or why in
                        ('OWNER_STOP', 'OWNER_OR_GUARDIAN_STOP', 'PROOF_CHECK_FAILURE', 'PROOF_PROCESS_FAILURE',
                         'UNEXPECTED_NATIVE_EXIT', 'CONTROLLER_WORKER_ERROR', 'SAT_CANDIDATE_REQUIRES_DOMAIN_REVIEW', 'ENCODED_QUEUE_CLOSED_PENDING_DOMAIN_AUDIT')):
                    reason = reason or why
                    break
                restarts = [t for t in restarts if time.time()-t < 900]
                restarts.append(time.time())
                journal(area/'JOURNAL.jsonl', 'controller_restart', returncode=child.returncode, count=len(restarts))
                if len(restarts) >= 3:
                    reason = 'UNSTABLE_REPEATED_CONTROLLER_CRASH'
                    break
                time.sleep(min(2, max(0, time_left(config))))
            reason = reason or ('DEADLINE' if time_left(config) <= 0 else 'OWNER_STOP')
        finally:
            if child is not None and child.poll() is None:
                try:
                    (area/'STOP').touch(); child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    stop_group(dict(pid=child.pid, start_ticks=process_identity(child.pid))); child.wait()
            recover(area)
            inhibit_sleep(False)
            value = dict(status='STOPPED', reason=reason, deadline=config['deadline'], stopped_utc=utc(),
                         verdict='UNKNOWN', whole_stratum_certified=False)
            atomic_json(area/'GUARDIAN.json', value)
            atomic_json(area/'STOPPED.json', {**value, 'progress': report(area)})
            journal(area/'JOURNAL.jsonl', 'guardian_stopped', reason=reason)
            print(json.dumps(value), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['guard', 'controller', 'status', 'stop', 'recover'])
    parser.add_argument('--directory', type=Path, default=DEFAULT)
    parser.add_argument('--deadline', default=DEADLINE)
    args = parser.parse_args()
    area = args.directory.resolve()
    if args.action == 'status':
        value=report(area)
        path=area/'RESIDENT_CONTEXTS.json'
        contexts=read_json(path).get('contexts',{}) if path.exists() else {}
        value['resident_contexts']={k:{name:v.get(name) for name in ('cell','state','turns','directory','active_seconds','worker')} for k,v in contexts.items()}
        value['resident_policy']='Per-region CDCL retained in RAM across turns; no cross-region Boolean sharing; no durable CDCL snapshot'
        value['warning']='Encoded domain only; no percentage or ETA; crash recovery retains semantic checkpoints, not RAM state'
        print(json.dumps(value, indent=2))
    elif args.action == 'stop':
        (area/'STOP').touch()
        print('STOP requested; regions remain UNKNOWN unless independently proof-closed')
    elif args.action == 'recover':
        with locked(area/'CONTROLLER.lock', blocking=False):
            recover(area)
    elif args.action == 'controller':
        assert os.environ.get('S035_GUARDIAN_PID'), 'Internal action: start the durable guard instead'
        Campaign(area).run()
    else:
        guardian(area)


if __name__ == '__main__':
    main()
