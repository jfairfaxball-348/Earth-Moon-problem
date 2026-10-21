"""Freeze S032 launch/provenance, not a numbered-session closeout."""
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'artifacts/tmp/S032'
DEST=ROOT/'validation/S032/start'


def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    c=json.loads((RUN/'campaign/CONTROLLER.json').read_text())
    assert c['status']=='SEARCH_RUNNING'
    assert not DEST.exists(),'Do not replace historical launch records'
    DEST.mkdir(parents=True)
    for name in ['SMOKE.json','GATE.json','ENVIRONMENT.json','CONTROLS.json','NATIVE_CONTROLS.json',
                 'DIAGNOSTIC_AUDIT.json','ENTRY_VERIFICATION.json','INPUTS.json','S030_REPLAY.json','INFINITE_TIMEOUT_CONTROL.json']:
        shutil.copy2(RUN/name,DEST/name)
    for name in ['CONTROLLER.json','WORKER.json','PROGRESS.json','CHECKPOINT.json']:
        shutil.copy2(RUN/'campaign'/name,DEST/('INITIAL_'+name))
    for name in ['BUILD.json','build.log']:
        shutil.copy2(RUN/'native'/name,DEST/name)
    prior=DEST/'prior-art';prior.mkdir()
    for name in ['FETCH_RECEIPTS.json','ARTICLE_COMPARISON.json']:
        shutil.copy2(RUN/'prior-art'/name,prior/name)
    # Exact necessary formula and instance; deterministic lossless compression.
    for name in ['original.cnf','base.cnf','S11.inst']:
        (DEST/(name+'.gz')).write_bytes(gzip.compress((RUN/name).read_bytes(),mtime=0))
    with tarfile.open(DEST/'diagnostics.tar.gz','w:gz') as tf:
        for dirname in ['controls','controls-v2','controls-v3','controls-v4','diagnostic']:
            for p in sorted((RUN/dirname).rglob('*')):
                if p.is_file():tf.add(p,arcname=p.relative_to(RUN).as_posix())
    # Preserve compiler inputs, licences, upstream source and native executable.
    vendor=RUN/'bipsat2';cad=ROOT/'artifacts/tmp/S004/cadical'
    compiler=ROOT/'artifacts/tmp/S004/compiler/llvm-mingw-20261006-ucrt-x86_64'
    files=[*sorted((cad/'src').rglob('*')),*sorted((vendor/'src').rglob('*')),
           *sorted((vendor/'third_party/edge-addition-planarity-suite/c/graphLib').rglob('*')),
           *sorted((vendor/'docs').glob('*')),*sorted((ROOT/'artifacts/tmp/S004/wincompat').rglob('*')),
           *sorted((RUN/'source-bytes').glob('*')),
           cad/'LICENSE',vendor/'LICENSE',vendor/'NOTICE.md',vendor/'README.md',
           vendor/'third_party/edge-addition-planarity-suite/LICENSE.TXT',
           RUN/'native/bipsat_s032.cpp',RUN/'native/bipsat_s032.exe',
           ROOT/'tools/s032_subdivision.hpp',compiler/'bin/libc++.dll',compiler/'bin/libunwind.dll']
    files += [p for p in compiler.iterdir() if p.is_file() and any(x in p.name.lower() for x in ['license','copying','readme'])]
    with tarfile.open(DEST/'native-source-runtime.tar.gz','w:gz') as tf:
        for p in sorted(set(files)):
            if p.is_file():tf.add(p,arcname=p.relative_to(ROOT).as_posix())
    (DEST/'THIRD_PARTY_NOTICES.md').write_text('''# S032 execution dependencies

SRC-0055 bipsat2, Sean Cook / Color the Colonies AI lanes, MIT, pinned
ab6e472b7ef4ab7dca1d12c8907b3c74399d3828. Modified optional-edge driver,
independent subdivision guard and build transformation are included.
CaDiCaL3.0.1 (Armin Biere et al., MIT) is the pinned S004 source.
Edge Addition Planarity Suite4.0.1, John M. Boyer, pinned upstream
c10f90f2d79fdb07a797a625a89ef70e23a1eb2c; original licence included.
LLVM-Mingw20261006-ucrt-x86_64 compiler/runtime paths/hashes in BUILD.json;
runtime DLLs and distributed licence notices included in source/runtime archive.
Original files and licences are retained under their repository-relative paths
inside native-source-runtime.tar.gz. This is execution provenance, no novelty
or mathematical-certification claim. Full source-stated boundaries unchanged.
''',encoding='utf-8',newline='\n')
    state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    assert state['last_completed_session']=='S031'
    state['active_session'].update(status='IN_PROGRESS_LONG_RUN',controller_pid=c['pid'],
        worker_pid=c['worker_pid'],started_utc=c['started_utc'],runtime_directory='artifacts/tmp/S032/campaign',
        running_handoff='sessions/S032/RUNNING.md',followup_automation_id='earth-moon-s032-monitor',
        worker_cap_seconds=None,no_fixed_wall_limit=True,duration_authority='D069',scientific_status='S11_UNKNOWN_NO_CERTIFIED_STRATUM_OR_WITNESS')
    state['standing_continuation_authorization']={'decision':'D069','invocation_decision':'D068','authorized_session':'S032',
        'successive_sessions_authorized':False,'status':'ACTIVE_S032_ONLY',
        'stop_conditions':['S032 closeout','owner stop','context or usage exhausted'],
        'preserve_session_scopes_and_publication_gates':True}
    dump(ROOT/'authoritative/STATE.json',state)
    manifest={'scope':'S032 running launch snapshot, not session closeout','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'artifact_sha256':{p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                           for p in sorted(DEST.rglob('*')) if p.is_file()}}
    dump(ROOT/'sessions/S032/START_MANIFEST.json',manifest)
    print('Recorded S032 IN_PROGRESS; S031 remains last completed; no final authored S032 commit')


if __name__=='__main__':main()
