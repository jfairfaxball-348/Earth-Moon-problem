"""S026 stdlib integrity/metadata audit; never a fresh scientific proof replay."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def read(p):
    return json.loads((ROOT/p).read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


recovered=read('validation/S026/recovered/MANIFEST.json')
for rec in recovered:
    for suffix, item in rec['files'].items():
        data=(ROOT/item['stored_path']).read_bytes()
        assert sha(data)==item['stored_sha256'], item['stored_path']
        raw=gzip.decompress(data) if suffix=='lemmas.json' else data
        assert sha(raw)==item['raw_sha256'], (rec['tag'],suffix)

summary=read('validation/S026/SUMMARY.json')
for item in summary['jobs']:
    d=ROOT/item['directory']
    smoke=json.loads((d/'SMOKE.json').read_text())
    assert smoke['verdict']=='PASS'
    assert (smoke['chromatic_rows_verified'],smoke['chromatic_cnf_byte_matches'])==(271,271)
    assert smoke['k9']['verified'] and smoke['solver_roundtrip']['fresh_proof_verified']
    source=json.loads((d/'SOURCE.json').read_text())
    for name, expected in source['source_sha256'].items():
        data=subprocess.check_output(['git','show',source['source_commit']+':'+name],cwd=ROOT)
        assert sha(data)==expected, (source['source_commit'],name)
    if item.get('certified'):
        r=json.loads((d/'SUMMARY.json').read_text())
        p=r['proof']
        assert r['verdict']=='NONBIPLANAR_CERTIFIED' and p['certified']
        assert p['justification']['returncode']==p['regeneration']['returncode']==0
        assert p['cnf_byte_match']
        c=p['certificate']
        assert c['verdict']=='UNSAT_DRAT_VERIFIED' and c['solver_returncode']==20
        assert 's VERIFIED' in c['checker_tail']
        proof=d/Path(c['drat_gz']).name
        data=proof.read_bytes(); raw=gzip.decompress(data)
        assert sha(data)==c['drat_gz_sha256'] and sha(raw)==c['drat_sha256']
        assert len(raw)==c['drat_bytes']
        assert (d/'lemmas.json.gz').is_file() and (d/'graph.edges').is_file()

state=read('authoritative/STATE.json')
assert state['last_completed_session']=='S026' and state['recommended_next_session']=='S027'
assert state['next_session_is_future_unexecuted'] is True
assert state['original_corpus_status']['certified_nonbiplanar']==271
assert state['original_corpus_status']['biplanarity_unknown']==0
assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S026/S027_FUTURE_PROMPT.md').read_bytes()
manifest=read('sessions/S026/MANIFEST.json')
for name, item in manifest['artifact_sha256'].items():
    data=(ROOT/name).read_bytes()
    assert len(data)==item['bytes'] and sha(data)==item['sha256'],name
print('PASS S026 byte integrity, archived checker receipts, job-local smoke records, source pins, state and identical S027 prompts')
print('Metadata/packaging only: no native proof replay or new mathematical computation')
