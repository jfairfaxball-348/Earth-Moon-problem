"""S046 slice controller: S045 protocol with arm encodings, CPU metering and tail audits.

Derived from tools/s045_driver.py (frozen). Loading and solving keep separate
clocks; the first stop cause wins; every candidate's two rotation systems and
nine-colouring are independently checked before feedback. Native UNSAT is
latched as UNKNOWN pending a standalone proof. Lazy re-addition: a candidate
properly coloured by an archived (non-resident) audited colouring is answered
with that colouring, re-adding its necessary clause; no new record is made.
"""
import itertools as it
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

import networkx as nx
import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import s046_encode as enc
from s045_policy import CampaignStop, deadline_reason, latch_stop, read_cause, slice_timeout
from s045_verify import check_pair, check_colouring, partition_clause
from s045_search import colouring, atomic, append, sha, env, identity, private_bytes
from s037_certificates import subdivision

EXE = ROOT / 'artifacts/tmp/S045/watchdog-native/bipsat_s045.exe'
EXE_SHA256 = None  # recorded per slice
CORE = ['tools/s046_driver.py', 'tools/s046_encode.py', 'tools/s045_native.cpp', 'tools/s045_main.hpp',
        'tools/s045_verify.py', 'tools/s045_policy.py', 'tools/s045_search.py']


def reason(available_floor=1.5 * 2**30, disk_floor=10 * 2**30, hard=3 * 2**30):
    if psutil.virtual_memory().available < available_floor:
        return 'AVAILABLE_RAM_FLOOR'
    if psutil.disk_usage(str(ROOT)).free < disk_floor:
        return 'DISK_RESERVE'
    if private_bytes() > hard:
        return 'PRIVATE_MEMORY_LIMIT'
    return None


