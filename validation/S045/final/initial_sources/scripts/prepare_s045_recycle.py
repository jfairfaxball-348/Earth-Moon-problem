"""Preserve stopped identities and pre-register bounded memory recycling."""
import hashlib,json,shutil,subprocess,time
from pathlib import Path
import sys
import psutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import s045_search as s
V=ROOT/'validation/S045/memory_recycle'
B=ROOT/'artifacts/tmp/S045/campaign'

def main():
    V.mkdir(exist_ok=False)
    assert not any((B/p).exists() for p in ('OWNER_STOP.json','ALERT.json','ERROR.json','LOCK.json'))
    assert json.loads((B/'STOP_CAUSE.json').read_text())['reason']=='PRIVATE_MEMORY_LIMIT'
    for name in ('CAMPAIGN','STATUS','IDENTITY','POWER','STOP_CAUSE','DEADLINE'):
        data=json.loads((B/(name+'.json')).read_text())
        for key in ('controller','generator','helper'):
            if key not in data:continue
            item=data[key]
            try:
                p=psutil.Process(item['pid'])
                assert abs(p.create_time()-item['create_time'])>.001 or p.exe().lower()!=item['exe'].lower(),'old identity alive'
            except psutil.Error:pass
        dest=V/'stop_snapshot';dest.mkdir(exist_ok=True);shutil.copy2(B/(name+'.json'),dest/(name+'.json'))
    shutil.copy2(B/'SLICES.jsonl',V/'stop_snapshot/SLICES.jsonl')
    manifest=json.loads((ROOT/'validation/S045/watchdog_repair/MANIFEST.json').read_text())
    index={}
    for p in manifest['sha256']:
        if p.endswith(('.py','.cpp','.hpp','.md','.yml','.json')) and not p.startswith('validation/'):
            dest=V/'initial_sources'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/p).read_bytes())
            index[p]={'archive':dest.relative_to(ROOT).as_posix(),'sha256':s.sha(dest)}
    s.atomic(V/'INITIAL_SOURCES.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),files=index))
    s.atomic(V/'REGISTRATION.json',dict(session='S045',authority='Owner authorises operational fixes and restart; installed heartbeat recovery instructions',domain_unchanged=True,deadline_epoch=1792913400,hard_private_bytes=3*2**30,soft_private_bytes=int(2.5*2**30),available_floor=1.5*2**30,disk_floor=10*2**30,benchmark_native_solve_ceiling_seconds=360,checkpoint_candidates=453656,previous_fully_audited_geometric_rules=1498165,partial_slice_audit_required=True,policy='soft cap only after READY; local native-stop path; cooperative MEMORY_RECYCLE is a completed slice only with checked rules and positive new activity; zero progress/loading cap remains stopped; all original journals preserved; private CDCL disposable; no scientific or owner-stop restart',registered_epoch=time.time()))
    # Seal only stopped raw journals. All records stay available to cold replay.
    receipts={}
    for p in (B/'journals').glob('*.jsonl'):receipts[p.name]=s.seal_file(p)
    receipts['NATIVE.log']=s.seal_file(B/'NATIVE.log',V/'preserved/NATIVE.log.gz')
    s.atomic(V/'SEAL_RECEIPTS.json',receipts)
    print('Preserved stop evidence; recycling benchmark registered')

if __name__=='__main__':main()
