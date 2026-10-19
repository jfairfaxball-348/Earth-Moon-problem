"""Run frozen S029 checker, resolving its outgoing live prompt to its archive.

The frozen checker/manifest are unmodified. Only the superseded live path
inside its manifest loop is redirected after S029, as in the D062 adapter.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'scripts/check_s029_records.py'
data=path.read_bytes()
pin=json.loads((ROOT/'sessions/S029/MANIFEST.json').read_text())['artifact_sha256']['scripts/check_s029_records.py']
assert len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256']
text=data.decode()
needle="    assert len((ROOT / name).read_bytes()) == item['bytes'] and sha(name) == item['sha256'], name"
assert text.count(needle)==1
replacement="    if name == 'authoritative/NEXT_SESSION_PROMPT.md' and state['last_completed_session'] != 'S029':\n        name = 'sessions/S029/S030_FUTURE_PROMPT.md'\n"+needle
exec(compile(text.replace(needle,replacement),str(path),'exec'),{'__file__':str(path)})
print('PASS S030 history adapter: frozen S029 checker intact; superseded prompt resolves to its byte-identical archive')
