"""S045 controller: loading and solving have separate clocks; first cause wins."""
import json
from pathlib import Path
import queue
import subprocess
import threading
import time

import networkx as nx
import psutil

import s045_search as common
from s045_policy import CampaignStop,deadline_reason,latch_stop,read_cause,slice_timeout
from s045_verify import check_pair,check_colouring,partition_clause,geometric_journal

CORE=['tools/s045_search.py','tools/s045_driver.py','tools/s045_policy.py',
      'tools/s045_verify.py','tools/s045_native.cpp','tools/s045_main.hpp',
      'scripts/s045_runtime.py','scripts/s045_campaign.py','scripts/s045_awake.py']


def run_slice(out,n,k,seconds,mode='partition',positive=False,status_path=None,
              records_path=None,fixed=None,absolute_deadline=None,records_sources=None,
              startup_ceiling=900,response_grace=15):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records_path=Path(records_path or out/'CANDIDATES.jsonl')
    status_path=Path(status_path or out/'STATUS.json')
    started=time.monotonic();count=None;old=0;last=started
    until=None if absolute_deadline is None else started+max(0,absolute_deadline-time.time())
    stage='CHECKPOINT_COUNT';p=None;ready=None;guard=None;error=None;ending=None;stats=''
    base=dict(n=n,k=k,mode=mode,positive_phases=positive,controller=common.identity(psutil.Process()),
              started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
              scientific_verdict='UNKNOWN',witness=False,domain_excluded=False,
              source_sha256={name:common.sha(common.ROOT/name) for name in CORE})

    def save(state,**extra):
        common.atomic(status_path,dict(base,state=state,stage=stage,
            elapsed_seconds=time.monotonic()-started,
            solve_elapsed_seconds=None if ready is None else time.monotonic()-ready,
            candidates=count,new_candidates=None if count is None else count-old,**extra))

    def cancellation():
        why=deadline_reason(absolute_deadline,time.time(),until,time.monotonic())
        if why:return latch_stop(out,why,stage=stage)
        if (out/'STOP').exists():return read_cause(out)
        return None

    def check_cancel():
        nonlocal last
        why=cancellation()
        if why:raise CampaignStop(why)
        if time.monotonic()-last>=5:save('PREPARING');last=time.monotonic()

    sources=records_sources or [records_path]
    def records():
        for source in sources:yield from common.journal(source,check_cancel)
    save('PREPARING')
    try:
        check_cancel();old=sum(1 for _ in records());count=old
        stage='CHECKPOINT_ENCODING';save('PREPARING')
        pairs=common.instance(out/'BASE.inst',n,records(),fixed,old,k,mode,check_cancel)
        stage='GEOMETRIC_REPLAY';save('PREPARING')
        lemmas=out/'PLANARITY.lem';geometric_journal(lemmas,n,check_cancel)
        check_cancel()
        resource=common.reason()
        if resource:raise CampaignStop(latch_stop(out,resource,stage=stage))
    except CampaignStop as e:
        stage='STOPPED';save('STOPPED',reason=str(e),audit_pending=True)
        return json.loads(status_path.read_text())

    base['input_sha256']=common.sha(out/'BASE.inst')
    log=(out/'NATIVE.log').open('a',encoding='utf-8',buffering=1)
    command=[str(common.EXE),str(out/'BASE.inst'),str(lemmas),str(seconds),str(out/'STOP'),str(int(positive)),mode]
    spawned=time.monotonic()
    p=subprocess.Popen(command,cwd=common.ROOT,env=common.env(),stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    base['generator']=common.identity(p)
    common.atomic(out/'IDENTITY.json',dict(base,command=command))
    q=queue.Queue()
    def reader():
        for line in p.stdout:log.write(line);q.put(line.rstrip())
        q.put(None)
    thread=threading.Thread(target=reader,daemon=True);thread.start()
    def send(s):p.stdin.write(s+'\n');p.stdin.flush()
    stage='NATIVE_LOADING';save('PREPARING')
    try:
        while True:
            why=cancellation()
            if not why:why=common.reason()
            if not why:why=slice_timeout(time.monotonic(),spawned,ready,seconds,startup_ceiling,response_grace)
            if why and guard is None:
                guard=latch_stop(out,why,stage=stage);ending=time.monotonic()
                try:send('STOP')
                except (OSError,BrokenPipeError):pass
            grace=2 if guard=='OWNER_DEADLINE_0730' else 30
            if ending and time.monotonic()-ending>grace:
                error='COOPERATIVE_STOP_FAILED:'+str(guard);p.terminate();break
            try:line=q.get(timeout=.1)
            except queue.Empty:line=''
            if line is None:break
            if line.startswith('READY '):
                assert ready is None,'duplicate native READY'
                ready=time.monotonic();stage='SOLVING'
                base['native_startup_seconds']=ready-spawned
                base['loaded_geometric_rules']=int(line.split()[1]);save('RUNNING')
            if line.startswith('c S045'):stats=line
            if line.startswith('CAND '):
                assert ready is not None,'candidate before native READY'
                if guard:
                    try:send('STOP')
                    except (OSError,BrokenPipeError):pass
                    continue
                bits=line.split()[2];assert len(bits)==2*len(pairs) and set(bits)<={'0','1'}
                layers=[[list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1'] for j in (0,1)]
                rotations=[]
                for ls in layers:
                    g=nx.Graph();g.add_nodes_from(range(n));g.add_edges_from(ls)
                    ok,embedding=nx.check_planarity(g);assert ok,'native nonplanar candidate'
                    rotations.append(embedding.get_data())
                check_pair(n,layers,rotations)
                remaining=max(.01,seconds-(time.monotonic()-ready))
                answer,cols=common.colouring(n,layers,k,min(60,remaining),cancellation)
                why=cancellation()
                if why:
                    guard=latch_stop(out,why,stage=stage);send('STOP');ending=time.monotonic();continue
                if answer is not True:
                    common.atomic(out/'ALERT.json',dict(n=n,k=k,layers=layers,rotations=rotations,
                        colouring_result=answer,proof_verified=False,verdict='UNKNOWN'))
                    guard=latch_stop(out,'NONCOLOUR_ALERT_UNVERIFIED' if answer is False else 'COLOUR_TIMEOUT',stage=stage)
                    send('STOP');ending=time.monotonic();continue
                check_colouring(n,layers,cols,k);partition_clause(n,cols)
                common.append(records_path,dict(n=n,k=k,layers=layers,rotations=rotations,
                    colours=cols,mode=mode,bits=bits,elapsed_seconds=time.monotonic()-started))
                count+=1;send('COLOR '+str(k)+' '+' '.join(map(str,cols)))
            if line.startswith('END 20') and guard is None:
                guard=latch_stop(out,'NATIVE_UNSAT_UNCERTIFIED',stage=stage);ending=time.monotonic()
            if time.monotonic()-last>=5:
                save('PREPARING' if ready is None else 'RUNNING',native_progress=stats);last=time.monotonic()
        p.wait(timeout=30)
    except BaseException as e:
        error=repr(e);guard=latch_stop(out,'CONTROLLER_ERROR',error=error,stage=stage)
        try:send('STOP')
        except (OSError,BrokenPipeError):pass
        try:p.wait(timeout=30)
        except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=10)
    finally:
        thread.join(timeout=3);log.close()
        p.stdin.close();p.stdout.close()
    stage='POST_SLICE_AUDIT';cuts=None
    try:
        check_cancel();cuts=geometric_journal(lemmas,n,check_cancel)
    except CampaignStop as e:
        if guard is None:guard=str(e)
    state='ERROR' if error or p.returncode not in (0,20) else 'STOPPED' if guard else 'SLICE_COMPLETE'
    save(state,reason=guard or 'NATIVE_TIMEOUT',native_returncode=p.returncode,error=error,
         verified_geometric_cuts=cuts,audit_pending=cuts is None,native_progress=stats,
         candidate_journal_sha256=common.sha(records_path) if records_path.exists() else None)
    data=json.loads(status_path.read_text());print(json.dumps(data),flush=True);return data
