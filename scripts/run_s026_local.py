"""Owner-authorised S026 local serial queue; no model calls, no future session.

Full local 271+K9 smoke gates all science. One externally supervised process tree
at <=11GiB; per-graph four-hour absolute cap. Durable queue, logs and handback.
"""
import ctypes
from datetime import datetime,timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import atomic_json,journal,run_step

TAGS=['24335','23525','23534','23435','24344','24425','33344','33434']
OUT=ROOT/'artifacts/tmp/S026-local'
OUT.mkdir(parents=True,exist_ok=True)
os.environ['EMP_S026_OUTPUT']=str(OUT)
os.environ['EMP_S026_MEMORY_KIB']=str(11*1024*1024)
os.environ['EMP_S026_SEARCH_SECONDS']='600'
os.environ['EMP_CADICAL']=str(ROOT/'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM']=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def say(message):
    print(datetime.now(timezone.utc).isoformat(),message,flush=True)


def verified_saved(d):
    p=d/'SUMMARY.json'
    if not p.exists(): return False
    r=json.loads(p.read_text())
    proof=r.get('proof',{}); c=proof.get('certificate',{})
    if not (r.get('verdict')=='NONBIPLANAR_CERTIFIED' and proof.get('certified') and
            proof.get('cnf_byte_match') and c.get('verdict')=='UNSAT_DRAT_VERIFIED'):
        return False
    path=d/Path(c['drat_gz']).name
    return path.exists() and sha(path)==c['drat_gz_sha256'] and (d/'lemmas.json.gz').exists()


def main():
    if os.name!='nt': raise RuntimeError('This owner local launcher targets the Windows workstation')
    # Prevent a second queue in this working directory. OS releases on crash.
    import msvcrt
    lock=(OUT/'RUN.lock').open('a+b'); lock.write(b'0'); lock.flush(); lock.seek(0)
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    power=ctypes.windll.kernel32
    power.SetThreadExecutionState(0x80000001)
    queue={'session':'S026','authority':'owner direct local instruction 2026-10-18',
           'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
           'memory_kib':11*1024*1024,'graph_absolute_wall_seconds':14400,'jobs':[]}
    try:
        for key,expected in [('EMP_CADICAL','120d2c53bf14a8b70cce78be980824651922d53523228d9f0f026998caea7e48'),
                             ('EMP_DRAT_TRIM','970caaea97a15c8a27d4747e0e92e058ac1b1d9d4e04a95e3fc58b069ed4c03e')]:
            assert sha(os.environ[key])==expected,(key,'native binary digest mismatch')
        env={'kind':'LOCAL_WINDOWS_OWNER_AUTHORISED_S026','python':sys.version,
             'packages':{k:metadata.version(k) for k in ('python-sat','networkx')},
             'native_sha256':{k:sha(os.environ[k]) for k in ('EMP_CADICAL','EMP_DRAT_TRIM')},
             'memory_cap_kib':11*1024*1024,'cpu_threads':os.cpu_count(),
             'source_commit':queue['source_commit'],'source_sha256':{
                 str(p.relative_to(ROOT)).replace('\\','/'):sha(p)
                 for pattern in ('s025_*.py','s026_*.py','biplanar_cegar.py','biplanar_cnf.py','blowup_graph.py')
                 for p in (ROOT/'tools').glob(pattern)}}
        atomic_json(OUT/'ENVIRONMENT.json',env)
        atomic_json(OUT/'QUEUE.json',queue)
        say('S026 local: FULL 271+K9 smoke starting; one worker,11GiB cap')
        smoke=run_step([sys.executable,str(ROOT/'scripts/cloud_smoke.py')],2400,
                       OUT/'smoke.log',OUT/'RUN_JOURNAL.jsonl',memory_kib=11*1024*1024)
        queue['smoke_process']=smoke
        if smoke['returncode']!=0: raise RuntimeError('Full smoke failed; scientific queue BLOCKED')
        s=ROOT/'artifacts/tmp/cloud_smoke/RESULT.json'
        assert json.loads(s.read_text())['verdict']=='PASS'
        shutil.copyfile(s,OUT/'SMOKE.json')
        say('FULL smoke PASS. Starting the eight-graph serial C5 queue.')
        for index,tag in enumerate(TAGS,1):
            d=OUT/('C5-'+tag)
            if verified_saved(d):
                item={'tag':tag,'status':'VERIFIED_PRIOR_LOCAL_RECEIPT','directory':str(d)}
                say(f'{index}/8 C5-{tag}: retained verified receipt; skipping repeat')
            else:
                say(f'{index}/8 C5-{tag}: starting search/certification')
                rec=run_step([sys.executable,str(ROOT/'tools/s026_campaign.py'),'c5',tag],14400,
                             OUT/(tag+'.driver.log'),OUT/'RUN_JOURNAL.jsonl',memory_kib=11*1024*1024)
                result=json.loads((d/'SUMMARY.json').read_text()) if (d/'SUMMARY.json').exists() else {'verdict':'UNKNOWN'}
                item={'tag':tag,'process':rec,'status':result['verdict'],'directory':str(d)}
                d.mkdir(exist_ok=True)
                for name in ('SMOKE.json','ENVIRONMENT.json','SOURCE.json'):
                    if (OUT/name).exists(): shutil.copyfile(OUT/name,d/name)
                say(f'{index}/8 C5-{tag}: {item["status"]}')
            queue['jobs'].append(item); atomic_json(OUT/'QUEUE.json',queue)
        queue['status']='QUEUE_FINISHED_NOT_A_SESSION_CLOSEOUT'
        queue['certified']=sum(verified_saved(OUT/('C5-'+t)) for t in TAGS)
        atomic_json(OUT/'QUEUE.json',queue)
        atomic_json(OUT/'HANDBACK.json',queue)
        journal(OUT/'RUN_JOURNAL.jsonl','queue_end',certified=queue['certified'],expected=8)
        say(f'Local queue finished: {queue["certified"]}/8 certified; other targets remain UNKNOWN. Handback saved.')
    except BaseException as e:
        queue['status']='INTERRUPTED_OR_BLOCKED'; queue['error']=repr(e)
        atomic_json(OUT/'QUEUE.json',queue); journal(OUT/'RUN_JOURNAL.jsonl','queue_error',error=repr(e))
        raise
    finally:
        power.SetThreadExecutionState(0x80000000)
        lock.close()


if __name__=='__main__': main()
