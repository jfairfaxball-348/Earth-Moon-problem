"""Read/verify cross-lane certificates before stopping only redundant graph solves."""
import json
import re
import subprocess
from pathlib import Path
from s005_replay import sha
from s007_run import save

root=Path('validation/S008')
save(root/'redundant_stop_launcher_hash.json',dict(path='tools/s008_stop_redundant.py',sha256=sha('tools/s008_stop_redundant.py')))
cmd=['powershell.exe','-NoProfile','-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 's008_(run|cover|tree_run|tree)\\.py' } | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Depth 3"]
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');assert r.returncode==0
processes=json.loads(r.stdout or '[]')
if isinstance(processes,dict):processes=[processes]
parents={}
for p in processes:
    line=p['CommandLine'].replace('\\','/')
    if re.search(r'tools/s008_run\.py search(?:\s|$)',line):parents[p['ProcessId']]='sequential'
    if re.search(r'tools/s008_tree_run\.py(?:\s|$)',line):parents[p['ProcessId']]='tree'
events=json.loads((root/'redundant_stops.json').read_text()) if (root/'redundant_stops.json').exists() else []
for p in processes:
    if p['ParentProcessId'] not in parents:continue
    lane=parents[p['ParentProcessId']];line=p['CommandLine'].replace('\\','/')
    expected='s008_cover' if lane=='sequential' else 's008_tree'
    if not re.search(r'tools/'+expected+r'\.py ',line) or ' check ' in line:continue
    match=re.search(r'targets/row(\d+)\.edges',line)
    if not match:continue
    idx=int(match.group(1));other='tree' if lane=='sequential' else 'sequential'
    folder=root/'tree' if other=='tree' else root
    result=folder/'search_results.json'
    if not result.exists():continue
    candidates=json.loads(result.read_text())
    known=next((x for x in candidates if x['target']['index']==idx and x['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'),None)
    if not known:continue
    cert=known['certificate'];ef=root/'targets'/f'row{idx}.edges'
    assert known['target']['edge_sha256']==sha(ef)
    assert sha(cert['archive'])==cert['archive_sha256']
    assert cert['check']['returncode']==cert['cold_retained_check']['returncode']==0
    assert 's VERIFIED' in Path(str(folder/'search'/f'cover-row{idx}')+'.check.log').read_text()
    assert 's VERIFIED' in Path(str(folder/'search'/f'cover-row{idx}')+'.cold.check.log').read_text()
    work=Path('artifacts/tmp/S008')/('tree' if lane=='tree' else '')/'search'/f'cover-row{idx}'
    meta=Path(str(work)+'.result.json');log=Path(str(work)+'.run.log')
    if not meta.exists() or not log.exists() or not log.read_text().strip():continue
    if json.loads(meta.read_text())['verdict'] not in ('INITIALISED','RUNNING'):continue
    assert Path(str(work)+'.initial.cnf').exists()
    kill=['taskkill.exe','/PID',str(int(p['ProcessId'])),'/T','/F']
    action=subprocess.run(kill,capture_output=True,text=True,timeout=15)
    events.append(dict(lane=lane,index=idx,pid=p['ProcessId'],parent=p['ParentProcessId'],
        observed_command=p['CommandLine'],stop_command=kill,returncode=action.returncode,stdout=action.stdout,stderr=action.stderr,
        reason='Redundant solve stopped after exact other-lane native/cold certificate; interrupted lane remains UNKNOWN',
        checked_other_lane=other,checked_archive=cert['archive'],edge_sha256=sha(ef)))
    print('Stopped redundant',lane,idx,'returncode',action.returncode)
save(root/'redundant_stops.json',events)
if not events:print('No eligible redundant solve')
