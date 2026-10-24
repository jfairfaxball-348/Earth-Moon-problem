"""Independent in-process guard around the accepted S045 campaign driver.

The guard latches STOP; it does not restart a campaign or touch legacy PIDs.
"""
import json
from pathlib import Path
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s045_search import atomic,campaign,reason,sha
from s045_policy import deadline_reason,latch_stop

BASE=ROOT/'artifacts/tmp/S045/campaign'

def guard_reason(deadline_epoch,now,expected,resource):
    if now>=deadline_epoch:return 'OWNER_DEADLINE_0730'
    if resource:return resource
    for p,h in expected.items():
        if sha(ROOT/p)!=h:return 'SOURCE_OR_BINARY_CHANGED:'+p
    return None

def main():
    BASE.mkdir(parents=True,exist_ok=True)
    controls=json.loads((ROOT/'validation/S045/watchdog_repair/ACCEPTANCE.json').read_text())
    expected=dict(controls['source_sha256'])
    build=json.loads((ROOT/'validation/S045/watchdog_repair/BUILD.json').read_text())
    expected.update({p:h for p,h in build['sha256'].items() if p.endswith('.exe') and 'bipsat_s045' in p})
    expected[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    cfg=BASE/'DEADLINE.json';directive=json.loads(cfg.read_text());roof=directive['deadline_epoch']
    expected[str(cfg.relative_to(ROOT))]=sha(cfg)
    started=time.monotonic();mono_roof=started+max(0,roof-time.time());done=threading.Event()
    assert not guard_reason(roof,time.time(),expected,reason())
    def watch():
        while not done.wait(.25):
            try:
                why=deadline_reason(roof,time.time(),mono_roof,time.monotonic())
                if not why:why=guard_reason(roof,time.time(),expected,reason())
            except BaseException as e:why='GUARD_ERROR:'+repr(e)
            if why:
                latch_stop(BASE,why)
                atomic(BASE/'GUARD_STOP.json',dict(reason=why,elapsed_seconds=time.monotonic()-started))
                return
    thread=threading.Thread(target=watch,daemon=True);thread.start()
    try:campaign()
    finally:done.set();thread.join(timeout=5)

if __name__=='__main__':main()
