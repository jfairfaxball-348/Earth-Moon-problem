"""Merge all accepted benchmark outputs, select measured concurrency and launch once."""
import copy
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import atomic_json, memory_available
from s035_regions import sha, validate_partition
from s035_storage import digest
from prepare_s035 import prepared,write_area
AREA=ROOT/'artifacts/tmp/S035'

def main():
    result=json.loads((AREA/'BENCHMARKS.json').read_text());assert result['status']=='PASS'
    rows={r['workers']:r for r in result['rows']}
    concurrency=json.loads((AREA/'SOLVER_CONCURRENCY.json').read_text())
    for count in (1,2,3):assert rows[count]['peak_genuine_worker_slots']==count
    assert concurrency['2']['solvers']>=2
    safe3=concurrency['3']['solvers']==3 and rows[3]['peak_private_bytes']*1.5<6*1024**3 and rows[3]['minimum_available_kib']>3*1024*1024
    throughput=lambda r:(r['new_proof_closed_regions'],r['new_checked_cuts'])
    workers=3 if safe3 and throughput(rows[3])>throughput(rows[2]) else 2
    assert memory_available()>3*1024*1024
    cfg,data=prepared(workers)
    baseline=copy.deepcopy(data)
    aliases=[]
    for count in (1,2,3):
        other=json.loads((AREA/f'benchmark-{count}/REGIONS.json').read_text())
        assert all(c['claim'] is None for c in other['cells']) and validate_partition(cfg,other['cells'])
        for row in other['accepted_cuts']:
            assert sha(row['path'])==row['sha256']
            match=next((x for x in data['accepted_cuts'] if x['sha256']==row['sha256']),None)
            if match:
                assert match['count']==row['count']
                if match['path']!=row['path']:aliases.append(dict(same_literal_mapping=True,sha256=row['sha256'],retained=match['path'],also_retained=row['path']))
            else:data['accepted_cuts'].append(row)
        for cell,old,initial in zip(data['cells'],other['cells'],baseline['cells'],strict=True):
            cell['visits']+=old['visits']-initial['visits'];cell['seconds']+=old['seconds']-initial['seconds']
            if old['status']=='UNSAT_DRAT_VERIFIED' and initial['status']!='UNSAT_DRAT_VERIFIED':
                cert=json.loads(Path(old['certificate']).read_text());proof=Path(cert['proof'])
                if proof.exists():actual=digest(proof)[0]
                else:actual=digest(proof.with_suffix(proof.suffix+'.gz'),True)[0]
                assert actual==cert['proof_sha256'] and sha(cert['checker_log'])==cert['checker_log_sha256']
                assert cert['cell']==cell['id'] and cert['assumptions']==cell['assumptions']
                cell.update(status='UNSAT_DRAT_VERIFIED',certificate=old['certificate'],pending_proof=None,last_outcome='INDEPENDENT_DRAT_VERIFIED')
            elif cell['status']!='UNSAT_DRAT_VERIFIED' and old.get('pending_proof'):
                cell['pending_proof']=old['pending_proof']
    cfg.update(concurrency_increase_validated=True,concurrency_selection=dict(workers=workers,reason='Greater checked-region throughput with measured memory headroom' if workers==3 else 'Two workers supported; third did not improve checked-region/cut throughput sufficiently',benchmarks_sha256=sha(AREA/'BENCHMARKS.json'),solver_concurrency_sha256=sha(AREA/'SOLVER_CONCURRENCY.json')))
    cfg['source_sha256']['scripts/start_s035.py']=sha(Path(__file__))
    atomic_json(AREA/'BENCHMARK_MERGE.json',dict(status='PASS',total_visits=sum(c['visits'] for c in data['cells']),proof_closed_regions=sum(c['status']=='UNSAT_DRAT_VERIFIED' for c in data['cells']),retained_checked_sources=len(data['accepted_cuts']),retained_new_occurrences=sum(r['count'] for r in data['accepted_cuts'])-93047,identical_block_aliases=aliases,all_benchmark_outputs_retained=True))
    area=AREA/'campaign';write_area(area,cfg,data)
    with (area/'launcher.log').open('a') as log:
        p=subprocess.Popen([sys.executable,str(ROOT/'scripts/s035_campaign.py'),'guard'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP)
    print(json.dumps(dict(guardian_launcher_pid=p.pid,workers=workers,config=str(area/'CONFIG.json'),deadline=None)),flush=True)

if __name__=='__main__':main()
