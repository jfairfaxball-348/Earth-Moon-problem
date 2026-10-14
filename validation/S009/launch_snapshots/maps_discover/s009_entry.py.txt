"""S009 live API evidence and frozen manifest blob audit (no scientific verdict)."""
import datetime, hashlib, json, subprocess
from pathlib import Path
MAIN='7957452c79c2b31088f93fff440783328c78942d'
HEAD='cbdb8236f27d8f39ceeb268975cd47ac39fc323a'
commands=[['git','ls-remote','origin'],['git','status','--porcelain']]
for ep in ('commits/'+MAIN,'commits/'+HEAD,'pulls/8','pulls/8/commits',
    'pulls?state=all&per_page=100','branches?per_page=100','actions/workflows',
    'actions/runs?per_page=20','actions/runs/38558584715/jobs','actions/runs/38558755112/jobs',
    'commits/'+HEAD+'/check-runs','commits/'+MAIN+'/check-runs',
    'commits/'+HEAD+'/status','commits/'+MAIN+'/status','branches/main/protection','rulesets'):
    commands.append(['gh','api','repos/jfairfaxball-348/Earth-Moon-problem/'+ep])
rows=[]
for cmd in commands:
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    row=dict(command=cmd,returncode=r.returncode,stderr=r.stderr)
    try:row['result']=json.loads(r.stdout)
    except ValueError:row['stdout']=r.stdout
    rows.append(row)
table=json.loads(Path('validation/S008_MANIFEST.json').read_text())['artifact_sha256']
for path,exp in table.items():
    raw=subprocess.check_output(['git','show',MAIN+':'+path])
    assert len(raw)==exp['bytes'] and hashlib.sha256(raw).hexdigest()==exp['sha256'],path
Path('sessions/S009/ENTRY_EVIDENCE.json').write_text(json.dumps(dict(
    as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commands=rows,
    note='Capture after isolated branch creation; prewrite observations in INPUT.',
    S008_manifest_git_blob_checks=len(table)),indent=1)+'\n',encoding='utf-8',newline='\n')
print('PASS live S009 entry and',len(table),'frozen Git blobs')
