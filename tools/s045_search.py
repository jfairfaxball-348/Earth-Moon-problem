"""S045 native generation / independently checked colouring feedback.

No independence/degree/symmetry restriction. Checkpoints are semantic only.
Search counts are activity; native UNSAT alone never excludes a domain.
"""
import argparse
import gzip
import hashlib
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
import psutil
from pysat.solvers import Solver

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s045_verify import check_pair, check_colouring, partition_clause, geometric_journal
from s045_policy import CampaignStop,deadline_reason,latch_stop,read_cause,slice_timeout

EXE=ROOT/'artifacts/tmp/S045/watchdog-native/bipsat_s045.exe'
COMP=ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def atomic(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.new')
    tmp.write_text(json.dumps(data,indent=1)+'\n',encoding='utf-8',newline='\n')
    for _ in range(20):
        try: os.replace(tmp,path); return
        except PermissionError: time.sleep(.05)
    raise RuntimeError('atomic status sharing retry exhausted')

def append(path,data):
    with Path(path).open('a',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(data,separators=(',',':'))+'\n'); f.flush(); os.fsync(f.fileno())

def journal(path,cancel=None):
    if not Path(path).exists(): return
    # Stream one row at a time; an incomplete row is never used as a rule.
    opener=gzip.open if str(path).endswith('.gz') else Path.open
    with opener(Path(path),'rt',encoding='utf-8') as f:
        for index,line in enumerate(f):
            if cancel and index%128==0:cancel()
            if not line.endswith('\n'): raise ValueError('incomplete journal; preserve and repair explicitly')
            yield json.loads(line)

def instance(path,n,records=(),fixed=None,record_count=None,target_k=None,target_mode=None,cancel=None):
    pairs=list(it.combinations(range(n),2))
    if record_count is None: record_count=len(records)
    if fixed is not None:
        fixed=[{tuple(sorted(e)) for e in ls} for ls in fixed]
    nc=len(pairs)+record_count+(2*len(pairs) if fixed is not None else 0)
    with Path(path).open('w',encoding='ascii',newline='\n') as f:
        f.write(f'p bipsat2 {n} {len(pairs)} 0 {nc}\n')
        f.writelines(f'e {a} {b}\n' for a,b in pairs)
        def emit(clause):f.write(' '.join(map(str,clause))+' 0\n')
        for i in range(len(pairs)):emit([-2*i-1,-2*i-2])
        count=0
        for row in records:
            if cancel and count%128==0:cancel()
            assert row['n']==n and (target_k is None or row['k']==target_k)
            assert row['mode'] in ('partition','block') and (target_mode is None or row['mode']==target_mode)
            check_pair(n,row['layers'],row['rotations'])
            check_colouring(n,row['layers'],row['colours'],row['k'])
            if row['mode']=='partition':emit(partition_clause(n,row['colours']))
            else:
                bits=row['bits'];assert len(bits)==2*len(pairs)
                emit([-(i+1) if b=='1' else i+1 for i,b in enumerate(bits)])
            count+=1
        assert count==record_count
        if fixed is not None:
            for i,e in enumerate(pairs):
                for k in (0,1):emit([2*i+1+k if e in fixed[k] else -(2*i+1+k)])
    return pairs

def colour_cnf(n,layers,k):
    clauses=[]
    for v in range(n):
        vs=[v*k+c+1 for c in range(k)]
        clauses.append(vs)
        clauses.extend([[-a,-b] for a,b in it.combinations(vs,2)])
    for a,b in set(map(tuple,layers[0]))|set(map(tuple,layers[1])):
        clauses.extend([[-(a*k+c+1),-(b*k+c+1)] for c in range(k)])
    clauses.append([1])  # colour-name permutation only
    return clauses

def colouring(n,layers,k,seconds=60,cancel=None):
    clauses=colour_cnf(n,layers,k)
    with Solver(name='g4',bootstrap_with=clauses) as s:
        done=threading.Event();until=time.monotonic()+seconds
        def interrupt():
            while not done.wait(.05):
                if time.monotonic()>=until or (cancel and cancel()):s.interrupt();return
        timer=threading.Thread(target=interrupt,daemon=True);timer.start()
        try:
            result=s.solve_limited(expect_interrupt=True)
            if result is not True: return result,None
            positive={v for v in s.get_model() if v>0}
            cols=[next(c for c in range(k) if v*k+c+1 in positive) for v in range(n)]
        finally:done.set();timer.join()
    # Split existing classes until all k colours are used; this remains proper
    # and makes a stronger (shorter) necessary partition clause.
    for missing in sorted(set(range(k))-set(cols)):
        counts=[cols.count(c) for c in range(k)]; largest=max(range(k),key=counts.__getitem__)
        if counts[largest]<=1: break
        cols[cols.index(largest)]=missing
    check_colouring(n,layers,cols,k)
    return True,cols

def env(): return dict(os.environ,PATH=str(COMP)+os.pathsep+os.environ['PATH'])

def private_bytes():
    total=0
    parent=psutil.Process()
    for p in [parent,*parent.children(recursive=True)]:
        try: total+=getattr(p.memory_info(),'private',p.memory_info().rss)
        except psutil.Error: pass
    return total


def reason():
    if psutil.virtual_memory().available < 1.5*2**30: return 'AVAILABLE_RAM_FLOOR'
    if psutil.disk_usage(str(ROOT)).free < 10*2**30: return 'DISK_RESERVE'
    total=private_bytes()
    if total>3*2**30: return 'PRIVATE_MEMORY_LIMIT'
    return None

def identity(p):
    q=psutil.Process(p.pid)
    return dict(pid=p.pid,create_time=q.create_time(),exe=q.exe())

def run_slice(*args,**kwargs):
    from s045_driver import run_slice as driver
    return driver(*args,**kwargs)


def seal_file(path,destination=None,cancel=None):
    """Compress a closed journal, independently verify decoded bytes, then retire raw."""
    path=Path(path)
    if not path.exists() or path.stat().st_size==0:return None
    dest=Path(destination or str(path)+'.gz');dest.parent.mkdir(parents=True,exist_ok=True)
    receipt=Path(str(dest)+'.seal.json')
    if dest.exists():
        saved=json.loads(receipt.read_text());assert sha(path)==saved['raw_sha256']
        assert sha(dest)==saved['archive_sha256'];path.unlink();return saved
    tmp=Path(str(dest)+'.partial');before=path.stat();raw=hashlib.sha256()
    with path.open('rb') as src,gzip.open(tmp,'wb') as dst:
        while block:=src.read(1024*1024):
            if cancel:cancel()
            raw.update(block);dst.write(block)
    decoded=hashlib.sha256()
    with gzip.open(tmp,'rb') as f:
        while block:=f.read(1024*1024):
            if cancel:cancel()
            decoded.update(block)
    assert decoded.hexdigest()==raw.hexdigest()
    after=path.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    data=dict(raw_sha256=raw.hexdigest(),raw_bytes=before.st_size,archive_sha256=sha(tmp),
              archive_bytes=tmp.stat().st_size,archive=str(dest),decoded_bytes_verified=True)
    atomic(receipt,data);os.replace(tmp,dest);path.unlink();return data


def checkpoint_sources(base):
    base=Path(base);sources=[]
    candidates=[base/'CANDIDATES.jsonl']
    directory=base/'journals'
    if directory.exists():
        names={p.name.removesuffix('.gz') for p in directory.iterdir() if p.name.endswith(('.jsonl','.jsonl.gz'))}
        candidates.extend(directory/name for name in sorted(names))
    for raw in candidates:
        gz=Path(str(raw)+'.gz')
        if gz.exists():
            saved=json.loads(Path(str(gz)+'.seal.json').read_text())
            if raw.exists():assert sha(raw)==saved['raw_sha256'],'ambiguous raw/compressed checkpoint'
            sources.append(gz)
        elif raw.exists():sources.append(raw)
    return sources

def benchmark(label='benchmark'):
    base=ROOT/'artifacts/tmp/S045'/label;rows=[]
    assert not (ROOT/'validation/S045/BENCHMARK.json').exists()
    for name,mode,positive in [('block','block',False),('partition','partition',False),('partition-positive','partition',True)]:
        row=run_slice(base/name,50,9,60,mode,positive)
        row['arm']=name;rows.append(row)
    eligible=[r for r in rows if r['mode']=='partition' and r['state']=='SLICE_COMPLETE' and r['new_candidates']>0]
    assert eligible,'No passing partition configuration; do not launch sustained search'
    best=max(eligible,key=lambda r:(r['new_candidates']/r['elapsed_seconds'],not r['positive_phases']))
    # Fresh-process semantic restart, not merely continued private solver state.
    restart=run_slice(base/best['arm'],50,9,15,'partition',best['positive_phases'])
    assert restart['state']=='SLICE_COMPLETE' and not restart['error']
    for d in base.iterdir():
        if d.is_dir():
            target=ROOT/'validation/S045'/label/d.name;target.mkdir(parents=True,exist_ok=True)
            import gzip
            for p in d.iterdir():
                if p.suffix in ('.jsonl','.lem'):
                    with gzip.open(target/(p.name+'.gz'),'wb') as f:f.write(p.read_bytes())
    result=dict(status='PASS',archive_directory=label,arms=rows,selected_arm=best['arm'],positive_phases=best['positive_phases'],
                restart=restart,gate='verified candidate feedback, audited external rules, cooperative slice end and semantic restart',
                counts_are_coverage=False,witness=False,domain_excluded=False)
    atomic(ROOT/'validation/S045/BENCHMARK.json',result)
    print('S045 benchmark PASS; selected '+best['arm'],flush=True)

def campaign():
    benchmark=json.loads((ROOT/'validation/S045/BENCHMARK.json').read_text()); assert benchmark['status']=='PASS'
    assert json.loads((ROOT/'validation/S045/CONTROLS.json').read_text())['status']=='PASS'
    assert json.loads((ROOT/'validation/S045/SMOKE.json').read_text())['verdict']=='PASS'
    base=ROOT/'artifacts/tmp/S045/campaign';base.mkdir(parents=True,exist_ok=True)
    lock=base/'LOCK.json'
    # Atomic exclusive creation; fail closed even if an old PID has disappeared.
    with lock.open('x',encoding='utf-8') as f:json.dump(identity(psutil.Process()),f)
    directive=json.loads((base/'DEADLINE.json').read_text())
    deadline_epoch=directive['deadline_epoch'];assert time.time()<deadline_epoch
    started=time.monotonic();deadline=started+max(0,deadline_epoch-time.time());index=0;result=None
    (base/'journals').mkdir(exist_ok=True)
    existing=[int(p.name.split('.')[0]) for p in (base/'journals').iterdir() if p.name.split('.')[0].isdigit()]
    sequence=max(existing,default=0)+1
    atomic(base/'CAMPAIGN.json',dict(state='RUNNING',controller=identity(psutil.Process()),
           deadline_epoch=deadline_epoch,deadline_utc=directive['deadline_utc'],started_epoch=time.time(),n=50,k=9,positive_phases=benchmark['positive_phases'],
           private_memory_cap=3*2**30,available_floor=1.5*2**30,disk_floor=10*2**30))
    def cancel():
        why=deadline_reason(deadline_epoch,time.time(),deadline,time.monotonic())
        if why:raise CampaignStop(latch_stop(base,why))
        if (base/'STOP').exists():raise CampaignStop(read_cause(base))
    try:
        while time.monotonic()<deadline:
            cancel()
            current=base/'journals'/f'{sequence:06d}.jsonl'
            sources=checkpoint_sources(base)+[current]
            result=run_slice(base,50,9,min(600,deadline-time.monotonic()),'partition',benchmark['positive_phases'],
                             records_path=current,records_sources=sources,absolute_deadline=deadline_epoch,
                             soft_private_bytes=int(2.5*2**30))
            index+=1
            append(base/'SLICES.jsonl',result)
            if result['state']!='SLICE_COMPLETE': break
            # Only closed files are sealed; new segments have distinct names.
            seal_file(current,cancel=cancel)
            seal_file(base/'NATIVE.log',base/'logs'/f'NATIVE-{int(time.time())}.log.gz',cancel)
            sequence+=1
        if time.time()>=deadline_epoch:latch_stop(base,'OWNER_DEADLINE_0730')
    except CampaignStop as e:
        latch_stop(base,str(e))
    except BaseException as e:
        latch_stop(base,'CAMPAIGN_ERROR',error=repr(e))
        atomic(base/'ERROR.json',dict(error=repr(e),elapsed_seconds=time.monotonic()-started));raise
    finally:
        atomic(base/'CAMPAIGN.json',dict(state='STOPPED',controller=identity(psutil.Process()),slices=index,
               deadline_epoch=deadline_epoch,deadline_utc=directive['deadline_utc'],
               reason=read_cause(base) if (base/'STOP').exists() else 'CAMPAIGN_COMPLETE',
               elapsed_seconds=time.monotonic()-started,last_slice=result,scientific_verdict='UNKNOWN',witness=False))
        lock.unlink()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['benchmark','campaign']);ap.add_argument('--label',default='benchmark');a=ap.parse_args()
    if a.mode=='benchmark': benchmark(a.label)
    else: campaign()

if __name__=='__main__': main()
