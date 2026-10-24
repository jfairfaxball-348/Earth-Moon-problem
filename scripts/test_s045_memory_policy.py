"""Regressions for slow native loading, first cause, hard roof and sealed journals."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import s045_search as search
from s045_driver import run_slice,CORE
from s045_policy import deadline_reason,latch_stop,read_cause,slice_timeout,CampaignStop


def main():
    assert slice_timeout(615,0,None,600) is None
    assert slice_timeout(625,0,25,600) is None
    assert slice_timeout(641,0,25,600)=='NATIVE_RESPONSE_TIMEOUT'
    assert slice_timeout(901,0,None,600)=='NATIVE_STARTUP_TIMEOUT'
    roof=datetime(2026,10,25,7,30,tzinfo=timezone.utc).timestamp()
    assert roof==1792913400
    assert deadline_reason(roof,roof-1,100,99) is None
    assert deadline_reason(roof,roof,100,99)=='OWNER_DEADLINE_0730'
    assert deadline_reason(roof,roof-3600,100,100)=='OWNER_DEADLINE_0730'
    rows=[]
    with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/tmp/S045') as temp:
        temp=Path(temp);first=temp/'first'
        latch_stop(first,'NATIVE_RESPONSE_TIMEOUT');latch_stop(first,'STOP_FILE')
        assert read_cause(first)=='NATIVE_RESPONSE_TIMEOUT'
        journal=temp/'records.jsonl';journal.write_text('{"a":1}\n{"a":2}\n',encoding='ascii')
        saved=journal.read_bytes();receipt=search.seal_file(journal)
        assert receipt['decoded_bytes_verified'] and not journal.exists()
        assert list(search.journal(Path(str(journal)+'.gz')))==[{'a':1},{'a':2}]
        # Simulate a crash after archive promotion but before raw retirement.
        base=temp/'choose';base.mkdir();raw=base/'CANDIDATES.jsonl';raw.write_bytes(saved)
        search.seal_file(raw);raw.write_bytes(saved)
        sources=search.checkpoint_sources(base);assert len(sources)==1
        assert list(search.journal(sources[0]))==[{'a':1},{'a':2}]
        raw.unlink()
        try:
            list(search.journal(sources[0],lambda:(_ for _ in ()).throw(CampaignStop('test'))))
        except CampaignStop:pass
        else:raise AssertionError('checkpoint cancellation not observed')
        expired=run_slice(temp/'expired',5,3,10,absolute_deadline=time.time()-1)
        assert expired['reason']=='OWNER_DEADLINE_0730' and 'generator' not in expired
        real_popen=subprocess.Popen
        def fixture(code):
            def create(command,**kwargs):return real_popen([sys.executable,'-u','-c',code],**kwargs)
            return patch('s045_driver.subprocess.Popen',side_effect=create)
        # Loading itself exceeds the synthetic solve+grace window. READY resets
        # only the solve clock; this would fail with the old spawn-based policy.
        with fixture("import time;time.sleep(.4);print('READY 0',flush=True);time.sleep(.2);print('END 0 0 0',flush=True)"):
            delayed=run_slice(temp/'delayed',5,3,.2,startup_ceiling=5,response_grace=.2)
        assert delayed['state']=='SLICE_COMPLETE' and delayed['native_startup_seconds']>=.4
        assert not (temp/'delayed/STOP').exists();rows.append(delayed)
        with fixture("import sys;sys.stdin.readline();print('END 0 0 0',flush=True)"):
            missing=run_slice(temp/'no-ready',5,3,.2,startup_ceiling=.3,response_grace=.2)
        assert missing['reason']=='NATIVE_STARTUP_TIMEOUT' and missing['native_returncode']==0
        assert read_cause(temp/'no-ready')=='NATIVE_STARTUP_TIMEOUT';rows.append(missing)
        # Deadline works while a child is loading and has not emitted READY.
        with fixture("import sys;sys.stdin.readline();print('END 0 0 0',flush=True)"):
            timed=run_slice(temp/'loading-deadline',5,3,10,absolute_deadline=time.time()+1)
        assert timed['reason']=='OWNER_DEADLINE_0730' and timed['elapsed_seconds']<3
        rows.append(timed)
        # Deadline also works in the post-READY solving stage.
        with fixture("import sys;print('READY 0',flush=True);sys.stdin.readline();print('END 0 0 0',flush=True)"):
            timed=run_slice(temp/'solving-deadline',5,3,10,absolute_deadline=time.time()+1)
        assert timed['reason']=='OWNER_DEADLINE_0730' and timed['elapsed_seconds']<3
        rows.append(timed)
    search.atomic(ROOT/'validation/S045/memory_recycle/POLICY_CONTROLS.json',dict(status='PASS',
        slow_loading=True,first_cause_preserved=True,startup_ceiling=True,deadline_preparation=True,
        deadline_loading=True,deadline_solving=True,clock_rollback=True,compression_verified=True,
        duplicate_archive_recovery=True,deadline_epoch=roof,fixtures=rows,
        source_sha256={name:search.sha(ROOT/name) for name in CORE}))
    print('S045 watchdog policy controls PASS',flush=True)


if __name__=='__main__':main()
