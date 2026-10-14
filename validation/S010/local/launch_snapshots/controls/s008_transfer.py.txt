"""CAM-0009B distinct-bag transfers, independently checked at vertex labels."""
import gzip
import itertools
import json
import sys
from pathlib import Path
import networkx as nx
from blowup_graph import blowup
from blowup_chi_cnf import bag_cnf
from s004_certify import write_cnf
from s005_search import run_logged
from s005_replay import sha
from s007_run import save

ROOT=Path('validation/S008');TMP=Path('artifacts/tmp/S008/transfer')


def search():
    full=json.loads((ROOT/'tree/search_results.json').read_text())
    row=next(r for r in full if r['target']['index']==157)
    assert row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
    cert=row['certificate']
    assert cert['check']['returncode']==cert['core_check']['returncode']==cert['cold_retained_check']['returncode']==0
    assert sha(cert['archive'])==cert['archive_sha256']
    proof=TMP/'source.drat';proof.write_bytes(gzip.decompress(Path(cert['archive']).read_bytes()))
    assert sha(proof)==cert['archive_raw_sha256']
    original=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    g,w,_=original[157];source,source_bags=blowup(g,w);base=nx.from_graph6_bytes(g.encode())
    attempts=[];maps=[];permutation_count=0
    for idx,(g2,w2,_) in enumerate(original):
        target,target_bags=blowup(g2,w2)
        rec=dict(index=idx,scope='Distinct eight-bag injections only',permutations=0,verdict='NO_MAP_IN_REGISTERED_FAMILY')
        if len(w2)==8 and sum(w2)>=sum(w) and len(target)>=len(source):
            other=nx.from_graph6_bytes(g2.encode())
            for p in itertools.permutations(range(8)):
                permutation_count+=1;rec['permutations']+=1
                if not all(w[i]<=w2[p[i]] for i in range(8)):continue
                if not all(other.has_edge(p[a],p[b]) for a,b in base.edges()):continue
                injection={v:target_bags[p[i]][j] for i,bag in enumerate(source_bags) for j,v in enumerate(bag)}
                assert len(set(injection.values()))==len(injection)==sum(w)
                eset=set(target)
                assert all(tuple(sorted((injection[a],injection[b]))) in eset for a,b in source)
                rec.update(verdict='INJECTIVE_CONTAINMENT_CHECKED',bag_permutation=p,vertex_map=injection)
                maps.append(idx);break
        attempts.append(rec);save(ROOT/'transfer_search.json',dict(source=157,attempts=attempts,mapped=maps,total_permutations=permutation_count))
    print('PASS271 registered transfer targets;',permutation_count,'permutations;',maps,'checked maps',flush=True)


def certify():
    result=json.loads((ROOT/'transfer_search.json').read_text());assert len(result['attempts'])==271
    known=set(json.loads(Path('validation/S007/SUMMARY.json').read_text())['excluded_indices'])
    for file in (ROOT/'search_results.json',ROOT/'tree/search_results.json'):
        known|={r['target']['index'] for r in json.loads(file.read_text()) if r['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'}
    chi=json.loads(Path('validation/S004/chi10_results.json').read_text())
    corpus=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text());rows=[];failures=0
    checker=str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
    for idx in result['mapped']:
        if idx in known:continue
        row=dict(index=idx,verdict='UNKNOWN')
        if failures>=2:row['reason']='NOT_RUN after two consecutive native check failures'
        else:
            g,w,_=corpus[idx];es,_=blowup(g,w);upper=chi[idx]['ten_colouring']
            assert len(upper)==sum(w) and all(0<=x<10 for x in upper) and all(upper[a]!=upper[b] for a,b in es)
            cnf=TMP/f'row{idx}.cnf';proof=TMP/f'row{idx}.drat'
            write_cnf(cnf,*bag_cnf(g,w,9));proof.write_bytes(gzip.decompress(Path(chi[idx]['bag']['archive']).read_bytes()))
            assert sha(cnf)==chi[idx]['bag']['cnf_sha256'] and sha(proof)==chi[idx]['bag']['drat_sha256']
            log=ROOT/f'transfer-chi-row{idx}.check.log'
            run=run_logged([checker,str(cnf),str(proof),'-t','600'],620,log)
            row.update(chromatic_check=run,cnf_sha256=sha(cnf),proof_sha256=sha(proof),ten_colouring=upper)
            if run['returncode']==0 and 's VERIFIED' in log.read_text():row['verdict']='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'
            failures=failures+1 if row['verdict']=='UNKNOWN' else 0
        rows.append(row);save(ROOT/'transfers.json',rows)
    if not rows:save(ROOT/'transfers.json',[])
    print('New accepted transfer rows',[r['index'] for r in rows if r['verdict']=='NON_BIPLANAR_INJECTIVE_TRANSFER_VERIFIED'])


if __name__=='__main__':
    TMP.mkdir(parents=True,exist_ok=True)
    if '--search-child' in sys.argv:search()
    else:
        save(ROOT/'transfer_launch_hashes.json',{p:sha(p) for p in (
            'tools/s008_transfer.py','tools/blowup_graph.py','tools/blowup_chi_cnf.py',
            'validation/S003/survivors_alpha_ge3.json','artifacts/tmp/S004/drat-trim-mingw.exe')})
        run=run_logged([sys.executable,'tools/s008_transfer.py','--search-child'],320,ROOT/'transfer_search.log')
        save(ROOT/'transfer_search_command.json',run)
        assert run['returncode']==0
        certify()
