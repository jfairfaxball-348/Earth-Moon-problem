"""Snapshot actual healthy launch and seal repair records, without process action."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import psutil

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'validation/S045/watchdog_repair'
BASE=ROOT/'artifacts/tmp/S045/campaign'

def put(path,value):path.write_text(json.dumps(value,indent=1)+'\n',encoding='utf-8',newline='\n')
def main():
    status=json.loads((BASE/'STATUS.json').read_text());assert status['stage']=='SOLVING',status['stage']
    identities={k:status[k] for k in ('controller','generator')}
    samples={}
    for label,item in identities.items():
        p=psutil.Process(item['pid']);assert abs(p.create_time()-item['create_time'])<.01 and p.exe().lower()==item['exe'].lower()
        samples[label]={'identity':item,'cpu_before':sum(p.cpu_times()[:2]),'private_bytes':getattr(p.memory_info(),'private',p.memory_info().rss)}
    time.sleep(2)
    for label,item in identities.items():samples[label]['cpu_after']=sum(psutil.Process(item['pid']).cpu_times()[:2])
    assert any(s['cpu_after']>s['cpu_before'] for s in samples.values())
    after=json.loads((BASE/'STATUS.json').read_text());assert after['candidates']>275961
    assert not any((BASE/p).exists() for p in ('STOP','ALERT.json','ERROR.json','OWNER_STOP.json'))
    records={p:json.loads((BASE/p).read_text()) for p in ('STATUS.json','CAMPAIGN.json','POWER.json','DEADLINE.json','IDENTITY.json')}
    put(V/'LAUNCH_SNAPSHOT.json',dict(status='PASS',observed_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),records=records,samples=samples,available_memory=psutil.virtual_memory().available,disk_free=psutil.disk_usage(str(ROOT)).free,live_observation_only=True))
    # Stable Git text bytes before recording hashes. Watched source files already
    # use LF and are never rewritten by this recording helper.
    for p in V.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.md','.py','.cpp','.hpp'):
            data=p.read_bytes();normal=data.replace(b'\r\n',b'\n')
            if data!=normal:p.write_bytes(normal)
    changes=subprocess.check_output(['git','ls-files','--modified','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    files=sorted(set(p for p in changes if p and not p.endswith('watchdog_repair/MANIFEST.json') and (ROOT/p).is_file()))
    # Archives are covered even if this helper is rerun after staging.
    files=sorted(set(files)|{p.relative_to(ROOT).as_posix() for p in V.rglob('*') if p.is_file() and p.name!='MANIFEST.json'})
    sha={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
    put(V/'MANIFEST.json',dict(session='S045',status='IN_PROGRESS_REPAIRED_RUNNING',entry_main='5d910fb86ecd2fdb3844051aaa01c63e4fb69442',scientific_verdict='UNKNOWN',sha256=sha))
    print(json.dumps(dict(status='PASS',manifest_files=len(files),candidates=after['candidates'],stage=after['stage'])))

if __name__=='__main__':main()
