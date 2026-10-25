"""Replay frozen pre-S046 checks against the exact S046 entry authority bytes.

S046 appends to ledgers and replaces live authority files that the frozen
S045 final manifest and the D078 handoff receipt hash. Their exact entry bytes
(commit 5f56fdf) are archived under validation/S046/entry_context with hashes
in validation/S046/ENTRY_CONTEXT.json. Only reads of those paths are served
from the archive; every other file, certificate and archive is read live. No
historical checker, receipt or manifest is modified or weakened.
"""
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'scripts/s045_replay_final.py', 'scripts/check_d078_handoff.py'}


def main():
    target = sys.argv[1].replace('\\', '/')
    assert target in ALLOWED, target
    index = json.loads((ROOT / 'validation/S046/ENTRY_CONTEXT.json').read_text())
    assert index['entry_commit'] == '5f56fdf14b88eef9b77f549679c35a1e59a5b106'
    frozen = {}
    for path, item in index['files'].items():
        data = (ROOT / item['archive']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256'], path
        frozen[(ROOT / path).resolve()] = data
    original = Path.open

    def opened(self, mode='r', *args, **kwargs):
        data = frozen.get(self.resolve())
        if data is not None and mode in ('r', 'rt', 'rb'):
            encoding = kwargs.get('encoding')
            encoding = 'utf-8' if encoding in (None, 'locale') else encoding
            return io.BytesIO(data) if mode == 'rb' else io.StringIO(data.decode(encoding))
        return original(self, mode, *args, **kwargs)

    print(f'HISTORICAL REPLAY of {target} against exact S046 entry authority (5f56fdf); live S046 checked separately',
          flush=True)
    with patch.object(Path, 'open', opened):
        sys.argv = [str(ROOT / target)]
        runpy.run_path(str(ROOT / target), run_name='__main__')


if __name__ == '__main__':
    main()
