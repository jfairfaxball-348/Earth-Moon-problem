"""Write validation/S046/MANIFEST.json (sha256 of every S046 deliverable except itself)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    paths = sorted(
        [p for p in (ROOT / 'sessions/S046').rglob('*') if p.is_file()] +
        [p for p in (ROOT / 'validation/S046').rglob('*') if p.is_file() and p.name != 'MANIFEST.json'] +
        sorted((ROOT / 'tools').glob('s046_*.py')) + sorted((ROOT / 'scripts').glob('*s046*.py')) +
        [ROOT / 'campaigns/CAM-0050.md'])
    data = dict(session='S046', scope='byte hashes of S046 deliverables; checked by scripts/check_s046_records.py',
                sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (ROOT / 'validation/S046/MANIFEST.json').write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(len(data['sha256']), 'files sealed')


if __name__ == '__main__':
    main()
