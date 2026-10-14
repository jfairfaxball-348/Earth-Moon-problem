#!/usr/bin/env python3
"""Supervise no-lex controls and the row165 challenge under CAM-0006."""
import json
from pathlib import Path
import sys

from s005_search import run_logged,certify
from independent_cover_search import Independent
from biplanar_cnf import read_edges
from check_layers import main as check_split


def main():
    root=Path('artifacts/tmp/S005/independent')
    root.mkdir(parents=True,exist_ok=True)
    controls=[]
    for idx in range(10):
        controls.append((str(idx),f'artifacts/tmp/S005/replay/control-{idx:02d}.edges'))
    controls.extend((tag,f'validation/S003/splits/{tag}.edges') for tag in ('K8','sulanke','K9e'))
    results=[]
    for tag,edgefile in ([] if '--row120' in sys.argv else controls):
        prefix=str(root/('control-'+tag))
        r=run_logged([sys.executable,'tools/independent_cover_search.py',edgefile,prefix,'30'],
                     40,prefix+'.run.log')
        meta=json.loads(Path(prefix+'.result.json').read_text()) if Path(prefix+'.result.json').exists() else {}
        result={'tag':tag,'run':r,'search':meta}
        results.append(result)
        Path('validation/S005/independent_controls.json').write_text(json.dumps(results,indent=1),newline='\n')
        if r['returncode']!=0 or meta.get('verdict')!='SAT_CHECKED':
            print('CONTROL FAILED/UNKNOWN',tag,flush=True)
            return
        check_split(edgefile,prefix+'.split.json')
    idx=120 if '--row120' in sys.argv else 165
    if idx==120:
        previous=json.loads(Path('validation/S005/independent_controls.json').read_text())
        assert len(previous)==13 and all(r['search']['verdict']=='SAT_CHECKED' for r in previous)
        edgefile='validation/S005/targets/row120.edges'
        prefix=str(root/'no-lex-row120')
        cmd=[sys.executable,'tools/independent_cover_search.py',edgefile,prefix,'180']
        cap=200
    else:
        edgefile='validation/S004/targets/full-min-survivor.edges'
        prefix=str(root/'no-lex-row165')
        cmd=[sys.executable,'tools/independent_cover_search.py',edgefile,prefix,'600',
             'validation/S004/search/cover-full-min-survivor.cuts.json']
        cap=620
    r=run_logged(cmd,cap,prefix+'.run.log')
    row={'run':r,'verdict':'UNKNOWN'}
    p=Path(prefix+'.result.json')
    if p.exists():
        meta=json.loads(p.read_text())
        row['search']=meta
        if r['returncode']==0 and meta['verdict']=='UNSAT':
            row['certificate']=certify(edgefile,Path(prefix),'tools/independent_cover_search.py')
            row['verdict']=row['certificate']['verdict']
        elif r['returncode']==0 and meta['verdict']=='SAT_CHECKED':
            check_split(edgefile,prefix+'.split.json')
            row['verdict']='BIPLANAR_CHECKED_CONTRADICTION_REQUIRES_AUDIT'
    for suffix in ('.cuts.json','.result.json','.run.log'):
        p=Path(prefix+suffix)
        if p.exists():
            Path(f'validation/S005/search/no-lex-row{idx}'+suffix).write_bytes(p.read_bytes())
    resultfile='independent_row120.json' if idx==120 else 'independent_result.json'
    Path('validation/S005',resultfile).write_text(json.dumps(row,indent=1),newline='\n')
    print('INDEPENDENT',row['verdict'],flush=True)


if __name__=='__main__':
    main()
