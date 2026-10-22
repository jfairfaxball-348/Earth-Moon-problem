"""Audit S034 import and replay each inherited encoded-region proof on Windows."""
import gzip
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_regions import sha, validate_partition
from s035_engine import materialise
from s035_windows import atomic_json
from audit_s033_fast import subdivision

AREA=ROOT/'artifacts/tmp/S035'
OLD=AREA/'imported-s034'

def rebase(value):
    if isinstance(value,list): return [rebase(x) for x in value]
    if isinstance(value,dict): return {k:rebase(v) for k,v in value.items()}
    if isinstance(value,str):
        for a,b in [('/root/Earth-Moon-problem/artifacts/tmp/S034/campaign/',str(OLD)+'\\'),
                    ('/root/Earth-Moon-problem/artifacts/tmp/S032/',str(ROOT/'artifacts/tmp/S032')+'\\')]:
            if value.startswith(a): return str(Path(b)/Path(value[len(a):]))
    return value

def main():
    start=time.monotonic()
    for name,row in json.loads((ROOT/'validation/S034/FINAL_MANIFEST.json').read_text())['files'].items():
        assert (ROOT/name).stat().st_size==row['bytes'] and sha(ROOT/name)==row['sha256'],name
    original=json.loads((OLD/'CONFIG.json').read_text()); cfg=rebase(original)
    data=json.loads((OLD/'REGIONS.json').read_text())
    assert validate_partition(cfg,data['cells']) and all(c['claim'] is None for c in data['cells'])
    assert sha(cfg['base'])==cfg['base_sha256']
    assert sha(ROOT/'artifacts/tmp/S032/INPUTS.json')==cfg['mapping_sha256']
    checked=0
    for row in data['accepted_cuts']:
        p=Path(rebase(row['path'])); assert sha(p)==row['sha256']
        count=0
        with p.open() as f:
            for line in f:
                xs=list(map(int,line.split())); assert xs.pop()==0
                assert xs and len(set(xs))==len(xs) and all(-756<=x<0 for x in xs)
                assert len({(-x-1)%2 for x in xs})==1
                subdivision([tuple(cfg['pairs'][(-x-1)//2]) for x in xs]);count+=1
        assert count==row['count']; checked+=count
    assert checked==93047
    out=AREA/'replay';out.mkdir(exist_ok=True)
    receipts=[]
    for cell in data['cells']:
        if cell['status']!='UNSAT_DRAT_VERIFIED':continue
        oldcert=Path(rebase(cell['certificate']));cert=rebase(json.loads(oldcert.read_text()))
        assert cert['assumptions']==cell['assumptions']==cert['formula_recipe']['assumptions']
        formula=out/f"cell-{cell['id']:04d}.cnf"
        assert materialise(formula,cert['formula_recipe'])==cert['formula_sha256']
        assert sha(cert['proof'])==cert['proof_sha256'] and sha(cert['checker_log'])==cert['checker_log_sha256']
        log=out/f"cell-{cell['id']:04d}.log"
        with log.open('w') as f:
            r=subprocess.run([str(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'),str(formula),cert['proof'],'-t','600'],stdout=f,stderr=subprocess.STDOUT,timeout=630,creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode==0 and 's VERIFIED' in log.read_text(),cell['id']
        receipts.append(dict(cell=cell['id'],formula_sha256=cert['formula_sha256'],proof_sha256=cert['proof_sha256'],checker_sha256=sha(ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'),log_sha256=sha(log),status='FRESH_WINDOWS_DRAT_VERIFIED'))
        formula.unlink()
        atomic_json(AREA/'IMPORT_PROGRESS.json',dict(checked_clauses=checked,replayed_regions=len(receipts)))
    assert len(receipts)==16
    atomic_json(AREA/'IMPORT_AUDIT.json',dict(status='PASS',manifest_files=85,clauses=checked,proofs=receipts,partition='PASS_256_DISJOINT_EXHAUSTIVE',pending_cases=sum(bool(c.get('pending_proof')) for c in data['cells']),seconds=time.monotonic()-start))
    print('PASS S034 manifest,93047 cuts,256 regions and16 fresh Windows DRAT replays',flush=True)

if __name__=='__main__':main()
