"""Independent exact local labels, cold tree CNF and archive audit."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
from s008_tree import TreeFullCover
from biplanar_cnf import read_edges
from check_layers import certify_layer
from s005_search import compress
from s005_replay import sha
from s007_run import save

root=Path('validation/S008/heavy_tree');tmp=Path('artifacts/tmp/S008/heavy_tree')
row=json.loads((root/'result.json').read_text());es=read_edges(row['edgefile'])
assert es==sorted(set(itertools.combinations(range(7),2))|{(a,b) for a in range(7) for b in range(7,12)})
assert row['edge_sha256']==sha(row['edgefile']) and (row['n'],row['m'],row['D'])==(12,56,4)
prefix=tmp/'K7-I5';d=json.loads((root/'K7-I5.cuts.json').read_text())
c=TreeFullCover(es,d['lex'],d.get('short_links',False));assert c.static==d['static'];c.cuts=d['cuts']
regen=tmp/'K7-I5.audit.cnf';c.write_cnf(regen)
c.cuts=[];initial=tmp/'K7-I5.initial.audit.cnf';c.write_cnf(initial)
assert initial.read_bytes()==Path(str(prefix)+'.initial.cnf').read_bytes()
if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
    rec=row['certificate'];archive=root/'search/K7-I5.cnf.gz'
    assert regen.read_bytes()==gzip.decompress(archive.read_bytes()) and sha(regen)==rec['cnf_sha256']
    raw=gzip.decompress(Path(rec['archive']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==rec['archive_raw_sha256'] and sha(rec['archive'])==rec['archive_sha256']
    assert rec['cold_retained_check']['returncode']==0 and 's VERIFIED' in (root/'search/K7-I5.cold.check.log').read_text()
else:
    assert row['verdict'] in ('UNKNOWN','BIPLANAR_CHECKED_CHI8')
    archive=root/'K7-I5.partial.cnf.gz';compress(regen,archive)
    native=Path(str(prefix)+'.drat')
    if row['verdict']=='UNKNOWN' and native.exists():
        row['unverified_native_export']=dict(path=str(native.resolve()),sha256=sha(native),bytes=native.stat().st_size,
            grade='POST_WORKER_CAPTURE_UNVERIFIED_EXPORT_NOT_AN_EXCLUSION')
        save(root/'result.json',row)
if row['verdict']=='BIPLANAR_CHECKED_CHI8':
    split=row['split'];a=set(map(tuple,split['E1']));b=set(map(tuple,split['E2']))
    assert not a&b and a|b==set(es)
    assert all(row['proper_colouring'][u]!=row['proper_colouring'][v] for u,v in es)
    assert set(itertools.combinations(row['clique_lower'],2))<=set(es)
    for k in ('E1','E2'):certify_layer(12,split[k])
initial_archive=archive if sha(initial)==sha(regen) else root/'K7-I5.initial.cnf.gz'
if initial_archive!=archive:compress(initial,initial_archive)
save(root/'archive_audit.json',dict(verdict=row['verdict'],raw_sha256=sha(regen),archive=str(archive),
    archive_sha256=sha(archive),initial_raw_sha256=sha(initial),initial_archive=str(initial_archive),
    initial_archive_sha256=sha(initial_archive),cuts=len(d['cuts']),static=d['static']))
print('PASS exact heavy graph/cold tree CNF/archives;',row['verdict'])
