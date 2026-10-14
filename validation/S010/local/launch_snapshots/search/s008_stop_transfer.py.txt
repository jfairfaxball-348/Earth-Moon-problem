"""Verify exact graph isomorphism/proof chain before stopping redundant row155 solve."""
import datetime
import json
import re
import subprocess
from pathlib import Path
from blowup_graph import blowup
from s005_replay import sha
from s007_run import save

root=Path('validation/S008')
records=json.loads((root/'last_transfers.json').read_text())
r=next(x for x in records if x['source']==159 and x['target']==155)
assert r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'
corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
source,_=blowup(*corpus[159][:2]);target,_=blowup(*corpus[155][:2])
mapping={int(k):v for k,v in r['vertex_map'].items()}
assert set(mapping)==set(range(24)) and set(mapping.values())==set(range(24))
assert {tuple(sorted((mapping[a],mapping[b]))) for a,b in source}==set(target)
assert len(source)==len(target)==130
source_cert=r['source_certificate']
assert source_cert['check']['returncode']==source_cert['core_check']['returncode']==source_cert['cold_retained_check']['returncode']==0
assert sha(source_cert['archive'])==source_cert['archive_sha256']
for suffix in ('.check.log','.core.check.log','.cold.check.log'):
    assert 's VERIFIED' in (root/'tree/search'/('cover-row159'+suffix)).read_text()
ef=root/'targets/row155.edges';assert sha(ef)==r['target_edge_sha256']
assert r['target_chromatic_check']['returncode']==0 and 's VERIFIED' in (root/'chi-row155.check.log').read_text()
cmd=['powershell.exe','-NoProfile','-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 's008_tree(_run)?\\.py' } | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Depth 3"]
got=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');assert got.returncode==0
ps=json.loads(got.stdout or '[]');ps=[ps] if isinstance(ps,dict) else ps
parents={p['ProcessId'] for p in ps if re.search(r'tools/s008_tree_run\.py(?:\s|$)',p['CommandLine'].replace('\\','/'))}
children=[p for p in ps if p['ParentProcessId'] in parents and
    re.search(r'tools/s008_tree\.py .*targets/row155\.edges .*tree/search/cover-row155 ',p['CommandLine'].replace('\\','/'))]
assert len(children)<=1
event=dict(as_of_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=159,target=155,
    proof_basis='EXACT_LABELLED_ISOMORPHISM_TO_CHECKED_NON_BIPLANAR_SOURCE',mapping=mapping,
    source_archive=source_cert['archive'],source_archive_sha256=source_cert['archive_sha256'],
    target_edge_sha256=sha(ef),interrupted_lane_verdict='UNKNOWN')
if children:
    p=children[0];prefix=Path('artifacts/tmp/S008/tree/search/cover-row155')
    state=json.loads(Path(str(prefix)+'.result.json').read_text())
    assert state['verdict'] in ('INITIALISED','RUNNING')
    assert Path(str(prefix)+'.initial.cnf').exists() and Path(str(prefix)+'.run.log').read_text().strip()
    kill=['taskkill.exe','/PID',str(int(p['ProcessId'])),'/T','/F']
    action=subprocess.run(kill,capture_output=True,text=True,timeout=15)
    event.update(pid=p['ProcessId'],parent=p['ParentProcessId'],observed_command=p['CommandLine'],
        stop_command=kill,returncode=action.returncode,stdout=action.stdout,stderr=action.stderr)
    assert action.returncode==0
    print('Stopped redundant tree row155 after checked exact isomorphism')
else:
    event['action']='No active row155 graph-solve child; no process cancelled'
    print(event['action'])
save(root/'transfer_stop.json',event)
