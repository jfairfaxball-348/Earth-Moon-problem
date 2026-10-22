"""Resolve a large committed archive from verified sub-90MiB Git parts."""
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]

def resolve(path):
    path=Path(path)
    if path.exists():return path
    manifest=path.with_name(path.name+'.parts.json')
    if not manifest.exists():return path
    row=json.loads(manifest.read_text());out=ROOT/'artifacts/tmp/S035-restored-archives'/path.relative_to(ROOT)
    if out.exists() and out.stat().st_size==row['bytes']:
        h=hashlib.sha256()
        with out.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        if h.hexdigest()==row['sha256']:return out
    out.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();size=0
    with out.open('wb') as dest:
        for item in row['parts']:
            p=manifest.parent/item['name'];part=hashlib.sha256();n=0
            with p.open('rb') as source:
                for b in iter(lambda:source.read(1024*1024),b''):
                    part.update(b);h.update(b);dest.write(b);size+=len(b);n+=len(b)
            assert n==item['bytes'] and part.hexdigest()==item['sha256'],str(p)
    assert size==row['bytes'] and h.hexdigest()==row['sha256'],str(path)
    return out

def split(path):
    path=Path(path);parts=[];h=hashlib.sha256();size=0
    with path.open('rb') as source:
        while True:
            b=source.read(80*1024*1024)
            if not b:break
            p=path.with_name(path.name+f'.part{len(parts):03d}');p.write_bytes(b)
            parts.append(dict(name=p.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));h.update(b);size+=len(b)
    path.with_name(path.name+'.parts.json').write_text(json.dumps(dict(bytes=size,sha256=h.hexdigest(),parts=parts),indent=1)+'\n')
    return parts
