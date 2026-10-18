"""Serial post-queue S026 audit. May wait without model calls for local queue.

Uses the same already-smoke-accepted local environment. Never starts while the
heavy queue is active. Preserves UNKNOWN on any capped secondary audit.
"""
import argparse
import ctypes
import gzip
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import atomic_json,run_step

LOCAL=ROOT/'artifacts/tmp/S026-local'
OUT=ROOT/'artifacts/tmp/S026-audit'
OUT.mkdir(parents=True,exist_ok=True)
os.environ['EMP_CADICAL']=str(ROOT/'artifacts/tmp/S004/cadical.exe')
os.environ['EMP_DRAT_TRIM']=str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe')


def py(tool,*args):return [sys.executable,str(ROOT/'tools'/tool),*map(str,args)]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canon(w):
    w=list(w)
    return min([tuple(w[i:]+w[:i]) for i in range(5)]+[tuple(reversed(w[i:]+w[:i])) for i in range(5)])


def main():
    p=argparse.ArgumentParser();p.add_argument('--wait',action='store_true');a=p.parse_args()
    if a.wait:print('Audit waiting for the local heavy queue; no model calls.',flush=True)
    while True:
        q=read(LOCAL/'QUEUE.json')
        if q.get('status')=='QUEUE_FINISHED_NOT_A_SESSION_CLOSEOUT':break
        if not a.wait or q.get('status')=='INTERRUPTED_OR_BLOCKED':raise RuntimeError('Local heavy queue not finished')
        time.sleep(30)
    import msvcrt
    lock=(LOCAL/'RUN.lock').open('a+b');lock.seek(0)
    for _ in range(20):
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);break
        except OSError:time.sleep(.5)
    else:raise RuntimeError('Another heavy local runner holds the queue lock')
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    journal=OUT/'RUN_JOURNAL.jsonl'
    def run(args,cap,log):return run_step(args,cap,log,journal,memory_kib=11*1024*1024)
    result={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'status':'IN_PROGRESS','source_checks':{},'containment':[]}
    try:
        assert read(LOCAL/'SMOKE.json')['verdict']=='PASS'
        run_source=run(py('s026_check_source.py',ROOT/'validation/S026/source',OUT/'SOURCE_GRAPH_AUDIT.json'),
                       300,OUT/'source-check.log')
        assert run_source['returncode']==0,run_source
        result['source_checks']['graph_audit']=read(OUT/'SOURCE_GRAPH_AUDIT.json')
        from s025_check import check_split
        from s026_check_source import graph
        data=json.load(gzip.open(ROOT/'validation/S025/C5_CLASSIFY.json.gz','rt'))
        positives={}
        for r in data['results']:
            if r.get('split_checked'):
                key=canon(r['w'])
                if key in positives:continue
                E=graph('Dhc',r['w']);check_split(sum(r['w']),sorted(E),r['E1'],r['E2'])
                positives[key]=r
        positive_domain=set();negative_domain=set();density_rejected=set()
        for w in it.product(range(1,8),repeat=5):
            n=sum(w)
            if n>17 or any(w[i]+w[(i+1)%5]>8 for i in range(5)):continue
            key=canon(w)
            if n<=16:positive_domain.add(key);continue
            cross=sum(w[i]*w[(i+1)%5] for i in range(5))
            edges=cross+sum(x*(x-1)//2 for x in w)
            if cross>4*n-8 or edges>6*n-12:density_rejected.add(key)
            else:negative_domain.add(key)
        assert positive_domain==set(positives) and len(positive_domain)==262
        old=[r for r in read(ROOT/'validation/S025/C5_CERTIFICATES.json') if r.get('certified')]
        obstructions={r['tag']:ROOT/'validation/S025/certs'/('C5-'+r['tag']+'.edges') for r in old}
        certified=set(canon(list(map(int,r['tag']))) for r in old)
        for path in sorted(LOCAL.glob('C5-*/SUMMARY.json')):
            r=read(path)
            if r.get('verdict')=='NONBIPLANAR_CERTIFIED' and r.get('proof',{}).get('certified'):
                tag=path.parent.name[3:];obstructions[tag]=path.parent/'graph.edges'
                certified.add(canon(list(map(int,tag))))
        result['classification']={'positive_classes_rechecked':262,'sum17_required_classes':len(negative_domain),
                                  'sum17_density_rejected_classes':len(density_rejected),
                                  'certified_sum17_classes':len(certified & negative_domain),
                                  'pending_sum17_classes':[list(w) for w in sorted(negative_domain-certified)],
                                  'iff_complete':negative_domain<=certified}
        atomic_json(OUT/'AUDIT.json',result)
        # Independent SAT quotient assignments audit all admitted cases against
        # old obstructions and new certified classes. Stop each candidate once a
        # positive map is found only AFTER the old18 absence audit is completed.
        for candidate in sorted((ROOT/'validation/S026/source/candidates').glob('*/CANDIDATE.json')):
            r=read(candidate);positive_new=False
            for tag,edgefile in obstructions.items():
                old_tag=any(x['tag']==tag for x in old)
                if positive_new and not old_tag:continue
                d=OUT/'containment'/r['name']/tag;d.mkdir(parents=True,exist_ok=True)
                inp={'g6':r['g6'],'w':r['w'],'tag':tag,'candidate':r['name']}
                atomic_json(d/'INPUT.json',inp)
                # The hand-encoded cycle labels must equal the actual certificate.
                targetH=graph('Dhc',list(map(int,tag)))
                recorded={tuple(map(int,l.split())) for l in edgefile.read_text().splitlines() if l.strip()}
                assert targetH==recorded
                cp=d/'RESULT.json'
                prior=read(cp) if cp.exists() else {}
                reusable=False
                if prior.get('verdict')=='AVOIDS_DRAT_VERIFIED':
                    proof=prior['proof']; gz=d/Path(proof['drat_gz']).name
                    reusable=gz.exists() and sha(gz)==proof['drat_gz_sha256'] and sha(d/'contain.cnf')==proof['cnf_sha256']
                elif prior.get('verdict')=='CONTAINS_EXPLICIT_CHECKED':
                    G=graph(r['g6'],r['w']);vm={int(a):b for a,b in prior['vertex_map'].items()}
                    reusable=len(vm)==17 and len(set(vm.values()))==17 and all(tuple(sorted((vm[a],vm[b]))) in G for a,b in targetH)
                if reusable:
                    step={'returncode':0,'reused_verified_case_receipt':True}
                    verdict=prior
                else:
                    step=run(py('s026_containment.py','decide',d/'INPUT.json',d),45,d/'run.log')
                    verdict=read(cp) if cp.exists() and step['returncode']==0 else {'verdict':'UNKNOWN'}
                entry={'candidate':r['name'],'tag':tag,'old18':old_tag,'process':step,**verdict}
                result['containment'].append(entry)
                if verdict['verdict']=='CONTAINS_EXPLICIT_CHECKED':
                    if old_tag:
                        result['status']='BLOCKER_OLD_FILTER_DISAGREEMENT';atomic_json(OUT/'AUDIT.json',result)
                        raise RuntimeError('Independent explicit map contradicts frozen old18 filter')
                    positive_new=True
                atomic_json(OUT/'AUDIT.json',result)
            print(r['name']+': independent old18 audit done; new obstruction map='+str(positive_new),flush=True)
        result['status']='FINISHED_WITH_EXPLICIT_PER_CASE_VERDICTS'
        result['old18_absence_proofs_checked']=sum(x['old18'] and x['verdict']=='AVOIDS_DRAT_VERIFIED' for x in result['containment'])
        result['old18_absence_audit_complete']=result['old18_absence_proofs_checked']==72
        atomic_json(OUT/'AUDIT.json',result)
        print(json.dumps({'audit':result['status'],'classification':result['classification'],
                          'old18_absence_proofs_checked':result['old18_absence_proofs_checked']}),flush=True)
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000);lock.close()


if __name__=='__main__':main()
