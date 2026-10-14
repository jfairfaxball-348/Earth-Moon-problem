"""Final scoped certificate, paired-record and governance checks."""
import json
import re
import sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save

root=Path('validation/S008')
save(root/'final_checks_launch_hashes.json',{p:sha(p) for p in (
    'tools/s008_checks.py','tools/check_s008_archives.py','tools/s008_cover.py','tools/s008_tree.py',
    'scripts/check_scaffold.py','tools/s005_search.py')})
commands=[([sys.executable,'scripts/check_scaffold.py'],120,'governance.log'),
          ([sys.executable,'-m','unittest','discover','-s','tests','-v'],120,'unit.log')]
rows=json.loads((root/'package_checks.json').read_text())
assert {r['lane'] for r in rows}=={'sequential','tree','heavy'} and all(r['returncode']==0 for r in rows)
for r in rows:
    for p,digest in json.loads(Path(r['launch_hashes']).read_text()).items():assert sha(p)==digest,p
# Packaging/necessity code is unchanged since the successful cold audits; do not repeat them.
save(root/'checks.json',rows)
for cmd,cap,name in commands:
    row=run_logged(cmd,cap,root/name);rows.append(row)
    save(root/'checks.json',rows)
    assert row['returncode']==0,root/name
    print('PASS',name,flush=True)
for name,prefix in [('SOURCES','SRC'),('CLAIMS','CLM')]:
    data=json.loads(Path('catalogue',name+'.json').read_text(encoding='utf-8'))
    md=Path('catalogue',name+'.md').read_text(encoding='utf-8')
    ids=re.findall(r'^## ('+prefix+r'-\d{4}) ',md,re.M)
    assert ids==[x['id'] for x in data]
from blowup_graph import blowup
transfers=json.loads((root/'transfer_search.json').read_text())
assert len(transfers['attempts'])==271
source=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
es,_=blowup(*source[157][:2])
for rec in transfers['attempts']:
    if rec['verdict']=='INJECTIVE_CONTAINMENT_CHECKED':
        target,_=blowup(*source[rec['index']][:2]);target=set(target)
        injection={int(k):v for k,v in rec['vertex_map'].items()}
        assert len(set(injection.values()))==len(injection)==sum(source[157][1])
        assert all(tuple(sorted((injection[a],injection[b]))) in target for a,b in es)
summary=json.loads((root/'SUMMARY.json').read_text())
sequential_summary=root/'sequential_SUMMARY.json'
lane=set(json.loads(sequential_summary.read_text())['S008_new_exclusions'])
lane|=set(json.loads((root/'tree/SUMMARY.json').read_text())['S008_new_exclusions'])
transfer_rows=json.loads((root/'transfers.json').read_text())
for r in transfer_rows:
    if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED':
        assert r['index'] in transfers['mapped'] and r['chromatic_check']['returncode']==0
        assert 's VERIFIED' in (root/f"transfer-chi-row{r['index']}.check.log").read_text()
        lane.add(r['index'])
last=json.loads((root/'last_transfers.json').read_text())
assert json.loads((root/'last_transfer_command.json').read_text())['returncode']==0
for r in last:
    if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED':
        original,_=blowup(*source[r['source']][:2]);target,_=blowup(*source[r['target']][:2]);target=set(target)
        injection={int(k):v for k,v in r['vertex_map'].items()}
        assert len(set(injection.values()))==len(injection)==sum(source[r['source']][1])
        image={tuple(sorted((injection[a],injection[b]))) for a,b in original}
        assert image<=target
        if r['source']==159 and r['target']==155:assert len(injection)==24 and image==target and len(target)==130
        assert r['source_certificate']['cold_retained_check']['returncode']==0
        assert r['target_chromatic_check']['returncode']==0
        lane.add(r['target'])
assert summary['S008_new_exclusions']==sorted(lane)
prior=json.loads(Path('validation/S007/SUMMARY.json').read_text())
assert summary['excluded_indices']==sorted(set(prior['excluded_indices'])|lane)
assert summary['remaining_unknown_indices']==sorted(set(range(271))-set(summary['excluded_indices']))
print('PASS paired source/claim identifiers (mathematics requires the separate certificates)')
