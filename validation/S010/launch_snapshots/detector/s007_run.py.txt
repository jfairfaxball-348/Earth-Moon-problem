#!/usr/bin/env python3
"""CAM-0008 baseline, supervised searches and actual native proof checks."""
import gzip
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from triangulation_cover import Cover
from s007_cover import StrongCover
from biplanar_cnf import read_edges
from blowup_graph import blowup
from blowup_chi_cnf import bag_cnf
from s004_certify import write_cnf
from check_layers import main as check_split
from s006_run import certificate as old_certificate

ROOT = Path('validation/S007')
TMP = Path('artifacts/tmp/S007')
CHECKER = str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
INDICES = (162,155,157,159)


def save(p, x):
    Path(p).write_text(json.dumps(x, indent=1)+'\n', encoding='utf-8', newline='\n')


def launch_hashes(mode):
    files = ['tools/s007_run.py','tools/s007_cover.py','tools/triangulation_cover.py',
             'tools/s005_search.py','tools/s005_replay.py','tools/biplanar_cegar.py']
    save(ROOT/(mode+'_launch_hashes.json'), {p:sha(p) for p in files})


def replay():
    import networkx, pysat
    old = json.loads(Path('validation/S006/environment.json').read_text())
    hashes = {name:sha(Path('artifacts/tmp/S004')/name) for name in old['native_sha256']}
    assert hashes == old['native_sha256']
    pins = {}
    for name, pin in old['native_sources'].items():
        source = Path('artifacts/tmp/S004')/name
        got = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        status = subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
        assert got == pin and not status
        pins[name] = got
    save(ROOT/'environment.json',dict(python=sys.version,platform=platform.platform(),
        networkx=networkx.__version__,python_sat=pysat.__version__,native_sha256=hashes,
        native_sources=pins,build='S004 reused; no build'))
    # Reuse inherited baseline without writing to any previous session.
    text = Path('tools/s005_replay.py').read_text().replace("'validation/S005'", "'validation/S007'")
    text = text.replace("'artifacts/tmp/S005/replay'", "'artifacts/tmp/S007/replay'")
    text = 'import sys\nsys.path.insert(0, '+repr(str(Path('tools').resolve()))+')\n'+text
    adapter = TMP/'baseline.py'; adapter.write_text(text, newline='\n')
    save(ROOT/'baseline_launch_hash.json',dict(path=str(adapter),sha256=sha(adapter)))
    run = run_logged([sys.executable,str(adapter)],2400,ROOT/'baseline.log')
    save(ROOT/'baseline_command.json',run)
    assert run['returncode'] == 0
    cold=[]
    for session, filenames in [('S005',['search_results.json']),('S006',['search_results.json','larger_search_results.json'])]:
        rows=[]
        for name in filenames:
            rows.extend(json.loads(Path('validation',session,name).read_text()))
        for r in rows:
            if r['verdict'] != 'NON_BIPLANAR_DRAT_VERIFIED':
                continue
            idx = r['target']['index']; rec = r['certificate']
            src = Path('validation',session,'search',f'cover-row{idx}')
            dest = TMP/'cold'/f'{session}-row{idx}'; dest.parent.mkdir(parents=True,exist_ok=True)
            cnf = Path(str(dest)+'.cnf'); proof = Path(str(dest)+'.drat')
            cnf.write_bytes(gzip.decompress(Path(str(src)+'.cnf.gz').read_bytes()))
            proof.write_bytes(gzip.decompress(Path(rec['archive']).read_bytes()))
            assert sha(cnf)==rec['cnf_sha256'] and sha(proof)==rec['archive_raw_sha256']
            d=json.loads(Path(str(src)+'.cuts.json').read_text())
            c=Cover(read_edges(r['target']['edgefile']),d['lex'],d.get('short_links',False));c.cuts=d['cuts']
            regen=Path(str(dest)+'.regenerated.cnf');c.write_cnf(regen)
            assert regen.read_bytes()==cnf.read_bytes()
            log=ROOT/f'cold-{session}-row{idx}.check.log'
            check=run_logged([CHECKER,str(cnf),str(proof),'-t','1200'],1220,log)
            assert check['returncode']==0 and 's VERIFIED' in log.read_text()
            cold.append(dict(session=session,index=idx,command=check,checker='VERIFIED',
                cnf_sha256=sha(cnf),proof_sha256=sha(proof),archive_sha256=sha(rec['archive'])))
            save(ROOT/'cold_prior.json',cold)
            print('cold',session,idx,'VERIFIED',flush=True)
    assert len(cold)==40
    targets=[]
    source=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    chi=json.loads(Path('validation/S004/chi10_results.json').read_text())
    for idx in INDICES:
        g,w,_=source[idx];rec=chi[idx];es,_=blowup(g,w)
        ef=ROOT/'targets'/f'row{idx}.edges';ef.parent.mkdir(exist_ok=True)
        ef.write_text(''.join(f'{a} {b}\n' for a,b in es),newline='\n')
        col=rec['ten_colouring'];assert len(col)==sum(w) and all(0<=x<10 for x in col)
        assert all(col[a]!=col[b] for a,b in es)
        cnf=TMP/f'chi-row{idx}.cnf';proof=TMP/f'chi-row{idx}.drat'
        write_cnf(cnf,*bag_cnf(g,w,9));proof.write_bytes(gzip.decompress(Path(rec['bag']['archive']).read_bytes()))
        assert sha(cnf)==rec['bag']['cnf_sha256'] and sha(proof)==rec['bag']['drat_sha256']
        log=ROOT/f'chi-row{idx}.check.log'
        check=run_logged([CHECKER,str(cnf),str(proof),'-t','600'],620,log)
        assert check['returncode']==0 and 's VERIFIED' in log.read_text()
        targets.append(dict(index=idx,g6=g,w=w,n=sum(w),m=len(es),D=6*sum(w)-12-len(es),
            edgefile=str(ef),edge_sha256=sha(ef),ten_colouring=col,chi=10,chromatic_check=check,
            bag_cnf_sha256=sha(cnf),bag_proof_sha256=sha(proof),bag_archive=rec['bag']['archive']))
        save(ROOT/'targets.json',targets)
    controls=[]
    for row in json.loads((ROOT/'controls.json').read_text())['results']:
        tag=f"control-{row['index']:02d}" if 'index' in row else 'control-'+row['tag']
        ef=TMP/'replay'/f'{tag}.edges' if 'index' in row else Path(f"validation/S003/splits/{row['tag']}.edges")
        prefix=TMP/('strong-'+tag)
        # Supervision protects even a baseline control from a blocked solver call.
        log=ROOT/(tag+'.strong.log')
        run=run_logged([sys.executable,'tools/s007_cover.py',str(ef),str(prefix),'30','--lex'],50,log)
        assert run['returncode']==0
        result=json.loads(Path(str(prefix)+'.result.json').read_text())
        assert result['verdict']=='SAT_CHECKED'
        check_split(str(ef),str(prefix)+'.split.json')
        controls.append(dict(tag=tag,command=run,result=result,
            split=json.loads(Path(str(prefix)+'.split.json').read_text())))
        save(ROOT/'strong_controls.json',controls)
    save(ROOT/'BASELINE_PASS.json',dict(cold_full_proofs=40,strong_controls=len(controls),fresh_chi10_targets=4,
        inherited_baseline='K9/row165/bag;271 hash/CNF/colour audit;23 actual controls'))
    print('BASELINE PASS',flush=True)


