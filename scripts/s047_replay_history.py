"""Replay frozen pre-S047 checks against the exact S047 entry authority bytes.

S047 (D079) appends to ledgers and replaces live authority files that the
S046 checker and the nested S046 historical replays hash. Their exact entry
bytes (commit 7fb60e1) are archived under validation/S047/entry_context with
hashes in validation/S047/ENTRY_CONTEXT.json. Only reads of those paths are
served from the archive; every other file is read live. No historical
checker, receipt or manifest is modified or weakened. Nested use with
scripts/s046_replay_history.py is supported: its own frozen map is consulted
first, then this one.
"""
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'scripts/check_s046_records.py', 'scripts/s046_replay_history.py'}


def main():
    target = sys.argv[1].replace('\\', '/')
    assert target in ALLOWED, target
    index = json.loads((ROOT / 'validation/S047/ENTRY_CONTEXT.json').read_text())
    assert index['entry_commit'] == '7fb60e1119fed86d61f44b95390ae5311b5a5344'
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

    print(f'HISTORICAL REPLAY of {" ".join(sys.argv[1:])} against exact S047 entry authority (7fb60e1); '
          'live S047 checked separately', flush=True)
    with patch.object(Path, 'open', opened):
        sys.argv = [str(ROOT / target)] + sys.argv[2:]
        runpy.run_path(str(ROOT / target), run_name='__main__')


if __name__ == '__main__':
    main()
