#!/usr/bin/env python3
"""CAM-0006 general injective subgraph transfer; only checked maps accepted."""
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153
from blowup_graph import blowup


def worker(idx):
    rows=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    ob=json.loads(Path('validation/S004/full_survivor_target.json').read_text())
    source,_=blowup(ob['g6'],ob['w'])
    g6,w,_=rows[idx]
    target,_=blowup(g6,w)
    sn,tn=sum(ob['w']),sum(w)
    sadj=[set() for _ in range(sn)]
    tadj=[set() for _ in range(tn)]
    for u,v in source:
        sadj[u].add(v);sadj[v].add(u)
    for u,v in target:
        tadj[u].add(v);tadj[v].add(u)
    pool=IDPool()
    domains={u:[v for v in range(tn) if len(tadj[v])>=len(sadj[u])] for u in range(sn)}
    x={(u,v):pool.id((u,v)) for u in range(sn) for v in domains[u]}
    cls=[]
    for u in range(sn):
        cls.extend(CardEnc.equals([x[u,v] for v in domains[u]],bound=1,
                   vpool=pool,encoding=EncType.seqcounter).clauses)
    for v in range(tn):
        cls.extend(CardEnc.atmost([x[u,v] for u in range(sn) if (u,v) in x],bound=1,
                   vpool=pool,encoding=EncType.seqcounter).clauses)
    for u,v in source:
        for a in domains[u]:
            for b in domains[v]:
                if b not in tadj[a]:
                    cls.append([-x[u,a],-x[v,b]])
    classes={}
    for u in range(sn):
        classes.setdefault(frozenset(sadj[u]|{u}),[]).append(u)
    for twins in classes.values():
        for u,v in zip(twins,twins[1:]):
            for a in domains[u]:
                for b in domains[v]:
                    if a>=b:
                        cls.append([-x[u,a],-x[v,b]])
    start=time.monotonic()
    with Cadical153(bootstrap_with=cls) as s:
        if not s.solve():
            return {'index':idx,'verdict':'NO_TRANSFER_FOUND_UNCERTIFIED',
                    'variables':pool.top,'clauses':len(cls),'solve_seconds':time.monotonic()-start}
        model={v for v in s.get_model() if v>0}
        mp=[next(v for v in domains[u] if x[u,v] in model) for u in range(sn)]
    assert len(mp)==len(set(mp))==sn
    eset=set(target)
    assert all(tuple(sorted((mp[u],mp[v]))) in eset for u,v in source)
    return {'index':idx,'verdict':'NON_BIPLANAR_BY_CHECKED_SUBGRAPH',
            'vertex_map':mp,'edges_checked':len(source),'variables':pool.top,'clauses':len(cls),
            'solve_seconds':time.monotonic()-start}


def main():
    if len(sys.argv)>1:
        print(json.dumps(worker(int(sys.argv[1]))))
        return
    start=time.monotonic()
    rows=[]
    root=Path('artifacts/tmp/S005/embeddings')
    root.mkdir(parents=True,exist_ok=True)
    for idx in range(271):
        r={'index':idx,'verdict':'UNKNOWN'}
        if time.monotonic()-start>=600:
            r['reason']='aggregate cap; not run'
        else:
            cmd=[sys.executable,__file__,str(idx)]
            t=time.monotonic()
            try:
                run=subprocess.run(cmd,capture_output=True,text=True,timeout=min(7,600-(t-start)))
                (root/f'{idx:03d}.log').write_text(run.stdout+run.stderr,newline='\n')
                if run.returncode==0:
                    r=json.loads(run.stdout)
                else:
                    r['reason']='worker failure'
            except subprocess.TimeoutExpired:
                r['reason']='hard 7 s wall cap (includes encoding/startup)'
            r['command']=cmd
            r['wall_seconds']=time.monotonic()-t
        rows.append(r)
        Path('validation/S005/general_transfers.json').write_text(json.dumps({
            'obstruction_source_index':165,'seconds':time.monotonic()-start,'results':rows},indent=1),newline='\n')
        if r['verdict']=='NON_BIPLANAR_BY_CHECKED_SUBGRAPH':
            print(idx,'checked general vertex map',flush=True)
    print('DONE',len(rows),'maps',sum(r['verdict']=='NON_BIPLANAR_BY_CHECKED_SUBGRAPH' for r in rows),flush=True)


if __name__=='__main__':
    main()
