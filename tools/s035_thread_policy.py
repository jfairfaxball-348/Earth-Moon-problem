"""Explicit original-thread-only S035 resumption; OS helper threads stay frozen."""
from pathlib import Path
from s035_windows import read_json
from s035_preserved_lifecycle import LifecycleError, thread_state

def keys(rows):return {(r['tid'],r['created_ticks']) for r in rows}

def validate(record, policy, paused=False):
    row=policy['processes'].get(str(record['pid']))
    if row is None or row['start_ticks']!=record['start_ticks']:
        raise LifecycleError('Missing exact thread preservation policy')
    state=thread_state(record)
    if keys(state)!=keys(row['threads']):
        raise LifecycleError('Thread set changed; preserve RAM and require classification')
    frozen=keys(row['quarantined_threads'])
    if row['kind']=='LEGACY_NEVER_RESUME' or paused:frozen=keys(state)
    if any(r['suspend_count']<1 for r in state if (r['tid'],r['created_ticks']) in frozen):
        raise LifecycleError('Protected thread is not suspended')
    return state

def load(area):
    p=Path(area)/'RESUME_CONTROL/THREAD_POLICY.json';policy=read_json(p)
    if policy['status']!='CLASSIFIED_HELPERS_REMAIN_SUSPENDED':
        raise LifecycleError('Thread policy has not passed classification')
    return policy
