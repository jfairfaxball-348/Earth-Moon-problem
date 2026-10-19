"""Write sessions/S027/MANIFEST.json (byte sizes and SHA-256 of S027 records)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rel(p):
    return p.relative_to(ROOT).as_posix()


files = sorted([rel(p) for p in (ROOT / 'sessions/S027').glob('*') if p.name != 'MANIFEST.json'] +
               ['research/S027_LEARNED_OBSTRUCTIONS.md', 'validation/S027/SUMMARY.json',
                'validation/S027/REPLAY.json', 'validation/S027/local/PACKAGE_MANIFEST.json',
                'campaigns/CAM-0032.md', 'campaigns/CAM-0033.md', 'authoritative/NEXT_SESSION_PROMPT.md'] +
               [rel(p) for p in sorted((ROOT / 'tools').glob('s027_*.py'))] +
               [rel(p) for p in sorted((ROOT / 'scripts').glob('*s027*.py'))])
env = json.loads((ROOT / 'validation/S027/local/ENVIRONMENT.json').read_text())
m = {'session': 'S027', 'entry_main': '4d74c5f276a2a512b2588d3267a5496a7cba134b',
     'environment': {'kind': env['kind'], 'executor': 'Claude Code (Opus 5.5), local owner workstation',
                     'record': 'validation/S027/local/ENVIRONMENT.json',
                     'smoke': 'validation/S027/local/SMOKE.json (PASS 271/271, K9 retained+fresh)',
                     'native_sha256': env['native_sha256']},
     'artifact_sha256': {f: {'bytes': len((ROOT / f).read_bytes()),
                             'sha256': hashlib.sha256((ROOT / f).read_bytes()).hexdigest()} for f in files}}
(ROOT / 'sessions/S027/MANIFEST.json').write_text(json.dumps(m, indent=2) + '\n', newline='\n')
print(len(files), 'files in manifest')
