"""Isolated alternative full search adapters with observed launch provenance."""
import inspect
import json
import sys
from pathlib import Path
import s008_run
from s005_search import run_logged
from s005_replay import sha
from s007_run import save

ROOT=Path('validation/S008/tree');TMP=Path('artifacts/tmp/S008/tree')
ROOT.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
assert Path('validation/S008/BASELINE_PASS.json').exists()
assert json.loads(Path('validation/S008/supervised_controls_command.json').read_text())['returncode']==0
files=['tools/s008_tree_run.py','tools/s008_tree.py','tools/s008_tree_controls.py','tools/s008_run.py',
       'tools/s008_cover.py','tools/s007_cover.py','tools/triangulation_cover.py','tools/s006_run.py','tools/s005_search.py']
save(ROOT/'launch_hashes.json',{p:sha(p) for p in files})
control=run_logged([sys.executable,'tools/s008_tree_controls.py'],920,ROOT/'controls.log')
save(ROOT/'controls_command.json',control)
assert control['returncode']==0
targets={r['index']:r for r in json.loads(Path('validation/S008/targets.json').read_text())}
save(ROOT/'targets.json',[targets[i] for i in (157,159,162,155)])
save(ROOT/'BASELINE_PASS.json',dict(parent='validation/S008/BASELINE_PASS.json',tree_controls=23))
# Reuse the proof/stop pipeline, with a distinct tree generator and paths.
scope=dict(s008_run.__dict__);scope.update(ROOT=ROOT,TMP=TMP)
cert=inspect.getsource(s008_run.certificate).replace('tools/s008_cover.py','tools/s008_tree.py')
cert=cert.replace('from s008_cover import FullCover','from s008_tree import TreeFullCover as FullCover')
search=inspect.getsource(s008_run.search).replace('tools/s008_cover.py','tools/s008_tree.py')
search=search.replace("'1200','--lex'", "'900','--lex'").replace("],1220,str(prefix)+'.run.log'", "],920,str(prefix)+'.run.log'")
# Only the parent's27 direct truth controls are applicable here; path explicitly recorded.
search=search.replace("(ROOT/'new_clause_controls.json')", "Path('validation/S008/new_clause_controls.json')")
for name,source in (('certificate',cert),('search',search)):
    p=TMP/(name+'_adapter.py.txt');p.write_text(source,newline='\n')
    save(ROOT/(name+'_adapter_launch.json'),dict(path=str(p),sha256=sha(p)))
    exec(source,scope)
scope['search']()
