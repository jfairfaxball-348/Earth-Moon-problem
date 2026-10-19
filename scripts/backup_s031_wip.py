"""Never-merged WIP snapshot without changing the actual session branch/index."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/tmp/S031'
REF='refs/heads/wip/S031-long-run'


def main():
    state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    assert state['active_session']['id']=='S031' and state['last_completed_session']=='S030'
    temp_index=OUT/f'backup-{os.getpid()}.index'
    assert temp_index.parent.resolve()==OUT.resolve()
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(temp_index)
    def git(args,**kw):
        return subprocess.check_output(['git',*args],cwd=ROOT,env=env,**kw).decode().strip()
    try:
        entry=git(['rev-parse','HEAD'])
        assert entry=='dd802686215781cbc35aa86ea14c54369aaec7e5'
        git(['read-tree','HEAD'])
        paths=['.gitattributes','AGENTS.md','authoritative/STATE.json','campaigns/CAM-0037.md',
               'campaigns/README.md','docs/D065_LONG_RUN_AUTHORIZATION.md','docs/DECISION_LOG.md',
               'docs/SESSION_LEDGER.md','sessions/S031','validation/S031']
        paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*s031*.py')]
        paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'tools').glob('s031_*.py')]
        git(['add','--',*paths])
        tree=git(['write-tree'])
        previous=subprocess.run(['git','rev-parse','--verify',REF],cwd=ROOT,capture_output=True,text=True)
        parent=previous.stdout.strip() if previous.returncode==0 else entry
        commit=git(['commit-tree',tree,'-p',parent],input=b'WIP S031 running long campaign; backup only, never merge\n')
        git(['update-ref',REF,commit,parent if previous.returncode==0 else '0'*40])
        git(['-c','credential.helper=','-c','credential.helper=manager','-c','credential.username=jfairfaxball-348',
             'push','origin',f'{commit}:{REF}'])
        remote=git(['ls-remote','origin',REF]).split()[0];assert remote==commit
        assert git(['rev-parse','HEAD'])==entry
        receipt={'commit':commit,'tree':tree,'ref':REF,'never_merge':True,'session_head_unchanged':entry,
                 'utc':datetime.now(timezone.utc).isoformat()}
        (OUT/'WIP_BACKUP.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(receipt))
    finally:
        temp_index.unlink(missing_ok=True)


if __name__=='__main__':main()
