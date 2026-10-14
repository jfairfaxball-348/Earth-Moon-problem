#!/usr/bin/env python3
"""Read-only remote API/git capture; outgoing evidence is ignored scratch."""
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO='repos/jfairfaxball-348/Earth-Moon-problem'


def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    row=dict(command=cmd,returncode=p.returncode)
    try:
        row['result']=json.loads(p.stdout)
    except ValueError:
        row['stdout']=p.stdout
    if p.stderr:
        row['stderr']=p.stderr
    return row


def main():
    mode=sys.argv[1]
    out=Path('sessions/S006/ENTRY_EVIDENCE.json' if mode=='entry' else 'artifacts/tmp/S006/LIVE_EXIT_EVIDENCE.json')
    capture={'as_of_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':mode,'commands':[]}
    def api(path):
        r=run(['gh','api',REPO+'/'+path]);capture['commands'].append(r);return r.get('result')
    capture['commands'].append(run(['git','ls-remote','origin','refs/heads/main']))
    branch=api('branches/main');sha=branch['commit']['sha']
    commit=api('git/commits/'+sha)
    capture.update(main=sha,tree=commit['tree']['sha'],parents=[p['sha'] for p in commit['parents']])
    pr_number=5 if mode=='entry' else int(sys.argv[2])
    pr=api('pulls/'+str(pr_number));head=pr['head']['sha']
    authored=api('git/commits/'+head)
    assert pr['merged'] and not pr['draft'] and pr['merge_commit_sha']==sha
    assert capture['parents']==[authored['parents'][0]['sha'],head]
    assert len(authored['parents'])==1 and authored['tree']['sha']==capture['tree']
    capture.update(pr=pr_number,authored_commit=head,sole_parent=authored['parents'][0]['sha'])
    api('pulls?state=all&per_page=30');api('branches?per_page=100');api('actions/workflows')
    api('rulesets');api('branches/main/protection')
    for ref in (head,sha):
        api('commits/'+ref+'/check-runs');api('commits/'+ref+'/status')
        runs=api('actions/runs?head_sha='+ref+'&per_page=10')
        for r in runs['workflow_runs']:
            api('actions/runs/'+str(r['id'])+'/jobs')
    capture['commands'].append(run(['git','show','-s','--format=%H %T %P',sha,head]))
    capture['commands'].append(run(['git','status','--porcelain']))
    out.write_text(json.dumps(capture,indent=1)+'\n',newline='\n')
    print(json.dumps({k:capture[k] for k in ('mode','main','tree','parents','pr','authored_commit','sole_parent')}))


if __name__=='__main__':
    main()
