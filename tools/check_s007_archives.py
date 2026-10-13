#!/usr/bin/env python3
"""CAM-0008 packaging/labels and direct SAT-model semantic audit; not external review."""
import collections
import gzip
import hashlib
import itertools
import json
import sys
from pathlib import Path
from s007_run import ROOT,TMP,save
from s007_cover import StrongCover
from s007_global import encode
from s005_replay import sha
from s005_search import compress
from s004_certify import write_cnf
from blowup_graph import blowup
from biplanar_cnf import read_edges
from check_layers import certify_layer


def globals_audit():
    rows=json.loads((ROOT/'global_results.json').read_text());audit=[]
    for row in rows:
        idx=row['index'];ef=row['edgefile'];edges=read_edges(ef)
        nv,cls,f,bits=encode(edges);regen=TMP/'global'/f'row{idx}.audit.cnf'
        write_cnf(regen,nv,cls);assert sha(regen)==row['cnf_sha256']
        if row['verdict']=='SAT_RELAXATION':
            log=ROOT/'global'/f'row{idx}.solve.log'
            model={int(x) for line in log.read_text().splitlines() if line.startswith('v ') for x in line[2:].split() if x!='0'}
            assert all(v in model or -v in model for v in range(1,nv+1))
            assert not any(-v in model for v in model)
            assert all(any(v in model for v in clause) for clause in cls)
            selected=[q for q,v in f.items() if v in model]
            occurrences={e:1+int(values[0] in model) if e in set(edges)
                else sum(v in model for v in values) for e,values in bits.items()}
            # Direct counts independent of cardinality-clause interpretation.
            incidence=collections.Counter(e for q in selected for e in itertools.combinations(q,2))
            assert all(incidence[e]==2*occ for e,occ in occurrences.items())
            assert all(occurrences[e]>=1 for e in edges)
            assert sum(occurrences.values())-len(edges)==2
            n=1+max(max(e) for e in edges);assert len(selected)==4*n-8
            compress(regen,ROOT/'global'/f'row{idx}.cnf.gz')
            projection=dict(index=idx,n=n,input_edges=edges,selected_faces=selected,
                pair_occurrences=[dict(pair=e,multiplicity=occ) for e,occ in occurrences.items() if occ],
                scope='Necessary global incidence only; no layer consistency/planarity',
                native_all_clause_check='PASS',direct_incidence_count_check='PASS',
                cnf_sha256=sha(regen),cnf_archive_sha256=sha(ROOT/'global'/f'row{idx}.cnf.gz'),
                model_log_sha256=sha(log))
            save(ROOT/'global'/f'row{idx}.model.json',projection);audit.append(dict(index=idx,verdict='SAT_RELAXATION_DIRECTLY_CHECKED'))
        elif row['verdict']=='UNKNOWN':
            audit.append(dict(index=idx,verdict='UNKNOWN'))
        else:
            assert row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
            proof=gzip.decompress(Path(row['archive']).read_bytes())
            assert hashlib.sha256(proof).hexdigest()==row['archive_raw_sha256']
            assert len(proof)==row['archive_raw_bytes'] and sha(row['archive'])==row['archive_sha256']
            assert 's VERIFIED' in (ROOT/'global'/f'row{idx}.check.log').read_text()
            audit.append(dict(index=idx,verdict='NON_BIPLANAR_DRAT_VERIFIED'))
    save(ROOT/'global_model_audit.json',audit)
    print('PASS global cold CNFs, every SAT clause and direct projected multiplicities',flush=True)


