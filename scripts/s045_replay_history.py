"""Replay immutable historical checks against the real pinned entry authority.

Only STATE.json and NEXT_SESSION_PROMPT.md reads see the archived entry bytes.
This explicitly tests historical evidence, not live S045 process state. The
separate check_s045_records.py validates current authority and launch evidence.
No historical file is changed or its manifest weakened.
"""
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

def main():
    target=ROOT/sys.argv[1]
    assert target.parent==ROOT/'scripts' and target.name.startswith('check_')
    assert target.name!='check_d072_active_prompt.py','D072 manages its own temporary prompt and restoration'
    frozen={
      ROOT/'authoritative/STATE.json':(ROOT/'validation/S045/ENTRY_STATE.json').read_bytes(),
      ROOT/'authoritative/NEXT_SESSION_PROMPT.md':(ROOT/'sessions/S044/S045_FUTURE_PROMPT.md').read_bytes()}
    read_text,read_bytes=Path.read_text,Path.read_bytes
    def text(self,*a,**kw):
        return frozen[self.resolve()].decode(kw.get('encoding') or 'utf-8') if self.resolve() in frozen else read_text(self,*a,**kw)
    def binary(self,*a,**kw):
        return frozen[self.resolve()] if self.resolve() in frozen else read_bytes(self,*a,**kw)
    print('HISTORICAL REPLAY against pinned S044 entry state; live S045 checked separately',flush=True)
    with patch.object(Path,'read_text',text),patch.object(Path,'read_bytes',binary):
        sys.argv=[str(target)];runpy.run_path(str(target),run_name='__main__')

if __name__=='__main__':main()
