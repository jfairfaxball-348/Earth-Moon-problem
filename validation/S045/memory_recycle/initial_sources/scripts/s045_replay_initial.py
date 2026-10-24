"""Replay original S045 evidence against its pinned source and authority bytes."""
import json
from pathlib import Path
import runpy
import sys
import types
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

def main():
    v=ROOT/'validation/S045/watchdog_repair'
    index=json.loads((v/'INITIAL_SOURCES.json').read_text())
    frozen={ROOT/name:(ROOT/row['archive']).read_bytes() for name,row in index['files'].items()}
    text,binary=Path.read_text,Path.read_bytes
    def read_text(self,*a,**kw):
        return frozen[self.resolve()].decode(kw.get('encoding') or 'utf-8') if self.resolve() in frozen else text(self,*a,**kw)
    def read_bytes(self,*a,**kw):
        return frozen[self.resolve()] if self.resolve() in frozen else binary(self,*a,**kw)
    print('INITIAL S045 REPLAY against actual 5d910fb source/authority bytes; repaired run checked separately',flush=True)
    sys.path.insert(0,str(ROOT/'tools'))
    # Execute the original independent verifier, rather than silently importing
    # its operational-cancellation extension in the repaired checkout.
    module=types.ModuleType('s045_verify');module.__file__=str(ROOT/'tools/s045_verify.py')
    exec(compile(frozen[ROOT/'tools/s045_verify.py'],module.__file__,'exec'),module.__dict__)
    sys.modules['s045_verify']=module
    with patch.object(Path,'read_text',read_text),patch.object(Path,'read_bytes',read_bytes):
        runpy.run_path(str(ROOT/'scripts/check_s045_records.py'),run_name='__main__')

if __name__=='__main__':main()
