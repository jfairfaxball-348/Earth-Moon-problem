#!/usr/bin/env python3
"""CAM-0008 D: independent Kuratowski-only challenge, retained partial lemmas."""
import json
import shutil
import sys
import time
from pathlib import Path
from pysat.solvers import Cadical153
from biplanar_cegar import Cegar
from biplanar_cnf import read_edges
from s007_run import ROOT,TMP,save,CHECKER
from s004_certify import write_cnf
from s005_replay import sha
from s005_search import run_logged,compress
from check_layers import main as check_split,certify_layer


def export(c,p,verdict,iterations):
    clauses=list(c.base)
    for lemma in c.lemmas:
        lits=[c.idx[e] for e in lemma];clauses.extend([lits,[-x for x in lits]])
    # Match the canonical original clause order for the separate checker.
    clauses=list(c.base)
    for lemma in c.lemmas:
        lits=[c.idx[e] for e in lemma];clauses.extend([[-x for x in lits],lits])
    write_cnf(Path(str(p)+'.cnf'),c.nv,clauses)
    save(str(p)+'.lemmas.json',dict(edges=c.edges,lemmas=c.lemmas,perms=c.perms))
    save(str(p)+'.result.json',dict(verdict=verdict,iterations=iterations,lemmas=len(c.lemmas),symmetries=len(c.perms)))


def worker():
    edges=read_edges(str(ROOT/'heavy/K7-I5.edges'));c=Cegar(edges,seed=1);p=TMP/'heavy-cegar/K7-I5'
    start=time.monotonic()
    with Cadical153(bootstrap_with=c.base) as solver:
        c.seed_small(solver,cap=200000);it=0
        while time.monotonic()-start<900:
            it+=1;export(c,p,'RUNNING',it)
            if not solver.solve():export(c,p,'UNSAT',it);return
            model={x for x in solver.get_model() if x>0}
            layers=[[e for e in edges if (c.idx[e] in model)==(i==0)] for i in range(2)]
            added=sum(c.lemmas_from(es,solver,12) for es in layers)
            if not added:
                save(str(p)+'.split.json',dict(n=12,E1=layers[0],E2=layers[1]));export(c,p,'SAT',it);return
        export(c,p,'UNKNOWN',it)


def main():
    root=ROOT/'heavy-cegar';root.mkdir(exist_ok=True);tmp=TMP/'heavy-cegar';tmp.mkdir(exist_ok=True)
    save(ROOT/'heavy_cegar_launch_hashes.json',{x:sha(x) for x in ('tools/s007_heavy_cegar.py','tools/biplanar_cegar.py','tools/check_cegar_certificate.py')})
    p=tmp/'K7-I5';r=run_logged([sys.executable,'tools/s007_heavy_cegar.py','worker'],920,str(p)+'.run.log')
    row=dict(verdict='UNKNOWN',run=r)
    if Path(str(p)+'.result.json').exists():row['search']=json.loads(Path(str(p)+'.result.json').read_text())
    if Path(str(p)+'.cnf').exists():
        validation=run_logged([sys.executable,'tools/check_cegar_certificate.py',str(ROOT/'heavy/K7-I5.edges'),str(p)],200,str(p)+'.regen.log')
        assert validation['returncode']==0;row['lemma_check']=validation
        edges=read_edges(str(ROOT/'heavy/K7-I5.edges'));c=Cegar(edges)
        data=json.loads(Path(str(p)+'.lemmas.json').read_text());clauses=list(c.base)
        for k in data['lemmas']:
            lits=[c.idx[tuple(e)] for e in k];clauses.extend([[-x for x in lits],lits])
        regen=Path(str(p)+'.regenerated.cnf');write_cnf(regen,c.nv,clauses)
        assert regen.read_bytes()==Path(str(p)+'.cnf').read_bytes();row['cnf_sha256']=sha(regen)
    if r['returncode']==0 and row.get('search',{}).get('verdict')=='SAT':
        split=json.loads(Path(str(p)+'.split.json').read_text());check_split(str(ROOT/'heavy/K7-I5.edges'),str(p)+'.split.json')
        col=list(range(7))+[7]*5;assert all(col[a]!=col[b] for a,b in read_edges(str(ROOT/'heavy/K7-I5.edges')))
        row.update(verdict='BIPLANAR_CONTROL',V=list(range(12)),split=split,chi=8,proper_eight_colouring=col,
            explicit_K8=list(range(8)),component_faces=[certify_layer(12,split[k]) for k in ('E1','E2')])
    elif r['returncode']==0 and row.get('search',{}).get('verdict')=='UNSAT':
        assert (ROOT/'BASELINE_PASS.json').exists()
        proof=Path(str(p)+'.drat');solver=str(Path('artifacts/tmp/S004/cadical.exe').resolve())
        solve=run_logged([solver,'-q','--no-binary',str(p)+'.cnf',str(proof)],1220,str(p)+'.solve.log');row['solve']=solve
        if solve['returncode']==20:
            log=Path(str(p)+'.check.log');check=run_logged([CHECKER,str(p)+'.cnf',str(proof),'-t','1200'],1220,log);row['check']=check
            if check['returncode']==0 and 's VERIFIED' in log.read_text():
                core=Path(str(p)+'.core.drat');trimlog=Path(str(p)+'.trim.log')
                trim=run_logged([CHECKER,str(p)+'.cnf',str(proof),'-l',str(core),'-t','600'],620,trimlog);row['trim']=trim;selected=proof
                if trim['returncode']==0 and core.exists() and 's VERIFIED' in trimlog.read_text():
                    corelog=Path(str(p)+'.core.check.log');chk=run_logged([CHECKER,str(p)+'.cnf',str(core),'-t','600'],620,corelog);row['core_check']=chk
                    if chk['returncode']==0 and 's VERIFIED' in corelog.read_text():selected=core
                compress(selected,root/'K7-I5.drat.gz')
                row.update(verdict='NON_BIPLANAR_DRAT_VERIFIED',original_proof_sha256=sha(proof),
                    archive=str(root/'K7-I5.drat.gz'),archive_sha256=sha(root/'K7-I5.drat.gz'),archive_raw_sha256=sha(selected),archive_raw_bytes=selected.stat().st_size)
    for suffix in ('.result.json','.lemmas.json','.run.log','.regen.log','.solve.log','.check.log','.trim.log','.core.check.log','.split.json'):
        file=Path(str(p)+suffix)
        if file.exists():shutil.copyfile(file,root/('K7-I5'+suffix))
    if Path(str(p)+'.cnf').exists():compress(str(p)+'.cnf',root/'K7-I5.cnf.gz')
    save(ROOT/'heavy_cegar_result.json',row)
    print('K7-I5 Kuratowski',row['verdict'],flush=True)


if __name__=='__main__':
    if 'worker' in sys.argv:worker()
    else:main()
