"""Publish the verified owner pause on existing main; never resume computation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_archive_parts import split
from s035_regions import sha
from s035_windows import read_json
OUT=ROOT/'validation/S035/pause'
ENTRY='4eac1237723134f1d1924938f476a06287aab919'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def row(path):return dict(bytes=path.stat().st_size,sha256=sha(path))

def main():
    assert git('branch','--show-current')=='main' and git('rev-parse','HEAD')==ENTRY
    while not (OUT/'ARCHIVE_VERIFICATION.json').exists():time.sleep(1)
    receipt=read_json(OUT/'ARCHIVE_VERIFICATION.json');assert receipt['status']=='PASS_ALL_ORIGINAL_OBJECT_BYTES_AND_GZIP_RECONSTRUCTION'
    archive=OUT/'runtime.tar.xz';assert sha(archive)==receipt['archive_sha256']
    print('ARCHIVE_VERIFIED; creating Git parts',flush=True);split(archive)
    inventory=read_json(OUT/'RUNTIME_INVENTORY.json')
    assert sha(ROOT/inventory['external_archive'])==inventory['external_archive_sha256']
    manifest=dict(status='OWNER_PAUSED_NOT_CLOSED',files={})
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name not in ('MANIFEST.json',) and p.suffix!='.part':manifest['files'][p.relative_to(ROOT).as_posix()]=row(p)
    for name in ('sessions/S035/PAUSE.md','sessions/S035/NINE_REGION_DIAGNOSTIC.md','sessions/S035/RESUME_PROMPT.md',
                 'scripts/archive_s035_pause.py','scripts/restore_s035_pause.py','scripts/audit_s035_pause.py',
                 'scripts/s035_pause_status.py','scripts/s035_sat_first_watch.py','scripts/check_s035_sat_first.py',
                 'scripts/check_s035_pause_records.py','scripts/finalize_s035_pause.py','tools/s035_archive_parts.py'):
        manifest['files'][name]=row(ROOT/name)
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=1)+'\n',encoding='utf-8')
    p=ROOT/'sessions/S035/RUNNING_MANIFEST.json';m=read_json(p)
    m['files']['validation/S035/pause/MANIFEST.json']=row(OUT/'MANIFEST.json')
    for name in m['files']:m['files'][name]=row(ROOT/name)
    p.write_text(json.dumps(m,indent=1)+'\n',encoding='utf-8')
    for script in ('scripts/check_s035_records.py','scripts/check_s035_resident_records.py','scripts/check_s035_sat_first.py','scripts/check_s035_pause_records.py'):
        subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
    pause=json.loads(subprocess.check_output([sys.executable,str(ROOT/'scripts/s035_pause_status.py')],cwd=ROOT,text=True))
    assert pause['all_surviving_processes_suspended'] and all(p['identity_alive'] and p['cpu_delta']==0 for p in pause['processes'])
    assert git('ls-remote','origin','refs/heads/main').split()[0]==ENTRY,'Remote changed; reconcile without reset or force'
    subprocess.run(['git','add','.'],cwd=ROOT,check=True)
    for name in git('diff','--cached','--name-only','--diff-filter=ACM').splitlines():
        assert (ROOT/name).stat().st_size<100*1024*1024, 'Oversized Git file: '+name
    subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
    subprocess.run(['git','commit','-m','S035: pause safely, preserve evidence and prioritize SAT'],cwd=ROOT,check=True)
    commit=git('rev-parse','HEAD');print('COMMIT',commit,flush=True)
    subprocess.run(['git','push','origin','main'],cwd=ROOT,check=True)
    remote=git('ls-remote','origin','refs/heads/main').split()[0];assert remote==commit
    evidence=ROOT/'artifacts/tmp/S035-publication';evidence.mkdir(exist_ok=True)
    value=dict(status='PUSHED_REMOTE_SHA_VERIFIED_HOSTED_JOBS_PENDING',commit=commit,remote=remote,url='https://github.com/jfairfaxball-348/Earth-Moon-problem/commit/'+commit,hosted_jobs='Not yet verified',campaign='PAUSED_ALL_PROCESS_IDENTITIES_RETAINED_SUSPENDED')
    (evidence/'COMMIT.json').write_text(json.dumps(value,indent=1)+'\n')
    print(json.dumps(value),flush=True)

if __name__=='__main__':main()
