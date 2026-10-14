"""Fresh native check of every retained non9 proof; no new solver run."""
import datetime, gzip, json, sys
from pathlib import Path
from blowup_chi_cnf import bag_cnf
from check_s009_records import labelled
from s004_certify import write_cnf
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S010');TMP=Path('artifacts/tmp/S010/chi');TMP.mkdir(parents=True,exist_ok=True)
CHECKER=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())

def worker():
    assert json.loads((ROOT/'BASELINE_PASS.json').read_text())['verdict']=='PASS'
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    chi=json.loads(Path('validation/S004/chi10_results.json').read_text());rows=[];consecutive=0
    for i,r in enumerate(corpus):
        if consecutive>=2:rows.append(dict(index=i,verdict='NOT_RUN'));continue
        n,es=labelled(r);col=chi[i]['ten_colouring'];assert len(col)==n and all(0<=x<10 for x in col) and all(col[a]!=col[b] for a,b in es)
        cnf=TMP/'current.cnf';proof=TMP/'current.drat';write_cnf(cnf,*bag_cnf(*r[:2],9))
        rec=chi[i]['bag'];proof.write_bytes(gzip.decompress(Path(rec['archive']).read_bytes()))
        assert sha(cnf)==rec['cnf_sha256'] and sha(proof)==rec['drat_sha256']
        log=ROOT/f'chi-{i:03d}.check.log';run=run_logged([CHECKER,str(cnf),str(proof),'-t','600'],620,log)
        ok=run['returncode']==0 and 's VERIFIED' in log.read_text();consecutive=0 if ok else consecutive+1
        rows.append(dict(index=i,verdict='EXACT_CHI10' if ok else 'UNKNOWN',command=run,cnf_sha256=sha(cnf),
                         proof_raw_sha256=sha(proof),proof_archive=rec['archive'],archive_sha256=sha(rec['archive']),proper10=col))
        save(ROOT/'chromatic_cold_replay.json',rows)
    assert len(rows)==271 and all(r['verdict']=='EXACT_CHI10' for r in rows)
    print('PASS271 fresh native non9/proper10',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1:worker();raise SystemExit
    assert (ROOT/'BASELINE_PASS.json').exists()
    record=ROOT/'chromatic_observed_launch.json';assert not record.exists()
    files=['tools/s010_chromatic_replay.py','tools/blowup_chi_cnf.py','tools/check_s009_records.py','tools/s005_search.py',
           'tools/s004_certify.py','validation/S003/survivors_alpha_ge3.json','validation/S004/chi10_results.json','campaigns/CAM-0011.md']
    native=json.loads((ROOT/'environment.json').read_text())['native_sha256']
    for name,digest in native.items():assert sha(Path('artifacts/tmp/S004')/name)==digest
    snap=ROOT/'launch_snapshots/chromatic';snap.mkdir(parents=True)
    for f in files:
        if f.endswith('.py'):snap.joinpath(Path(f).name+'.txt').write_bytes(Path(f).read_bytes())
    cmd=[sys.executable,'tools/s010_chromatic_replay.py','worker'];save(record,dict(grade='OBSERVED_BEFORE_LAUNCH',
        as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=cmd,sha256={f:sha(f) for f in files},native_sha256=native))
    run=run_logged(cmd,1800,ROOT/'chromatic_driver.log');save(ROOT/'chromatic_command.json',run);print(run);assert run['returncode']==0
