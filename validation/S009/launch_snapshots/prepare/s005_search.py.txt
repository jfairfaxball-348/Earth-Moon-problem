#!/usr/bin/env python3
"""CAM-0006 six fixed full candidates, supervised and certificate checked."""
import gzip
import json
import subprocess
import sys
import time
from pathlib import Path

from blowup_graph import blowup
from check_layers import main as check_split
from s005_replay import sha


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


def run_logged(cmd, cap, logfile):
    t = time.monotonic()
    peak=0
    reason=None
    with open(logfile,'wb') as log:
        p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
        while p.poll() is None:
            current=windows_tree_bytes(p.pid) if sys.platform=='win32' else 0
            peak=max(peak,current)
            if time.monotonic()-t>=cap or current>12*1024**3:
                reason='external wall cap' if time.monotonic()-t>=cap else '12 GiB private memory cap'
                if sys.platform=='win32':
                    subprocess.run(['taskkill.exe','/PID',str(p.pid),'/T','/F'],
                                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
                else:
                    p.kill()
                p.wait(timeout=15)
                break
            time.sleep(0.1)
    row={'command':cmd,'returncode':None if reason else p.returncode,
         'seconds':time.monotonic()-t,'hard_cap':cap,'observed_peak_tree_private_bytes':peak}
    if reason:
        row['reason']=reason
    return row


def compress(source, dest):
    with open(source,'rb') as src, open(dest,'wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            import shutil
            shutil.copyfileobj(src, gz)


def certify(edgefile, prefix, generator='tools/triangulation_cover.py'):
    solver = str(Path('artifacts/tmp/S004/cadical.exe').resolve())
    checker = str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
    gen = run_logged([sys.executable, generator, 'check',
                      str(edgefile), str(prefix)], 120, str(prefix)+'.regen.log')
    assert gen['returncode'] == 0
    proof = str(prefix)+'.drat'
    solve = run_logged([solver, '-q', '--no-binary', str(prefix)+'.cnf', proof],
                       1220, str(prefix)+'.proof-solve.log')
    row = {'regenerate':gen, 'solve':solve, 'verdict':'UNKNOWN'}
    if solve['returncode'] != 20:
        return row
    chk = run_logged([checker, str(prefix)+'.cnf', proof, '-t', '1200'],
                     1220, str(prefix)+'.check.log')
    row['check'] = chk
    if 's VERIFIED' not in Path(str(prefix)+'.check.log').read_text():
        return row
    row.update(verdict='NON_BIPLANAR_DRAT_VERIFIED', cnf_sha256=sha(str(prefix)+'.cnf'),
               proof_sha256=sha(proof), proof_bytes=Path(proof).stat().st_size)
    # Compact only if extraction and a fresh check both succeed.
    core = str(prefix)+'.core.drat'
    trim = run_logged([checker, str(prefix)+'.cnf', proof, '-l', core, '-t','600'],
                      620, str(prefix)+'.trim.log')
    row['trim'] = trim
    archive_proof = proof
    if Path(core).exists() and 's VERIFIED' in Path(str(prefix)+'.trim.log').read_text():
        corechk = run_logged([checker, str(prefix)+'.cnf', core, '-t', '600'],
                            620, str(prefix)+'.core.check.log')
        row['core_check'] = corechk
        if 's VERIFIED' in Path(str(prefix)+'.core.check.log').read_text():
            archive_proof = core
    dest = Path('validation/S005/search')/Path(prefix).name
    compress(str(prefix)+'.cnf', str(dest)+'.cnf.gz')
    compress(archive_proof, str(dest)+'.drat.gz')
    row.update(archive=str(dest)+'.drat.gz', archive_raw_sha256=sha(archive_proof),
               archive_raw_bytes=Path(archive_proof).stat().st_size,
               archive_sha256=sha(str(dest)+'.drat.gz'))
    for suffix in ('.cuts.json','.result.json','.check.log','.core.check.log','.proof-solve.log','.regen.log','.trim.log'):
        src = Path(str(prefix)+suffix)
        if src.exists():
            Path(str(dest)+suffix).write_bytes(src.read_bytes())
    return row


def main():
    root = Path('validation/S005')
    (root/'targets').mkdir(parents=True, exist_ok=True)
    (root/'search').mkdir(exist_ok=True)
    scratch = Path('artifacts/tmp/S005/search')
    scratch.mkdir(parents=True, exist_ok=True)
    src = json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    targets = []
    if '--one-first' in sys.argv:
        indices = (177,179,180,102,103,117,123,143)
    elif '--zero-rest' in sys.argv:
        indices = (176,171,120,126,128,130,42,44,133,135,262)
    else:
        indices = (161,163,164,154,158,160)
    for idx in indices:
        g6,w,_ = src[idx]
        edges,_ = blowup(g6,w)
        edgefile = root/'targets'/f'row{idx}.edges'
        edgefile.write_text(''.join(f'{a} {b}\n' for a,b in edges), newline='\n')
        targets.append({'index':idx,'g6':g6,'w':w,'n':sum(w),'m':len(edges),
                        'D':6*sum(w)-12-len(edges), 'edgefile':str(edgefile),
                        'edge_sha256':sha(edgefile)})
    oldtargets=json.loads((root/'targets.json').read_text()) if (root/'targets.json').exists() else []
    merged={r['index']:r for r in oldtargets}
    merged.update({r['index']:r for r in targets})
    (root/'targets.json').write_text(json.dumps(list(merged.values()),indent=1), newline='\n')
    results=json.loads((root/'search_results.json').read_text()) if (root/'search_results.json').exists() else []
    for target in targets:
        idx=target['index']
        if any(r['target']['index']==idx for r in results):
            print(idx,'already recorded; skipped',flush=True)
            continue
        prefix=scratch/f'cover-row{idx}'
        oldmeta=Path(str(prefix)+'.result.json')
        resume='--resume' in sys.argv and oldmeta.exists() and json.loads(oldmeta.read_text()).get('verdict')=='UNSAT'
        if resume:
            run={'returncode':0,'resumed':'previous unverified internal UNSAT; fresh proof required',
                 'command_previously_registered':[sys.executable,'tools/triangulation_cover.py',target['edgefile'],str(prefix),'600','--lex']}
        else:
            run=run_logged([sys.executable,'tools/triangulation_cover.py',target['edgefile'],
                            str(prefix),'600','--lex'],620,str(prefix)+'.run.log')
        row={'target':target,'run':run,'verdict':'UNKNOWN'}
        p=Path(str(prefix)+'.result.json')
        if run['returncode']==0 and p.exists():
            meta=json.loads(p.read_text())
            row['search']=meta
            if meta['verdict']=='UNSAT':
                row['certificate']=certify(target['edgefile'],prefix)
                row['verdict']=row['certificate']['verdict']
            elif meta['verdict']=='SAT_CHECKED':
                check_split(target['edgefile'],str(prefix)+'.split.json')
                row['verdict']='BIPLANAR_CHECKED'
                Path(f'validation/S005/search/row{idx}.split.json').write_bytes(Path(str(prefix)+'.split.json').read_bytes())
        for suffix in ('.result.json','.cuts.json','.run.log'):
            p=Path(str(prefix)+suffix)
            if p.exists():
                Path('validation/S005/search',prefix.name+suffix).write_bytes(p.read_bytes())
        results.append(row)
        (root/'search_results.json').write_text(json.dumps(results,indent=1),newline='\n')
        print(idx,row['verdict'],run.get('seconds','resumed'),flush=True)
        if row['verdict']=='BIPLANAR_CHECKED':
            break


if __name__=='__main__':
    main()
