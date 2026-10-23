"""Windows-sharing-tolerant SAT-first scanner for S036.

Repairs the S035 WATCHER_FAILURE: an unretried ``open('rb')`` raised
PermissionError on a concurrently replaced control file, and the scan cache had
already advanced, so a recovery rescan with the same scanner could skip it.

* stat, open/read and hashing retry Windows sharing/delete-pending errors with
  bounded backoff inside one scan;
* the cache entry for a file is committed only after a complete successful read;
* a file that stays unreadable is carried as PENDING across scans and raises
  ``ScanUnavailable`` (fail closed) once its exhaustion budget is spent;
* SAT/exit-10/candidate detection is never suppressed by another file's failure:
  hits are returned first and the caller handles SAT before any unavailability.
"""
import hashlib
import re
import stat
import time
from pathlib import Path

SAT = re.compile(rb'^\s*s SATISFIABLE\s*$', re.M)
EXIT10 = re.compile(rb'"(?:returncode|exitcode|exit_code)"\s*:\s*10\b')
OVERLAP = 512
BLOCK = 1024 * 1024
SUFFIXES = ('.log', '.json', '.jsonl')
# Windows: 5 access denied (delete pending), 32 sharing violation, 33 lock violation.
SHARING_WINERRORS = (5, 32, 33)


class ScanUnavailable(RuntimeError):
    """A file stayed unreadable after bounded retries; callers must fail closed."""
    def __init__(self, failures):
        self.failures = failures
        super().__init__('SAT scan unavailable: ' + '; '.join(
            f"{row['path']} ({row['error']}, {row['attempts']} attempts, "
            f"{row['seconds']:.1f}s)" for row in failures))


def transient(exc):
    if isinstance(exc, FileNotFoundError):
        return False
    if isinstance(exc, PermissionError):
        return True
    return isinstance(exc, OSError) and getattr(exc, 'winerror', None) in SHARING_WINERRORS


def retry(operation, budget=2.0, sleep=time.sleep):
    """Run ``operation`` until it succeeds, a non-sharing error occurs or ``budget`` expires.

    Returns ``(value, attempts)``. Raises the last transient error on exhaustion
    with an ``attempts`` attribute; FileNotFoundError is never retried.
    """
    deadline = time.monotonic() + budget
    delay = .01
    attempts = 0
    while True:
        attempts += 1
        try:
            return operation(), attempts
        except OSError as exc:
            if not transient(exc) or time.monotonic() >= deadline:
                exc.attempts = attempts
                raise
        sleep(delay)
        delay = min(.25, delay * 2)


def sha(path, budget=5.0):
    def digest():
        h = hashlib.sha256()
        with Path(path).open('rb') as f:
            for block in iter(lambda: f.read(BLOCK), b''):
                h.update(block)
        return h.hexdigest()
    return retry(digest, budget)[0]


def read_text(path, budget=5.0):
    return retry(lambda: Path(path).read_text(encoding='utf-8'), budget)[0]


def contains_signal(path, start=0):
    """Read from ``start`` to EOF; detect a marker even across block boundaries."""
    with Path(path).open('rb') as f:
        f.seek(start)
        tail = b''
        for block in iter(lambda: f.read(BLOCK), b''):
            data = tail + block
            if SAT.search(data) or EXIT10.search(data):
                return True
            tail = data[-OVERLAP:]
    return False


class Scanner:
    """Cache (size, mtime) per file; rescan only changed files.

    ``attempt_budget`` bounds retries within one scan. ``exhaustion_seconds``
    bounds how long one file may remain PENDING across scans before
    ``ScanUnavailable`` is raised. ``heartbeat`` is called at most every
    ``heartbeat_seconds`` so a long scan cannot make the supervisor look stale.
    """
    IGNORED_NAMES = ('SAT_ALERT.json', 'WATCHER.json', 'WATCHER_FAILURE.json', 'GUARD_PAUSE.json',
                     'SAT_AUDIT.json')

    def __init__(self, attempt_budget=2.0, exhaustion_seconds=30.0, heartbeat=None,
                 heartbeat_seconds=.5, sleep=time.sleep):
        self.seen = {}
        self.pending = {}
        self.scanned_files = 0
        self.retried_reads = 0
        self.controls = []
        self.attempt_budget = attempt_budget
        self.exhaustion_seconds = exhaustion_seconds
        self.heartbeat = heartbeat
        self.heartbeat_seconds = heartbeat_seconds
        self.sleep = sleep
        self._beat = 0.0

    def _pulse(self):
        if self.heartbeat and time.monotonic() - self._beat >= self.heartbeat_seconds:
            self._beat = time.monotonic()
            self.heartbeat()

    def _failed(self, key, exc, attempts):
        now = time.monotonic()
        row = self.pending.setdefault(key, dict(path=key, first=now, attempts=0))
        row.update(error=repr(exc), attempts=row['attempts'] + attempts, last=now)

    def inspect(self, paths, classify_controls=False, raise_unavailable=True):
        hits = []
        for path in paths:
            self._pulse()
            path = Path(path)
            if path.suffix.lower() not in SUFFIXES:
                continue
            if path.name in self.IGNORED_NAMES or 'SAT_EVENTS' in path.parts:
                continue
            key = str(path)
            try:
                st, attempts = retry(path.stat, self.attempt_budget, self.sleep)
            except FileNotFoundError:
                self.pending.pop(key, None)
                continue
            except OSError as exc:
                self._failed(key, exc, getattr(exc, 'attempts', 1))
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            old = self.seen.get(key)
            signature = (st.st_size, st.st_mtime_ns)
            if old == signature and key not in self.pending:
                continue
            candidate = 'CANDIDATE' in path.name.upper()
            # Appends to a log are read from the previous EOF with overlap; any
            # truncation, replacement or non-log change is read in full.
            start = max(0, old[0] - OVERLAP) if (old and st.st_size >= old[0] and
                                                 path.suffix.lower() == '.log') else 0
            try:
                found, attempts = retry(lambda: contains_signal(path, start),
                                        self.attempt_budget, self.sleep)
            except FileNotFoundError:
                self.pending.pop(key, None)
                continue
            except OSError as exc:
                # Cache is NOT advanced: the next scan re-reads this file.
                self._failed(key, exc, getattr(exc, 'attempts', 1))
                if candidate:
                    hits.append(path)
                continue
            if attempts > 1:
                self.retried_reads += 1
            self.pending.pop(key, None)
            self.seen[key] = signature
            self.scanned_files += 1
            if found or candidate:
                imported_control = (classify_controls and 'imported-s034' in path.parts and
                                    any('control' in p.lower() for p in
                                        path.parts[path.parts.index('imported-s034') + 1:-1]))
                if imported_control:
                    item = dict(path=key, candidate_file=candidate)
                    try:
                        item['sha256'] = sha(path)
                    except OSError as exc:
                        item['sha256_error'] = repr(exc)
                    self.controls.append(item)
                else:
                    hits.append(path)
        if raise_unavailable and not hits:
            self.check_exhausted()
        return hits

    def exhausted(self):
        now = time.monotonic()
        return [dict(path=row['path'], error=row['error'], attempts=row['attempts'],
                     seconds=now - row['first'])
                for row in self.pending.values() if now - row['first'] >= self.exhaustion_seconds]

    def check_exhausted(self):
        failures = self.exhausted()
        if failures:
            raise ScanUnavailable(failures)
