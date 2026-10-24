"""S044 bounded verification only. Windows jobs account for all descendant CPU."""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'validation/S044'
TMP = ROOT/'artifacts/tmp/S044'


class Accounting(C.Structure):
    _fields_ = [(n, C.c_longlong) for n in ('user', 'kernel', 'period_user', 'period_kernel')]+[(n, W.DWORD) for n in ('faults', 'total', 'active', 'terminated')]


def main():
    assert os.name == 'nt', 'this accounting driver is Windows-specific'
    assert not (OUT/'VERIFICATION.json').exists(), 'do not overwrite a completed audit'
    reg = json.loads((OUT/'REGISTRATION.json').read_text())
    for p, h in reg['sha256'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h
    k = C.WinDLL('kernel32', use_last_error=True)
    k.CreateJobObjectW.argtypes = [W.LPVOID, W.LPCWSTR]; k.CreateJobObjectW.restype = W.HANDLE
    k.AssignProcessToJobObject.argtypes = [W.HANDLE, W.HANDLE]; k.AssignProcessToJobObject.restype = W.BOOL
    k.QueryInformationJobObject.argtypes = [W.HANDLE, C.c_int, W.LPVOID, W.DWORD, W.LPVOID]; k.QueryInformationJobObject.restype = W.BOOL
    k.TerminateJobObject.argtypes = [W.HANDLE, W.UINT]; k.TerminateJobObject.restype = W.BOOL
    k.CloseHandle.argtypes = [W.HANDLE]; k.CloseHandle.restype = W.BOOL
    checks = ['scripts/cloud_smoke.py', 'scripts/check_s037_records.py',
              'scripts/check_s038_records.py', 'scripts/check_s040_handoff.py',
              'scripts/check_s039_adversarial.py', 'scripts/check_s040_adversarial.py',
              'scripts/check_s040_records.py', 'scripts/check_s041_adversarial.py',
              'scripts/check_s041_records.py', 'scripts/check_s042_adversarial.py',
              'scripts/check_s042_records.py', 'scripts/check_s043_adversarial.py',
              'scripts/check_s043_records.py']
    # The child waits until job assignment. All scientific work happens in the job.
    gate_code = ('import pathlib,sys,time,runpy; p=pathlib.Path(sys.argv[1]); '
                 'target=sys.argv[2];\nwhile not p.exists(): time.sleep(.01)\n'
                 'sys.path.insert(0,str(pathlib.Path(target).parent)); sys.argv=[target]; '
                 'runpy.run_path(target,run_name="__main__")')
    env = dict(os.environ, PYTHONPATH=str(ROOT/'.venv/Lib/site-packages'),
               EMP_CADICAL=str(ROOT/'artifacts/tmp/S004/cadical.exe'),
               EMP_DRAT_TRIM=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'))
    rows, total = [], 0.0
    started, own_start = time.monotonic(), time.process_time()
    for index, check in enumerate(checks):
        gate = TMP/f'gate-{index}'
        assert not gate.exists()
        job = k.CreateJobObjectW(None, None)
        assert job
        log = TMP/(Path(check).stem+'.log')
        with log.open('w', encoding='utf-8') as f:
            p = subprocess.Popen([sys._base_executable, '-c', gate_code, str(gate), str(ROOT/check)], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
            assigned = k.AssignProcessToJobObject(job, W.HANDLE(int(p._handle)))
            if not assigned:
                p.terminate(); p.wait()
                raise OSError(C.get_last_error(), 'job assignment failed; no checker released')
            gate.touch()
            capped = False
            while True:
                a = Accounting()
                assert k.QueryInformationJobObject(job, 1, C.byref(a), C.sizeof(a), None)
                cpu = (a.user+a.kernel)/10_000_000
                # 0.1s/process conservative allowance for pre-assignment bootstrap.
                bound = total+cpu+(index+1)*.1+time.process_time()-own_start
                if bound >= 600 or time.monotonic()-started >= 900:
                    assert k.TerminateJobObject(job, 124)
                    capped = True
                if p.poll() is not None and a.active == 0:
                    break
                time.sleep(.02)
            p.wait()
        assert k.QueryInformationJobObject(job, 1, C.byref(a), C.sizeof(a), None)
        cpu = (a.user+a.kernel)/10_000_000
        total += cpu
        k.CloseHandle(job)
        row = dict(script=check, returncode=p.returncode, cpu_seconds=cpu,
                   processes=a.total, capped=capped, log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
                   output_tail=log.read_text(encoding='utf-8', errors='replace')[-1800:])
        rows.append(row)
        print(json.dumps(row), flush=True)
        if check.endswith('cloud_smoke.py') and p.returncode == 0:
            data = (ROOT/'artifacts/tmp/cloud_smoke/RESULT.json').read_text()
            (OUT/'SMOKE.json').write_text(data, encoding='utf-8', newline='\n')
        if capped or p.returncode != 0:
            break
    result = dict(status='PASS' if len(rows) == len(checks) and all(r['returncode'] == 0 and not r['capped'] for r in rows) else 'INCOMPLETE',
                  checks=rows, job_cpu_seconds=total, supervisor_cpu_seconds=time.process_time()-own_start,
                  bootstrap_allowance_seconds=.1*len(rows), cpu_upper_accounted=total+time.process_time()-own_start+.1*len(rows),
                  wall_seconds=time.monotonic()-started, cpu_cap=600,
                  scope='fresh environment smoke plus frozen portable replay; no new search or fresh 97-proof DRAT replay')
    (OUT/'VERIFICATION.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    assert result['status'] == 'PASS' and result['cpu_upper_accounted'] < 600


if __name__ == '__main__':
    main()
