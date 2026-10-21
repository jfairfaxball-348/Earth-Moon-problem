"""Exact disjoint-region accounting; default report never starts a solver.

Counts graph-presence assignments, existentially leaving layer/counter variables
free. A region closes only with standalone DRAT checked by drat-trim. This is
coverage of the stated encoded domain, not a time-to-solution percentage.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from s026_supervision import atomic_json, kill_tree, windows_tree_bytes


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def weight(total, present, low, high):
    return sum(math.comb(total, m-present) for m in range(low, high+1)
               if 0 <= m-present <= total)


def partition(variables, units, bits, low, high):
    free = [v for v in variables if v not in units]
    assert 0 <= bits <= min(12, len(free))
    chosen = free[:bits]
    pinned = sum(units.values())
    rows = []
    for i, values in enumerate(itertools.product((False, True), repeat=bits)):
        rows.append(dict(id=i, assumptions=[v if b else -v for v,b in zip(chosen, values)],
            weight=str(weight(len(free)-bits, pinned+sum(values), low, high)), status='PENDING'))
    assert sum(int(row['weight']) for row in rows) == weight(len(free), pinned, low, high)
    return rows


def initialise(area, bits, include_rules=True):
    assert not area.exists(), 'Use another directory; existing progress is never overwritten.'
    data_root = ROOT/'artifacts/tmp/S032'
    audit = json.loads((data_root/'CAMPAIGN_AUDIT.json').read_text())
    assert audit['status']=='PASS'
    inputs = json.loads((data_root/'INPUTS.json').read_text())
    m = len(inputs['pairs']); variables = list(range(2*m+1, 3*m+1))
    units = {}
    with (data_root/'base.cnf').open() as f:
        for line in f:
            if line.startswith(('c','p')):continue
            cs = list(map(int, line.split()))
            if len(cs)==2 and abs(cs[0]) in variables:
                v=abs(cs[0]);b=cs[0]>0
                assert v not in units or units[v]==b
                units[v]=b
    rows = partition(variables, units, bits, 155, 156)
    files = {'base':data_root/'base.cnf'}
    if include_rules:files['rules']=data_root/'campaign/learned.lem'
    hashes = {k:sha(p) for k,p in files.items()}
    if include_rules:assert hashes['rules']==audit['lemma_sha256']
    total = sum(int(row['weight']) for row in rows)
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        meaning='Labelled edge sets satisfying graph unit pins and m155/156; other constraints remain to be checked.',
        warning='Encoder symmetry pins/sorting are not nonbiplanarity exclusions of differently labelled graphs. No ETA.',
        raw_edge_set_count=str(weight(m, 0, 155, 156)),
        graph_unit_pins={str(k):v for k,v in units.items()},
        total_region_weight=str(total), bits=bits, include_retained_rules=include_rules,
        files={k:str(p) for k,p in files.items()}, sha256=hashes,
        variables=inputs['variables'], base_clauses=inputs['base_clauses'],
        retained_clauses=audit['independently_checked_native_clauses'] if include_rules else 0,
        cells=rows, mathematical_verdict='UNKNOWN')
    area.mkdir(parents=True)
    atomic_json(area/'coverage.json', manifest)


def supervise(command, log, seconds):
    start=time.monotonic();reason=None
    assert math.isfinite(seconds) and seconds>0
    assert shutil.disk_usage(ROOT).free>10*1024**3
    with log.open('w') as f:
        p=subprocess.Popen(list(map(str,command)), stdout=f, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            while p.poll() is None:
                if time.monotonic()-start>seconds:reason='WALL_CAPPED'
                elif windows_tree_bytes(os.getpid())>11*1024**3:reason='MEMORY_CAPPED'
                elif shutil.disk_usage(ROOT).free<10*1024**3:reason='DISK_RESERVE_STOP'
                if reason:kill_tree(p);break
                time.sleep(.5)
        finally:
            if p.poll() is None:kill_tree(p)
    return dict(command=list(map(str,command)),returncode=p.returncode,
                seconds=time.monotonic()-start,stop_reason=reason)


def formula(path, data, units):
    count=data['base_clauses']+data['retained_clauses']+len(units)
    with path.open('w',newline='\n') as dst:
        dst.write(f"p cnf {data['variables']} {count}\n")
        with Path(data['files']['base']).open() as src:
            next(src);shutil.copyfileobj(src,dst)
        if 'rules' in data['files']:
            with Path(data['files']['rules']).open() as src:shutil.copyfileobj(src,dst)
        if 'extra_rules' in data['files']:
            with Path(data['files']['extra_rules']).open() as src:shutil.copyfileobj(src,dst)
        for lit in units:dst.write(f'{lit} 0\n')


def check(area, cell_id, seconds, extra_rules=None):
    assert not (ROOT/'artifacts/tmp/S032/ACTIVE.lock').exists(), 'A campaign is active; do not duplicate heavy work.'
    lock=area/'CHECK.lock'
    fd=os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
    try:
        data=json.loads((area/'coverage.json').read_text());cell=data['cells'][cell_id]
        assert cell['id']==cell_id and cell['status']!='UNSAT_DRAT_VERIFIED'
        for k,p in data['files'].items():assert sha(p)==data['sha256'][k],p
        trial=area/f'cell-{cell_id:04d}'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        trial.mkdir(parents=True);cnf=trial/'formula.cnf';proof=trial/'proof.drat'
        if extra_rules:
            from check_s032_native import lemmas
            inputs=json.loads((ROOT/'artifacts/tmp/S032/INPUTS.json').read_text())
            extra_rules=extra_rules.resolve()
            before=sha(extra_rules)
            count=lemmas(extra_rules,28,[tuple(e) for e in inputs['pairs']])
            assert before==sha(extra_rules),'Do not check a mutable native lemma file'
            data['files']['extra_rules']=str(extra_rules)
            data['retained_clauses']+=count
            atomic_json(trial/'EXTRA_RULES_AUDIT.json',dict(status='PASS',count=count,sha256=before,
                method='independent subdivision suppression',edge_order_sha256=sha(ROOT/'artifacts/tmp/S032/INPUTS.json')))
        formula(cnf,data,cell['assumptions'])
        if extra_rules:assert sha(extra_rules)==before,'Extra lemmas changed during formula construction'
        native=ROOT/'artifacts/tmp/S004/cadical.exe'
        checker=ROOT/'artifacts/tmp/S004/drat-trim-mingw.exe'
        result=supervise([native,cnf,proof],trial/'solve.log',seconds)
        cell['status']='UNKNOWN';cell['last_attempt']=str(trial)
        if result['stop_reason'] is None and result['returncode']==20:
            checked=supervise([checker,cnf,proof],trial/'check.log',seconds)
            result['checker']=checked
            if checked['stop_reason'] is None and checked['returncode']==0 and 's VERIFIED' in (trial/'check.log').read_text():
                cell['status']='UNSAT_DRAT_VERIFIED'
                cell['certificate']={str(p):sha(p) for p in [cnf,proof,trial/'check.log']}
                if extra_rules:cell['certificate'][str(trial/'EXTRA_RULES_AUDIT.json')]=sha(trial/'EXTRA_RULES_AUDIT.json')
        elif result['stop_reason'] is None and result['returncode']==10:
            cell['status']='RELAXATION_SAT_NOT_A_PLANAR_WITNESS'
        atomic_json(trial/'RESULT.json',result)
        if extra_rules:
            del data['files']['extra_rules'];data['retained_clauses']-=count
        atomic_json(area/'coverage.json',data)
    finally:lock.unlink(missing_ok=True)


def export(area, cell_id):
    data=json.loads((area/'coverage.json').read_text());cell=data['cells'][cell_id]
    for k,p in data['files'].items():assert sha(p)==data['sha256'][k],p
    target=area/f'cell-{cell_id:04d}.inst'
    assert not target.exists(),'Do not overwrite an existing exported input'
    inputs=json.loads((ROOT/'artifacts/tmp/S032/INPUTS.json').read_text())
    pairs=inputs['pairs'];count=data['base_clauses']+data['retained_clauses']+len(cell['assumptions'])
    with target.open('w',newline='\n') as dst:
        dst.write(f"p bipsat2 28 {len(pairs)} {data['variables']-2*len(pairs)} {count}\n")
        for a,b in pairs:dst.write(f'e {a} {b}\n')
        with Path(data['files']['base']).open() as src:
            next(src);shutil.copyfileobj(src,dst)
        if 'rules' in data['files']:
            with Path(data['files']['rules']).open() as src:shutil.copyfileobj(src,dst)
        for lit in cell['assumptions']:dst.write(f'{lit} 0\n')
    atomic_json(target.with_suffix('.json'),dict(input=str(target),sha256=sha(target),
        graph_region=cell['assumptions'],scope='S032 encoded graph-presence region; no search launched'))
    print('Exported input only:',target)


def report(area):
    data=json.loads((area/'coverage.json').read_text());closed=0;count=0
    for cell in data['cells']:
        if cell['status']=='UNSAT_DRAT_VERIFIED':
            for p,h in cell['certificate'].items():assert sha(p)==h,p
            closed+=int(cell['weight']);count+=1
    total=int(data['total_region_weight'])
    assert sum(int(c['weight']) for c in data['cells'])==total
    assert len({tuple(c['assumptions']) for c in data['cells']})==len(data['cells'])
    out=dict(raw_labelled_edge_sets_before_other_constraints=data['raw_edge_set_count'],
        encoded_region_weight=str(total), proof_closed_region_weight=str(closed),
        unresolved_region_weight=str(total-closed), proof_closed_regions=count,
        total_regions=len(data['cells']), encoded_region_percentage=100*closed/total if total else 100,
        includes_retained_rules=data['include_retained_rules'], mathematical_verdict='UNKNOWN',
        meaning=data['meaning'], warning=data['warning'],
        limitation='This counts checked closed regions of the encoded domain, not graphs excluded solely by new rules or progress towards a witness. SAT and caps stay unresolved. A high percentage need not imply a short remaining runtime.')
    atomic_json(area/'REPORT.json',out)
    print(json.dumps(out,indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['init','report','check','export'])
    ap.add_argument('--directory',type=Path,default=ROOT/'artifacts/tmp/S032/coverage')
    ap.add_argument('--bits',type=int,default=8)
    ap.add_argument('--base-only',action='store_true',help='Separate baseline ledger without campaign lemmas')
    ap.add_argument('--cell',type=int,default=0)
    ap.add_argument('--extra-lemmas',type=Path,help='Stopped region worker lemmas, independently audited before proof replay')
    ap.add_argument('--seconds',type=float,default=60,help='Each proof/check step; UNKNOWN if capped')
    args=ap.parse_args()
    if args.command=='init':initialise(args.directory,args.bits,not args.base_only)
    elif args.command=='check':check(args.directory,args.cell,args.seconds,args.extra_lemmas)
    elif args.command=='export':export(args.directory,args.cell)
    report(args.directory)


if __name__=='__main__':main()
