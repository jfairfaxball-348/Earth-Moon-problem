"""Freeze S034 entry/gates and record an active campaign, never a closeout."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s034_regions import report, sha

OUT = ROOT/'validation/S034'
OUT.mkdir(exist_ok=True)
runtime = ROOT/'artifacts/tmp/S034'
area = runtime/'campaign'
live = report(area)
assert live['status'] == 'RUNNING' and live['controller_process_alive']
config = json.loads((area/'CONFIG.json').read_text())
assert config['workers'] == 1 and config['deadline'] == 1792648800
entry_main = '236d97e8c142b8fdf8d124f02f9c1b754693002f'
assert subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0] == entry_main
for name in ('SMOKE.json', 'ENVIRONMENT.json', 'INPUT_AUDIT.json', 'NATIVE_CONTROLS.json', 'SCHEDULER_CONTROLS.json'):
    shutil.copy2(runtime/name, OUT/name)
shutil.copy2(runtime/'native/BUILD.json', OUT/'BUILD.json')
shutil.copy2(area/'CONFIG.json', OUT/'REGISTERED_CONFIG.json')
(OUT/'LAUNCH_SNAPSHOT.json').write_text(json.dumps(live, indent=2)+'\n')
(OUT/'ENTRY.json').write_text(json.dumps(dict(session='S034', entry_main=entry_main,
    entry_tree='f8ae881e2a9a0f6edbfc4412e5d89ac371ac1b49',
    entry_check_utc='2026-10-21T20:09:08.375111+00:00',
    deadline_utc='2026-10-22T06:00:00Z', deadline_uk='2026-10-22T07:00:00+01:00',
    absolute_deadline_epoch=1792648800, status='RUNNING_NOT_CLOSED',
    publication='D072 existing main/non-force; authenticated owner GitHub connection',
    scientific_verdict='UNKNOWN', range=dict(lower=9, upper=12)), indent=2)+'\n')
with tarfile.open(OUT/'native.tar.gz', 'w:gz') as archive:
    for name in ('bipsat_s034', 'bipsat_s032.cpp', 'BUILD.json', 'build.log'):
        archive.add(runtime/'native'/name, arcname='native/'+name)
    for name in ('LICENSE', 'NOTICE.md'):
        archive.add(ROOT/'artifacts/tmp/S033/bipsat2'/name, arcname='bipsat2/'+name)
    archive.add(ROOT/'validation/S032/start/THIRD_PARTY_NOTICES.md', arcname='THIRD_PARTY_NOTICES.md')
controls = json.loads((runtime/'SCHEDULER_CONTROLS.json').read_text())
with tarfile.open(OUT/'controls.tar.gz', 'w:gz') as archive:
    archive.add(Path(controls['controls_directory']), arcname='scheduler-controls')
    archive.add(runtime/'controls-v2', arcname='native-controls')
names = sorted(set([*ROOT.glob('tools/s034*.py'), *ROOT.glob('scripts/*s034*.py'),
                    *(ROOT/name for name in config['source_sha256']),
                    ROOT/'scripts/build_s033_native.py', ROOT/'scripts/build_s032_native.py']))
with tarfile.open(OUT/'source-bytes.tar.gz', 'w:gz') as archive:
    for name in names:
        archive.add(name, arcname=str(name.relative_to(ROOT)))
session = ROOT/'sessions/S034'
shutil.copy2(ROOT/'authoritative/NEXT_SESSION_PROMPT.md', session/'EXECUTED_PROMPT.md')
running = '''# S034 RUNNING — owner-authorised overnight campaign

This is not a closeout. Last completed session remains S033. Owner explicitly
invoked S034 and authorised continuing through UNKNOWNs and milestones until
22 October2026 at07:00 UK/06:00 UTC. No S035 authorization.

Real guarded native cell0 started2026-10-21T20:52:22.847406Z, after fresh full
271/271 CNF/native DRAT plus retained/fresh K9,1024n5/K33/positive24, all2579937
rules and exact mapping, and live scheduler/proof/deadline/crash controls passed.
An actual killed controller resumed a new worker using independently audited
nonempty cuts. Small two-worker controls do not justify two full phone workers.

Live authority:artifacts/tmp/S034/campaign/GUARDIAN.json,CONTROLLER.json,
REGIONS.json,JOURNAL.jsonl and per-attempt checkpoints. Static launch PIDs are
only historical; inspect PID/start ticks before any restart. Never duplicate a
live guardian/controller/worker. Read docs/S034_OVERNIGHT_GUIDE.md. The guard
enforces the absolute deadline and a monotonic backstop, recovers identified
orphans and resumes recoverable crashes. Repeated crashes or actual safety
conditions stop safely. Android can kill the entire environment.

One worker;1GiB aggregate RSS,4GiB disk reserve,384MiB MemAvailable floor;
no readable thermal/PSI sensors. RSS-budget caps checkpoint/requeue individual
visits; sustained low memory stops the campaign. UNKNOWN and SAT candidates
remain unresolved. Exact region closure needs standalone CaDiCaL DRAT and
independent drat-trim. Whole-stratum promotion needs separate domain audit.

Status: .venv/bin/python scripts/s034_campaign.py status
STOP: .venv/bin/python scripts/s034_campaign.py stop

Keep working until the owner deadline or an actual stop/safety condition; do
not end because this running handoff or a commit has been achieved. At deadline,
checkpoint/stop then archive and close S034, write identical complete S035 future
prompts, print the full prompt and verify ordinary non-force main publication.
No later session runs automatically. Classical9<=chi2<=12; S11 UNKNOWN,
regular154 SOURCE_STATED, S10/S9/S8 NOT_RUN. Preserve all immutable archives.
'''
(session/'RUNNING.md').write_text(running)
state_path = ROOT/'authoritative/STATE.json'
state = json.loads(state_path.read_text())
assert state['last_completed_session'] == 'S033'
state['next_session_is_future_unexecuted'] = False
state['active_session'] = dict(id='S034', status='RUNNING', authority='D073 owner overnight invocation',
    deadline_utc='2026-10-22T06:00:00Z', deadline_uk='2026-10-22T07:00:00+01:00',
    runtime_status_authority='artifacts/tmp/S034/campaign/GUARDIAN.json',
    runtime_directory='artifacts/tmp/S034/campaign', workers=1,
    entry_main=entry_main, running_handoff='sessions/S034/RUNNING.md',
    no_automatic_S035=True, whole_stratum_certified=False, witness_established=False)
state['next_session_priority'] = 'S034 RUNNING until2026-10-22T06:00:00Z; inspect actual processes, do not duplicate or stop at a milestone; no S035 invocation.'
state_path.write_text(json.dumps(state, indent=2)+'\n')
header = '''# S034 RUNNING — D073 overnight owner authority

Owner explicitly invoked S034 through22 October2026,07:00 UK/06:00 UTC.
One genuine worker initially; safeguards/checkpoints; continue UNKNOWN regions
and do not stop at a milestone. Inspect live guardian/PID/start ticks before
launching anything. Absolute deadline clean stop; no automatic S035. Last
completed S033; math9..12 unchanged. See sessions/S034/RUNNING.md and
docs/S034_OVERNIGHT_GUIDE.md. D072 same-main/no-PR workflow continues.

'''
for name in ('AGENTS.md', 'authoritative/START_HERE.md'):
    p = ROOT/name
    if not p.read_text().startswith('# S034 RUNNING'):
        p.write_text(header+p.read_text())
def append(name, text):
    p = ROOT/name
    if text not in p.read_text():
        p.write_text(p.read_text()+'\n'+text+'\n')
append('docs/SESSION_LEDGER.md', '| S034 | 2026-10-21/22 | D073 explicit overnight invocation; CAM0039 | Fresh full phone acceptance and scheduler controls PASS; genuine256-region campaign RUNNING until07:00 UK | IN_PROGRESS; no S035 invocation |')
append('docs/DECISION_LOG.md', '**D073 (owner,2026-10-21):** invoke S034 now, finish setup/verification/256-region scheduling then genuine computation continuously until22 October07:00 UK/06:00 UTC. One worker initially, more only after verified safety, continue through individual UNKNOWNs/milestones, checkpoints/resource safeguards, clean deadline stop. No further confirmation except actual safety issue/unavoidable blocker; no S035 authorization.')
append('docs/PHASE_GATE_LEDGER.md', 'S034 RUNNING (D073): phone verification/scheduler acceptance PASS; no stratum or lower-bound result. Phase1 gate NOT PASSED. Source/claim catalogues remain unchanged and synced.')
append('campaigns/README.md', '**CAM-0039 / S034 RUNNING:** owner-authorised overnight exact256-region S11 campaign until22 October07:00 UK; one phone worker with checkpoints/proof gates; no session closeout or S035 invocation yet.')
(OUT/'SETUP_FAILURES.md').write_text('''# Setup diagnostics — no mathematical claims

An initial deadline-source escaping error prevented compilation and was corrected.
The first scheduler controls were strengthened to require actual live restart and
deadline-stop behaviour. This caught a cut-journal logging keyword collision after
successful independent audit; corrected before scientific launch. Final controls
require a new native worker using nonempty recovered audited cuts and pass.

An already-started verifier had loaded the earlier S033 output path and temporarily
rewrote its prior audit JSON with a fresh successful audit. Original committed S033
bytes were restored exactly; the fresh S034 audit evidence was preserved. The S034
verifier now routes output separately. S033 archive integrity passes. No prior
certificate/native archive or mathematical verdict was changed.
''')
files = {}
with tarfile.open(OUT/'session-start.tar.gz', 'w:gz') as archive:
    for p in session.glob('*.md'):
        archive.add(p, arcname=str(p.relative_to(ROOT)))
for p in [*OUT.glob('*'), session/'EXECUTED_PROMPT.md']:
    if p.is_file():
        files[str(p.relative_to(ROOT))] = dict(bytes=p.stat().st_size, sha256=sha(p))
(session/'RUNNING_MANIFEST.json').write_text(json.dumps(dict(status='RUNNING_NOT_CLOSED', files=files), indent=2)+'\n')
print('Recorded S034 RUNNING; the campaign continues independently until its deadline')