def audit_tail(path, n, offset=0, cancel=None):
    """Check every geometric clause written after byte offset as a Kuratowski subdivision."""
    path = Path(path)
    if not path.exists():
        return 0, 0
    pairs = list(it.combinations(range(n), 2))
    count = 0
    with path.open('rb') as f:
        f.seek(offset)
        for index, raw in enumerate(f):
            if cancel and index % 1024 == 0:
                cancel()
            line = raw.decode('ascii')
            assert line.endswith('\n'), 'incomplete geometric journal'
            xs = list(map(int, line.split()))
            assert xs and xs[-1] == 0
            xs = xs[:-1]
            assert xs and len(xs) == len(set(xs)) and all(-2 * len(pairs) <= x < 0 for x in xs)
            assert len({(-x - 1) % 2 for x in xs}) == 1
            subdivision([pairs[(-x - 1) // 2] for x in xs])
            count += 1
        end = f.tell()
    return count, end


class Lazy:
    """Archived audited colourings enforced lazily (bit-parallel proper-colouring test)."""

    def __init__(self, n, colourings):
        self.n = n
        self.pairs = list(it.combinations(range(n), 2))
        a = np.array([[c[x] == c[y] for x, y in self.pairs] for c in colourings], dtype=bool)
        self.same = np.packbits(a, axis=1) if len(colourings) else np.zeros((0, (len(self.pairs) + 7) // 8), np.uint8)
        self.colourings = [list(c) for c in colourings]

    def violated(self, union_bits):
        if not len(self.colourings):
            return None
        u = np.packbits(np.array(union_bits, dtype=bool))
        hit = ~np.any(self.same & u, axis=1)  # no same-class union edge: colouring proper
        idx = np.flatnonzero(hit)
        return int(idx[0]) if len(idx) else None


def run_slice(out, n, k, seconds, arm, positive=True, partition_colourings=(), lazy=None,
              records_path=None, absolute_deadline=None, startup_ceiling=120, response_grace=15,
              soft_private_bytes=None, lemma_path=None, oracle_cap=60):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records_path = Path(records_path or out / 'CANDIDATES.jsonl')
    status_path = out / 'STATUS.json'
    lemmas = Path(lemma_path or out / 'PLANARITY.lem')
    started = time.monotonic()
    count = 0
    lazy_readds = 0
    last = started
    until = None if absolute_deadline is None else started + max(0, absolute_deadline - time.time())
    stage = 'ENCODING'
    p = ready = guard = error = ending = None
    stats = ''
    peak_private = 0
    native_cpu = 0.0
    me = psutil.Process()
    t = me.cpu_times()
    cpu0 = t.user + t.system
    oracle_seconds = 0.0
    base = dict(n=n, k=k, arm=arm, mode='partition', positive_phases=positive, controller=identity(me),
                started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                scientific_verdict='UNKNOWN', witness=False, domain_excluded=False,
                source_sha256={name: sha(ROOT / name) for name in CORE}, native_sha256=sha(EXE))

    def controller_cpu():
        t = me.cpu_times()
        return t.user + t.system - cpu0

    def save(state, **extra):
        atomic(status_path, dict(base, state=state, stage=stage, elapsed_seconds=time.monotonic() - started,
                                 solve_elapsed_seconds=None if ready is None else time.monotonic() - ready,
                                 candidates=count, lazy_readds=lazy_readds, peak_private_bytes=peak_private,
                                 controller_cpu_seconds=controller_cpu(), native_cpu_seconds=native_cpu,
                                 oracle_seconds=oracle_seconds, **extra))

    def cancellation():
        why = deadline_reason(absolute_deadline, time.time(), until, time.monotonic())
        if why:
            return latch_stop(out, 'EXPERIMENT_DEADLINE', stage=stage)
        if (out / 'STOP').exists():
            return read_cause(out)
        return None

    def check_cancel():
        why = cancellation()
        if why:
            raise CampaignStop(why)

    save('PREPARING')
    try:
        check_cancel()
        t_enc = time.monotonic()
        size = enc.write(out / 'BASE.inst', n, arm, k, partition_colourings)
        base['instance'] = dict(size, sha256=sha(out / 'BASE.inst'), encode_seconds=time.monotonic() - t_enc)
        pairs = enc.pairs_of(n)
        check_cancel()
        why = reason()
        if why:
            raise CampaignStop(latch_stop(out, why, stage=stage))
    except CampaignStop as e:
        stage = 'STOPPED'
        save('STOPPED', reason=str(e))
        return json.loads(status_path.read_text())
    lemma_offset = lemmas.stat().st_size if lemmas.exists() else 0
    log = (out / 'NATIVE.log').open('a', encoding='utf-8', buffering=1)
    native_stop = out / 'SLICE_STOP'
    native_stop.unlink(missing_ok=True)
    command = [str(EXE), str(out / 'BASE.inst'), str(lemmas), str(seconds), str(native_stop), str(int(positive)), 'partition']
    spawned = time.monotonic()
    p = subprocess.Popen(command, cwd=ROOT, env=env(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    base['generator'] = identity(p)
    atomic(out / 'IDENTITY.json', dict(base, command=command))
    proc = psutil.Process(p.pid)
    q = queue.Queue()

    def reader():
        for line in p.stdout:
            log.write(line)
            q.put(line.rstrip())
        q.put(None)
    thread = threading.Thread(target=reader, daemon=True)
    thread.start()

    def send(s):
        p.stdin.write(s + '\n')
        p.stdin.flush()

    def stop_native(cause):
        nonlocal guard, ending
        guard = cause
        ending = time.monotonic()
        native_stop.touch()
        try:
            send('STOP')
        except (OSError, BrokenPipeError):
            pass
    stage = 'NATIVE_LOADING'
    save('PREPARING')
    try:
        while True:
            try:
                ct = proc.cpu_times()
                native_cpu = ct.user + ct.system
            except psutil.Error:
                pass
            why = cancellation() or reason() or slice_timeout(time.monotonic(), spawned, ready, seconds,
                                                              startup_ceiling, response_grace)
            if why and guard in (None, 'MEMORY_RECYCLE'):
                stop_native(latch_stop(out, why, stage=stage))
            used = private_bytes()
            peak_private = max(peak_private, used)
            if ready is not None and soft_private_bytes is not None and guard is None and used >= soft_private_bytes:
                stop_native('MEMORY_RECYCLE')
            if ending and time.monotonic() - ending > 30:
                error = 'COOPERATIVE_STOP_FAILED:' + str(guard)
                p.terminate()
                break
            try:
                line = q.get(timeout=.1)
            except queue.Empty:
                line = ''
            if line is None:
                break
            if line.startswith('READY '):
                assert ready is None, 'duplicate native READY'
                ready = time.monotonic()
                stage = 'SOLVING'
                base['native_startup_seconds'] = ready - spawned
                base['loaded_geometric_rules'] = int(line.split()[1])
                save('RUNNING')
            if line.startswith('c S045'):
                stats = line
            if line.startswith('CAND '):
                assert ready is not None, 'candidate before native READY'
                if guard:
                    try:
                        send('STOP')
                    except (OSError, BrokenPipeError):
                        pass
                    continue
                bits = line.split()[2]
                assert len(bits) == 2 * len(pairs) and set(bits) <= {'0', '1'}
                union = [bits[2 * i] == '1' or bits[2 * i + 1] == '1' for i in range(len(pairs))]
                hit = lazy.violated(union) if lazy is not None else None
                if hit is not None:
                    cols = lazy.colourings[hit]
                    layers = [[list(e) for i, e in enumerate(pairs) if bits[2 * i + j] == '1'] for j in (0, 1)]
                    check_colouring(n, layers, cols, k)  # re-checked, then its clause is re-added
                    lazy_readds += 1
                    send('COLOR ' + str(k) + ' ' + ' '.join(map(str, cols)))
                    continue
                layers = [[list(e) for i, e in enumerate(pairs) if bits[2 * i + j] == '1'] for j in (0, 1)]
                rotations = []
                for ls in layers:
                    g = nx.Graph()
                    g.add_nodes_from(range(n))
                    g.add_edges_from(ls)
                    ok, embedding = nx.check_planarity(g)
                    assert ok, 'native nonplanar candidate'
                    rotations.append(embedding.get_data())
                check_pair(n, layers, rotations)
                remaining = max(.01, seconds - (time.monotonic() - ready))
                t_or = time.monotonic()
                answer, cols = colouring(n, layers, k, min(oracle_cap, remaining), cancellation)
                oracle_seconds += time.monotonic() - t_or
                why = cancellation()
                if why:
                    stop_native(latch_stop(out, why, stage=stage))
                    continue
                if answer is not True:
                    atomic(out / 'ALERT.json', dict(n=n, k=k, arm=arm, layers=layers, rotations=rotations,
                                                    colouring_result=answer, proof_verified=False, verdict='UNKNOWN'))
                    stop_native(latch_stop(out, 'NONCOLOUR_ALERT_UNVERIFIED' if answer is False else 'COLOUR_TIMEOUT',
                                           stage=stage))
                    continue
                check_colouring(n, layers, cols, k)
                partition_clause(n, cols)
                append(records_path, dict(n=n, k=k, arm=arm, layers=layers, rotations=rotations, colours=cols,
                                          mode='partition', bits=bits, elapsed_seconds=time.monotonic() - started))
                count += 1
                send('COLOR ' + str(k) + ' ' + ' '.join(map(str, cols)))
            if line.startswith('END 20') and guard is None:
                guard = latch_stop(out, 'NATIVE_UNSAT_UNCERTIFIED', stage=stage)
                ending = time.monotonic()
            if time.monotonic() - last >= 5:
                save('PREPARING' if ready is None else 'RUNNING', native_progress=stats)
                last = time.monotonic()
        p.wait(timeout=30)
        if p.returncode == 20 and guard in (None, 'MEMORY_RECYCLE'):
            guard = latch_stop(out, 'NATIVE_UNSAT_UNCERTIFIED', stage=stage)
    except BaseException as e:
        error = repr(e)
        guard = latch_stop(out, 'CONTROLLER_ERROR', error=error, stage=stage)
        try:
            send('STOP')
        except (OSError, BrokenPipeError):
            pass
        try:
            p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            p.terminate()
            p.wait(timeout=10)
    finally:
        thread.join(timeout=3)
        log.close()
        p.stdin.close()
        p.stdout.close()
    solve_seconds = None if ready is None else time.monotonic() - ready
    stage = 'POST_SLICE_AUDIT'
    t_audit = time.monotonic()
    cuts = None
    try:
        cuts, lemma_end = audit_tail(lemmas, n, lemma_offset)
    except AssertionError as e:
        error = error or 'GEOMETRIC_AUDIT_FAILED:' + repr(e)
    audit_seconds = time.monotonic() - t_audit
    if guard == 'MEMORY_RECYCLE' and count == 0:
        guard = latch_stop(out, 'CHECKPOINT_MEMORY_NO_PROGRESS', stage=stage)
    state = ('ERROR' if error or p.returncode not in (0, 20) else
             'STOPPED' if guard and guard != 'MEMORY_RECYCLE' else 'SLICE_COMPLETE')
    save(state, reason=guard or 'NATIVE_TIMEOUT', native_returncode=p.returncode, error=error,
         verified_geometric_cuts_new=cuts, audit_seconds=audit_seconds, solve_seconds=solve_seconds,
         native_progress=stats, lemma_offset=lemma_offset,
         candidate_journal_sha256=sha(records_path) if records_path.exists() else None)
    return json.loads(status_path.read_text())