def full_audit():
    src=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    rows=json.loads((ROOT/'search_results.json').read_text());excluded=set()
    for row in rows:
        t=row['target'];idx=t['index'];g,w,_=src[idx];edges,_=blowup(g,w)
        assert t['g6']==g and t['w']==w and read_edges(t['edgefile'])==edges
        assert sha(t['edgefile'])==t['edge_sha256']
        assert t['n']==sum(w) and t['m']==len(edges) and t['D']==2
        assert len(t['ten_colouring'])==sum(w) and all(t['ten_colouring'][a]!=t['ten_colouring'][b] for a,b in edges)
        assert 's VERIFIED' in (ROOT/f'chi-row{idx}.check.log').read_text()
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
            rec=row['certificate'];p=ROOT/'search'/f'cover-row{idx}'
            cnf=gzip.decompress(Path(str(p)+'.cnf.gz').read_bytes())
            d=json.loads(Path(str(p)+'.cuts.json').read_text())
            c=StrongCover(edges,d['lex'],d.get('short_links',False));assert c.static==d['static'];c.cuts=d['cuts']
            regen=TMP/f'audit-row{idx}.cnf';c.write_cnf(regen)
            assert regen.read_bytes()==cnf and sha(regen)==rec['cnf_sha256']
            proof=gzip.decompress(Path(rec['archive']).read_bytes())
            assert hashlib.sha256(proof).hexdigest()==rec['archive_raw_sha256']
            assert len(proof)==rec['archive_raw_bytes'] and sha(rec['archive'])==rec['archive_sha256']
            suffix='.core.check.log' if rec.get('core_check',{}).get('returncode')==0 else '.check.log'
            assert 's VERIFIED' in Path(str(p)+suffix).read_text()
            excluded.add(idx)
        elif row['verdict']=='UNKNOWN':pass
        else:assert row['verdict']=='BIPLANAR_CHECKED_CHI10',row['verdict']
    prior=json.loads(Path('validation/S006/SUMMARY.json').read_text())
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    globals_rows=json.loads((ROOT/'global_results.json').read_text())
    excluded|={r['index'] for r in globals_rows if r['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'}
    assert s['S007_new_exclusions']==sorted(excluded)
    assert s['excluded_indices']==sorted(set(prior['excluded_indices'])|excluded)
    assert s['remaining_unknown_indices']==sorted(set(range(271))-set(s['excluded_indices']))
    for row in json.loads((ROOT/'heavy_search.json').read_text()):
        if row['verdict']=='BIPLANAR_CONTROL':
            es=set(map(tuple,read_edges(row['edgefile'])));split=row['split']
            e1=set(map(tuple,split['E1']));e2=set(map(tuple,split['E2']))
            assert not e1&e2 and e1|e2==es
            assert all(row['proper_colouring'][a]!=row['proper_colouring'][b] for a,b in es)
            assert row['component_faces']==[certify_layer(row['n'],split[k]) for k in ('E1','E2')]
    heavy=json.loads((ROOT/'heavy_cegar_result.json').read_text())
    if heavy['verdict']=='UNKNOWN':
        pkg=json.loads((ROOT/'heavy_partial_packaging.json').read_text())
        raw=gzip.decompress(Path(pkg['archive']).read_bytes())
        assert len(raw)==pkg['raw_bytes'] and hashlib.sha256(raw).hexdigest()==pkg['raw_sha256']
        assert sha(pkg['archive'])==pkg['archive_sha256']
        data=json.loads(raw);assert len(data['lemmas'])==pkg['lemmas']==heavy['search']['lemmas']
        from biplanar_cegar import Cegar
        c=Cegar(read_edges(str(ROOT/'heavy/K7-I5.edges')))
        assert c.perms==data['perms'];clauses=list(c.base)
        for lemma in data['lemmas']:
            lits=[c.idx[tuple(e)] for e in lemma];clauses.extend([[-v for v in lits],lits])
        regen=TMP/'heavy-cegar/packaging.regenerated.cnf';write_cnf(regen,c.nv,clauses)
        archived=gzip.decompress((ROOT/'heavy-cegar/K7-I5.cnf.gz').read_bytes())
        assert regen.read_bytes()==archived and sha(regen)==heavy['cnf_sha256']
        assert heavy['lemma_check']['returncode']==0 and 'certificate structure PASS' in (ROOT/'heavy-cegar/K7-I5.regen.log').read_text()
    print('PASS exact full-source labels, retained certificates, heavy control and frontier indices')


if __name__=='__main__':
    globals_audit()
    if '--global-only' not in sys.argv:full_audit()
