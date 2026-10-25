"""Check live governance amendment separately from frozen S045 science."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    state = json.loads((ROOT / 'authoritative/STATE.json').read_text())
    old = json.loads((ROOT / 'validation/D078/s045_context/authoritative/STATE.json').read_text())
    assert state['last_completed_session'] == 'S045'
    assert state['recommended_next_session'] == 'S046'
    assert state['next_session_is_future_unexecuted'] and not state.get('active_session')
    assert state['s045_result'] == old['s045_result']
    assert state['s036_closeout'] == old['s036_closeout']
    assert state['s046_queued']['status'] == 'FUTURE_UNEXECUTED'
    assert state['s046_queued']['directive'] == 'D078'
    assert state['s046_queued']['pilot_orders'] == [24, 28, 32, 40, 50]
    prompt = (ROOT / 'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()
    assert prompt == (ROOT / 'sessions/S045/S046_FUTURE_PROMPT.md').read_bytes()
    receipt = json.loads((ROOT / 'validation/D078/HANDOFF.json').read_text())
    assert receipt['status'] == 'GOVERNANCE_ONLY_S046_FUTURE_UNEXECUTED'
    assert not receipt['scientific_computation_started']
    assert hashlib.sha256(prompt).hexdigest() == receipt['prompt_sha256']
    for path, digest in receipt['sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    # All changes to old manifest-covered bytes must have an exact original copy.
    index = json.loads((ROOT / 'validation/D078/S045_CONTEXT.json').read_text())
    manifest = json.loads((ROOT / 'validation/S045/final/MANIFEST.json').read_text())
    for path, digest in manifest['sha256'].items():
        if path in index['files']:
            item = index['files'][path]
            assert digest == item['sha256']
            data = (ROOT / item['archive']).read_bytes()
        else:
            data = (ROOT / path).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, path
    print('D078 PASS: mirrored target-selection prompt; S046 unexecuted; S045 evidence preserved')

if __name__ == '__main__':
    main()
