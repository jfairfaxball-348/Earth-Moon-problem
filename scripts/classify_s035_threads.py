"""Read-only thread classification; no SuspendThread/ResumeThread call."""
import ctypes
from ctypes import wintypes as W
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
import s035_preserved_lifecycle as life
from s035_windows import read_json,atomic_json

def main():
    area=ROOT/'artifacts/tmp/S035/campaign';control=area/'RESUME_CONTROL'
    adopted=read_json(control/'ADOPTION.json');symbols=read_json(ROOT/'validation/S035/thread-repair/SYMBOL_CLASSIFICATION.json')
    assert symbols['symbol']=='TppWorkerThread' and symbols['displacement']==0
    module=Path(symbols['module']);assert hashlib.sha256(module.read_bytes()).hexdigest()==symbols['module_sha256']
    address=int(symbols['address'],16);reference=ctypes.string_at(address,64)
    k=life.kernel;k.ReadProcessMemory.argtypes=[W.HANDLE,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)];k.ReadProcessMemory.restype=W.BOOL
    q=life.ntdll.NtQueryInformationThread
    native={c['worker']['pid']:c for c in adopted['contexts']}
    processes={}
    for record in adopted['original_processes']:
        p=life.checked(record);counts=life.thread_counts(record);trusted=life.thread_state(record)
        original={(t['tid'],t['created_ticks']) for t in native[p.pid]['threads']} if p.pid in native else None
        quarantined=[];details=[]
        for row in counts:
            h=k.OpenThread(0x0040,False,row['tid']);assert h
            try:
                pointer=ctypes.c_void_p();n=W.ULONG();assert q(h,9,ctypes.byref(pointer),ctypes.sizeof(pointer),ctypes.byref(n))>=0
            finally:k.CloseHandle(h)
            extra=((row['tid'],row['created_ticks']) not in original) if original is not None else int(row['created_ticks'])>134371680000000000
            if extra:
                assert pointer.value==address,'Unclassified new thread entry point'
                handle=k.OpenProcess(0x410,False,p.pid);assert handle
                try:
                    buf=ctypes.create_string_buffer(64);n=ctypes.c_size_t();assert k.ReadProcessMemory(handle,pointer,buf,64,ctypes.byref(n)) and n.value==64
                    assert buf.raw==reference,'Remote entry code differs from matched local ntdll'
                finally:k.CloseHandle(handle)
                quarantined.append(row)
            details.append(dict(**row,start_address=hex(pointer.value),role='OS_THREADPOOL_QUARANTINED_NEVER_RESUME' if extra else 'ORIGINAL_THREAD'))
        if original is not None:
            assert len(original)==1 and original=={(r['tid'],r['created_ticks']) for r in counts if r not in quarantined}
        processes[str(p.pid)]=dict(start_ticks=record['start_ticks'],kind='NATIVE_ORIGINAL_THREAD_ONLY' if original else 'LEGACY_NEVER_RESUME',threads=counts,quarantined_threads=quarantined,classification=details)
    policy=dict(status='CLASSIFIED_HELPERS_REMAIN_SUSPENDED',processes=processes,symbol_evidence=symbols,creator='NOT_ESTABLISHED; no permission inferred to run these helpers',rule='Resume only original native thread IDs/create times; preserve every helper and all legacy threads suspended')
    target=control/'THREAD_POLICY.json';assert not target.exists(),'Never overwrite a prior policy'
    atomic_json(target,policy);atomic_json(ROOT/'validation/S035/thread-repair/THREAD_POLICY.json',policy)
    print('PASS read-only classification and original-native-only policy; no thread resumed')

if __name__=='__main__':main()
