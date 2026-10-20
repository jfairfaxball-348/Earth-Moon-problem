"""One persistent CaDiCaL300 S11 solver, semantic checkpoints, no model blockers.

Incremental UNSAT only requests native proof replay; it is not a graph verdict.
"""
import argparse
from datetime import datetime,timezone
import gzip
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import shutil
import sys
import time

import networkx as nx
from pysat.solvers import Solver

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s026_supervision import atomic_json,journal
from s030_op1b import encode,triangle_free,library_cut
from s031_check import cut as check_cut,model as check_model


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def search(out,cap,resume=False,conflicts=100000,decisions=1000000):
    out.mkdir(parents=True,exist_ok=True)
    smoke=json.loads((ROOT/'artifacts/tmp/S031/SMOKE.json').read_text())
    assert smoke['verdict']=='PASS' and smoke['chromatic_rows_verified']==271
    assert json.loads((ROOT/'artifacts/tmp/S031/CONTROLS.json').read_text())['status']=='PASS'
    f,g,layers=encode(28,11,155,156,anchor=True,sorted_anchor=True)
    base_clauses=len(f.clauses);cuts=[];seen=set();models=0
    if resume:
        checkpoint=json.loads((out/'CHECKPOINT.json').read_text())
        incoming=checkpoint['cuts'];models=checkpoint['models']
    else:
        incoming=[]
        for name in ('sorted','pilot'):
            incoming+=json.loads((ROOT/f'validation/S030/{name}/CUTS.json').read_text())
    for c in incoming:
        check_cut(c,g,layers);key=tuple(sorted(c['clause']))
        if key not in seen:
            seen.add(key);cuts.append(c);f.append(c['clause'])
    atomic_json(out/'VARIABLES.json',{'g':[[*e,x] for e,x in g.items()],
               'layers':[[[*e,x] for e,x in ls.items()] for ls in layers]})
    start=time.monotonic();slices=0;last_full=0
    meta={'pid':os.getpid(),'solver':'cadical300','persistent_instance_count':1,
          'started_utc':datetime.now(timezone.utc).isoformat(),'cap_seconds':cap,
          'base_clauses':base_clauses,'seed_cuts':len(cuts),'resumed_semantic_checkpoint':resume,
          'conflicts_per_slice':conflicts,'decisions_per_slice':decisions,
          'native_learned_state_restored':False,'source_sha256':sha(__file__)}
    atomic_json(out/'WORKER.json',meta)

    def save(status,stats,full=False):
        nonlocal last_full
        progress={**meta,'status':status,'verdict':'UNKNOWN','models':models,'cuts':len(cuts),
                  'slices':slices,'seconds':round(time.monotonic()-start,3),'stats':stats,
                  'updated_utc':datetime.now(timezone.utc).isoformat(),
                  'free_disk_bytes':shutil.disk_usage(out).free}
        atomic_json(out/'PROGRESS.json',progress)
        if full:
            # This single atomic JSON is the authoritative semantic checkpoint.
            atomic_json(out/'CHECKPOINT.json',{**progress,'cuts':cuts})
            atomic_json(out/'CUTS.json',cuts)
            tmp=out/'checkpoint.cnf.tmp';f.to_file(str(tmp));os.replace(tmp,out/'final.cnf')
            last_full=time.monotonic()
        return progress

    status='WALL_CAPPED';stats={}
    with Solver(name='cadical300',bootstrap_with=f,use_timer=True) as solver:
        save('RUNNING',solver.accum_stats(),True)
        while time.monotonic()-start<cap:
            if (out/'STOP').exists():status='OWNER_OR_CONTROLLER_STOP';break
            if shutil.disk_usage(out).free<10*1024**3:status='DISK_RESERVE_STOP';break
            # Both budgets are reset on the SAME live instance, retaining CDCL state.
            solver.conf_budget(conflicts);solver.dec_budget(decisions)
            answer=solver.solve_limited();slices+=1;stats=solver.accum_stats()
            save('RUNNING',stats,time.monotonic()-last_full>300)
            if answer is None:continue
            if answer is False:status='INCREMENTAL_UNSAT_PENDING_NATIVE_PROOF';break
            positive={x for x in solver.get_model() if x>0}
            graph,parts=check_model(positive,g,layers,f)
            models+=1
            model={'n':28,'E1':sorted(parts[0]),'E2':sorted(parts[1]),
                   'positive_model':sorted(positive),'clauses_before':len(f.clauses),
                   'stats':stats,'seconds':time.monotonic()-start}
            modeldir=out/'models';modeldir.mkdir(exist_ok=True)
            data=json.dumps(model,separators=(',',':')).encode()
            (modeldir/f'{models:07d}.json.gz').write_bytes(gzip.compress(data,mtime=0))
            new=[];cliques=set()
            for maximal in nx.find_cliques(graph):
                if len(maximal)<9:continue
                for nine in it.combinations(sorted(maximal),9):
                    cliques.add(nine)
                    if len(cliques)>=1000:break
                if len(cliques)>=1000:break
            for nine in sorted(cliques):
                es=list(it.combinations(nine,2));new.append({'kind':'K9','edges':es,'clause':[-g[e] for e in es]})
            tf=triangle_free(graph)
            if len(tf)>104:new.append({'kind':'triangle_free','edges':tf,'clause':[-g[e] for e in tf]})
            if not cliques:
                c=library_cut(graph,g)
                if c:new.append(c)
            planar=[]
            for k,part in enumerate(parts):
                h=nx.Graph();h.add_nodes_from(range(28));h.add_edges_from(part)
                ok,certificate=nx.check_planarity(h,counterexample=True);planar.append(ok)
                if not ok:
                    es=sorted(tuple(sorted(e)) for e in certificate.edges())
                    new.append({'kind':'Kuratowski','layer':k,'edges':es,'clause':[-layers[k][e] for e in es]})
            if all(planar):
                from s025_check import check_split
                check_split(28,list(graph.edges()),sorted(parts[0]),sorted(parts[1]))
                atomic_json(out/'WITNESS_CANDIDATE.json',model)
                status='WITNESS_CANDIDATE_STOP';break
            added=0
            for c in new:
                check_cut(c,g,layers);key=tuple(sorted(c['clause']))
                if key in seen:continue
                # Record the independent audit BEFORE extending the live solver.
                c={**c,'model_number':models}
                journal(out/'CUT_JOURNAL.jsonl','validated_cut',cut=c)
                seen.add(key);cuts.append(c);f.append(c['clause']);solver.add_clause(c['clause']);added+=1
            assert added>0,'SAT model yielded no new valid exclusion; stop instead of blocking it'
            p=save('RUNNING',stats,True)
            print(json.dumps({k:p[k] for k in ('models','cuts','seconds','stats')}),flush=True)
        p=save(status,stats,True)
    result={**p,'stop_reason':status,'S11_m155_156':'UNKNOWN','S10':'NOT_RUN','S9':'NOT_RUN',
            'witness_candidate':status=='WITNESS_CANDIDATE_STOP','whole_stratum_certified':False,
            'final_cnf_sha256':sha(out/'final.cnf'),'cuts_sha256':sha(out/'CUTS.json')}
    atomic_json(out/'RESULT.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='artifacts/tmp/S031/search')
    ap.add_argument('--cap',type=int,default=28680);ap.add_argument('--resume',action='store_true')
    ap.add_argument('--conflicts',type=int,default=100000);ap.add_argument('--decisions',type=int,default=1000000)
    a=ap.parse_args();search(ROOT/a.out,a.cap,a.resume,a.conflicts,a.decisions)
