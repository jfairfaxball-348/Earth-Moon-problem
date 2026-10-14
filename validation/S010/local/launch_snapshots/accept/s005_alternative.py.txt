#!/usr/bin/env python3
"""CAM-0006 J: fresh proof-export calibration then a separate row179 proof."""
import json
import sys
from pathlib import Path

from s005_search import run_logged,compress
from s005_replay import sha
from biplanar_cnf import read_edges
from triangulation_cover import Cover


def main():
    scratch=Path('artifacts/tmp/S005/alternative')
    scratch.mkdir(parents=True,exist_ok=True)
    checker=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
    rows=[]
    for tag,cnf,solve_cap,check_cap in (
        ('K9','artifacts/tmp/S005/replay/K9.cnf',620,620),
        ('row179','artifacts/tmp/S005/search/cover-row179.cnf',620,1220)):
        if tag=='row179':
            data=json.loads(Path('artifacts/tmp/S005/search/cover-row179.cuts.json').read_text())
            c=Cover(read_edges('validation/S005/targets/row179.edges'),data['lex'],data.get('short_links',False))
            c.cuts=data['cuts'];regen=scratch/'row179.regenerated.cnf';c.write_cnf(regen)
            assert regen.read_bytes()==Path(cnf).read_bytes()
        prefix=scratch/tag
        proof=str(prefix)+'.drat'
        solve=run_logged([sys.executable,'tools/export_pysat_drat.py',cnf,proof],solve_cap,str(prefix)+'.solve.log')
        row={'tag':tag,'solve':solve,'verdict':'UNKNOWN','cnf_sha256':sha(cnf)}
        if solve['returncode']!=0:
            rows.append(row);break
        check=run_logged([checker,cnf,proof,'-t',str(check_cap-20)],check_cap,str(prefix)+'.check.log')
        row['check']=check
        if 's VERIFIED' not in Path(str(prefix)+'.check.log').read_text():
            rows.append(row);break
        row.update(verdict='DRAT_VERIFIED',proof_sha256=sha(proof),proof_bytes=Path(proof).stat().st_size)
        chosen=proof
        if tag=='row179':
            core=str(prefix)+'.core.drat'
            trim=run_logged([checker,cnf,proof,'-l',core,'-t','600'],620,str(prefix)+'.trim.log')
            row['trim']=trim
            if Path(core).exists() and 's VERIFIED' in Path(str(prefix)+'.trim.log').read_text():
                corecheck=run_logged([checker,cnf,core,'-t','600'],620,str(prefix)+'.core.check.log')
                row['core_check']=corecheck
                if 's VERIFIED' in Path(str(prefix)+'.core.check.log').read_text():
                    chosen=core
            archive='validation/S005/search/alternative-row179.drat.gz'
            compress(chosen,archive)
            row.update(archive=archive,archive_raw_sha256=sha(chosen),archive_raw_bytes=Path(chosen).stat().st_size,
                       archive_sha256=sha(archive))
        for suffix in ('.solve.log','.check.log','.trim.log','.core.check.log'):
            p=Path(str(prefix)+suffix)
            if p.exists():
                Path('validation/S005/search',f'alternative-{tag}'+suffix).write_bytes(p.read_bytes())
        rows.append(row)
        Path('validation/S005/alternative_results.json').write_text(json.dumps(rows,indent=1),newline='\n')
        print('ALTERNATIVE',tag,row['verdict'],flush=True)
    Path('validation/S005/alternative_results.json').write_text(json.dumps(rows,indent=1),newline='\n')


if __name__=='__main__':
    main()
