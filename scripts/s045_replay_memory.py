"""Replay the memory-recovery receipt against its exact pre-closeout context."""
import io,json,runpy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def main():
    index=json.loads((ROOT/'validation/S045/final/INITIAL_SOURCES.json').read_text())
    frozen={ROOT/p:(ROOT/v['archive']).read_bytes() for p,v in index['files'].items()}
    original=Path.open
    def opened(self,mode='r',*args,**kw):
        data=frozen.get(self.resolve())
        if data is not None and mode in ('r','rt','rb'):
            enc=kw.get('encoding');enc='utf-8' if enc in (None,'locale') else enc
            return io.BytesIO(data) if mode=='rb' else io.StringIO(data.decode(enc))
        return original(self,mode,*args,**kw)
    print('Historical memory-recovery replay against exact 307399a source/authority context',flush=True)
    with patch.object(Path,'open',opened):runpy.run_path(str(ROOT/'scripts/check_s045_memory.py'),run_name='__main__')
if __name__=='__main__':main()
