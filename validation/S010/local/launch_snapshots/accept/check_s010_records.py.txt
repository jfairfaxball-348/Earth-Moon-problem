"""Independent stdlib audit of S010 labels, sphere certificates and scoped records."""
import gzip, hashlib, json
from pathlib import Path
from check_rotation import check
ROOT=Path('validation/S010')

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

assert load(ROOT/'BASELINE_PASS.json')['direct_row_proofs']==48
cold=load(ROOT/'cold_replay.json');assert len(cold)==50 and len({r['tag'] for r in cold})==50
for r in cold:
    assert r['verdict']=='VERIFIED' and r['command']['returncode']==0 and r['regenerate']['returncode']==0
    assert 's VERIFIED' in (ROOT/(r['tag']+'.check.log')).read_text()
    assert sha(r['archive'])==r['archive_sha256']
    assert hashlib.sha256(gzip.decompress(Path(r['archive']).read_bytes())).hexdigest()==r['archive_raw_sha256']
chi=load(ROOT/'chromatic_cold_replay.json');assert [r['index'] for r in chi]==list(range(271))
for r in chi:
    assert r['verdict']=='EXACT_CHI10' and r['command']['returncode']==0
    assert 's VERIFIED' in (ROOT/f"chi-{r['index']:03d}.check.log").read_text()
det=load(ROOT/'bipartite_detector.json');assert len(det['rows'])==813 and not det['maps']
assert det['allocation_cases']==977231 and det['comparisons']==4096
local=load(ROOT/'local/results.json');assert len(local)==2
for r in local:
    size=4 if r['tag']=='P4-I9' else 5;n=size+9
    expected={(a,a+1) for a in range(size-1)}|{(u,v) for u in range(size) for v in range(size,n)}
    if size==5:expected.add((0,4))
    parts=[{tuple(sorted(e)) for e in r['split'][key]} for key in ('E1','E2')]
    assert not parts[0]&parts[1] and parts[0]|parts[1]==expected
    actual={tuple(map(int,line.split())) for line in Path(r['edgefile']).read_text().splitlines()}
    assert actual==expected and sha(r['edgefile'])==r['edge_sha256']
    assert r['V']==list(range(n)) and r['n']==n and r['m']==len(expected)
    col=r['proper_colouring'];assert len(col)==n and all(0<=x<r['chi'] for x in col) and all(col[a]!=col[b] for a,b in expected)
    assert r['chi']==(3 if size==4 else 4) and r['verdict']=='BIPLANAR_EXACT_CHI'+str(r['chi'])
    for edges,comps in zip(parts,r['rotations']):
        covered=set()
        for c in comps:
            if 'isolated' in c:
                covered.update(c['isolated']);assert not any(v in e for v in c['isolated'] for e in edges);continue
            labels=c['labels'];assert not covered&set(labels);covered.update(labels);rel={v:i for i,v in enumerate(labels)}
            subset=[tuple(sorted((rel[a],rel[b]))) for a,b in edges if a in rel]
            assert all((a in rel)==(b in rel) for a,b in edges)
            assert check(len(labels),subset,c['rotation'])==c['independent_sphere']
        assert covered==set(range(n))
    pack=r['cnf_package']
    assert pack['grade']=='PARTIAL_NECESSARY_CNF_NOT_A_REFUTATION'  # positive CNF is never a refutation
    assert sha(pack['archive'])==pack['archive_sha256']
    assert hashlib.sha256(gzip.decompress(Path(pack['archive']).read_bytes())).hexdigest()==pack['raw_sha256']
assert load(ROOT/'safe_pair_audit.json')['pair_assignment_cases']==112640
assert load(ROOT/'upper_controls.json')['instances']==2692
for name in ('baseline_v3','detector','upper','safe_pair','chromatic'):
    assert load(ROOT/(name+'_command.json'))['returncode']==0
for name in ('controls','search','accept'):
    assert load(ROOT/'local'/(name+'_command.json'))['returncode']==0
# Failed setup attempts explicitly preserved, not substituted by corrected successful launch.
assert load(ROOT/'baseline_command.json')['returncode']==1 and load(ROOT/'baseline_v2_command.json')['returncode']==1
sources=load('catalogue/SOURCES.json');claims=load('catalogue/CLAIMS.json')
for stem,data,field in [('SOURCES',sources,'access'),('CLAIMS',claims,'status')]:
    md=Path('catalogue',stem+'.md').read_text(encoding='utf-8')
    for r in data:assert f"## {r['id']} — {r[field]}" in md
summary=load(ROOT/'SUMMARY.json');assert summary['remaining_unknown_indices']==load('validation/S009/SUMMARY.json')['remaining_unknown_indices']
assert summary['S010_new_exclusions']==[] and summary['headline_bounds']==[9,12]
Path(ROOT/'INDEPENDENT_RECORD_AUDIT_PASS.json').write_text(json.dumps(dict(verdict='PASS',cold_proofs=50,chromatic_proofs=271,
    independent_label_sphere_local_positives=2,detector_source_row_pairs=813,headline_advance=False),indent=1)+'\n',newline='\n')
print('PASS independent S010 proof/archive/label/rotation/colour/status/paired-catalogue records')
