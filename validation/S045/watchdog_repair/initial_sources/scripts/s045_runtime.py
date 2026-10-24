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

BASE=ROOT/'artifacts/tmp/S045/campaign'

def guard_reason(started,now,expected,resource):
    if now-started>=8*3600:return 'EIGHT_HOUR_WALL_CEILING'
    if resource:return resource
    for p,h in expected.items():
        if sha(ROOT/p)!=h:return 'SOURCE_OR_BINARY_CHANGED:'+p
    return None

def main():
    BASE.mkdir(parents=True,exist_ok=True)
    controls=json.loads((ROOT/'validation/S045/CONTROLS.json').read_text())
    expected=controls['stop_test']['source_sha256']
    build=json.loads((ROOT/'validation/S045/BUILD.json').read_text())
    expected.update({p:h for p,h in build['sha256'].items() if p.endswith('.exe') and 'bipsat_s045' in p})
    expected[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    started=time.monotonic();done=threading.Event()
    maintenance=BASE/'MAINTENANCE.json'
    if maintenance.exists():
        original=json.loads(maintenance.read_text())['original_started_epoch']
        started-=max(0,time.time()-original)  # preserve the original eight-hour ceiling
    assert not guard_reason(started,started,expected,reason())
    def watch():
        while not done.wait(1):
            try: why=guard_reason(started,time.monotonic(),expected,reason())
            except BaseException as e:why='GUARD_ERROR:'+repr(e)
            if why:
                (BASE/'STOP').touch(exist_ok=True)
                atomic(BASE/'GUARD_STOP.json',dict(reason=why,elapsed_seconds=time.monotonic()-started))
                return
    thread=threading.Thread(target=watch,daemon=True);thread.start()
    try:campaign()
    finally:done.set();thread.join(timeout=5)

if __name__=='__main__':main()
