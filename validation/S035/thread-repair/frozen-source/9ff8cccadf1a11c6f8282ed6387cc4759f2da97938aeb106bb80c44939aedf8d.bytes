"""Identity-aware Windows suspension without termination or legacy recovery.

The old executable cannot acquire a cooperative exit hook after it is loaded.
These operations preserve it through OS suspension. They never kill, terminate,
send a console signal, or resume an unregistered thread. A finite solver result
can still exit naturally; ProcessHandle retains its exact exit status.
"""
import ctypes
from ctypes import wintypes
from pathlib import Path
import os
import time

import psutil


class LifecycleError(RuntimeError):
    pass


def identity(pid):
    p = psutil.Process(int(pid))
    return {"pid": p.pid, "start_ticks": str(p.create_time())}


def checked(record):
    try:
        p = psutil.Process(int(record["pid"]))
        if str(p.create_time()) != record["start_ticks"]:
            raise LifecycleError("Process creation-time mismatch")
        return p
    except psutil.Error as exc:
        raise LifecycleError("Registered process no longer survives") from exc


if os.name == "nt":
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenThread.restype = wintypes.HANDLE
    for name in ("SuspendThread", "ResumeThread", "GetProcessIdOfThread"):
        fn = getattr(kernel, name)
        fn.argtypes = [wintypes.HANDLE]
        fn.restype = wintypes.DWORD
    kernel.GetThreadTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.GetThreadTimes.restype = wintypes.BOOL
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL


def _failed(message):
    raise LifecycleError(message + ": " + str(ctypes.WinError(ctypes.get_last_error())))


def _change(handle, resume=False):
    n = (kernel.ResumeThread if resume else kernel.SuspendThread)(handle)
    if n == 0xffffffff:
        _failed("ResumeThread failed" if resume else "SuspendThread failed")
    return n


def _threads(record):
    """Open stable thread handles and reject an ownership/identity race."""
    if os.name != "nt":
        raise LifecycleError("Windows thread-count handling required")
    p = checked(record)
    handles = []
    try:
        for row in p.threads():
            handle = kernel.OpenThread(0x0002 | 0x0040, False, row.id)
            if not handle:
                _failed("OpenThread failed")
            handles.append((row.id, handle))
            if kernel.GetProcessIdOfThread(handle) != p.pid:
                raise LifecycleError("Thread ownership changed")
        checked(record)
        if not handles:
            raise LifecycleError("No live registered threads")
        yield handles
    finally:
        for _, handle in handles:
            kernel.CloseHandle(handle)


def _thread_stamp(handle):
    values = [wintypes.FILETIME() for _ in range(4)]
    if not kernel.GetThreadTimes(handle, *[ctypes.byref(v) for v in values]):
        _failed("GetThreadTimes failed")
    return str((values[0].dwHighDateTime << 32) | values[0].dwLowDateTime)


def thread_counts(record):
    """Inspect an already paused identity using a balanced extra suspension.

    SuspendThread returns its previous count. The matching ResumeThread only
    removes our extra count, so an originally paused thread never runs here.
    A count-zero surprise retains our protective suspension and is rejected.
    """
    from contextlib import contextmanager
    if checked(record).status() != psutil.STATUS_STOPPED:
        raise LifecycleError("Count inspection requires a paused process")
    rows = []
    with contextmanager(_threads)(record) as handles:
        for tid, handle in handles:
            previous = _change(handle)
            if previous < 1:
                raise LifecycleError("A supposedly paused thread had count zero; protective suspension retained")
            balanced = _change(handle, resume=True)
            if balanced != previous + 1:
                raise LifecycleError("Concurrent suspend-count modification")
            rows.append(dict(tid=tid, created_ticks=_thread_stamp(handle), suspend_count=previous))
    return rows


def pause_identity(record):
    """Idempotently leave every current thread suspended, preserving prior counts."""
    from contextlib import contextmanager
    previous_set = None
    # A newly started process can create a thread during our first inventory.
    # Repeat without increasing existing counts until the inventory is stable.
    for attempt in range(50):
        with contextmanager(_threads)(record) as handles:
            current_set = {tid for tid, _ in handles}
            for _, handle in handles:
                previous = _change(handle)
                if previous:
                    balanced = _change(handle, resume=True)
                    if balanced != previous + 1:
                        raise LifecycleError("Concurrent suspend-count modification")
        if current_set == previous_set and checked(record).status() == psutil.STATUS_STOPPED:
            return thread_counts(record)
        previous_set = current_set
        time.sleep(.01)
    raise LifecycleError("Process did not become fully paused after stable thread inventory")


def resume_identity(record, expected_threads):
    """Resume only a paused process whose exact thread identities/counts match."""
    from contextlib import contextmanager
    actual = thread_counts(record)
    expected = sorted(expected_threads, key=lambda row: row["tid"])
    if sorted(actual, key=lambda row: row["tid"]) != expected:
        raise LifecycleError("Suspended thread inventory/count mismatch; no resume")
    expected = {row["tid"]: row for row in expected}
    try:
        with contextmanager(_threads)(record) as handles:
            if {tid for tid, _ in handles} != set(expected):
                raise LifecycleError("Thread set changed; no resume")
            for tid, handle in handles:
                row = expected[tid]
                if _thread_stamp(handle) != row["created_ticks"]:
                    raise LifecycleError("Thread creation identity mismatch")
                for previous in range(row["suspend_count"], 0, -1):
                    if _change(handle, resume=True) != previous:
                        raise LifecycleError("Suspend count changed during resume")
        checked(record)
    except BaseException:
        # A partial resume is returned to preservation, never force-exited.
        pause_identity(record)
        raise


class ProcessHandle:
    """A retained Windows handle can report the exit code of an adopted process."""
    def __init__(self, record):
        if os.name != "nt":
            raise LifecycleError("Windows process handle required")
        self.record = dict(record)
        checked(record)
        self.handle = kernel.OpenProcess(0x1000 | 0x00100000, False, record["pid"])
        if not self.handle:
            _failed("OpenProcess failed")
        try:
            checked(record)
        except BaseException:
            self.close()
            raise

    def poll(self):
        result = kernel.WaitForSingleObject(self.handle, 0)
        if result == 258:  # WAIT_TIMEOUT; STILL_ACTIVE is not an exit result.
            return None
        if result != 0:
            _failed("WaitForSingleObject failed")
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(self.handle, ctypes.byref(code)):
            _failed("GetExitCodeProcess failed")
        return code.value

    def close(self):
        if self.handle:
            kernel.CloseHandle(self.handle)
            self.handle = None


def sample_identities(records):
    """Sample a de-duplicated registry, including suspended legacy parents."""
    private = rss = cpu = 0
    seen = set()
    for record in records:
        key = (record["pid"], record["start_ticks"])
        if key in seen:
            continue
        seen.add(key)
        p = checked(record)
        mem, clock = p.memory_info(), p.cpu_times()
        private += mem.private
        rss += mem.rss
        cpu += clock.user + clock.system
    return dict(private=private, rss=rss, cpu=cpu, processes=len(seen))
