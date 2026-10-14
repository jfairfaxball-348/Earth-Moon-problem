#!/usr/bin/env python3
"""CAM-0007 B: fresh checked non9-colourability of the exact13 targets."""
import gzip
import json
import sys
from pathlib import Path
from blowup_graph import blowup
from blowup_chi_cnf import bag_cnf
from s004_certify import write_cnf
from s005_search import run_logged
from s005_replay import sha
from s006_run import save,CHECKER


def main():
    source=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    old=json.loads(Path('validation/S004/chi10_results.json').read_text())
    root=Path('validation/S006/chromatic');root.mkdir(exist_ok=True)
    scratch=Path('artifacts/tmp/S006/chromatic');scratch.mkdir(exist_ok=True)
    rows=[]
    larger='--larger-one' in sys.argv
    indices=(197,17,190,195,187,189) if larger else (29,35,46,47,80,81,82,258,260,162,155,157,159)
    for idx in indices:
        rec=old[idx];g,w,_=source[idx]
        assert (rec['index'],rec['g6'],rec['w'])==(idx,g,w)
        edges,_=blowup(g,w);col=rec['ten_colouring']
        assert len(col)==sum(w) and all(type(c)==int and 0<=c<10 for c in col)
        assert all(col[a]!=col[b] for a,b in edges)
        cnf=scratch/f'row{idx}.cnf';proof=scratch/f'row{idx}.drat'
        write_cnf(cnf,*bag_cnf(g,w,9))
        proof.write_bytes(gzip.decompress(Path(rec['bag']['archive']).read_bytes()))
        assert sha(cnf)==rec['bag']['cnf_sha256'] and sha(proof)==rec['bag']['drat_sha256']
        log=root/f'row{idx}.check.log'
        run=run_logged([CHECKER,str(cnf),str(proof),'-t','600'],620,log)
        assert run['returncode']==0 and 's VERIFIED' in log.read_text()
        rows.append(dict(index=idx,g6=g,w=w,ten_colouring=col,cnf_sha256=sha(cnf),
                         archived_proof=rec['bag']['archive'],proof_sha256=sha(proof),
                         command=run,checker='VERIFIED',chi=10))
        save(root/('larger_results.json' if larger else 'results.json'),rows)
    print('PASS',len(rows),'fresh bag DRAT checks and proper10-colourings',flush=True)


if __name__=='__main__':
    main()
