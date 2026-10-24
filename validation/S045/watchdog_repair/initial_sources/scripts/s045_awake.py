"""Keep Windows awake only while the exact S045 controller lives, up to its cap."""
import ctypes
import json
import os
from pathlib import Path
import sys
import time

import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s045_search import atomic,identity

def main():
    base=ROOT/'artifacts/tmp/S045/campaign'
    data=json.loads((base/'CAMPAIGN.json').read_text())
    ident=data['controller'];deadline=data['started_epoch']+data['wall_ceiling_seconds']
    if (base/'MAINTENANCE.json').exists():
        original=json.loads((base/'MAINTENANCE.json').read_text())['original_started_epoch']
        deadline=min(deadline,original+data['wall_ceiling_seconds'])
    power=ctypes.WinDLL('kernel32',use_last_error=True)
    power.SetThreadExecutionState.argtypes=[ctypes.c_uint32]
    power.SetThreadExecutionState.restype=ctypes.c_uint32
    assert power.SetThreadExecutionState(0x80000001),'Windows rejected keep-awake request'
    atomic(base/'POWER.json',dict(state='ACTIVE',helper=identity(psutil.Process()),controller=ident,deadline_epoch=deadline,
           display_kept_on=False,system_awake_requested=True))
    try:
        while time.time()<deadline:
            try:
                p=psutil.Process(ident['pid'])
                if abs(p.create_time()-ident['create_time'])>.001 or p.exe().lower()!=ident['exe'].lower():break
            except psutil.Error:break
            time.sleep(5)
    finally:
        power.SetThreadExecutionState(0x80000000)
        atomic(base/'POWER.json',dict(state='RELEASED',helper=identity(psutil.Process()),system_awake_requested=False))

if __name__=='__main__':main()
