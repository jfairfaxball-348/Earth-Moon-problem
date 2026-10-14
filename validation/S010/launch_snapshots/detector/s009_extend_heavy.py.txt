"""One prospective compact/cold continuation; original UNKNOWN remains intact."""
import datetime,gzip,json,shutil,sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged,compress
from s007_run import save
ROOT=Path('validation/S009');OUT=ROOT/'heavy_extended';TMP=Path('artifacts/tmp/S009/heavy_extended')
CHECKER=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())

def worker():
    from s009_heavy_cover import HeavyCover
    from biplanar_cnf import read_edges
    assert json.loads((ROOT/'heavy_accept_stage_command.json').read_text())['returncode']==0
    old=json.loads((ROOT/'heavy/result.json').read_text())
    if old['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
        save(ROOT/'heavy_extension_status.json',dict(status='CONDITIONAL_NOT_RUN_INITIAL_PIPELINE_ALREADY_PASS'));return
    assert old['verdict']=='UNKNOWN';prior=old.get('certificate',{})
    assert prior['solve']['returncode']==20 and prior['check']['returncode']==0
    original=Path('artifacts/tmp/S009/heavy/K7-I5.drat');cnf=Path('artifacts/tmp/S009/heavy/K7-I5.cnf')
    assert sha(original)==prior['proof_sha256'] and sha(cnf)==prior['cnf_sha256']
    assert 's VERIFIED' in (ROOT/'heavy/search/K7-I5.check.log').read_text()
    row=dict(old);row.update(verdict='UNKNOWN',initial_attempt='validation/S009/heavy/result.json',
        initial_pipeline_verdict='UNKNOWN',continuation='SAME_CHECKED_ORIGINAL_NEW_REGISTERED_COMPACT_COLD_BUDGET')
    certificate=dict(prior);row['certificate']=certificate
    certificate['original_check_provenance']='REUSED_ACTUAL_VERIFIED_ORIGINAL_CHECK_NOT_A_NEW_RUN'
    d=json.loads((ROOT/'heavy/search/K7-I5.cuts.json').read_text())
    c=HeavyCover(read_edges(old['edgefile']),d['lex'],d.get('short_links',False));assert c.static==d['static'];c.cuts=d['cuts']
    cold=TMP/'K7-I5.cnf';c.write_cnf(cold);assert cold.read_bytes()==cnf.read_bytes()
    prefix=OUT/'search/K7-I5'
    for suffix in ('.cuts.json','.result.json','.check.log','.proof-solve.log','.regen.log'):
        p=ROOT/'heavy/search'/('K7-I5'+suffix)
        if p.exists():shutil.copyfile(p,str(prefix)+suffix)
    compact=TMP/'K7-I5.core.drat';trimlog=Path(str(prefix)+'.trim.log')
    trim=run_logged([CHECKER,str(cold),str(original),'-l',str(compact),'-t','1200'],1220,trimlog)
    certificate['trim']=trim;save(OUT/'result.json',row)
    if trim['returncode']!=0 or not compact.exists() or 's VERIFIED' not in trimlog.read_text():return
    checklog=Path(str(prefix)+'.core.check.log')
    check=run_logged([CHECKER,str(cold),str(compact),'-t','1200'],1220,checklog)
    certificate['core_check']=check;save(OUT/'result.json',row)
    if check['returncode']!=0 or 's VERIFIED' not in checklog.read_text():return
    compress(cold,str(prefix)+'.cnf.gz');compress(compact,str(prefix)+'.drat.gz')
    certificate.update(archive=str(prefix)+'.drat.gz',archive_raw_sha256=sha(compact),
        archive_raw_bytes=compact.stat().st_size,archive_sha256=sha(str(prefix)+'.drat.gz'))
    # Freshly read retained bytes and regenerate the exact necessary CNF again.
    regen=TMP/'K7-I5.cold.cnf';c.write_cnf(regen)
    assert regen.read_bytes()==gzip.decompress(Path(str(prefix)+'.cnf.gz').read_bytes())
    proof=TMP/'K7-I5.cold.drat';proof.write_bytes(gzip.decompress(Path(certificate['archive']).read_bytes()))
    assert sha(proof)==certificate['archive_raw_sha256']
    log=Path(str(prefix)+'.cold.check.log')
    run=run_logged([CHECKER,str(regen),str(proof),'-t','1200'],1220,log);certificate['cold_retained_check']=run
    if run['returncode']==0 and 's VERIFIED' in log.read_text():
        row['verdict']=certificate['verdict']='NON_BIPLANAR_DRAT_VERIFIED'
        row['cnf_package']=dict(grade='FULL_CNF_CHECKED_DRAT',cuts=len(d['cuts']),static=d['static'],
            raw_sha256=sha(regen),archive=str(prefix)+'.cnf.gz',archive_sha256=sha(str(prefix)+'.cnf.gz'),
            initial_raw_sha256=sha(regen),initial_archive=str(prefix)+'.cnf.gz',initial_archive_sha256=sha(str(prefix)+'.cnf.gz'))
    save(OUT/'result.json',row);print('Heavy continuation',row['verdict'],flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker();raise SystemExit
    (OUT/'search').mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
    p=ROOT/'heavy_extension_observed_launch.json';assert not p.exists()
    files=['tools/s009_extend_heavy.py','tools/s009_heavy_cover.py','tools/s005_search.py',
           'validation/S009/heavy/result.json','campaigns/CAM-0010.md']
    cmd=[sys.executable,'tools/s009_extend_heavy.py','worker']
    native=json.loads((ROOT/'environment.json').read_text())['native_sha256']
    for name,exp in native.items():assert sha(Path('artifacts/tmp/S004')/name)==exp
    snap=ROOT/'launch_snapshots/heavy_extension';snap.mkdir(parents=True,exist_ok=True)
    for f in files:(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    save(p,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256={f:sha(f) for f in files},
        native_sha256=native,original_raw_sha256=sha('artifacts/tmp/S009/heavy/K7-I5.drat'),
        cnf_sha256=sha('artifacts/tmp/S009/heavy/K7-I5.cnf'),grade='OBSERVED_BEFORE_LAUNCH'))
    r=run_logged(cmd,4800,ROOT/'heavy_extension_driver.log');save(ROOT/'heavy_extension_command.json',r)
    print(r,flush=True);assert r['returncode']==0
