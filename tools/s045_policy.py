"""S045 timing and first-cause stop policy, independent of solver internals."""
import json
import os
from pathlib import Path
import time


class CampaignStop(Exception):
    pass


def read_cause(out):
    p=Path(out)/'STOP_CAUSE.json'
    for _ in range(30):
        try:return json.loads(p.read_text(encoding='utf-8'))['reason']
        except FileNotFoundError:return 'STOP_FILE'
        except (json.JSONDecodeError,PermissionError):time.sleep(.01)
    return 'STOP_CAUSE_UNREADABLE'


def latch_stop(out,reason,**details):
    """First writer wins; STOP is visible only after the cause is durable."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    path=out/'STOP_CAUSE.json'
    try:
        with path.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(dict(reason=reason,time_epoch=time.time(),**details),f,indent=1)
            f.write('\n');f.flush();os.fsync(f.fileno())
    except FileExistsError:
        reason=read_cause(out)
    (out/'STOP').touch(exist_ok=True)
    return reason


def deadline_reason(deadline_epoch,wall_now,monotonic_deadline=None,mono_now=None):
    if deadline_epoch is not None and (wall_now>=deadline_epoch or
            (monotonic_deadline is not None and mono_now>=monotonic_deadline)):
        return 'OWNER_DEADLINE_0730'
    return None


def slice_timeout(now,spawned,ready,seconds,startup_ceiling=900,response_grace=15):
    if ready is None:
        return 'NATIVE_STARTUP_TIMEOUT' if now-spawned>startup_ceiling else None
    return 'NATIVE_RESPONSE_TIMEOUT' if now-ready>seconds+response_grace else None
