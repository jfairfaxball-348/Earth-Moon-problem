"""Real child protocol regressions for soft memory recycle and hard-stop priority."""
import json
from pathlib import Path
import subprocess,sys,tempfile,time
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import s045_search as s
from s045_driver import run_slice,CORE

def main():
    rows=[];real=subprocess.Popen
    with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/tmp/S045') as temp:
        root=Path(temp)
        def fixture(candidate=True,ignore=False,unsat=False):
            code="import pathlib,sys,time;stop=pathlib.Path(sys.argv[1]);print('READY 0',flush=True);"
            if candidate:code+="print('CAND 1 '+'0'*20,flush=True);sys.stdin.readline();"
            code+=("time.sleep(6);" if ignore else "\nwhile not stop.exists():time.sleep(.01)\n")
            code+=("print('END 20 0 0',flush=True);sys.exit(20)" if unsat else "print('END 0 0 0',flush=True)")
            return patch('s045_driver.subprocess.Popen',side_effect=lambda command,**kw:real([sys.executable,'-u','-c',code,command[4]],**kw))
        d=root/'recycle'
        def memory():return int(2.6*2**30) if (d/'CANDIDATES.jsonl').exists() else 1000000
        with fixture(),patch('s045_search.private_bytes',side_effect=memory):
            result=run_slice(d,5,3,30,soft_private_bytes=int(2.5*2**30))
        assert result['state']=='SLICE_COMPLETE' and result['reason']=='MEMORY_RECYCLE' and result['new_candidates']==1
        assert not (d/'STOP').exists() and not result['audit_pending'] and result['native_returncode']==0
        assert result['peak_private_bytes']<3*2**30;rows.append(result)
        d=root/'recycle-native-unsat'
        def memory_unsat():return int(2.6*2**30) if (d/'CANDIDATES.jsonl').exists() else 1000000
        with fixture(unsat=True),patch('s045_search.private_bytes',side_effect=memory_unsat):
            result=run_slice(d,5,3,30,soft_private_bytes=int(2.5*2**30))
        assert result['state']=='STOPPED' and result['reason']=='NATIVE_UNSAT_UNCERTIFIED'
        assert result['native_returncode']==20 and (d/'STOP').exists();rows.append(result)
        # A loaded checkpoint already above the soft roof must not spin forever.
        d=root/'no-progress'
        with fixture(False),patch('s045_search.private_bytes',return_value=int(2.6*2**30)):
            result=run_slice(d,5,3,30,soft_private_bytes=int(2.5*2**30))
        assert result['state']=='STOPPED' and result['reason']=='CHECKPOINT_MEMORY_NO_PROGRESS';rows.append(result)
        # A hard memory breach remains a latched campaign stop.
        with patch('s045_search.private_bytes',return_value=int(3.1*2**30)):
            result=run_slice(root/'hard',5,3,30,soft_private_bytes=int(2.5*2**30))
        assert result['reason']=='PRIVATE_MEMORY_LIMIT' and 'generator' not in result;rows.append(result)
        d=root/'deadline'
        def memory2():return int(2.6*2**30) if (d/'CANDIDATES.jsonl').exists() else 1000000
        with fixture(True,True),patch('s045_search.private_bytes',side_effect=memory2):
            result=run_slice(d,5,3,30,soft_private_bytes=int(2.5*2**30),absolute_deadline=time.time()+1)
        assert result['reason']=='OWNER_DEADLINE_0730' and (d/'STOP').exists();rows.append(result)
    s.atomic(ROOT/'validation/S045/memory_recycle/MEMORY_CONTROLS.json',dict(status='PASS',soft_cooperative_recycle=True,positive_activity_required=True,hard_cap_stays_latched=True,deadline_overrides_recycle=True,native_unsat_overrides_recycle=True,fixtures=rows,source_sha256={p:s.sha(ROOT/p) for p in CORE}))
    print('Memory recycling controls PASS')

if __name__=='__main__':main()
