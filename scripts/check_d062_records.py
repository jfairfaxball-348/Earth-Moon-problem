"""D062 governance audit: frozen S028 checks plus the D062 S029 prompt identity.

D062 replaced the queued S029 prompt while S028 stays the last completed session.
The S028 checker and its S029 prompt copy are hash-pinned in sessions/S028/MANIFEST.json,
so neither is edited. This runs the byte-exact S028 checker with only its prompt-identity
target redirected to the D062 copy. Metadata only; no proof replay or computation.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S028_CHECKER = ROOT / 'scripts/check_s028_records.py'
FROZEN = "(ROOT / 'sessions/S028/S029_FUTURE_PROMPT.md').read_bytes()"
D062 = "(ROOT / 'sessions/S028/S029_FUTURE_PROMPT_D062.md').read_bytes()"

state = json.loads((ROOT / 'authoritative/STATE.json').read_text(encoding='utf-8'))
assert 'd062_owner_decision' in state
assert (ROOT / 'docs/D062_LANDSCAPE_THEN_ALPHA3_DIRECTIVE.md').is_file()
source = S028_CHECKER.read_bytes()
pinned = json.loads((ROOT / 'sessions/S028/MANIFEST.json').read_text())['artifact_sha256']
assert hashlib.sha256(source).hexdigest() == pinned['scripts/check_s028_records.py']['sha256']
text = source.decode()
assert text.count(FROZEN) == 1
exec(compile(text.replace(FROZEN, D062), str(S028_CHECKER), 'exec'), {'__file__': str(S028_CHECKER)})
print('PASS D062: frozen S028 records intact; authoritative S029 prompt identical to sessions/S028/S029_FUTURE_PROMPT_D062.md')
