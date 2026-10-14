"""S008 isolated replay, direct new-clause controls and supervised search."""
import itertools
import json
import shutil
import subprocess
import sys
from pathlib import Path
from s005_replay import sha
from s005_search import run_logged
from s007_run import save

ROOT = Path('validation/S008')
TMP = Path('artifacts/tmp/S008')


def launch(mode):
    files = ['tools/s008_run.py','tools/s008_cover.py','tools/s007_run.py',
             'tools/s007_cover.py','tools/triangulation_cover.py','tools/s005_search.py',
             'tools/s005_replay.py','tools/s006_run.py']
    save(ROOT/(mode+'_launch_hashes.json'), {p:sha(p) for p in files})


def replay():
    src = Path('tools/s007_run.py').read_text()
    src = src.replace("'validation/S007'", "'validation/S008'")
    src = src.replace("'artifacts/tmp/S007'", "'artifacts/tmp/S008'")
    src = src.replace("'artifacts/tmp/S007/replay'", "'artifacts/tmp/S008/replay'")
    src = 'import sys\nsys.path.insert(0, '+repr(str(Path('tools').resolve()))+')\n'+src
    adapter = TMP/'replay_adapter.py'; adapter.write_text(src, newline='\n')
    save(ROOT/'replay_adapter_launch.json',dict(path=str(adapter),sha256=sha(adapter)))
    run = run_logged([sys.executable,str(adapter),'replay'],7200,ROOT/'replay_driver.log')
    save(ROOT/'replay_driver_command.json',run)
    assert run['returncode'] == 0 and (ROOT/'BASELINE_PASS.json').exists()


def controls():
    from s008_cover import obstructions
    from check_layers import certify_layer
    rows=[]
    # Frozen independently checked completions from S007, directly checked anew.
    sources=json.loads(Path('validation/S007/static_truth_controls.json').read_text())
    sources+=json.loads(Path('validation/S007/global_controls.json').read_text())
    witness=json.loads(Path('validation/degree11_witness.json').read_text())
    sources.append(dict(n=witness['num_vertices'],completion_edges=[witness[k] for k in ('edges_part1','edges_part2')]))
    for idx,row in enumerate(sources):
        n=row['n']; layers=[{tuple(e) for e in es} for es in row['completion_edges']]
        original=set.union(*layers)
        for e in row.get('removed',[]): original.remove(tuple(e))
        counts={'K5':0,'K33':0}
        for kind,es in obstructions(n, sorted(original)):
            counts[kind]+=1
            for layer in layers:
                assert not set(es)<=layer
            # Independent structural nonplanarity obligation for generated premise.
            if kind=='K5':assert len(set(sum((list(e) for e in es),[])))==5 and len(es)==10
            else:
                import networkx as nx
                g=nx.Graph(es)
                assert len(g)==6 and g.number_of_edges()==9 and nx.is_bipartite(g)
                assert set(dict(g.degree()).values())=={3}
        checks=[certify_layer(n,sorted(es)) for es in layers]
        rows.append(dict(index=idx,n=n,counts=counts,rotation_checks=checks,new_clause_truth='PASS'))
        save(ROOT/'new_clause_controls.json',rows)
    assert len(rows)==27
    print('PASS27 actual completion clause/rotation controls',flush=True)


def certificate(ef,prefix):
    import s006_run
    src=Path('tools/s006_run.py').read_text()
    start=src.index('def certificate(');end=src.index('\n\ndef search()',start)
    src=src[start:end].replace('tools/triangulation_cover.py','tools/s008_cover.py')
    scope=dict(s006_run.__dict__);scope['ROOT']=ROOT
    exec(src,scope)
    result=scope['certificate'](ef,prefix)
    if result['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
        import gzip
        from s008_cover import FullCover
        from biplanar_cnf import read_edges
        cdata=json.loads(Path(str(prefix)+'.cuts.json').read_text())
        c=FullCover(read_edges(str(ef)),cdata['lex'],cdata.get('short_links',False))
        c.cuts=cdata['cuts'];cold=Path(str(prefix)+'.cold.cnf');c.write_cnf(cold)
        assert cold.read_bytes()==gzip.decompress(Path(str(ROOT/'search'/prefix.name)+'.cnf.gz').read_bytes())
        proof=Path(str(prefix)+'.cold.drat');proof.write_bytes(gzip.decompress(Path(result['archive']).read_bytes()))
        assert sha(proof)==result['archive_raw_sha256']
        log=ROOT/'search'/(prefix.name+'.cold.check.log')
        chk=run_logged([scope['CHECKER'],str(cold),str(proof),'-t','600'],620,log)
        result['cold_retained_check']=chk
        if chk['returncode']!=0 or 's VERIFIED' not in log.read_text():result['verdict']='UNKNOWN'
    return result


def search():
    assert (ROOT/'BASELINE_PASS.json').exists() and len(json.loads((ROOT/'new_clause_controls.json').read_text()))==27
    from check_layers import main as check_split
    (ROOT/'search').mkdir(exist_ok=True);(TMP/'search').mkdir(exist_ok=True)
    rows=[];consecutive=0
    for target in json.loads((ROOT/'targets.json').read_text()):
        idx=target['index'];prefix=TMP/'search'/f'cover-row{idx}'
        row=dict(target=target,verdict='UNKNOWN')
        if consecutive>=2:row['reason']='NOT_RUN after two consecutive final UNKNOWNs'
        else:
            run=run_logged([sys.executable,'tools/s008_cover.py',target['edgefile'],str(prefix),'1200','--lex'],1220,str(prefix)+'.run.log')
            row['run']=run
            meta=Path(str(prefix)+'.result.json')
            if meta.exists():row['search']=json.loads(meta.read_text())
            if run['returncode']==0 and row.get('search',{}).get('verdict')=='UNSAT':
                row['certificate']=certificate(target['edgefile'],prefix);row['verdict']=row['certificate']['verdict']
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
    launch(sys.argv[1]);{'replay':replay,'controls':controls,'search':search}[sys.argv[1]]()
