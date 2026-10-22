"""Lossless content-addressed S035 pause archive; never start/stop a solver.

Gzip proofs are stored decoded and rebuilt with their original envelope and
pinned deflate settings. Verification checks BOTH original gzip and raw bytes.
The original pre-upgrade gzip container stays local; every contained file is
also preserved here. Already committed S034 proof bytes are external references.
"""
import argparse
import gzip
import hashlib
import io
import json
import lzma
from pathlib import Path
import sys
import tarfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s035_archive_parts import resolve
AREA = ROOT/'artifacts/tmp/S035'
OUT = ROOT/'validation/S035/pause'
CHUNK = 1024*1024

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(CHUNK),b''):h.update(b)
    return h.hexdigest()

def add(tf,name,data):
    m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o644
    tf.addfile(m,io.BytesIO(data))

def envelope(p):
    with p.open('rb') as f:
        head=f.read(10);assert head[:3]==b'\x1f\x8b\x08'
        flags=head[3]
        if flags&4:
            b=f.read(2);head+=b+f.read(int.from_bytes(b,'little'))
        for flag in (8,16):
            if flags&flag:
                while True:
                    b=f.read(1);head+=b
                    if b==b'\0':break
        if flags&2:head+=f.read(2)
        f.seek(-8,2);tail=f.read()
    return head,tail