def certificate(edgefile,prefix):
    import s006_run
    # Use the proven pipeline without overwriting earlier evidence; change generator only.
    s006_run.ROOT=ROOT
    text=Path('tools/s006_run.py').read_text()
    start=text.index('def certificate(');end=text.index('\n\ndef search()',start)
    code=text[start:end].replace('tools/triangulation_cover.py','tools/s007_cover.py')
    scope=dict(s006_run.__dict__);exec(code,scope)
    return scope['certificate'](edgefile,prefix)


def search():
    assert (ROOT/'BASELINE_PASS.json').exists()
    (ROOT/'search').mkdir(exist_ok=True);(TMP/'search').mkdir(exist_ok=True)
    rows=[];consecutive=0
    for target in json.loads((ROOT/'targets.json').read_text()):
        idx=target['index'];prefix=TMP/'search'/f'cover-row{idx}'
        row=dict(target=target,verdict='UNKNOWN')
        if consecutive>=2:
            row['reason']='NOT_RUN after two consecutive final UNKNOWNs'
        else:
            run=run_logged([sys.executable,'tools/s007_cover.py',target['edgefile'],str(prefix),'900','--lex'],
                920,str(prefix)+'.run.log');row['run']=run
            meta=Path(str(prefix)+'.result.json')
            if meta.exists():
                row['search']=json.loads(meta.read_text())
            if run['returncode']==0 and row.get('search',{}).get('verdict')=='UNSAT':
                row['certificate']=certificate(target['edgefile'],prefix)
                row['verdict']=row['certificate']['verdict']
            elif run['returncode']==0 and row.get('search',{}).get('verdict')=='SAT_CHECKED':
                check_split(target['edgefile'],str(prefix)+'.split.json')
                shutil.copyfile(str(prefix)+'.split.json',ROOT/'search'/f'row{idx}.split.json')
                row['verdict']='BIPLANAR_CHECKED_CHI10'
            consecutive=consecutive+1 if row['verdict']=='UNKNOWN' else 0
            for suffix in ('.cuts.json','.result.json','.run.log'):
                p=Path(str(prefix)+suffix)
                if p.exists():shutil.copyfile(p,ROOT/'search'/(prefix.name+suffix))
        rows.append(row);save(ROOT/'search_results.json',rows)
        print(idx,row['verdict'],row.get('run',{}).get('seconds','NOT_RUN'),flush=True)
        if row['verdict']=='BIPLANAR_CHECKED_CHI10':break


if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
    launch_hashes(sys.argv[1]);{'replay':replay,'search':search}[sys.argv[1]]()
