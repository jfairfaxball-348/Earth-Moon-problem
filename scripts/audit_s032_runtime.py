"""Independently audit completed S032 theory clauses and input renaming."""
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tools')]
from check_s032_native import lemmas


def main():
    name=sys.argv[1] if len(sys.argv)>1 else 'diagnostic'
    root=ROOT/'artifacts/tmp/S032';out=root/name
    start=time.monotonic()
    inputs=json.loads((root/'INPUTS.json').read_text())
    controller=json.loads((out/'CONTROLLER.json').read_text())
    assert controller['status']!='SEARCH_RUNNING','Inspect real liveness, do not audit a mutable final file'
    for p,h in inputs['sha256'].items():assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h,p
    rename={int(k):v for k,v in inputs['original_to_native'].items()}
    assert sorted(rename)==sorted(rename.values())==list(range(1,inputs['variables']+1))
    with (root/'original.cnf').open() as old,(root/'base.cnf').open() as new:
        old_head=next(old).split();new_head=next(new).split();assert old_head==new_head
        count=0
        for a,b in zip(old,new,strict=True):
            xs=list(map(int,a.split()));ys=list(map(int,b.split()))
            assert xs[-1]==ys[-1]==0
            assert [rename[abs(x)]*(1 if x>0 else -1) for x in xs[:-1]]==ys[:-1]
            count+=1
        assert count==inputs['base_clauses']==336030
    checked=lemmas(out/'learned.lem',28,[tuple(e) for e in inputs['pairs']])
    raw=(out/'worker.log').read_text()
    matches=re.findall(r'checks=(\d+) nonplanar=(\d+) clauses_added=(\d+) model_checks=(\d+)',raw)
    native_stats=dict(zip(['checks','nonplanar','clauses_added','model_checks'],map(int,matches[-1]))) if matches else None
    if native_stats:assert checked==native_stats['nonplanar']+controller.get('resumed_lemma_count',0)
    data={'status':'PASS','directory':name,'independently_checked_native_clauses':checked,
          'base_clauses':count,'bijective_renaming_checked':True,'native_stats':native_stats,
          'worker_result':controller.get('worker_result'),'verdict':'UNKNOWN',
          'whole_stratum_certified':False,'witness_established':False,
          'native_source_sha256':controller['native_sha256'],
          'lemma_sha256':hashlib.sha256((out/'learned.lem').read_bytes()).hexdigest(),
          'seconds':time.monotonic()-start}
    target=root/('DIAGNOSTIC_AUDIT.json' if name=='diagnostic' else 'CAMPAIGN_AUDIT.json')
    target.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(data,indent=2))


if __name__=='__main__':main()
