"""Verify immutable 673d4a6 watchdog evidence against its exact source context."""
import io,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]

def main():
    index=json.loads((ROOT/'validation/S045/memory_recycle/INITIAL_SOURCES.json').read_text())
    frozen={ROOT/p:(ROOT/row['archive']).read_bytes() for p,row in index['files'].items()}
    original_open=Path.open
    def opened(self,mode='r',*a,**kw):
        data=frozen.get(self.resolve())
        if data is not None and mode in ('r','rt','rb'):
            encoding=kw.get('encoding')
            if encoding in (None,'locale'):encoding='utf-8'
            return io.BytesIO(data) if mode=='rb' else io.StringIO(data.decode(encoding))
        return original_open(self,mode,*a,**kw)
    print('Historical watchdog replay against exact 673d4a6 source/authority context',flush=True)
    with patch.object(Path,'open',opened):runpy.run_path(str(ROOT/'scripts/check_s045_watchdog.py'),run_name='__main__')

if __name__=='__main__':main()
