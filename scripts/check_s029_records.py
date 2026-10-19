"""S029 governance audit: frozen landscape hash, S030 prompt identity, executed prompt. Metadata only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


freeze = json.loads((ROOT / 'validation/S029/LANDSCAPE_FREEZE.json').read_text())
assert sha(freeze['landscape_file']) == freeze['landscape_sha256']
assert sha('sessions/S029/EXECUTED_PROMPT.md') == sha('sessions/S028/S029_FUTURE_PROMPT_D062.md')
state = json.loads((ROOT / 'authoritative/STATE.json').read_text(encoding='utf-8'))
if state['last_completed_session'] == 'S029':
    assert state['recommended_next_session'] == 'S030'
    assert (ROOT / 'authoritative/NEXT_SESSION_PROMPT.md').read_bytes() == \
        (ROOT / 'sessions/S029/S030_FUTURE_PROMPT.md').read_bytes()
ids = {s['id'] for s in json.loads((ROOT / 'catalogue/SOURCES.json').read_text())}
assert set(freeze['sources']) <= ids
for name, item in json.loads((ROOT / 'sessions/S029/MANIFEST.json').read_text())['artifact_sha256'].items():
    assert len((ROOT / name).read_bytes()) == item['bytes'] and sha(name) == item['sha256'], name
print('PASS S029: frozen landscape hash, executed D062 prompt, identical S030 prompts, manifest')
