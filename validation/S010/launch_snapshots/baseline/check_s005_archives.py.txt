#!/usr/bin/env python3
"""S005 cold packaging check: inputs, regenerated CNFs, proof hashes, maps.

Does not replace DRAT checking; actual independent checker logs are separate.
"""
import gzip
import hashlib
import json
from pathlib import Path

from blowup_graph import blowup
from biplanar_cnf import read_edges
from dense_face_cnf import encode as dense
from deficit_one_cnf import encode as one
from independent_cover_search import Independent
from triangulation_cover import Cover
from s004_certify import write_cnf


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def raw_archive(path,expected,bytes_expected=None):
    raw=gzip.decompress(Path(path).read_bytes())
    assert digest(raw)==expected,(path,'hash mismatch')
    if bytes_expected is not None:
        assert len(raw)==bytes_expected
    return raw


def cnf_bytes(nv,cls):
    return (f'p cnf {nv} {len(cls)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in cls)).encode()


def cover_certificate(edgefile,archive_prefix,record,independent=False):
    data=json.loads(Path(str(archive_prefix)+'.cuts.json').read_text())
    if independent:
        c=Independent(read_edges(edgefile),data['cuts'])
    else:
        c=Cover(read_edges(edgefile),data['lex'],data.get('short_links',False))
        c.cuts=data['cuts']
    scratch=Path('artifacts/tmp/S005/cold')
    scratch.mkdir(parents=True,exist_ok=True)
    regen=scratch/(Path(archive_prefix).name+'.cnf')
    c.cnf(str(regen)) if independent else c.write_cnf(regen)
    stored=gzip.decompress(Path(str(archive_prefix)+'.cnf.gz').read_bytes())
    assert stored==regen.read_bytes()
    assert digest(stored)==record['cnf_sha256']
    assert digest(Path(record['archive']).read_bytes())==record['archive_sha256']
    raw_archive(record['archive'],record['archive_raw_sha256'],record['archive_raw_bytes'])
    log=Path(str(archive_prefix)+'.core.check.log')
    if not log.exists():
        log=Path(str(archive_prefix)+'.check.log')
    assert 's VERIFIED' in log.read_text()


def main():
    source=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    results=json.loads(Path('validation/S005/search_results.json').read_text())
    seen=set();certified=set()
    for row in results:
        target=row['target'];idx=target['index']
        assert idx not in seen;seen.add(idx)
        g6,w,_=source[idx]
        assert g6==target['g6'] and w==target['w']
        edges,_=blowup(g6,w)
        assert read_edges(target['edgefile'])==edges
        assert target['n']==sum(w) and target['m']==len(edges)
        assert target['D']==6*sum(w)-12-len(edges)
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
            cover_certificate(target['edgefile'],f'validation/S005/search/cover-row{idx}',row['certificate'])
            certified.add(idx)
    zero={i for i,(g,w,_) in enumerate(source) if 6*sum(w)-12-len(blowup(g,w)[0])==0}
    assert len(zero)==17 and zero<=certified
    d=json.loads(Path('validation/S005/independent_row120.json').read_text())
    assert d['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
    cover_certificate('validation/S005/targets/row120.edges','validation/S005/search/no-lex-row120',d['certificate'],True)
    for recordfile,encoder,mode in (('validation/S005/dense/results.json',dense,'dense'),
                                    ('validation/S005/deficit_one/results.json',one,'one')):
        for row in json.loads(Path(recordfile).read_text()):
            if row['verdict']!='NON_BIPLANAR_DRAT_VERIFIED':
                continue
            edgefile=f"validation/S005/targets/row{row['index']}.edges"
            args=[read_edges(edgefile)]
            if mode=='dense':
                args.append(row['mode']=='global')
            nv,cls,*_=encoder(*args)
            assert digest(cnf_bytes(nv,cls))==row['cnf_sha256']
            assert digest(Path(row['archive']).read_bytes())==row['archive_sha256']
            raw_archive(row['archive'],row.get('archived_raw_sha256',row['proof_sha256']),
                        row.get('archived_raw_bytes',row['proof_bytes']))
    for recordfile in ('validation/S005/general_transfers.json','validation/S005/bag_transfers.json'):
        data=json.loads(Path(recordfile).read_text())
        for row in data['results']:
            if row['verdict']!='NON_BIPLANAR_BY_CHECKED_SUBGRAPH':
                continue
            obidx=row.get('obstruction_index',data.get('obstruction_source_index'))
            assert obidx==165 or obidx in certified
            edges,_=blowup(source[obidx][0],source[obidx][1])
            tg,tw,_=source[row['index']]
            target=set(blowup(tg,tw)[0]);mp=row['vertex_map']
            assert len(mp)==len(set(mp))==sum(source[obidx][1])
            assert all(type(v) is int and 0<=v<sum(tw) for v in mp)
            assert all(tuple(sorted((mp[a],mp[b]))) in target for a,b in edges)
    small=json.loads(Path('validation/S005/small_result.json').read_text())
    if small['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
        cover_certificate('validation/S005/targets/small-row158.edges','validation/S005/search/small-row158',small['certificate'])
        graph=set(blowup(small['target']['g6'],small['target']['w'])[0])
        transfers=json.loads(Path('validation/S005/small_transfers.json').read_text())
        for row in transfers['results']:
            if row['verdict']=='UNKNOWN':
                continue
            mp=row['vertex_map'];g,w,_=source[row['index']]
            target=set(blowup(g,w)[0])
            assert len(mp)==len(set(mp))==small['target']['n']
            assert all(0<=v<sum(w) for v in mp)
            assert all(tuple(sorted((mp[a],mp[b]))) in target for a,b in graph)
    print('PASS S005 archived proof hashes, regenerated CNFs, all 17 D=0 rows, checked transfer maps;',len(certified),'full exclusions')


if __name__=='__main__':
    main()
