"""Supervised repeat of registered finite upper controls with initial evidence retained."""
import shutil
import sys
from pathlib import Path
from s005_search import run_logged
from s005_replay import sha
from s007_run import save

root=Path('validation/S008')
for name in ('upper_controls.json','upper_launch_hashes.json'):
    shutil.copyfile(root/name,root/('initial_'+name))
save(root/'upper_repeat_launch_hashes.json',{p:sha(p) for p in (
    'tools/s008_upper_repeat.py','tools/s008_upper.py','tools/s005_search.py')})
run=run_logged([sys.executable,'tools/s008_upper.py'],200,root/'supervised_upper.log')
save(root/'supervised_upper_command.json',run)
assert run['returncode']==0
assert (root/'upper_controls.json').read_bytes()==(root/'initial_upper_controls.json').read_bytes()
print('PASS supervised5/512 upper controls, bytes equal initial finite result')
