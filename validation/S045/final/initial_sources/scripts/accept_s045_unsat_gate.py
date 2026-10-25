"""Bind the final UNSAT-priority amendment to its tests and prior normal benchmark."""
import hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'validation/S045/memory_recycle';B=ROOT/'artifacts/tmp/S045/campaign'
sys.path.insert(0,str(ROOT/'tools'))
from s045_search import atomic,sha
from s045_driver import CORE
ADDED=b"        if p.returncode==20:\n            guard=latch_stop(out,'NATIVE_UNSAT_UNCERTIFIED',stage=stage)\n"
def main():
    b=json.loads((V/'RESTART_BENCHMARK.json').read_text());assert b['status']=='PASS' and b['native_returncode']==0
    current={p:sha(ROOT/p) for p in CORE}
    data=(ROOT/'tools/s045_driver.py').read_bytes();assert data.count(ADDED)==1
    assert hashlib.sha256(data.replace(ADDED,b'',1)).hexdigest()==b['source_sha256']['tools/s045_driver.py']
    assert sha(V/'unsat_amendment/driver_before.py')==b['source_sha256']['tools/s045_driver.py']
    for p,h in current.items():
        if p!='tools/s045_driver.py':assert b['source_sha256'][p]==h,p
    for name in ('MEMORY_CONTROLS','POLICY_CONTROLS','CONTROLS'):
        row=json.loads((V/(name+'.json')).read_text());assert row['status']=='PASS'
        assert (row['stop_test']['source_sha256'] if name=='CONTROLS' else row['source_sha256'])==current
    controls=json.loads((V/'MEMORY_CONTROLS.json').read_text());assert controls['native_unsat_overrides_recycle']
    assert any(r['reason']=='NATIVE_UNSAT_UNCERTIFIED' and r['native_returncode']==20 and r['state']=='STOPPED' for r in controls['fixtures'])
    for name in ('CAMPAIGN','STATUS','STOP_CAUSE'):
        shutil.copy2(B/(name+'.json'),V/'unsat_amendment'/(name+'.json'))
    atomic(V/'UNSAT_GATE_AMENDMENT.json',dict(status='PASS',current_source_sha256=current,benchmark_source_sha256=b['source_sha256'],only_source_delta='tools/s045_driver.py adds unconditional post-exit return-code-20 latch',normal_exit_zero_path_byte_identical=True,native_unsat_overrides_recycle=True,benchmark_rerun_after_amendment=False,scope='Prior full-checkpoint benchmark used the preceding driver and returned 0. Exact byte comparison removes only the guarded return-code-20 block. Fresh full native, timing and memory regressions use final source hashes; forced concurrent recycle/UNSAT stays STOPPED.'))
    a=json.loads((V/'ACCEPTANCE.json').read_text());a['source_sha256']=current
    a['benchmark_source_sha256']=b['source_sha256'];a['benchmark_compatibility']='UNSAT_GATE_AMENDMENT.json: normal exit-zero path unchanged by exact byte comparison; source hashes are explicitly different'
    atomic(V/'ACCEPTANCE.json',a)
    note='''\n\nFinal UNSAT-priority amendment: while the resumed controller was still in\ncheckpoint replay (no native generator), review found that concurrent memory\nrecycle and native exit 20 needed an unconditional stop latch. Replay was\ncooperatively paused; final native/protocol, timing and memory regressions PASS,\nincluding forced concurrent recycle/UNSAT remaining STOPPED. The prior full\ncheckpoint benchmark returned 0 and retains its ORIGINAL source hashes. An\nexact byte comparison proves the only driver delta is the added exit-20 latch;\nthe normal exit-zero path is unchanged. It was not labelled a rerun of that\nfull benchmark. See memory_recycle/UNSAT_GATE_AMENDMENT.json for this explicit\ncompatibility gate and final tested hashes. No mathematical claim follows.\n'''
    for p in ('sessions/S045/EXECUTION_PROMPT.md','sessions/S045/RUNNING.md','sessions/S045/RESEARCH.md','sessions/S045/ADVERSARIAL.md'):
        path=ROOT/p;path.write_text(path.read_text(encoding='utf-8')+note,encoding='utf-8',newline='\n')
    shutil.copy2(ROOT/'sessions/S045/EXECUTION_PROMPT.md',ROOT/'authoritative/NEXT_SESSION_PROMPT.md')
    p=ROOT/'authoritative/STATE.json';state=json.loads(p.read_text());state['current_computation']='REPAIR_ACCEPTED_AWAITING_RESTART'
    state['s045_memory_recycle']['unsat_priority_amendment']='PASS_EXPLICIT_NORMAL_PATH_COMPATIBILITY'
    atomic(p,state)
    print('Final UNSAT-priority gate and explicit prior-benchmark compatibility PASS')
if __name__=='__main__':main()
