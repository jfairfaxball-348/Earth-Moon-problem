"""Real native region workers with standalone proof gates and bounded resources."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from s035_windows import locked, tree_sample, directory_bytes, live_identity
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re

import shutil
import signal
import subprocess
import sys
import threading
import time

from s035_windows import atomic_json, journal, observed_tree_bytes
from s035_regions import (claim, checkpoint, ledger, memory_available, process_identity,
                          recover, release, safety, sha, stop_group, temperatures,
                          update_claim, utc, validate_partition, time_left)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_s033_fast import subdivision


class InterruptedAudit(Exception):
    pass


def audit_cuts(path, config, deadline, stop=None):
    """Every accepted clause is independently a one-layer K5/K33 subdivision."""
    path = Path(path)
    prefix = checkpoint(path, path.with_suffix('.checkpoint.json'))
    if not prefix or not prefix['complete_lines']:
        return None
    target = path.with_suffix('.accepted.lem')
    temp = target.with_suffix('.part')
    pairs = config['pairs']
    count = 0
    h = hashlib.sha256()
    with path.open('rb') as source, temp.open('wb') as dest:
        while source.tell() < prefix['complete_bytes']:
            if count % 1024 == 0 and (time.time() >= deadline or stop and stop.is_set()):
                raise InterruptedAudit()
            line = source.readline()
            xs = list(map(int, line.split()))
            assert xs and xs[-1] == 0
            xs = xs[:-1]
            assert xs and len(xs) == len(set(xs))
            assert all(-2*len(pairs) <= x < 0 for x in xs)
            assert len({(-x-1) % 2 for x in xs}) == 1
            edges = [tuple(pairs[(-x-1)//2]) for x in xs]
            subdivision(edges)
            dest.write(line)
            h.update(line)
            count += 1
        dest.flush()
        os.fsync(dest.fileno())
    assert count == prefix['complete_lines'] and h.hexdigest() == prefix['sha256']
    os.replace(temp, target)
    record = dict(path=str(target), count=count, sha256=h.hexdigest(),
                  audit='INDEPENDENT_SUBDIVISION_PASS', n=config['n'], utc=utc())
    atomic_json(path.with_suffix('.audit.json'), record)
    return record


def recipe(config, cut_sources, assumptions):
    return dict(n=config['n'], pairs=config['pairs'], variables=config['variables'],
                base=config['base'], base_clauses=config['base_clauses'],
                base_sha256=config['base_sha256'], sources=[config['seed'], *cut_sources],
                assumptions=assumptions, mapping_sha256=config['mapping_sha256'])


def materialise(path, value, native=False):
    sources = value['sources']
    assert sha(value['base']) == value['base_sha256']
    for source in sources:
        assert sha(source['path']) == source['sha256']
    clauses = value['base_clauses'] + sum(s['count'] for s in sources) + len(value['assumptions'])
    with Path(path).open('w', newline='\n') as dest:
        if native:
            dest.write(f"p bipsat2 {value['n']} {len(value['pairs'])} {value['variables']-2*len(value['pairs'])} {clauses}\n")
            for a, b in value['pairs']:
                dest.write(f'e {a} {b}\n')
        else:
            dest.write(f"p cnf {value['variables']} {clauses}\n")
        with Path(value['base']).open() as source:
            next(source)
            shutil.copyfileobj(source, dest)
        for row in sources:
            with Path(row['path']).open() as source:
                shutil.copyfileobj(source, dest)
        for lit in value['assumptions']:
            dest.write(f'{lit} 0\n')
        dest.flush()
        os.fsync(dest.fileno())
    return sha(path)


def independent_sat(config, native_input, log, target):
    """Candidate validation is separate from the native planarity propagator."""
    import networkx as nx
    values = {}
    for line in Path(log).read_text().splitlines():
        if line.startswith('v '):
            for x in map(int, line.split()[1:]):
                if x:
                    assert abs(x) not in values or values[abs(x)] == (x > 0)
                    values[abs(x)] = x > 0
    assert set(values) == set(range(1, config['variables']+1))
    with Path(native_input).open() as source:
        next(source)
        for _ in config['pairs']:
            next(source)
        for line in source:
            cs = list(map(int, line.split()))
            assert cs[-1] == 0 and any(values[abs(x)] == (x > 0) for x in cs[:-1])
    pairs = list(map(tuple, config['pairs']))
    layers = [[e for i, e in enumerate(pairs) if values[2*i+k+1]] for k in (0, 1)]
    graph_edges = {e for i, e in enumerate(pairs) if values[2*len(pairs)+i+1]}
    assert not set(layers[0]) & set(layers[1])
    assert set(layers[0]) | set(layers[1]) == graph_edges
    rotations = []
    for layer in layers:
        g = nx.Graph(); g.add_nodes_from(range(config['n'])); g.add_edges_from(layer)
        planar, embedding = nx.check_planarity(g, counterexample=False)
        assert planar
        embedding.check_structure()
        rotations.append({str(v): list(embedding.neighbors_cw_order(v)) for v in g})
    g = nx.Graph(); g.add_nodes_from(range(config['n'])); g.add_edges_from(graph_edges)
    colours = nx.coloring.greedy_color(g, strategy='largest_first')
    assert all(colours[a] != colours[b] for a, b in graph_edges)
    alpha3 = all(any(tuple(sorted(e)) in graph_edges for e in itertools.combinations(vs, 2))
                 for vs in itertools.combinations(range(config['n']), 4))
    if config.get('scientific'):
        assert config['n'] == 28 and alpha3 and len(graph_edges) in (155, 156)
        assert min(dict(g.degree()).values()) >= 11 and g.degree(0) == 11
    value = dict(status='INDEPENDENT_CANDIDATE_CHECK_PASS_PENDING_DOMAIN_REVIEW',
                 V=list(range(config['n'])), E1=layers[0], E2=layers[1],
                 rotations=rotations, proper_colouring=colours, alpha_at_most_3=alpha3,
                 counting_lower_bound=math.ceil(config['n']/3) if alpha3 else None,
                 proof='With alpha<=3, nine independent colour classes cover at most27 vertices; order28 forbids a9-colouring.',
                 mathematical_headline_promoted=False)
    atomic_json(target, value)
    return value


class Campaign:
    def __init__(self, area):
        self.area = Path(area).resolve()
        self.config = json.loads((self.area/'CONFIG.json').read_text())
        self.deadline = self.config.get('deadline') or float('inf')
        self.stop = threading.Event()
        self.reason = None
        self.start = time.time()
        self.disk_cache_time = 0
        self.disk_cache_bytes = 0
        self.peak = 0
        self.last_available = None
        self.active = {}
        self.active_lock = threading.Lock()
        self.cancelled = set()
        self.cooldown_until = 0

    def halt(self, reason):
        if not self.stop.is_set():
            self.reason = reason
            self.stop.set()
            journal(self.area/'JOURNAL.jsonl', 'stop_requested', reason=reason)

    def watch(self, args, directory, cell, phase, end, cuts=None):
        directory = Path(directory)
        log = directory/(phase+'.log')
        env = os.environ.copy()
        env.pop('EMP_ABSOLUTE_DEADLINE', None)
        cpu_seconds = peak_private = peak_rss = 0
        start = time.monotonic()
        p = None
        reason = None
        next_snapshot = 0
        next_status = 0
        worker = None
        try:
            with log.open('w') as output:
                p = subprocess.Popen(list(map(str, args)), stdout=output, stderr=subprocess.STDOUT,
                                     env=env, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
                worker = dict(pid=p.pid, start_ticks=process_identity(p.pid), phase=phase,
                              command=list(map(str, args)), utc=utc())
                update_claim(self.area, cell['id'], cell['claim']['token'], worker=worker, phase=phase)
                with self.active_lock:
                    self.active[cell['claim']['token']] = worker
                while p.poll() is None:
                    now = time.time()
                    sample = tree_sample(p.pid)
                    cpu_seconds = max(cpu_seconds, sample["cpu"])
                    peak_private = max(peak_private, sample["private"])
                    peak_rss = max(peak_rss, sample["rss"])
                    if sample["private"] > self.config.get("per_worker_private_bytes", 2**63):
                        reason = "PRIVATE_MEMORY_CAP"; break
                    if (directory/"proof.drat").exists() and (directory/"proof.drat").stat().st_size > self.config.get("proof_cap_bytes", 2**63):
                        reason = "PROOF_DISK_CAP"; break
                    if time_left(self.config) <= 0:
                        self.halt('DEADLINE')
                    if self.stop.is_set():
                        reason = self.reason; break
                    if cell['claim']['token'] in self.cancelled:
                        reason = 'RSS_CAPPED'; break
                    if now >= end:
                        reason = 'VISIT_QUANTUM'; break
                    if cuts and now >= next_snapshot:
                        checkpoint(cuts, directory/'CHECKPOINT.json')
                        next_snapshot = now+60
                    if now >= next_status:
                        with log.open('rb') as source:
                            source.seek(max(0, source.seek(0, 2)-65536))
                            tail = source.read().decode(errors='replace')
                        progress = re.findall(r'^c S032_(?:PROGRESS|LOGIC) .*', tail, re.M)
                        atomic_json(directory/'WORKER.json', dict(**worker, elapsed=time.monotonic()-start,
                            deadline=self.config.get('deadline'), phase_end=end, verdict='UNKNOWN', native_progress=progress[-4:]))
                        next_status = now+10
                    time.sleep(min(.5, max(.01, self.deadline-now)))
        finally:
            if p is not None:
                if p.poll() is None:
                    stop_group(worker)
                p.wait()
            if cuts:
                checkpoint(cuts, directory/'CHECKPOINT.json')
            with self.active_lock:
                self.active.pop(cell['claim']['token'], None)

        value = dict(command=list(map(str, args)), returncode=p.returncode if p else None,
                     reason=reason, wall_seconds=time.monotonic()-start,
                     aggregate_child_cpu_delta=cpu_seconds, peak_private_bytes=peak_private, peak_rss_bytes=peak_rss,
                     cpu_note='Sampled per-process tree CPU; excludes unsampled exit tail',
                     log=str(log), verdict='UNKNOWN')
        atomic_json(directory/(phase+'-RESULT.json'), value)
        return value

    def accept_cuts(self, path):
        row = audit_cuts(path, self.config, self.deadline, self.stop)
        if row:
            with ledger(self.area) as data:
                if not any(r['sha256'] == row['sha256'] for r in data['accepted_cuts']):
                    data['accepted_cuts'].append(row)
            journal(self.area/'JOURNAL.jsonl', 'cuts_accepted', cut_source=row)
        return row

    def proof(self, value, directory, cell, end):
        directory = Path(directory)
        formula = directory/'formula.cnf'
        proof = directory/'proof.drat'
        if self.stop.is_set() or time.time() >= min(end, self.deadline):
            return None
        formula_hash = materialise(formula, value)
        atomic_json(directory/'PROOF_INPUT.json', dict(recipe=value, formula_sha256=formula_hash))
        seconds = max(1, int(min(end, self.deadline)-time.time()))
        if self.stop.is_set() or time.time() >= min(end, self.deadline):
            return None
        result = self.watch([self.config['cadical'], '--no-binary', formula, proof],
                            directory, cell, 'proof', end)
        if result['reason'] or result['returncode'] != 20:
            if not result['reason'] and result['returncode'] not in (0, 10):
                self.halt('PROOF_PROCESS_FAILURE')
            return None
        seconds = max(1, int(min(end, self.deadline)-time.time()))
        checked = self.watch([self.config['checker'], formula, proof, '-t', str(seconds)],
                             directory, cell, 'check', end)
        if checked['reason']:
            return None
        if checked['returncode'] != 0 or 's VERIFIED' not in (directory/'check.log').read_text():
            if time.time() >= min(end, self.deadline)-2:
                return None
            self.halt('PROOF_CHECK_FAILURE')
            return None
        assert sha(formula) == formula_hash
        cert = dict(status='UNSAT_DRAT_VERIFIED', cell=cell['id'], assumptions=cell['assumptions'],
                    formula_sha256=formula_hash, formula_recipe=value, proof=str(proof),
                    proof_sha256=sha(proof), checker_log=str(directory/'check.log'),
                    checker_log_sha256=sha(directory/'check.log'),
                    checker_sha256=self.config['checker_sha256'], mapping_sha256=self.config['mapping_sha256'],
                    scope='Exact encoded region only; whole stratum/domain promotion requires final audit', utc=utc())
        atomic_json(directory/'CERTIFICATE.json', cert)
        return cert

    def visit(self, cell):
        token = cell['claim']['token']
        directory = Path(cell['claim']['directory'])
        started = time.time()
        with ledger(self.area) as data:
            pending = len([c for c in data['cells'] if c['status'] != 'UNSAT_DRAT_VERIFIED'])
            cuts = list(data['accepted_cuts'])
        quantum = min(self.config['max_visit_seconds'], max(self.config['min_visit_seconds'],
                      (self.deadline-time.time())/max(1, pending)))
        end = min(self.deadline, time.time()+quantum, time.time()+time_left(self.config))
        status = 'UNKNOWN'
        details = {}
        value = cell.get('pending_proof')
        try:
            if not value:
                value = recipe(self.config, cuts, cell['assumptions'])
                native_input = directory/'input.inst'
                digest = materialise(native_input, value, native=True)
                atomic_json(directory/'INPUT.json', dict(recipe=value, input_sha256=digest,
                           native_sha256=self.config['native_sha256'], fair_visit_seconds=quantum,
                           private_cdcl_state_saved=False, source_sha256=self.config['source_sha256']))
                if self.stop.is_set() or time.time() >= self.deadline:
                    return
                journal(self.area/'JOURNAL.jsonl', 'native_start', cell=cell['id'], input_sha256=digest)
                # Internal timer backs up the guardian; absolute native UTC hook is independent.
                seconds = max(1, int(min(end, self.deadline)-time.time()))
                new_cuts = directory/'new-cuts.lem'
                result = self.watch([self.config['native'], native_input, '--timeout', str(seconds),
                                     '--lemmas', new_cuts], directory, cell, 'native', end, new_cuts)
                if not self.stop.is_set():
                    own = self.accept_cuts(new_cuts)
                    if own:
                        value['sources'].append(own)
                if result['reason'] or self.stop.is_set():
                    details['last_outcome'] = result['reason'] or self.reason
                    return
                if result['returncode'] == 10:
                    candidate = independent_sat(self.config, native_input, directory/'native.log', directory/'CANDIDATE.json')
                    details.update(last_outcome='SAT_CANDIDATE_INDEPENDENT_CHECKED', candidate=str(directory/'CANDIDATE.json'))
                    journal(self.area/'JOURNAL.jsonl', 'candidate', cell=cell['id'], alpha3=candidate['alpha_at_most_3'])
                    if self.config.get('scientific'): self.halt('SAT_CANDIDATE_REQUIRES_DOMAIN_REVIEW')
                    return
                if result['returncode'] != 20:
                    details['last_outcome'] = 'NATIVE_UNKNOWN'
                    if result['returncode'] != 0:
                        self.halt('UNEXPECTED_NATIVE_EXIT')
                    return
                details['pending_proof'] = value
                with ledger(self.area) as data:
                    data['cells'][cell['id']]['pending_proof'] = value
            cert = self.proof(value, directory, cell, end)
            if cert:
                status = 'UNSAT_DRAT_VERIFIED'
                details.update(certificate=str(directory/'CERTIFICATE.json'), pending_proof=None,
                               last_outcome='INDEPENDENT_DRAT_VERIFIED')
                journal(self.area/'JOURNAL.jsonl', 'proof_closed', cell=cell['id'], certificate=details['certificate'])
            else:
                details['last_outcome'] = 'PROOF_PENDING_UNKNOWN'
        except InterruptedAudit:
            details['last_outcome'] = 'AUDIT_PENDING_UNKNOWN'
        finally:
            atomic_json(directory/'RESULT.json', dict(status=status, seconds=time.time()-started,
                        **details, whole_stratum_certified=False, verdict='UNKNOWN'))
            release(self.area, cell['id'], token, status=status, seconds=time.time()-started, **details)
            from s035_storage import compress_proof
            compress_proof(directory/'proof.drat')
            # Reproducible derived files only; source blocks, hashes, journals and proofs remain.
            for name in ('input.inst', 'formula.cnf'):
                path = directory/name
                if path.exists() and (directory/('INPUT.json' if name == 'input.inst' else 'PROOF_INPUT.json')).exists():
                    path.unlink()

    def worker_loop(self, index):
        while not self.stop.is_set():
            if time_left(self.config) <= 0:
                self.halt('DEADLINE'); break
            if time.time() < self.cooldown_until:
                self.stop.wait(.5)
                continue
            cell = claim(self.area, os.getpid(), owner=f'worker-{index}')
            if cell is None:
                with ledger(self.area) as data:
                    if all(c['status']=='UNSAT_DRAT_VERIFIED' for c in data['cells']): self.halt('ENCODED_QUEUE_CLOSED_PENDING_DOMAIN_AUDIT')
                self.stop.wait(.5)
                continue
            try:
                self.visit(cell)
            except BaseException as exc:
                journal(self.area/'JOURNAL.jsonl', 'worker_error', worker=index, error=repr(exc))
                self.halt('CONTROLLER_WORKER_ERROR')
                raise

    def run(self):
        previous = {}
        for sig in (signal.SIGINT, signal.SIGTERM):
            previous[sig] = signal.signal(sig, lambda signum, frame: self.halt('OWNER_OR_GUARDIAN_STOP'))
        low_memory = 0
        lock = locked(self.area/'CONTROLLER.lock', blocking=False)
        acquired = False
        next_heartbeat = 0
        try:
            lock.__enter__()
            acquired = True
            if acquired:
                with ledger(self.area) as data:
                    validate_partition(self.config, data['cells'])
                recover(self.area)
                # Crashed attempts retain partial proof bytes; preserve them compactly too.
                from s035_storage import compress_proof
                for path in self.area.glob('attempts/cell-*/*/proof.drat'):
                    compress_proof(path)
                # Recover unaudited complete journals without treating a crash as UNSAT.
                for path in self.area.glob('attempts/cell-*/*/new-cuts.lem'):
                    if not path.with_suffix('.audit.json').exists():
                        try:
                            self.accept_cuts(path)
                        except InterruptedAudit:
                            break
                with ThreadPoolExecutor(max_workers=self.config['workers']) as executor:
                    futures = [executor.submit(self.worker_loop, i) for i in range(self.config['workers'])]
                    while any(not f.done() for f in futures):
                        now = time.time()
                        if time_left(self.config) <= 0:
                            self.halt('DEADLINE')
                        if (self.area/'STOP').exists():
                            self.halt('OWNER_STOP')
                        try:
                            root = int(os.environ.get('S035_GUARDIAN_PID', os.getpid()))
                            if root != os.getpid() and not live_identity(root, os.environ.get('S035_GUARDIAN_START','')):
                                self.halt('SAFETY_GUARDIAN_LOST')
                            rss = observed_tree_bytes(root)//1024
                            self.peak = max(self.peak, rss)
                            issue = safety(self.config, rss)
                            if now-self.disk_cache_time > 10:
                                self.disk_cache_bytes = directory_bytes(self.area)
                                self.disk_cache_time = now
                                if directory_bytes(ROOT/'artifacts/tmp/S035') > self.config.get('total_s035_disk_bytes', 2**63): self.halt('SAFETY_TOTAL_S035_DISK_CAP')
                            if self.disk_cache_bytes > self.config.get('aggregate_disk_bytes', 2**63): issue = 'AGGREGATE_DISK_CAP'
                            self.last_available = memory_available()
                            low_memory = low_memory+1 if self.last_available is not None and self.last_available < self.config['available_floor_kib'] else 0
                            if self.last_available is None:
                                issue = 'MEMAVAILABLE_UNAVAILABLE'
                            if low_memory >= 3:
                                issue = 'LOW_MEMORY_PRESSURE'
                            thermal = temperatures()
                            if thermal and max(thermal.values()) >= self.config['temperature_cap_c']:
                                issue = 'THERMAL_CAP'
                            if issue == 'RSS_CAP':
                                self.halt('SAFETY_AGGREGATE_PRIVATE_CAP')
                            elif issue:
                                self.halt('SAFETY_'+issue)
                        except OSError:
                            self.halt('SAFETY_RSS_UNAVAILABLE')
                        except RuntimeError:
                            self.halt('SAFETY_RSS_UNAVAILABLE')
                        with self.active_lock:
                            workers = dict(self.active)
                        if now >= next_heartbeat or self.stop.is_set():
                            atomic_json(self.area/'CONTROLLER.json', dict(status='STOPPING' if self.stop.is_set() else 'RUNNING',
                                reason=self.reason, pid=os.getpid(), start_ticks=process_identity(os.getpid()),
                                deadline=self.config.get('deadline'), updated_utc=utc(), active=workers,
                                peak_aggregate_rss_kib=self.peak, available_kib=self.last_available,
                                temperatures_c=temperatures(), verdict='UNKNOWN', whole_stratum_certified=False))
                            next_heartbeat = now+10
                        time.sleep(.5)
                    for future in futures:
                        future.result()
        finally:
            if acquired:
                recover(self.area)
                atomic_json(self.area/'CONTROLLER.json', dict(status='STOPPED', reason=self.reason or 'CONTROLLER_EXIT',
                    deadline=self.config.get('deadline'), updated_utc=utc(), peak_aggregate_rss_kib=self.peak,
                    available_kib=self.last_available, verdict='UNKNOWN', whole_stratum_certified=False))
            if acquired: lock.__exit__(None,None,None)
            for sig, handler in previous.items():
                signal.signal(sig, handler)
