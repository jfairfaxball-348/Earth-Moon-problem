"""Quiet GitHub Actions watcher. Polling loop makes NO model/API-to-OpenAI calls.

Returns on a newly completed job, completed run, changed failure state, or its
wall cap. Run it independently of the chat to keep routine polling out of LLM
turns. GitHub API access is read-only; no scientific computation is performed.
"""
import argparse
import json
import subprocess
import time

p=argparse.ArgumentParser()
p.add_argument('--run',default='39142133864')
p.add_argument('--interval',type=float,default=300)
p.add_argument('--max-wait',type=float,default=7200)
a=p.parse_args()


def snapshot():
    run=subprocess.run(['gh','run','view',a.run,'--repo','jfairfaxball-348/Earth-Moon-problem',
                        '--json','status,conclusion,jobs,url'],capture_output=True,text=True,timeout=45)
    if run.returncode:
        return {'error':'GITHUB_STATUS_UNAVAILABLE','detail':run.stderr[-300:]}
    r=json.loads(run.stdout)
    return {'status':r['status'],'conclusion':r['conclusion'],'url':r['url'],
            'jobs':[{'name':j['name'],'status':j['status'],'conclusion':j['conclusion']}
                    for j in r['jobs']]}


start=time.monotonic()
first=snapshot()
if 'error' in first or first.get('status')=='completed':
    print(json.dumps(first)); raise SystemExit(0)
completed={j['name'] for j in first['jobs'] if j['status']=='completed'}
while time.monotonic()-start<a.max_wait:
    time.sleep(min(a.interval,max(0,a.max_wait-(time.monotonic()-start))))
    now=snapshot()
    if 'error' in now:
        print(json.dumps(now)); break
    ended={j['name'] for j in now['jobs'] if j['status']=='completed'}
    if now['status']=='completed' or ended-completed:
        print(json.dumps(now)); break
else:
    print(json.dumps({'status':'WATCH_CAP_REACHED','run':a.run,'seconds':a.max_wait}))
