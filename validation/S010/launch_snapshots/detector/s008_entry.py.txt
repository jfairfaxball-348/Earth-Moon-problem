"""Live read-only GitHub audit capture and frozen S007 manifest verification."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

REPO='repos/jfairfaxball-348/Earth-Moon-problem/'
MAIN='23d36d93ebb225668180c8499eb6793775d4fa1d'
HEAD='2751cfc659462b888d5579c98358e85d3f909d03'
commands=[['git','ls-remote','origin'],['git','status','--porcelain']]
for ep in ('commits/'+MAIN,'commits/'+HEAD,'pulls/7','pulls/7/commits',
           'pulls?state=all&per_page=100','branches?per_page=100','actions/workflows',
           'actions/runs?per_page=20','actions/runs/38455256198/jobs',
           'actions/runs/38455487692/jobs','commits/'+HEAD+'/check-runs',
           'commits/'+MAIN+'/check-runs','commits/'+HEAD+'/status',
           'commits/'+MAIN+'/status','branches/main/protection','rulesets'):
    commands.append(['gh','api',REPO+ep])
rows=[]
for cmd in commands:
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    row=dict(command=cmd,returncode=r.returncode,stderr=r.stderr)
    try:row['result']=json.loads(r.stdout)
    except ValueError:row['stdout']=r.stdout
    rows.append(row)
data=json.loads(Path('validation/S007_MANIFEST.json').read_text())
table=data['artifact_sha256']
for path,expected in table.items():
    raw=subprocess.check_output(['git','show',MAIN+':'+path])
    assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],path
Path('sessions/S008/ENTRY_EVIDENCE.json').write_text(json.dumps(dict(
    as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    note='Refreshed capture after branch creation; prewrite observations transcribed in INPUT.',
    commands=rows,S007_manifest_git_blob_checks=len(table)),indent=1)+'\n',encoding='utf-8',newline='\n')
print('PASS live entry capture; frozen S007 manifest',len(table),'Git blobs')
