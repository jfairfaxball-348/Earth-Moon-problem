"""Lossless proof journals: verify restored bytes before removing redundant raw data."""
import gzip
import hashlib
import os
from pathlib import Path
import shutil
from s035_windows import atomic_json

def digest(path, compressed=False):
    h=hashlib.sha256(); size=0
    with (gzip.open(path,'rb') if compressed else Path(path).open('rb')) as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block); size+=len(block)
    return h.hexdigest(),size

def compress_proof(path):
    path=Path(path)
    if not path.exists(): return
    expected=digest(path); target=path.with_suffix(path.suffix+'.gz'); temp=target.with_suffix('.part')
    with path.open('rb') as source, gzip.open(temp,'wb',compresslevel=1) as dest:
        shutil.copyfileobj(source,dest,1024*1024)
    assert digest(temp,True)==expected
    os.replace(temp,target)
    assert digest(target,True)==expected
    receipt=dict(status='LOSSLESS_RESTORATION_VERIFIED', raw_sha256=expected[0],raw_bytes=expected[1],
                 archive=str(target),archive_sha256=digest(target)[0],archive_bytes=target.stat().st_size)
    atomic_json(path.with_suffix('.ARCHIVE.json'),receipt)
    path.unlink()
    return receipt
