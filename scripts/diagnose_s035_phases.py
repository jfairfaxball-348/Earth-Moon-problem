"""Preregistered equal90s native phase comparison on one unresolved S035 region."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_engine import recipe,materialise,audit_cuts,independent_sat
from s035_windows import atomic_json
from s035_regions import sha,ledger
from s026_supervision import run_step

def main():
    area=ROOT/'artifacts/tmp/S035/campaign';out=ROOT/'artifacts/tmp/S035/phase-diagnostic';out.mkdir(exist_ok=False)
    cfg=json.loads((area/'CONFIG.json').read_text());data=json.loads((area/'REGIONS.json').read_text())
    assert all(c['claim'] is None for c in data['cells'])
    native=ROOT/'artifacts/tmp/S035/native-resident/bipsat_s032.exe'
    gate=ROOT/'artifacts/tmp/S035/resident-acceptance'
    assert json.loads((gate/'SMOKE.json').read_text())['verdict']=='PASS'
    controls=json.loads((gate/'NATIVE_CONTROLS.json').read_text())
    assert controls['native_sha256']==sha(native) and controls['exhaustive_n5_fixed_graphs']==1024
    cell=next(c for c in data['cells'] if c['status']=='UNKNOWN')
    value=recipe(cfg,list(data['accepted_cuts']),cell['assumptions'])
    input=out/'shared-input.inst';digest=materialise(input,value,native=True)
    atomic_json(out/'REGISTERED.json',dict(cell=cell['id'],seconds_per_arm=90,arms=['default_congruence','congruence_disabled'],
        input_sha256=digest,recipe=value,native_sha256=sha(native),per_worker_private_cap=2*1024**3,verdict='UNKNOWN'))
    # Each arm has a separately fixed environment; never mutate os.environ across threads.
    def run(name):
        dest=out/name;dest.mkdir();env=os.environ.copy()
        env.pop('EMP_ABSOLUTE_DEADLINE',None)
        if name=='congruence_disabled':env['EMP_S035_DISABLE_CONGRUENCE']='1'
        else:env.pop('EMP_S035_DISABLE_CONGRUENCE',None)
        env['PATH']=str(ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64/bin')+os.pathsep+env['PATH']
        args=[str(native),str(input),'--timeout','90','--lemmas',str(dest/'new-cuts.lem')]
        # A small wrapper supplies the fixed environment to the existing external supervisor.
        fixed_env={'PATH':env['PATH']}
        if name=='congruence_disabled':fixed_env['EMP_S035_DISABLE_CONGRUENCE']='1'
        wrapper=dest/'launch.py';wrapper.write_text('import os,subprocess,sys\nos.environ.pop("EMP_ABSOLUTE_DEADLINE",None)\nos.environ.pop("EMP_S035_DISABLE_CONGRUENCE",None)\nos.environ.update('+repr(fixed_env)+')\nsys.exit(subprocess.call('+repr(args)+'))\n',encoding='utf-8')
        result=run_step([sys.executable,str(wrapper)],105,dest/'native.log',dest/'JOURNAL.jsonl',memory_kib=2*1024*1024)
        assert result['returncode'] in (0,10,20),result
        row=audit_cuts(dest/'new-cuts.lem',cfg,time.time()+600)
        arm_recipe=copy.deepcopy(value)
        if row:
            arm_recipe['sources'].append(row)
            with ledger(area) as current:
                if not any(x['sha256']==row['sha256'] for x in current['accepted_cuts']):current['accepted_cuts'].append(row)
        if result['returncode']==20:
            atomic_json(dest/'PENDING_PROOF.json',dict(recipe=arm_recipe,status='NATIVE_UNSAT_ONLY_UNKNOWN'))
            with ledger(area) as current:current['cells'][cell['id']]['pending_proof']=arm_recipe
        elif result['returncode']==10:
            independent_sat(cfg,input,dest/'native.log',dest/'CANDIDATE.json')
            raise RuntimeError('Candidate requires independent domain review before continuation')
        log=(dest/'native.log').read_text()
        logic=re.findall(r'c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)',log)
        phases=[dict((k,int(v)) for k,v in re.findall(r'(\w+)=(\d+)',line)) for line in log.splitlines() if line.startswith('c S035_PHASE')]
        row=dict(name=name,returncode=result['returncode'],wall_seconds=result['seconds'],
            conflicts=int(logic[-1][0]),decisions=int(logic[-1][1]),propagations=int(logic[-1][2]),
            checked_cut_occurrences=row['count'] if row else 0,phase_samples=phases,
            verdict='UNKNOWN',source_sha256=sha(native))
        atomic_json(dest/'RESULT.json',row);return row
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(run,['default_congruence','congruence_disabled']))
    default,disabled=rows
    choose=bool(default['phase_samples'] and any(p['mode'] & 4 for p in default['phase_samples']) and disabled['conflicts']>default['conflicts'])
    atomic_json(out/'SUMMARY.json',dict(status='PASS_DIAGNOSTIC_NOT_A_MATHEMATICAL_RESULT',rows=rows,
        disable_congruence=choose,selection='Disable optional congruence only if measured flat interval is CONGRUENCE and the other arm advances more search conflicts; no completeness/formula change',
        all_outputs_retained=True,all_new_geometric_clauses_independently_audited=True))
    print(json.dumps(dict(disable_congruence=choose,rows=[{k:v for k,v in r.items() if k!='phase_samples'} for r in rows])),flush=True)

if __name__=='__main__':main()
