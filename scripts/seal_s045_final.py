"""Seal final closeout files after all audits and authority updates complete."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'validation/S045/final'
def main():
    for p in V.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.jsonl','.py','.md','.yml','.cpp','.hpp','.log'):
            data=p.read_bytes();normal=data.replace(b'\r\n',b'\n')
            if data!=normal:p.write_bytes(normal)
    changes=subprocess.check_output(['git','diff','HEAD','--name-only','-z'],cwd=ROOT).decode().split('\0')
    changes+=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    paths={p for p in changes if p and (ROOT/p).is_file()}|{p.relative_to(ROOT).as_posix() for p in V.rglob('*') if p.is_file()}
    paths.discard('validation/S045/final/MANIFEST.json')
    data=dict(session='S045',status='CLOSED_OWNER_DEADLINE_UNKNOWN',entry_main='307399a7ce471f722181098a93c8378d5b2f5824',scientific_verdict='UNKNOWN',sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)})
    (V/'MANIFEST.json').write_text(json.dumps(data,indent=1)+'\n',encoding='utf-8',newline='\n')
    print('Final manifest sealed',len(paths),'files')
if __name__=='__main__':main()
