"""Restore S035 pause evidence into a NEW directory; never launch any worker."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_archive_parts import resolve
from archive_s035_pause import verify,digest

def safe_target(root,name):
    relative=PurePosixPath(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    return root.joinpath(*relative.parts)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    target=args.output.resolve();assert not target.exists(),'Never overwrite a live or previous recovery directory'
    inv=json.loads((ROOT/'validation/S035/pause/RUNTIME_INVENTORY.json').read_text())
    need=sum(v['bytes'] for v in inv['files'].values())+sum(v['bytes'] for v in inv['objects'].values())+2*sum(v['bytes'] for v in inv['external_S034'].values())+10*1024**3
    parent=target.parent
    assert parent.exists() and shutil.disk_usage(parent).free>need,'Insufficient space for full recovery plus10GiB reserve'
    target.mkdir();objects=target/'_verified_objects'
    verify(resolve(ROOT/'validation/S035/pause/runtime.tar.xz'),inv,objects)
    for name,row in inv['files'].items():
        p=safe_target(target/'S035',name);p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(objects/row['sha256'],p)
        assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256']
    external=target/'_S034_original'
    assert digest(ROOT/inv['external_archive'])==inv['external_archive_sha256']
    subprocess.run([sys.executable,str(ROOT/'scripts/restore_s034.py'),'--output',str(external),'--proofs'],check=True)
    for name,row in inv['external_S034'].items():
        p=safe_target(target/'S035',name);p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(safe_target(external,name.removeprefix('imported-s034/')),p)
        assert p.stat().st_size==row['bytes'] and digest(p)==row['sha256']
    print('PASS all restored S035 original file bytes; no process launched. Absolute recipe paths are provenance and need explicit hash-checked rebasing.')
    print('Dependencies: restore validation/S035/pause/dependencies.tar.xz into another new root using DEPENDENCIES.json. Do not run old STOP/recover or remove STOP.')

if __name__=='__main__':main()
