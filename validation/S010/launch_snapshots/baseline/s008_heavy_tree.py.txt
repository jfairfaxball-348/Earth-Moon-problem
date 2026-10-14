"""CAM-0009C one exact local heavy-endblock graph, new tree full encoding."""
import inspect
import itertools
import json
import shutil
import sys
from pathlib import Path
import s008_run
from s005_search import run_logged,compress
from s005_replay import sha
from s007_run import save
from check_layers import main as check_split

ROOT=Path('validation/S008/heavy_tree');TMP=Path('artifacts/tmp/S008/heavy_tree')
ROOT.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
assert Path('validation/S008/BASELINE_PASS.json').exists()
assert json.loads(Path('validation/S008/tree/controls_command.json').read_text())['returncode']==0
assert json.loads(Path('validation/S008/supervised_controls_command.json').read_text())['returncode']==0
es=sorted(set(itertools.combinations(range(7),2))|{(a,b) for a in range(7) for b in range(7,12)})
ef=ROOT/'K7-I5.edges';ef.write_text(''.join(f'{a} {b}\n' for a,b in es),newline='\n')
save(ROOT/'launch_hashes.json',{p:sha(p) for p in (
    'tools/s008_heavy_tree.py','tools/s008_tree.py','tools/s008_cover.py','tools/s008_run.py','tools/s006_run.py',str(ef))})
prefix=TMP/'K7-I5'
run=run_logged([sys.executable,'tools/s008_tree.py',str(ef),str(prefix),'300','--lex'],320,str(prefix)+'.run.log')
row=dict(n=12,m=len(es),D=4,edgefile=str(ef),edge_sha256=sha(ef),run=run,verdict='UNKNOWN')
meta=Path(str(prefix)+'.result.json')
if meta.exists():row['search']=json.loads(meta.read_text())
if run['returncode']==0 and row.get('search',{}).get('verdict')=='UNSAT':
    scope=dict(s008_run.__dict__);scope['ROOT']=ROOT
    cert=inspect.getsource(s008_run.certificate).replace('tools/s008_cover.py','tools/s008_tree.py')
    cert=cert.replace('from s008_cover import FullCover','from s008_tree import TreeFullCover as FullCover')
    (ROOT/'search').mkdir(exist_ok=True)
    adapter=TMP/'certificate_adapter.py.txt';adapter.write_text(cert,newline='\n')
    save(ROOT/'certificate_adapter_launch.json',dict(path=str(adapter),sha256=sha(adapter)))
    exec(cert,scope);row['certificate']=scope['certificate'](str(ef),prefix)
    row['verdict']=row['certificate']['verdict']
elif run['returncode']==0 and row.get('search',{}).get('verdict')=='SAT_CHECKED':
    check_split(str(ef),str(prefix)+'.split.json')
    split=json.loads(Path(str(prefix)+'.split.json').read_text())
    upper=list(range(7))+[7]*5
    assert all(upper[a]!=upper[b] for a,b in es)
    assert set(itertools.combinations(range(8),2))<=set(es)
    row.update(verdict='BIPLANAR_CHECKED_CHI8',split=split,proper_colouring=upper,clique_lower=list(range(8)))
    shutil.copyfile(str(prefix)+'.split.json',ROOT/'split.json')
for suffix in ('.cuts.json','.result.json','.run.log'):
    p=Path(str(prefix)+suffix)
    if p.exists():shutil.copyfile(p,ROOT/(prefix.name+suffix))
save(ROOT/'result.json',row)
print('Heavy K7-I5 tree',row['verdict'],flush=True)
