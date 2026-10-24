"""Preserve frozen S039 replay while checking the D077 owner-revised handoff."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'validation/S039/MANIFEST.json').read_text())
    checker = ROOT/'scripts/check_s039_records.py'
    data = checker.read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest['sha256']['scripts/check_s039_records.py']
    old = "(ROOT/'sessions/S039/S040_FUTURE_PROMPT.md').read_bytes()"
    new = "(ROOT/'sessions/S039/S040_FUTURE_PROMPT_OWNER_REVISION.md').read_bytes()"
    source = data.decode('utf-8')
    assert source.count(old) == 1
    namespace = {'__file__': str(checker), '__name__': 's039_frozen_owner_handoff_replay'}
    exec(compile(source.replace(old, new), str(checker), 'exec'), namespace)
    namespace['main']()
    prompt = (ROOT/'sessions/S039/S040_FUTURE_PROMPT_OWNER_REVISION.md').read_text(encoding='utf-8')
    assert 'D077' in prompt and 'PROGRESS or PIVOT' in prompt
    assert 'at least two genuinely different' in prompt
    assert 'Do not lower the criterion' in prompt
    state = json.loads((ROOT/'authoritative/STATE.json').read_text())
    if state['last_completed_session'] == 'S039':
        queued = state['s040_queued']
        assert queued['status'] == 'FUTURE_UNEXECUTED' and queued['owner_progress_gate'] == 'D077'
        assert queued['archival_copy'] == 'sessions/S039/S040_FUTURE_PROMPT_OWNER_REVISION.md'
        assert queued['original_archival_copy'] == 'sessions/S039/S040_FUTURE_PROMPT.md'
        assert state['current_computation'] == 'STOPPED' and 'active_session' not in state
    print('D077 PASS: frozen S039 intact; revised S040 progress-or-pivot handoff; no session invoked')


if __name__ == '__main__':
    main()
