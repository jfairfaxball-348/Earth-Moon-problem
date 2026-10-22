"""Windows lifecycle primitives. Identity uses creation time; locks cover threads and processes."""
from contextlib import contextmanager
import ctypes
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import threading
import time
import uuid
import psutil

COMPILER_BIN=Path(__file__).resolve().parents[1]/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin'
os.environ['PATH']=str(COMPILER_BIN)+os.pathsep+os.environ['PATH']

_locks = {}
_guard = threading.Lock()
_writes = threading.RLock()

@contextmanager
def locked(path, blocking=True):
    path = str(Path(path).resolve())
    with _guard:
        mutex = _locks.setdefault(path, threading.RLock())
    if not mutex.acquire(blocking=blocking):
        raise BlockingIOError(path)
    try:
        with open(path, 'a+b') as f:
            if not Path(path).stat().st_size:
                f.write(b'0'); f.flush()
            while True:
                try:
                    f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if not blocking:
                        raise BlockingIOError(path)
                    time.sleep(.05)
            try:
                yield f
            finally:
                f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    finally:
        mutex.release()

def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=1); f.write('\n'); f.flush(); os.fsync(f.fileno())
    for i in range(100):
        try:
            os.replace(temp, path); return
        except PermissionError:
            time.sleep(.01)
    raise RuntimeError('Atomic replace unavailable: '+str(path))

def read_json(path):
    for i in range(100):
        try:
            return json.loads(Path(path).read_text())
        except PermissionError:
            time.sleep(.01)
    raise RuntimeError('Read unavailable: '+str(path))

def journal(path, kind, **fields):
    from datetime import datetime, timezone
    with _writes:
        with Path(path).open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(dict(kind=kind, utc=datetime.now(timezone.utc).isoformat(), **fields))+'\n')
            f.flush(); os.fsync(f.fileno())

def process_identity(pid):
    try:
        return str(psutil.Process(pid).create_time())
    except psutil.Error as exc:
        raise OSError(str(exc)) from exc

def live_identity(pid, ticks):
    try:
        return pid > 0 and process_identity(pid) == ticks
    except OSError:
        return False

def stop_group(record):
    if record and live_identity(record['pid'], record['start_ticks']):
        subprocess.run(['taskkill', '/PID', str(record['pid']), '/T', '/F'],
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

def memory_available():
    return psutil.virtual_memory().available//1024

def temperatures():
    # Windows exposes no reliable core sensor through psutil. No thermal guarantee.
    return {}

def tree_sample(pid):
    try:
        root = psutil.Process(pid); processes = [root, *root.children(recursive=True)]
    except psutil.Error:
        return dict(private=0, rss=0, cpu=0, processes=0)
    private = rss = cpu = 0
    for p in processes:
        try:
            m = p.memory_info(); c = p.cpu_times()
            private += m.private; rss += m.rss; cpu += c.user+c.system
        except psutil.Error:
            pass
    return dict(private=private, rss=rss, cpu=cpu, processes=len(processes))

def observed_tree_bytes(pid):
    return tree_sample(pid)['private']

def directory_bytes(path):
    total=0
    for p in Path(path).rglob('*'):
        try:
            if p.is_file(): total+=p.stat().st_size
        except FileNotFoundError:
            pass
    return total

def inhibit_sleep(enable):
    flags = 0x80000000 | (0x00000001 if enable else 0)
    result = ctypes.windll.kernel32.SetThreadExecutionState(flags)
    assert result, 'Windows sleep-inhibition request failed'

class LockCompat:
    LOCK_EX=1; LOCK_NB=2
    def flock(self, f, flags):
        ctx=locked(f.name, blocking=not bool(flags & self.LOCK_NB)); ctx.__enter__()
        # Retain the context until this file closes, matching POSIX lock lifetime.
        original=f.close
        def close():
            ctx.__exit__(None,None,None); original()
        f.close=close

fcntl = LockCompat()
