"""Live entry reconciliation and whole incoming manifest audit; no solver."""
import datetime, hashlib, json, subprocess
from pathlib import Path

ENTRY='8626b6419f12d706f3ba567f6733d26d6e4dd7be'
AUTHOR='6a3765f6db7d7a6bd8197ec1e4b99f0b1cf19f6c'
ROOT=Path('sessions/S010')
rows=[]
for ep in ('git/ref/heads/main','git/commits/'+ENTRY,'git/commits/'+AUTHOR,
           'pulls/9','pulls/9/commits','pulls?state=all&per_page=100',
           'branches?per_page=100','actions/workflows','actions/runs?per_page=20',
           'actions/runs/38600425084/jobs','actions/runs/38600592078/jobs',
           'commits/'+AUTHOR+'/check-runs','commits/'+ENTRY+'/check-runs',
           'commits/'+AUTHOR+'/status','commits/'+ENTRY+'/status',
           'branches/main/protection','rulesets'):
    cmd=['gh','api','repos/jfairfaxball-348/Earth-Moon-problem/'+ep]
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    rows.append(dict(command=cmd,returncode=r.returncode,result=json.loads(r.stdout),stderr=r.stderr))
assert rows[0]['result']['object']['sha']==ENTRY
assert [x['sha'] for x in rows[1]['result']['parents']]==['7957452c79c2b31088f93fff440783328c78942d',AUTHOR]
assert rows[1]['result']['tree']['sha']==rows[2]['result']['tree']['sha']
assert [x['sha'] for x in rows[4]['result']]==[AUTHOR]
assert not [x for x in rows[5]['result'] if x['state']=='open']
for i in (9,10):
    assert all(j['conclusion']=='success' and all(s['conclusion']=='success' for s in j['steps']) for j in rows[i]['result']['jobs'])
manifest=json.loads(Path('validation/S009_MANIFEST.json').read_text())
checked=[]
for name,rec in manifest['artifact_sha256'].items():
    raw=subprocess.check_output(['git','show',ENTRY+':'+name])
    assert hashlib.sha256(raw).hexdigest()==rec['sha256'] and len(raw)==rec['bytes'],name
    assert Path(name).read_bytes()==raw,name
    checked.append(name)
for stem in ('SOURCES','CLAIMS'):
    data=json.loads(Path('catalogue',stem+'.json').read_text(encoding='utf-8'))
    md=Path('catalogue',stem+'.md').read_text(encoding='utf-8')
    for item in data:
        assert item['id'] in md and (item.get('access') or item['status']) in md
Path('validation/S010').mkdir(exist_ok=True)
ROOT.joinpath('ENTRY_EVIDENCE.json').write_text(json.dumps(dict(as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    commands=rows,incoming_manifest_artifacts_checked=len(checked),paired_catalogue_ids_grades_checked=True,
    entry_main=ENTRY,entry_tree=rows[1]['result']['tree']['sha']),indent=1)+'\n',encoding='utf-8',newline='\n')
print('PASS live main/parents/PR/jobs and',len(checked),'incoming artifact Git blobs/working bytes')
