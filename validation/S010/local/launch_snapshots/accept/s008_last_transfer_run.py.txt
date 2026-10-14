"""Supervised launch of the prospectively registered two-source transfer test."""
import sys
from s005_search import run_logged
from s005_replay import sha
from s007_run import save

save('validation/S008/last_transfer_launch_hashes.json',{p:sha(p) for p in (
    'tools/s008_last_transfer_run.py','tools/s008_last_transfer.py','tools/blowup_graph.py',
    'validation/S003/survivors_alpha_ge3.json','tools/s005_search.py')})
run=run_logged([sys.executable,'tools/s008_last_transfer.py'],200,'validation/S008/last_transfer.log')
save('validation/S008/last_transfer_command.json',run)
assert run['returncode']==0
print('PASS supervised last-target transfer check')
