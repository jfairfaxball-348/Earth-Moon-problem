"""SAT-first external supervisor for a FUTURE owner-authorised S035 continuation.

Never launches or resumes computation. A SAT marker is a high-priority alert,
even if independent validation fails or a legacy result says UNKNOWN. The live
guardian tree is suspended without killing processes before verification.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]

def sat_signal(text):
    return bool(re.search(r'^s SATISFIABLE\s*$',text,re.M) or
                re.search(r'"returncode"\s*:\s*10\b',text))

def inspect(area):
    hits=[]
    for p in (Path(area)/'attempts').glob('cell-*/*/*'):
        if p.name not in ('native.log','native-RESULT.json','CANDIDATE.json'):continue
        if p.name=='CANDIDATE.json' or sat_signal(p.read_text(errors='replace')):hits.append(p)
    return hits

def handle(area,hits):
    from s035_windows import read_json,atomic_json,live_identity
    from s035_regions import checkpoint,sha
    import psutil
    area=Path(area);records=[];g=read_json(area/'GUARDIAN.json')
    # The supervisor must run outside the guardian tree.
    if g.get('pid') and live_identity(g['pid'],g['start_ticks']):
        root=psutil.Process(g['pid']);processes=[root,*root.children(recursive=True)]
        assert all(p.pid!=__import__('os').getpid() for p in processes)
        for p in processes:
            try:p.suspend();records.append(dict(pid=p.pid,start_ticks=str(p.create_time())))
            except psutil.NoSuchProcess:pass
    (area/'STOP').touch()
    alert=dict(status='SAT_DISCOVERY_REQUIRES_PROMINENT_REVIEW',paths=[str(p) for p in hits],hashes={str(p):sha(p) for p in hits},processes_suspended=records,ordinary_UNKNOWN_forbidden=True,epoch=time.time(),verification=[])
    # Persist the alert before any validator can fail.
    atomic_json(area/'SAT_ALERT.json',alert)
    contexts=read_json(area/'RESIDENT_CONTEXTS.json').get('contexts',{})
    for c in contexts.values():checkpoint(Path(c['directory'])/'new-cuts.lem',Path(c['directory'])/'SAT_PAUSE_CHECKPOINT.json')
    from s035_engine import independent_sat,materialise
    cfg=read_json(area/'CONFIG.json')
    for directory in sorted({p.parent for p in hits}):
        if (directory/'CANDIDATE.json').exists():
            alert['verification'].append(dict(directory=str(directory),status='EXISTING_CANDIDATE_REQUIRES_DOMAIN_REVIEW'));continue
        target=directory/'SAT_FIRST_CANDIDATE.json'
        try:
            source=directory/'input.inst'
            if not source.exists():
                source=directory/'SAT_FIRST_RECOVERY_INPUT.inst';materialise(source,read_json(directory/'INPUT.json')['recipe'],native=True)
            independent_sat(cfg,source,directory/'native.log',target)
            alert['verification'].append(dict(directory=str(directory),status='INDEPENDENT_CANDIDATE_CHECK_PASS_PENDING_DOMAIN_REVIEW',candidate=str(target)))
        except Exception as exc:
            alert['verification'].append(dict(directory=str(directory),status='SAT_SIGNAL_PRESERVED_VALIDATION_PENDING_OR_FAILED',error=repr(exc)))
    atomic_json(area/'SAT_ALERT.json',alert)
    print('SAT ALERT: campaign suspended; independent review required. '+str(area/'SAT_ALERT.json'),flush=True)
    return alert

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,default=ROOT/'artifacts/tmp/S035/campaign');parser.add_argument('--once',action='store_true');args=parser.parse_args()
    while True:
        hits=inspect(args.directory)
        if hits:handle(args.directory,hits);return
        if args.once:print('No SAT signal found; no process action taken.');return
        time.sleep(.2)

if __name__=='__main__':main()