def verify(archive,inventory,output=None):
    states={};target=Path(output) if output else None
    if target:assert not target.exists();target.mkdir(parents=True)
    with tarfile.open(archive,'r|xz') as tf:
        for m in tf:
            if m.name=='INVENTORY.json':
                assert json.loads(tf.extractfile(m).read())==inventory;continue
            _,key,offset=m.name.split('/');row=inventory['objects'][key]
            if key not in states:
                st=dict(size=0,raw=hashlib.sha256(),original=hashlib.sha256())
                if row['encoding']=='gzip-deflate-1':
                    st['z']=zlib.compressobj(1,zlib.DEFLATED,-15)
                    st['original'].update(bytes.fromhex(row['header']))
                if target:st['file']=(target/key).open('wb')
                states[key]=st
                if target and row['encoding']=='gzip-deflate-1':st['file'].write(bytes.fromhex(row['header']))
            st=states[key];assert st['size']==int(offset)
            b=tf.extractfile(m).read();st['size']+=len(b);st['raw'].update(b)
            encoded=st['z'].compress(b) if 'z' in st else b
            st['original'].update(encoded)
            if target:st['file'].write(encoded)
    for key,row in inventory['objects'].items():
        st=states[key]
        if 'z' in st:
            end=st['z'].flush()+bytes.fromhex(row['footer']);st['original'].update(end)
            if target:st['file'].write(end)
        if target:st['file'].close()
        assert st['size']==row['decoded_bytes'] and st['raw'].hexdigest()==row['decoded_sha256'],key
        assert st['original'].hexdigest()==key,key
        if target:assert (target/key).stat().st_size==row['bytes']
    assert len(states)==len(inventory['objects'])
    return len(states)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--restore-objects',type=Path)
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    inventory_path=OUT/'RUNTIME_INVENTORY.json';archive=OUT/'runtime.tar.xz'
    if args.verify or args.restore_objects:
        inv=json.loads(inventory_path.read_text());print('PASS restored original object bytes',verify(resolve(archive),inv,args.restore_objects));return
    assert not archive.exists()
    assert (AREA/'campaign/OWNER_PAUSE.json').exists()
    staging=ROOT/'artifacts/tmp/S035-pause-staging';staging.mkdir(exist_ok=True)
    objects={};files={};paths={};external={};locks=[]
    def register(name,p):
        key=digest(p);files[name]=dict(sha256=key,bytes=p.stat().st_size)
        if key not in objects:
            row=dict(bytes=p.stat().st_size,encoding='identity')
            if p.name=='proof.drat.gz':
                head,tail=envelope(p);row.update(encoding='gzip-deflate-1',header=head.hex(),footer=tail.hex())
            objects[key]=row;paths[key]=p
    committed=json.loads((ROOT/'validation/S034/RUNTIME_INVENTORY.json').read_text())
    for p in sorted(AREA.rglob('*')):
        if not p.is_file() or p.name=='pre-resident-runtime.tar.gz':continue
        name=p.relative_to(AREA).as_posix()
        if p.suffix=='.lock':
            locks.append(dict(path=name,bytes=p.stat().st_size,note='Live advisory lock, not evidence; recreate only in a new recovery directory'))
            continue
        if name.startswith('imported-s034/') and p.name=='proof.drat':
            rel=name.removeprefix('imported-s034/');row=committed['files'][rel]
            assert digest(p)==row['sha256'] and p.stat().st_size==row['bytes']
            external[name]=row;continue
        register(name,p)
    print('CURRENT_FILES',len(files),'unique objects',len(objects),flush=True)
    # Preserve the old archive's file contents, including superseded snapshots.
    with tarfile.open(AREA/'pre-resident-runtime.tar.gz','r|gz') as tf:
        for m in tf:
            if not m.isfile():continue
            f=tf.extractfile(m);p=staging/Path(m.name).name
            # Stream to staging instead of keeping a large materialization in RAM.
            with p.open('wb') as dest:
                for b in iter(lambda:f.read(CHUNK),b''):dest.write(b)
            key=digest(p);name='pre-resident-runtime-expanded/'+m.name
            if key in objects:files[name]=dict(sha256=key,bytes=p.stat().st_size);p.unlink()
            else:
                unique=staging/key; p.rename(unique)
                # Keep the gzip transformation decision despite the hashed name.
                register(name,unique)
                if Path(m.name).name=='proof.drat.gz':
                    h,t=envelope(unique);objects[key].update(encoding='gzip-deflate-1',header=h.hex(),footer=t.hex())
    inv=dict(format='S035_PAUSE_CONTENT_ADDRESSED_V1',zlib_version=zlib.ZLIB_VERSION,
             files=files,objects=objects,external_S034=external,operational_lock_files=locks,
             external_archive='validation/S034/campaign.tar.xz',external_archive_sha256=digest(ROOT/'validation/S034/campaign.tar.xz'),
             original_preupgrade_container=dict(path=str(AREA/'pre-resident-runtime.tar.gz'),sha256=digest(AREA/'pre-resident-runtime.tar.gz'),bytes=(AREA/'pre-resident-runtime.tar.gz').stat().st_size,storage='LOCAL_ORIGINAL_RETAINED; every member file also in this archive'))
    temporary=archive.with_suffix('.part')
    with lzma.open(temporary,'wb',preset=3) as comp,tarfile.open(fileobj=comp,mode='w|') as tf:
        regular=[k for k,r in objects.items() if r['encoding']=='identity']
        compressed=[k for k,r in objects.items() if r['encoding']!='identity']
        for i,key in enumerate(regular):
            h=hashlib.sha256();size=0
            with paths[key].open('rb') as f:
                while True:
                    b=f.read(CHUNK)
                    if not b:break
                    h.update(b);add(tf,f'objects/{key}/{size}',b);size+=len(b)
                if not size:add(tf,f'objects/{key}/0',b'')
            objects[key].update(decoded_bytes=size,decoded_sha256=h.hexdigest());assert h.hexdigest()==key
            if i%500==0:print('REGULAR',i,'of',len(regular),flush=True)
        handles={k:gzip.open(paths[k],'rb') for k in compressed};states={k:[hashlib.sha256(),0] for k in compressed}
        while handles:
            for key in list(handles):
                b=handles[key].read(CHUNK);st=states[key]
                if not b:handles.pop(key).close();continue
                st[0].update(b);add(tf,f'objects/{key}/{st[1]}',b);st[1]+=len(b)
        for key,(h,size) in states.items():objects[key].update(decoded_bytes=size,decoded_sha256=h.hexdigest())
        add(tf,'INVENTORY.json',json.dumps(inv,sort_keys=True).encode())
    print('ARCHIVE_WRITTEN',temporary.stat().st_size,flush=True)
    verify(temporary,inv);temporary.rename(archive)
    inventory_path.write_text(json.dumps(inv,indent=1)+'\n',encoding='utf-8')
    receipt=dict(status='PASS_ALL_ORIGINAL_OBJECT_BYTES_AND_GZIP_RECONSTRUCTION',archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,files=len(files),unique_objects=len(objects),external_S034_files=len(external),no_original_deleted=True)
    (OUT/'ARCHIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=1)+'\n')
    print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
