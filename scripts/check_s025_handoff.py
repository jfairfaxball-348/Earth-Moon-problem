"""Stdlib S025 packaging integrity audit, not a fresh scientific proof check."""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def digest(data):return hashlib.sha256(data).hexdigest()

manifest=read('sessions/S025/MANIFEST.json')
assert manifest['session']=='S025'
for name,expected in manifest['tool_sha256'].items():
    path=ROOT/'tools'/name
    assert digest(path.read_bytes())==expected, str(path)

certificates=read('validation/S025/C5_CERTIFICATES.json')
certified=[r for r in certificates if r.get('certified')]
assert len(certificates)==26 and len(certified)==18
for row in certified:
    prefix=ROOT/'validation/S025/certs'/('C5-'+row['tag'])
    for suffix,key in [('.edges','edges_sha256'),('.drat.gz','drat_gz_sha256'),('.lemmas.json.gz','lemmas_gz_sha256')]:
        assert digest(Path(str(prefix)+suffix).read_bytes())==row[key],(row['tag'],key)
    for suffix,key in [('.drat.gz','drat_sha256'),('.lemmas.json.gz','lemmas_json_sha256')]:
        raw=gzip.decompress(Path(str(prefix)+suffix).read_bytes())
        assert digest(raw)==row[key],(row['tag'],key)
        if suffix=='.drat.gz':assert len(raw)==row['drat_bytes']
    assert row['drat_verdict']=='UNSAT_DRAT_VERIFIED'

transfer=read('validation/S025/TRANSFER_271.json')
assert (transfer['unknown_total'],transfer['unknown_settled'],transfer['unknown_unsettled'])==(219,219,[])
rows=transfer['rows']
assert len(rows)==271 and {r['row'] for r in rows}==set(range(271))
assert all(r['tag'] in {c['tag'] for c in certified} for r in rows)
state=read('authoritative/STATE.json')
assert state['last_completed_session']=='S025' and state['recommended_next_session']=='S026'
assert state['next_session_is_future_unexecuted'] is True
assert state['original_corpus_status']['certified_nonbiplanar']==271
assert state['original_corpus_status']['biplanarity_unknown']==0
assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S025/S026_FUTURE_PROMPT.md').read_bytes()
assert read('validation/S025/SMOKE.json')['verdict']=='PASS'
print('PASS S025 packaging:20 tool digests;18 complete certificate byte chains;271 transfer records;identical S026 prompts')
print('Integrity/metadata only: no new scientific run, native proof replay, or S026 invocation')

if '--staged' in sys.argv:
    package=read('validation/S025/INTEGRATION_MANIFEST.json')
    for name,item in package['artifact_sha256'].items():
        data=subprocess.check_output(['git','show',':'+name],cwd=ROOT)
        assert len(data)==item['bytes'] and digest(data)==item['sha256'],name
        assert data==(ROOT/name).read_bytes(),name
    data=subprocess.check_output(['git','show',':validation/S025/INTEGRATION_MANIFEST.json'],cwd=ROOT)
    assert data==(ROOT/'validation/S025/INTEGRATION_MANIFEST.json').read_bytes()
    print('PASS exact staged integration artifact hashes and manifest bytes')
