"""Owner-authorised S045 launch/status/cooperative stop. Never touches S036."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s045_search import atomic,sha

BASE=ROOT/'artifacts/tmp/S045/campaign'

def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def alive(ident):
    try:
        p=psutil.Process(ident['pid'])
        return abs(p.create_time()-ident['create_time'])<.001 and p.exe().lower()==ident['exe'].lower()
    except psutil.Error:return False

def status():
    result={}
    for name in ('CAMPAIGN','STATUS','ERROR'):
        p=BASE/(name+'.json')
        if p.exists():result[name]=read(p)
    for name in ('CAMPAIGN','STATUS'):
        if name in result:
            r=result[name]
            result[name+'_controller_alive']=alive(r['controller'])
            if 'generator' in r:result[name+'_generator_alive']=alive(r['generator'])
    result['STOP_exists']=(BASE/'STOP').exists()
    print(json.dumps(result,indent=1));return result

def launch(resume_maintenance=False):
    assert os.name=='nt'
    for filename in ('CONTROLS.json','BENCHMARK.json'):
        assert read(ROOT/'validation/S045'/filename)['status']=='PASS'
    assert read(ROOT/'validation/S045/SMOKE.json')['verdict']=='PASS'
    # Tested source and binary bytes must still match at launch.
    for p,h in read(ROOT/'validation/S045/CONTROLS.json')['stop_test']['source_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in read(ROOT/'validation/S045/BUILD.json')['sha256'].items():assert sha(ROOT/p)==h,p
    BASE.mkdir(parents=True,exist_ok=True)
    if resume_maintenance:
        assert (BASE/'MAINTENANCE.json').exists() and not (BASE/'OWNER_STOP.json').exists()
        assert not (BASE/'LOCK.json').exists(),'controller must exit before maintenance recovery'
        for name in ('CAMPAIGN','STATUS','IDENTITY'):
            old=read(BASE/(name+'.json'))
            assert not alive(old['controller'])
            if 'generator' in old:assert not alive(old['generator'])
        archive=BASE/'before-streaming';archive.mkdir(exist_ok=False)
        # Exact named control files only; preserve all semantic journals in place.
        for name in ('CAMPAIGN.json','STATUS.json','IDENTITY.json','LAUNCH.json','STOP','GUARD_STOP.json','POWER.json'):
            p=BASE/name
            if p.exists():
                (archive/name).write_bytes(p.read_bytes());p.unlink()
    assert not (BASE/'LOCK.json').exists() and not (BASE/'CAMPAIGN.json').exists(),'no duplicate or automatic restart'
    assert not (BASE/'STOP').exists(),'owner/resource STOP remains latched'
    log=BASE/'controller.log'
    command=[str(ROOT/'.venv/Scripts/python.exe'),str(ROOT/'scripts/s045_runtime.py')]
    quote=lambda s:'"'+str(s)+'"'
    line='cmd.exe /d /s /c "'+' '.join(map(quote,command))+' >> '+quote(log)+' 2>&1"'
    script=("$r=Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
            "-Arguments @{CommandLine=$env:S045_CMD;CurrentDirectory=$env:S045_CWD}; "
            "Write-Output \"$($r.ReturnValue) $($r.ProcessId)\"")
    p=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',script],
                     env=dict(os.environ,S045_CMD=line,S045_CWD=str(ROOT)),capture_output=True,text=True,timeout=60)
    fields=p.stdout.strip().split()
    assert p.returncode==0 and len(fields)==2 and fields[0]=='0',p.stdout+p.stderr
    receipt=dict(wmi=True,cmd_pid=int(fields[1]),command=command,log=str(log),time_epoch=time.time(),
                 source_sha256={str(q.relative_to(ROOT)):sha(q) for q in
                    [Path(__file__),ROOT/'tools/s045_search.py',ROOT/'tools/s045_verify.py']},
                 stage='WMI_DISPATCHED_NOT_YET_PROVEN_RUNNING')
    atomic(BASE/'LAUNCH.json',receipt)
    print(json.dumps(receipt,indent=1))

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','resume-maintenance','status','stop']);a=p.parse_args()
    if a.action in ('launch','resume-maintenance'):launch(a.action=='resume-maintenance')
    elif a.action=='status':status()
    else:
        BASE.mkdir(parents=True,exist_ok=True)
        (BASE/'STOP').touch(exist_ok=True)
        atomic(BASE/'OWNER_STOP.json',dict(time_epoch=time.time(),authority='explicit CLI stop',private_cdcl_checkpoint=False))
        print('S045 cooperative STOP latched; use status to verify actual exit.')

if __name__=='__main__':main()
