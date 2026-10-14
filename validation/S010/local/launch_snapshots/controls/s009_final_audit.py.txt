"""One completed-source cold CNF audit plus independent record/label verification."""
import datetime,gzip,json,sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save
ROOT=Path('validation/S009');TMP=Path('artifacts/tmp/S009')

def worker():
    import s009_run
    import check_s009_records
    from s009_heavy_evidence import effective_heavy
    s009_run.audit()
    row,record,prefix=effective_heavy()
    if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED' and 'heavy_extended' in str(record):
        from s009_heavy_cover import HeavyCover
        from biplanar_cnf import read_edges
        d=json.loads(Path(str(prefix)+'.cuts.json').read_text())
        c=HeavyCover(read_edges(row['edgefile']),d['lex'],d.get('short_links',False));assert c.static==d['static'];c.cuts=d['cuts']
        p=TMP/'independent-extended-heavy.cnf';c.write_cnf(p)
        assert p.read_bytes()==gzip.decompress(Path(str(prefix)+'.cnf.gz').read_bytes())
        assert sha(p)==row['certificate']['cnf_sha256']
        save(ROOT/'EXTENDED_COLD_CNF_AUDIT_PASS.json',dict(record=str(record),cnf_sha256=sha(p),verdict='PASS'))
    check_s009_records.worker()
    assert json.loads((ROOT/'public_control_command.json').read_text())['returncode']==0
    assert len(json.loads((ROOT/'public_control_repeat.json').read_text()))==23
    print('PASS final cold selected-source CNFs, public controls and independent label/proof/colour/map records',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker();raise SystemExit
    p=ROOT/'final_audit_observed_launch.json';assert not p.exists()
    files=['tools/s009_final_audit.py','tools/check_s009_records.py','tools/s009_run.py','tools/s009_heavy_cover.py',
        'tools/s009_heavy_evidence.py','tools/s005_search.py','validation/S009/full/results.json',
        'validation/S009/heavy/result.json','campaigns/CAM-0010.md']
    from s009_heavy_evidence import effective_heavy
    _,record,_=effective_heavy();files.append(str(record))
    snap=ROOT/'launch_snapshots/final_audit';snap.mkdir(parents=True,exist_ok=True)
    for f in sorted(set(files)):(snap/(Path(f).name+'.txt')).write_bytes(Path(f).read_bytes())
    cmd=[sys.executable,'tools/s009_final_audit.py','worker']
    save(p,dict(command=cmd,as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256={f:sha(f) for f in set(files)},
        grade='OBSERVED_BEFORE_LAUNCH',effective_source=str(record)))
    r=run_logged(cmd,3600,ROOT/'final_audit_driver.log');save(ROOT/'final_audit_command.json',r)
    print(r,flush=True);assert r['returncode']==0
