"""Replay frozen S045 closeout against its original authority/workflow bytes."""
import hashlib
import io
import json
import runpy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def main():
    index = json.loads((ROOT / 'validation/D078/S045_CONTEXT.json').read_text())
    assert index['commit'] == 'a55d0d00ce5eb620df941ee19650e3a2d804639e'
    manifest = json.loads((ROOT / 'validation/S045/final/MANIFEST.json').read_text())
    frozen = {}
    for path, item in index['files'].items():
        data = (ROOT / item['archive']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256'] == manifest['sha256'][path]
        frozen[(ROOT / path).resolve()] = data
    original = Path.open

    def opened(self, mode='r', *args, **kwargs):
        data = frozen.get(self.resolve())
        if data is not None and mode in ('r', 'rt', 'rb'):
            encoding = kwargs.get('encoding')
            encoding = 'utf-8' if encoding in (None, 'locale') else encoding
            return io.BytesIO(data) if mode == 'rb' else io.StringIO(data.decode(encoding))
        return original(self, mode, *args, **kwargs)

    print('Historical S045 final replay against exact a55d0d0 authority context', flush=True)
    with patch.object(Path, 'open', opened):
        runpy.run_path(str(ROOT / 'scripts/check_s045_final.py'), run_name='__main__')

if __name__ == '__main__':
    main()
