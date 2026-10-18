"""Preserve S026 local output/source bytes. Packaging only, not a proof replay."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'validation/S026'
LOCAL=ROOT/'artifacts/tmp/S026-local'


def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def gz_copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    with Path(src).open('rb') as a,dst.open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as b:shutil.copyfileobj(a,b)


def copy_tree(src,dst):
    for p in Path(src).rglob('*'):
        if not p.is_file() or p.name=='RUN.lock' or p.suffix=='.tmp':continue
        target=Path(dst)/p.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix=='.drat':
            # An uncompressed leftover is an interrupted proof, not a certificate.
            # Keep its size/digest provenance, not gigabytes of unchecked text.
            h=hashlib.sha256()
            with p.open('rb') as f:
                for b in iter(lambda:f.read(1<<20),b''):h.update(b)
            target.with_suffix('.partial-proof.json').write_text(json.dumps(
                {'status':'UNCHECKED_PARTIAL_NOT_A_CERTIFICATE','bytes':p.stat().st_size,'sha256':h.hexdigest()},indent=1))
        elif p.suffix in ('.cnf',) or p.name.endswith('.lemmas.json'):
            gz_copy(p,Path(str(target)+'.gz'))
        else:shutil.copyfile(p,target)


def main():
    assert read(LOCAL/'QUEUE.json').get('status')=='QUEUE_FINISHED_NOT_A_SESSION_CLOSEOUT'
    copy_tree(LOCAL,V/'local')
    audit=ROOT/'artifacts/tmp/S026-audit'
    if (audit/'AUDIT.json').exists():
        assert read(audit/'AUDIT.json')['status']=='FINISHED_WITH_EXPLICIT_PER_CASE_VERDICTS'
        copy_tree(audit,V/'audit')
    recovery=ROOT/'artifacts/tmp/S026-filter-recovery'
    if (recovery/'SUMMARY.json').exists():copy_tree(recovery,V/'filter-recovery')
    snapshots=V/'source-bytes';snapshots.mkdir(exist_ok=True)
    index=[]
    files=list(V.rglob('SOURCE.json'))+list(V.rglob('FAILED_CONTROL_SOURCE.json'))+[V/'local/ENVIRONMENT.json']
    for manifest in files:
        d=read(manifest)
        for filename,expected in d.get('source_sha256',{}).items():
            filename=filename.replace('\\','/')
            target=snapshots/(expected+'.py.gz')
            method='existing verified snapshot'
            if target.exists():raw=gzip.decompress(target.read_bytes())
            else:
                options=[]
                pin=d.get('source_commit')
                if pin:
                    proc=subprocess.run(['git','show',pin+':'+filename],cwd=ROOT,capture_output=True)
                    if proc.returncode==0:options.append(('recorded Git commit',proc.stdout))
                p=ROOT/filename
                if p.exists():options.append(('matching current file, recovered after execution',p.read_bytes()))
                p=V/'local/launch-source-bytes'/(Path(filename).name+'.gz')
                if p.exists():options.append(('preserved observed launch CRLF bytes',gzip.decompress(p.read_bytes())))
                found=next(((m,b) for m,b in options if digest(b)==expected),None)
                assert found is not None,('missing observed source bytes',manifest,filename,expected)
                method,raw=found
                with target.open('wb') as f:
                    with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as g:g.write(raw)
            assert digest(raw)==expected
            index.append({'manifest':str(manifest.relative_to(ROOT)).replace('\\','/'),
                          'path':filename,'observed_sha256':expected,'base_git_commit':d.get('source_commit'),
                          'snapshot':str(target.relative_to(ROOT)).replace('\\','/'),'recovery':method})
    (V/'SOURCE_BYTE_MANIFEST.json').write_text(json.dumps(index,indent=1),encoding='utf-8')
    print(json.dumps({'source_fingerprint_entries':len(index),'unique_source_byte_archives':len(list(snapshots.glob('*.gz')))}))


if __name__=='__main__':main()
