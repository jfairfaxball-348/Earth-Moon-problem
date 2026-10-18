#!/usr/bin/env python3
"""Durable serial-run supervision, adapted from Davenport S110's run records.

Infrastructure only: progress records never certify a graph or prove exhaustion.
Linux process-tree wall/RSS caps supplement the workflow address-space limit.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def atomic_json(path, value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    with temp.open('w',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=1)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)


def journal(path, kind, **fields):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    value={'kind':kind,'utc':datetime.now(timezone.utc).isoformat(),**fields}
    with path.open('a',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(value)+'\n'); f.flush(); os.fsync(f.fileno())


# Private-memory observer reused verbatim from S005.
def windows_tree_bytes(root_pid):
    """Observe descendant private memory, including the Windows venv launcher."""
    import ctypes
    from ctypes import wintypes as w
    class Entry(ctypes.Structure):
        _fields_=[('dwSize',w.DWORD),('cntUsage',w.DWORD),('pid',w.DWORD),
                  ('heap',ctypes.c_size_t),('module',w.DWORD),('threads',w.DWORD),
                  ('parent',w.DWORD),('priority',w.LONG),('flags',w.DWORD),
                  ('exe',w.WCHAR*260)]
    class Memory(ctypes.Structure):
        _fields_=[('cb',w.DWORD),('faults',w.DWORD)]+[(name,ctypes.c_size_t) for name in
                  ('peak_ws','ws','peak_paged','paged','peak_nonpaged','nonpaged','peak_page','page','private')]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateToolhelp32Snapshot.restype=w.HANDLE
    kernel.CreateToolhelp32Snapshot.argtypes=[w.DWORD,w.DWORD]
    kernel.Process32FirstW.argtypes=[w.HANDLE,ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes=[w.HANDLE,ctypes.POINTER(Entry)]
    kernel.OpenProcess.restype=w.HANDLE
    kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD]
    kernel.CloseHandle.argtypes=[w.HANDLE]
    psapi=ctypes.WinDLL('psapi',use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[w.HANDLE,ctypes.POINTER(Memory),w.DWORD]
    snap=kernel.CreateToolhelp32Snapshot(2,0)
    assert snap != ctypes.c_void_p(-1).value
    entry=Entry();entry.dwSize=ctypes.sizeof(entry)
    parents={}
    ok=kernel.Process32FirstW(snap,ctypes.byref(entry))
    while ok:
        parents[entry.pid]=entry.parent
        ok=kernel.Process32NextW(snap,ctypes.byref(entry))
    kernel.CloseHandle(snap)
    selected={root_pid}
    while True:
        more={pid for pid,parent in parents.items() if parent in selected}
        if more<=selected:
            break
        selected|=more
    total=0
    for pid in selected:
        handle=kernel.OpenProcess(0x410,False,pid)
        if not handle:
            continue  # process may have ended between snapshot and query
        info=Memory();info.cb=ctypes.sizeof(info)
        if psapi.GetProcessMemoryInfo(handle,ctypes.byref(info),ctypes.sizeof(info)):
            total+=info.private
        kernel.CloseHandle(handle)
    return total


def linux_tree(root):
    """Return descendants and their resident KiB, across process-group changes."""
    processes={}
    for d in Path('/proc').iterdir():
        if not d.name.isdecimal():
            continue
        try:
            fields=(d/'stat').read_text().rsplit(')',1)[1].split()
            ppid=int(fields[1])
            rss=next(int(l.split()[1]) for l in (d/'status').read_text().splitlines() if l.startswith('VmRSS:'))
            processes[int(d.name)]=(ppid,rss)
        except (OSError,ValueError,IndexError,StopIteration):
            continue
    found={root}
    while True:
        new={p for p,(pp,rss) in processes.items() if pp in found}-found
        if not new:
            break
        found |= new
    return found, sum(processes.get(p,(0,0))[1] for p in found)


def kill_tree(process):
    if os.name=='posix':
        descendants,_=linux_tree(process.pid)
        for pid in descendants-{process.pid}:
            try: os.kill(pid,signal.SIGKILL)
            except ProcessLookupError: pass
        try: os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError: pass
    else:
        subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
    process.wait()


def run_step(args,cap,log,journal_path,heartbeat=30,memory_kib=12*1024*1024):
    log=Path(log); log.parent.mkdir(parents=True,exist_ok=True)
    step=str(log)
    start=time.monotonic(); next_heartbeat=start+heartbeat
    peak=0; reason=None
    journal(journal_path,'start',step=step,command=list(map(str,args)),wall_cap=cap)
    with log.open('w') as f:
        kwargs={'start_new_session':True} if os.name=='posix' else {
            'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW}
        p=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,**kwargs)
        while p.poll() is None:
            now=time.monotonic()
            if os.name=='posix':
                _,rss=linux_tree(p.pid)
                # Include the lightweight supervising controller in the total.
                try:
                    rss+=next(int(l.split()[1]) for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmRSS:'))
                except (OSError,StopIteration): pass
                peak=max(peak,rss)
                if rss>memory_kib:
                    reason='MEMORY_CAPPED'
            else:
                current=windows_tree_bytes(os.getpid())//1024
                peak=max(peak,current)
                if current>memory_kib:
                    reason='MEMORY_CAPPED'
            if now-start>cap:
                reason='WALL_CAPPED'
            if reason:
                kill_tree(p); break
            if now>=next_heartbeat:
                journal(journal_path,'heartbeat',step=step,elapsed=round(now-start,2),peak_tree_rss_kib=peak)
                next_heartbeat=now+heartbeat
            time.sleep(min(0.5,max(0.01,cap-(now-start))))
    rec={'command':list(map(str,args)),'returncode':reason if reason else p.returncode,
         'seconds':round(time.monotonic()-start,3),'peak_tree_rss_kib':peak,
         'completed_process':reason is None and p.returncode==0,'log':str(log)}
    rec['memory_measure']='aggregate_private_commit' if os.name=='nt' else 'aggregate_resident_set'
    rec['memory_cap_kib']=memory_kib
    journal(journal_path,'end',step=step,**rec)
    return rec
