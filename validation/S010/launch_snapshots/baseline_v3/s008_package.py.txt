"""Supervised cold packaging audits, each once after its worker has finished."""
import json
import sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save

root=Path('validation/S008')
specs={'sequential':('tools/check_s008_archives.py',[],'archives.log'),
       'tree':('tools/check_s008_archives.py',['--tree'],'tree_archives.log'),
       'heavy':('tools/check_s008_heavy.py',[],'heavy_archives.log')}
key=sys.argv[1];script,args,log=specs[key]
files=['tools/s008_package.py',script,'tools/s008_cover.py','tools/s008_tree.py','tools/s007_cover.py',
       'tools/triangulation_cover.py','tools/s005_search.py']
record=root/(key+'_package_launch_hashes.json');save(record,{p:sha(p) for p in files})
run=run_logged([sys.executable,script]+args,1220,root/log)
run['lane']=key;run['launch_hashes']=str(record)
rows=json.loads((root/'package_checks.json').read_text()) if (root/'package_checks.json').exists() else []
assert key not in {x['lane'] for x in rows},'Duplicate packaging audit needs an explicitly justified rerun'
rows.append(run);save(root/'package_checks.json',rows)
assert run['returncode']==0,root/log
print('PASS supervised cold package',key)
