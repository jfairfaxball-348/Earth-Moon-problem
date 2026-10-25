"""Snapshot current healthy identities and seal memory-recovery records."""
import hashlib,json,subprocess,time
from pathlib import Path
import psutil
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'validation/S045/memory_recycle';B=ROOT/'artifacts/tmp/S045/campaign'
def put(p,v):p.write_text(json.dumps(v,indent=1)+'\n',encoding='utf-8',newline='\n')
def main():
    a=json.loads((V/'ACCEPTANCE.json').read_text());status=json.loads((B/'STATUS.json').read_text())
    assert status['stage'] in ('SOLVING','POST_SLICE_AUDIT','CHECKPOINT_COUNT','CHECKPOINT_ENCODING','GEOMETRIC_REPLAY','NATIVE_LOADING')
    samples={}
    for key in ('controller','generator'):
        if key not in status:continue
        item=status[key]
        try:
            p=psutil.Process(item['pid']);matched=abs(p.create_time()-item['create_time'])<.001 and p.exe().lower()==item['exe'].lower()
            assert matched or key=='generator'
            samples[key]=dict(identity=item,alive=matched,cpu_before=sum(p.cpu_times()[:2]) if matched else 0,private_bytes=getattr(p.memory_info(),'private',p.memory_info().rss) if matched else 0)
        except psutil.Error:
            assert key=='generator';samples[key]=dict(identity=item,alive=False,cpu_before=0,private_bytes=0)
    time.sleep(2)
    for key,row in samples.items():
        try:row['cpu_after']=sum(psutil.Process(row['identity']['pid']).cpu_times()[:2]) if row['alive'] else 0
        except psutil.Error:row['cpu_after']=row['cpu_before'];row['exited_during_sample']=True
    assert any(row['cpu_after']>row['cpu_before'] for row in samples.values())
    status=json.loads((B/'STATUS.json').read_text())
    slices=[json.loads(line) for line in (B/'SLICES.jsonl').read_text().splitlines()]
    observed=max([status.get('candidates') or 0]+[r['candidates'] for r in slices])
    assert observed>a['seed_candidates']
    assert not any((B/p).exists() for p in ('STOP','OWNER_STOP.json','ALERT.json','ERROR.json'))
    put(V/'LAUNCH_SNAPSHOT.json',dict(status='PASS',scope='Active campaign/controller and observed new native candidates; phase disclosed, native may have exited for normal audit/recycle',observed_epoch=time.time(),samples=samples,max_observed_candidates=observed,records={p:json.loads((B/p).read_text()) for p in ('CAMPAIGN.json','STATUS.json','IDENTITY.json','DEADLINE.json','POWER.json')},available_memory=psutil.virtual_memory().available,disk_free=psutil.disk_usage(str(ROOT)).free))
    for p in V.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.jsonl','.md','.py','.cpp','.hpp','.yml'):
            data=p.read_bytes();normal=data.replace(b'\r\n',b'\n')
            if data!=normal:p.write_bytes(normal)
    changes=subprocess.check_output(['git','ls-files','--modified','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    paths=set(p for p in changes if p and (ROOT/p).is_file())|{p.relative_to(ROOT).as_posix() for p in V.rglob('*') if p.is_file()}
    paths.discard('validation/S045/memory_recycle/MANIFEST.json')
    put(V/'MANIFEST.json',dict(session='S045',status='IN_PROGRESS_MEMORY_RECOVERED',scientific_verdict='UNKNOWN',entry_main='673d4a6b38cecf2533f3fc21ae66f09c7908685e',sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}))
    print('Memory recovery healthy-launch and manifest PASS')
if __name__=='__main__':main()
