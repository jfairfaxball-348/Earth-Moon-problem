"""S035 resident per-region processes: preserve CDCL in RAM between scheduled turns.

No learned Boolean clause crosses a region boundary. Only independently audited
geometric clauses enter the shared ledger. Crash recovery falls back to semantic
checkpoints; process memory is not represented as a durable proof certificate.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
import uuid
import psutil
import s035_engine as old
from s035_regions import (claim,checkpoint,ledger,release,process_identity,live_identity,
                          stop_group,update_claim,sha,utc,time_left,recover as legacy_recover)
from s035_windows import atomic_json,journal,read_json,tree_sample,memory_available
from s035_storage import compress_proof


def suspend(worker):
    assert live_identity(worker['pid'],worker['start_ticks'])
    root=psutil.Process(worker['pid']);root.suspend()
    for p in root.children(recursive=True):
        try:p.suspend()
        except psutil.NoSuchProcess:pass


def resume(worker):
    assert live_identity(worker['pid'],worker['start_ticks'])
    root=psutil.Process(worker['pid'])
    for p in root.children(recursive=True):
        try:p.resume()
        except psutil.NoSuchProcess:pass
    root.resume()


def recover(area):
    path=Path(area)/'RESIDENT_CONTEXTS.json'
    if path.exists():
        data=read_json(path)
        for context in data.get('contexts',{}).values():
            stop_group(context.get('worker'))
            directory=Path(context['directory'])
            checkpoint(directory/'new-cuts.lem',directory/'CHECKPOINT.json')
        atomic_json(Path(area)/('RESIDENT_RECOVERY-'+str(time.time_ns())+'.json'),
                    dict(status='RECOVERED_UNKNOWN',previous=data,utc=utc()))
        atomic_json(path,dict(contexts={},utc=utc(),reason='PROCESS_CONTEXTS_CLEARED_SEMANTIC_RECOVERY_ONLY'))
    legacy_recover(area)


class Campaign(old.Campaign):
    def __init__(self,area):
        super().__init__(area)
        self.contexts={};self.context_lock=threading.RLock();self.handles={}

    def claim_resident(self,index):
        """Bound admission before allocating a context; avoid a cache-size+1 cycle."""
        with self.context_lock:
            with ledger(self.area) as data:
                available=[c for c in data['cells'] if c['status']!='UNSAT_DRAT_VERIFIED' and c['claim'] is None]
                if not available:return None
                retained=[c for c in available if str(c['id']) in self.contexts]
                fresh=[c for c in available if str(c['id']) not in self.contexts]
                # Claims in flight also reserve an admission slot before materialization.
                reserved={str(c['id']) for c in data['cells'] if c['claim']}|set(self.contexts)
                headroom=tree_sample(os.getpid())['private']+self.config.get('resident_admission_bytes',1024**3)
                may_admit=(len(reserved)<self.config.get('resident_max_contexts',4)
                    and headroom<self.config.get('resident_cache_private_bytes',5*1024**3)
                    and memory_available()>self.config.get('resident_available_floor_kib',2560*1024)+512*1024)
                choices=fresh if fresh and may_admit else retained
                if not choices:return None
                cell=min(choices,key=lambda c:(c['visits'],c['seconds'],c['id']))
                token=uuid.uuid4().hex
                directory=self.area/'attempts'/f"cell-{cell['id']:04d}"/token;directory.mkdir(parents=True)
                cell['visits']+=1
                cell['claim']=dict(token=token,controller_pid=os.getpid(),owner=f'resident-worker-{index}',
                    claimed_utc=utc(),directory=str(directory),worker=None)
                cell['last_attempt']=str(directory)
                journal(self.area/'JOURNAL.jsonl','claim',cell=cell['id'],token=token,retained=str(cell['id']) in self.contexts)
                return copy.deepcopy(cell)

    def worker_loop(self,index):
        while not self.stop.is_set():
            if time_left(self.config)<=0:self.halt('DEADLINE');break
            cell=self.claim_resident(index)
            if cell is None:
                with ledger(self.area) as data:
                    if all(c['status']=='UNSAT_DRAT_VERIFIED' for c in data['cells']):self.halt('ENCODED_QUEUE_CLOSED_PENDING_DOMAIN_AUDIT')
                self.stop.wait(.2);continue
            try:self.visit(cell)
            except BaseException as exc:
                journal(self.area/'JOURNAL.jsonl','worker_error',worker=index,error=repr(exc))
                self.halt('CONTROLLER_WORKER_ERROR');raise

    def save_contexts(self):
        with self.context_lock:
            atomic_json(self.area/'RESIDENT_CONTEXTS.json',dict(contexts=self.contexts,utc=utc(),
                persistence='RAM_ONLY_PID_CREATE_TIME_IDENTITY',cross_region_cdcl_sharing=False))

    def accept_delta(self,context):
        source=Path(context['directory'])/'new-cuts.lem'
        cp=checkpoint(source,source.with_suffix('.checkpoint.json'))
        if not cp:return
        offset=context.get('accepted_bytes',0)
        assert offset<=cp['complete_bytes']
        if offset==cp['complete_bytes']:return
        h=hashlib.sha256();count=0
        temp=source.with_name('delta-'+str(offset)+'.part')
        with source.open('rb') as f,temp.open('wb') as dest:
            f.seek(offset)
            while f.tell()<cp['complete_bytes']:
                line=f.readline();xs=list(map(int,line.split()))
                assert xs.pop()==0 and xs and len(xs)==len(set(xs))
                assert all(-2*len(self.config['pairs'])<=x<0 for x in xs)
                assert len({(-x-1)%2 for x in xs})==1
                old.subdivision([tuple(self.config['pairs'][(-x-1)//2]) for x in xs])
                dest.write(line);h.update(line);count+=1
            dest.flush();os.fsync(dest.fileno())
        # Short leaf keeps Windows atomic-temp paths below legacy MAX_PATH;
        # every reuse still compares the full SHA256 and fails on collision.
        target=source.with_name('a-'+h.hexdigest()[:16]+'.lem')
        if target.exists():assert sha(target)==h.hexdigest();temp.unlink()
        else:os.replace(temp,target)
        row=dict(path=str(target),count=count,sha256=h.hexdigest(),audit='INDEPENDENT_SUBDIVISION_PASS',
                 n=self.config['n'],utc=utc(),origin=str(source),start_byte=offset,end_byte=cp['complete_bytes'])
        with ledger(self.area) as data:
            if not any(r['sha256']==row['sha256'] for r in data['accepted_cuts']):data['accepted_cuts'].append(row)
        if not any(r['sha256']==row['sha256'] for r in context['recipe']['sources']):context['recipe']['sources'].append(row)
        context['accepted_bytes']=cp['complete_bytes']
        atomic_json(target.with_suffix('.audit.json'),row)
        journal(self.area/'JOURNAL.jsonl','resident_delta_audited',cell=context['cell'],count=count,sha256=row['sha256'])

    def evict_if_needed(self):
        with self.context_lock:
            changed=False
            while (tree_sample(os.getpid())['private']>self.config.get('resident_cache_private_bytes',5*1024**3)
                   or memory_available()<self.config.get('resident_available_floor_kib',2560*1024)):
                parked=[c for c in self.contexts.values() if c['state']=='PARKED']
                if not parked:
                    if changed:self.save_contexts()
                    return
                context=min(parked,key=lambda c:c.get('last_parked',0))
                stop_group(context['worker']);self.handles.pop(str(context['cell']),None)
                self.contexts.pop(str(context['cell']))
                changed=True
                journal(self.area/'JOURNAL.jsonl','resident_memory_eviction',cell=context['cell'],
                        private_cdcl_lost=True,semantic_cuts_preserved=True)
            if changed:self.save_contexts()

    def native_turn(self,context,cell,directory):
        token=cell['claim']['token'];key=str(cell['id']);start=time.monotonic()
        pilot=self.config.get('resident_pilot_turn_seconds',0)
        seconds=pilot if pilot and context.get('turns',0)<2 else self.config.get('resident_turn_seconds',600)
        end=time.time()+seconds
        reused=key in self.handles
        if reused:
            p=self.handles[key];assert p.poll() is None
            resume(context['worker'])
            journal(self.area/'JOURNAL.jsonl','resident_resumed',cell=cell['id'],worker=context['worker'])
        else:
            env=os.environ.copy();env.pop('EMP_ABSOLUTE_DEADLINE',None)
            if self.config.get('disable_random_walk'):env['EMP_S035_DISABLE_WALK']='1'
            else:env.pop('EMP_S035_DISABLE_WALK',None)
            if self.config.get('disable_congruence'):env['EMP_S035_DISABLE_CONGRUENCE']='1'
            else:env.pop('EMP_S035_DISABLE_CONGRUENCE',None)
            args=[self.config['native'],str(Path(context['directory'])/'input.inst'),'--timeout','inf',
                  '--lemmas',str(Path(context['directory'])/'new-cuts.lem')]
            with (Path(context['directory'])/'native.log').open('w') as log:
                p=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW)
            context['worker']=dict(pid=p.pid,start_ticks=process_identity(p.pid),phase='native',command=args,utc=utc())
            self.handles[key]=p
            self.save_contexts()
            journal(self.area/'JOURNAL.jsonl','resident_created',cell=cell['id'],worker=context['worker'])
        context['state']='RUNNING';context['turns']=context.get('turns',0)+1
        self.save_contexts();worker=context['worker'];reason=None;next_status=0;next_cp=0
        update_claim(self.area,cell['id'],token,worker=worker,phase='native',resident_origin=context['directory'],resident_reused=reused)
        with self.active_lock:self.active[token]=worker
        try:
            while p.poll() is None:
                self.evict_if_needed();now=time.time()
                if self.stop.is_set():reason=self.reason;break
                if time_left(self.config)<=0:self.halt('DEADLINE');reason=self.reason;break
                if tree_sample(p.pid)['private']>self.config.get('per_worker_private_bytes',2*1024**3):
                    reason='PRIVATE_MEMORY_CAP';break
                if now>=end:
                    suspend(worker);context['state']='PARKED';context['last_parked']=now
                    reason='RESIDENT_TURN_PARKED';break
                if now>=next_cp:
                    checkpoint(Path(context['directory'])/'new-cuts.lem',directory/'CHECKPOINT.json');next_cp=now+30
                if now>=next_status:
                    log=Path(context['directory'])/'native.log'
                    with log.open('rb') as f:
                        f.seek(max(0,f.seek(0,2)-65536));tail=f.read().decode(errors='replace')
                    progress=re.findall(r'^c S0(?:32_(?:PROGRESS|LOGIC)|35_PHASE) .*',tail,re.M)
                    atomic_json(directory/'WORKER.json',dict(**worker,elapsed=time.monotonic()-start,phase_end=end,
                        resident_origin=context['directory'],resident_reused=reused,resident_turn=context['turns'],
                        native_progress=progress[-6:],deadline=None,verdict='UNKNOWN'))
                    if Path(context['directory'])!=directory:
                        (directory/'native.log').write_text('c S035_RESIDENT_ORIGIN '+str(log)+'\n'+'\n'.join(progress[-12:])+'\n')
                    next_status=now+5
                time.sleep(.2)
            if reason!='RESIDENT_TURN_PARKED':
                if p.poll() is None:stop_group(worker)
                p.wait();context['state']='FINISHED'
            self.accept_delta(context)
        finally:
            with self.active_lock:self.active.pop(token,None)
            checkpoint(Path(context['directory'])/'new-cuts.lem',directory/'CHECKPOINT.json')
            context['active_seconds']=context.get('active_seconds',0)+time.monotonic()-start
            self.save_contexts()
        value=dict(returncode=p.returncode,reason=reason,resident_reused=reused,worker=worker,
                   wall_seconds=time.monotonic()-start,private_cdcl_retained=reason=='RESIDENT_TURN_PARKED')
        atomic_json(directory/'native-RESULT.json',value)
        return value

    def visit(self,cell):
        directory=Path(cell['claim']['directory']);started=time.time();token=cell['claim']['token'];key=str(cell['id'])
        status='UNKNOWN';details={};context=None
        try:
            with self.context_lock:
                context=self.contexts.get(key)
                if context is not None:context['state']='CLAIMED'
            if context is None and cell.get('pending_proof'):
                value=copy.deepcopy(cell['pending_proof'])
                with ledger(self.area) as data:shared=list(data['accepted_cuts'])
                for row in shared:
                    if not any(r['sha256']==row['sha256'] for r in value['sources']):value['sources'].append(row)
                details['pending_proof']=value
                cert=self.proof(value,directory,cell,time.time()+self.config.get('resident_proof_seconds',1800))
                if cert:status='UNSAT_DRAT_VERIFIED';details.update(certificate=str(directory/'CERTIFICATE.json'),pending_proof=None,last_outcome='INDEPENDENT_DRAT_VERIFIED')
                else:details['last_outcome']='PROOF_PENDING_UNKNOWN'
                return
            if context is None:
                with ledger(self.area) as data:cuts=list(data['accepted_cuts'])
                value=old.recipe(self.config,cuts,cell['assumptions'])
                context=dict(cell=cell['id'],directory=str(directory),recipe=value,state='CREATING',accepted_bytes=0,turns=0)
                digest=old.materialise(directory/'input.inst',value,native=True)
                atomic_json(directory/'INPUT.json',dict(recipe=copy.deepcopy(value),input_sha256=digest,native_sha256=self.config['native_sha256'],source_sha256=self.config['source_sha256'],resident=True))
                with self.context_lock:self.contexts[key]=context
            result=self.native_turn(context,cell,directory)
            if result['reason']=='RESIDENT_TURN_PARKED':
                details.update(last_outcome='RESIDENT_TURN_PARKED',resident_origin=context['directory'],private_cdcl_retained_in_ram=True)
                return
            with self.context_lock:self.contexts.pop(key,None);self.handles.pop(key,None);self.save_contexts()
            if result['reason']:
                details['last_outcome']=result['reason'];return
            if result['returncode']==10:
                old.independent_sat(self.config,Path(context['directory'])/'input.inst',Path(context['directory'])/'native.log',directory/'CANDIDATE.json')
                details['last_outcome']='SAT_CANDIDATE_INDEPENDENT_CHECKED'
                if self.config.get('scientific'):self.halt('SAT_CANDIDATE_REQUIRES_DOMAIN_REVIEW')
                return
            if result['returncode']!=20:
                details['last_outcome']='NATIVE_UNKNOWN'
                if result['returncode']!=0:self.halt('UNEXPECTED_NATIVE_EXIT')
                return
            value=context['recipe']
            with ledger(self.area) as data:data['cells'][cell['id']]['pending_proof']=value
            details['pending_proof']=value
            cert=self.proof(value,directory,cell,time.time()+self.config.get('resident_proof_seconds',1800))
            if cert:status='UNSAT_DRAT_VERIFIED';details.update(certificate=str(directory/'CERTIFICATE.json'),pending_proof=None,last_outcome='INDEPENDENT_DRAT_VERIFIED')
            else:details['last_outcome']='PROOF_PENDING_UNKNOWN'
        finally:
            atomic_json(directory/'RESULT.json',dict(status=status,seconds=time.time()-started,**details,verdict='UNKNOWN',whole_stratum_certified=False))
            release(self.area,cell['id'],token,status=status,seconds=time.time()-started,**details)
            compress_proof(directory/'proof.drat')
            if context and context.get('state')=='FINISHED':
                # Retain recipes/logs/clauses; only large reproducible materializations are redundant.
                for p in (Path(context['directory'])/'input.inst',directory/'formula.cnf'):
                    if p.exists():p.unlink()


# Existing controller lifecycle retains all its tested safety/resource handling.
# Its startup/final recovery additionally stops parked identity-checked processes.
old.recover=recover
