#!/usr/bin/env python3
"""CAM-0006 G: transform only accepted reduced proofs, then cold recheck."""
import json
from pathlib import Path

from s005_search import run_logged,compress
from s005_replay import sha


def main():
    records=Path('validation/S005/dense/results.json')
    rows=json.loads(records.read_text())
    checker=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
    for row in rows:
        if row['verdict']!='NON_BIPLANAR_DRAT_VERIFIED':
            continue
        prefix=Path('artifacts/tmp/S005/dense')/f"{row['mode']}-row{row['index']}"
        cnf=str(prefix)+'.cnf'
        original=str(prefix)+'.drat'
        assert sha(cnf)==row['cnf_sha256'] and sha(original)==row['proof_sha256']
        core=str(prefix)+'.core.drat'
        trim=run_logged([checker,cnf,original,'-l',core,'-t','600'],620,str(prefix)+'.trim.log')
        row['compact_attempt']={'trim':trim}
        if Path(core).exists() and 's VERIFIED' in Path(str(prefix)+'.trim.log').read_text():
            check=run_logged([checker,cnf,core,'-t','600'],620,str(prefix)+'.core.check.log')
            row['compact_attempt']['check']=check
            if 's VERIFIED' in Path(str(prefix)+'.core.check.log').read_text():
                row['original_archive_sha256']=row['archive_sha256']
                compress(core,row['archive'])
                row.update(archived_raw_sha256=sha(core),archived_raw_bytes=Path(core).stat().st_size,
                           archive_sha256=sha(row['archive']),compact_checker='VERIFIED')
                dest=Path('validation/S005/dense')/prefix.name
                for suffix in ('.trim.log','.core.check.log'):
                    Path(str(dest)+suffix).write_bytes(Path(str(prefix)+suffix).read_bytes())
        records.write_text(json.dumps(rows,indent=1),newline='\n')
        print(row['mode'],row['index'],'compact',row.get('archived_raw_bytes',row['proof_bytes']),flush=True)


if __name__=='__main__':
    main()
