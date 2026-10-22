"""Atomic exact-region ledger. Claims and progress never certify a graph."""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import signal
import time
import uuid

from s026_supervision import atomic_json, journal


def utc():
    return datetime.now(timezone.utc).isoformat()


def time_left(config):
    wall = config['deadline']-time.time()
    return min(wall, config['deadline_monotonic']-time.monotonic()) if 'deadline_monotonic' in config else wall


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def process_identity(pid):
    return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]


def live_identity(pid, ticks):
    try:
        return process_identity(pid) == ticks
    except (OSError, IndexError):
        return False


def stop_group(worker):
    if not worker or not live_identity(worker['pid'], worker['start_ticks']):
        return
    try:
        os.killpg(worker['pid'], signal.SIGTERM)
        time.sleep(.15)
        if live_identity(worker['pid'], worker['start_ticks']):
            os.killpg(worker['pid'], signal.SIGKILL)
    except ProcessLookupError:
        pass


@contextmanager
def ledger(area):
    area = Path(area)
    with (area/'LEDGER.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        value = json.loads((area/'REGIONS.json').read_text())
        yield value
        atomic_json(area/'REGIONS.json', value)


def validate_partition(config, cells):
    variables = config['graph_variables']
    units = {int(k): v for k, v in config['graph_units'].items()}
    free = [v for v in variables if v not in units]
    bits = config['bits']
    assert len(cells) == 2**bits and bits <= len(free)
    assert [c['id'] for c in cells] == list(range(2**bits))
    assignments = list(itertools.product((False, True), repeat=bits))
    import math
    def weight(total, present):
        return sum(math.comb(total, m-present) for m in range(config['edge_low'], config['edge_high']+1)
                   if 0 <= m-present <= total)
    for cell, values in zip(cells, assignments, strict=True):
        expected = [v if b else -v for v, b in zip(free[:bits], values)]
        assert cell['assumptions'] == expected
        assert int(cell['weight']) == weight(len(free)-bits, sum(units.values())+sum(values))
    assert sum(int(c['weight']) for c in cells) == weight(len(free), sum(units.values()))
    return True


def create(area, config):
    area = Path(area)
    assert not area.exists(), 'Never overwrite an existing campaign'
    area.mkdir(parents=True)
    import math
    units = {int(k): v for k, v in config['graph_units'].items()}
    free = [v for v in config['graph_variables'] if v not in units]
    cells = []
    for i, values in enumerate(itertools.product((False, True), repeat=config['bits'])):
        count = sum(units.values())+sum(values)
        weight = sum(math.comb(len(free)-config['bits'], m-count)
                     for m in range(config['edge_low'], config['edge_high']+1)
                     if 0 <= m-count <= len(free)-config['bits'])
        cells.append(dict(id=i, assumptions=[v if b else -v for v, b in zip(free, values)],
                          weight=str(weight), status='UNKNOWN', visits=0, seconds=0, claim=None))
    validate_partition(config, cells)
    atomic_json(area/'CONFIG.json', config)
    atomic_json(area/'REGIONS.json', dict(cells=cells, accepted_cuts=[], created_utc=utc(),
                 mathematical_verdict='UNKNOWN', whole_stratum_certified=False))
    atomic_json(area/'CONTROLLER.json', dict(status='READY', deadline=config['deadline'],
                 verdict='UNKNOWN', workers=config.get('workers', 1)))


def claim(area, controller, owner=None):
    with ledger(area) as data:
        available = [c for c in data['cells'] if c['status'] != 'UNSAT_DRAT_VERIFIED' and c['claim'] is None]
        if not available:
            return None
        cell = min(available, key=lambda c: (c['visits'], c['seconds'], c['id']))
        token = uuid.uuid4().hex
        directory = Path(area)/'attempts'/f"cell-{cell['id']:04d}"/token
        directory.mkdir(parents=True)
        cell['visits'] += 1
        cell['claim'] = dict(token=token, controller_pid=controller, owner=owner or str(controller),
                             claimed_utc=utc(), directory=str(directory), worker=None)
        cell['last_attempt'] = str(directory)
        journal(Path(area)/'JOURNAL.jsonl', 'claim', cell=cell['id'], token=token)
        return json.loads(json.dumps(cell))


def update_claim(area, cell_id, token, **fields):
    with ledger(area) as data:
        cell = data['cells'][cell_id]
        assert cell['claim'] and cell['claim']['token'] == token, 'Lost or duplicate claim'
        cell['claim'].update(fields)


def release(area, cell_id, token, status='UNKNOWN', seconds=0, **fields):
    with ledger(area) as data:
        cell = data['cells'][cell_id]
        assert cell['claim'] and cell['claim']['token'] == token, 'Claim mismatch'
        if status == 'UNSAT_DRAT_VERIFIED':
            cert = json.loads(Path(fields['certificate']).read_text())
            assert cert['status'] == status and cert['cell'] == cell_id
            assert cert['assumptions'] == cell['assumptions']
            assert sha(cert['proof']) == cert['proof_sha256']
            assert sha(cert['checker_log']) == cert['checker_log_sha256']
        cell.update(status=status, claim=None, seconds=cell['seconds']+seconds, **fields)
        journal(Path(area)/'JOURNAL.jsonl', 'release', cell=cell_id, token=token, status=status)


def recover(area):
    with ledger(area) as data:
        for cell in data['cells']:
            old = cell['claim']
            if old:
                stop_group(old.get('worker'))
                directory = Path(old['directory'])
                checkpoint(directory/'new-cuts.lem', directory/'CHECKPOINT.json')
                atomic_json(directory/'RECOVERY.json', dict(status='RECOVERED_UNKNOWN', utc=utc(), claim=old))
                cell.update(status='UNKNOWN', claim=None)
                journal(Path(area)/'JOURNAL.jsonl', 'recover', cell=cell['id'], token=old['token'])


def checkpoint(path, target):
    path = Path(path)
    if not path.exists():
        return None
    limit = path.stat().st_size
    remaining = limit
    tail = b''
    count = size = 0
    h = hashlib.sha256()
    with path.open('rb') as source:
        os.fsync(source.fileno())
        while remaining:
            block = source.read(min(1024*1024, remaining))
            if not block:
                break
            remaining -= len(block)
            buf = tail+block
            end = buf.rfind(b'\n')+1
            complete, tail = buf[:end], buf[end:]
            count += complete.count(b'\n')
            size += len(complete)
            h.update(complete)
    record = dict(file=str(path), complete_lines=count, complete_bytes=size,
                  sha256=h.hexdigest(), omitted_tail_bytes=limit-size,
                  native_cdcl_state_saved=False, verdict='UNKNOWN', utc=utc())
    atomic_json(target, record)
    return record


def safety(config, rss_kib):
    if rss_kib > config['rss_cap_kib']:
        return 'RSS_CAP'
    if shutil.disk_usage(config['root']).free < config['disk_reserve_bytes']:
        return 'DISK_RESERVE'
    return None


def memory_available():
    try:
        return next(int(l.split()[1]) for l in Path('/proc/meminfo').read_text().splitlines()
                    if l.startswith('MemAvailable:'))
    except (OSError, StopIteration, ValueError):
        return None


def temperatures():
    values = {}
    for pattern in ('/sys/class/thermal/thermal_zone*/temp', '/sys/class/power_supply/*/temp'):
        import glob
        for name in glob.glob(pattern):
            try:
                raw = float(Path(name).read_text())
                celsius = raw/1000 if raw > 1000 else raw/10 if raw > 100 else raw
                if 0 < celsius < 150:
                    values[name] = celsius
            except (OSError, ValueError):
                pass
    return values


def report(area):
    """Pure reads: never claim cells, write a report, or start a solver."""
    area = Path(area)
    data = json.loads((area/'REGIONS.json').read_text())
    config = json.loads((area/'CONFIG.json').read_text())
    controller = json.loads((area/'CONTROLLER.json').read_text())
    guardian = json.loads((area/'GUARDIAN.json').read_text()) if (area/'GUARDIAN.json').exists() else {}
    closed = [c for c in data['cells'] if c['status'] == 'UNSAT_DRAT_VERIFIED']
    active = []
    for cell in data['cells']:
        if cell['claim']:
            value = dict(id=cell['id'], claim=cell['claim'])
            directory = Path(cell['claim']['directory'])
            for name in ('WORKER', 'CHECKPOINT'):
                path = directory/(name+'.json')
                if path.exists():
                    value[name.lower()] = json.loads(path.read_text())
            active.append(value)
    return dict(status=guardian.get('status', controller['status']), controller=controller, guardian=guardian,
                controller_process_alive=live_identity(controller.get('pid', -1), controller.get('start_ticks', '')),
                deadline=config['deadline'], total_regions=len(data['cells']),
                proof_closed_regions=len(closed), unresolved_regions=len(data['cells'])-len(closed),
                total_visits=sum(c['visits'] for c in data['cells']), active=active,
                accepted_new_clauses=sum(s['count'] for s in data['accepted_cuts']),
                proof_closed_weight=str(sum(int(c['weight']) for c in closed)),
                encoded_domain_weight=str(sum(int(c['weight']) for c in data['cells'])),
                mathematical_verdict='UNKNOWN', whole_stratum_certified=False,
                weight_meaning='Labelled graph-presence sets satisfying graph unit pins and edge count only; other CNF constraints unchecked in this denominator.',
                warning='Encoded labelled domain only; no percent-to-solution or ETA; private CDCL state not saved')
