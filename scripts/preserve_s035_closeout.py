"""Preserve stopped S035 without process mutation; delta over immutable pause archive."""
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'scripts')]
import psutil
import s035_preserved_lifecycle as lifecycle
import s035_thread_policy as policy_tools
import s035_sat_first_resume as guard
from audit_s033_fast import subdivision

AREA = ROOT/'artifacts/tmp/S035'
CAMP = AREA/'campaign'
CONTROL = CAMP/'RESUME_CONTROL'
OUT = ROOT/'validation/S035/closeout'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=1)+'\n', encoding='utf-8')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def main():
    OUT.mkdir(exist_ok=True, parents=True)
    assert not (OUT/'DELTA_INVENTORY.json').exists(), 'Refuse overwrite'
    a = read(CONTROL/'ADOPTION.json'); policy = read(CONTROL/'THREAD_POLICY.json')
    assert a['status']=='PAUSED' and not a['pause_errors']
    assert (CONTROL/'STOP').exists() and (CAMP/'STOP').exists()
    processes = []
    for r in a['original_processes']:
        p = lifecycle.checked(r)
        threads = policy_tools.validate(r, policy, paused=True)
        processes.append(dict(identity=r, threads=threads, cpu=sum(p.cpu_times()[:2]), private=p.memory_info().private))
    time.sleep(2)
    for r in processes:
        p = lifecycle.checked(r['identity'])
        r['cpu_delta'] = sum(p.cpu_times()[:2])-r['cpu']
        assert r['cpu_delta']==0
    controls = {}
    for name in ('controller','watcher'):
        try:
            lifecycle.checked(a[name]); controls[name]='IDENTITY_STILL_ALIVE'
        except lifecycle.LifecycleError:
            controls[name]='EXACT_IDENTITY_NO_LONGER_ALIVE'
    for p,h in a['source_sha256'].items(): assert sha(ROOT/p)==h,p
    scanner = guard.Scanner()
    hits = scanner.inspect(guard.scientific_paths(CAMP), classify_controls=True)
    assert not hits, 'SAT REVIEW REQUIRED: '+repr(hits)
    write('SAT_RESCAN.json',dict(hits=[], scanned_files=scanner.scanned_files, controls=scanner.controls, epoch=time.time()))
    write('PROCESS_SNAPSHOT.json',dict(processes=processes, controls=controls, all_original_threads_suspended=True,
        available_ram_bytes=psutil.virtual_memory().available, free_disk_bytes=psutil.disk_usage(str(ROOT)).free,
        source_hashes='PASS', private_cdcl_serialized=False, epoch=time.time()))
    cfg=read(CAMP/'CONFIG.json'); prefixes=[]; contexts=[]
    for c in a['contexts']:
        d=Path(c['directory']); assert sha(d/'input.inst')==c['input_sha256']
        assert sha(c['worker']['command'][0])==c['native_sha256']
        h=hashlib.sha256();n=0;size=0
        with (d/'new-cuts.lem').open('rb') as f:
            for line in f:
                assert line.endswith(b'\n'), 'Incomplete suffix must be preserved separately'
                xs=list(map(int,line.split()));assert xs.pop()==0 and xs and len(set(xs))==len(xs)
                assert all(-756<=x<0 for x in xs) and len({(-x-1)%2 for x in xs})==1
                subdivision([tuple(cfg['pairs'][(-x-1)//2]) for x in xs])
                h.update(line);n+=1;size+=len(line)
        prefixes.append(dict(cell=c['cell'],source=str(d/'new-cuts.lem'),sha256=h.hexdigest(),bytes=size,occurrences=n,status='INDEPENDENT_SUBDIVISION_AUDIT_PASS'))
        text=(d/'native.log').read_text(encoding='utf-8',errors='replace')
        counters=re.findall(r'^c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)',text,re.M)
        contexts.append(dict(cell=c['cell'],worker=c['worker'],turns=c['turns'],active_seconds=c['active_seconds'],
            counters=dict(zip(('conflicts','decisions','propagations'),map(int,counters[-1]))) if counters else None))
        print('PREFIX_AUDIT',c['cell'],n,flush=True)
    write('PREFIX_AUDIT.json',dict(prefixes=prefixes,occurrences=sum(x['occurrences'] for x in prefixes),
        note='Whole retained journals, overlapping historical prefixes; not globally unique or all new. No frozen ledger mutated.'))
    write('CONTEXTS.json',dict(contexts=contexts,unresolved_ids=a['unresolved_ids'],cold_ids=a['cold_ids'],proof_closed_regions=a['proof_closed_regions']))
    base=read(ROOT/'validation/S035/pause/RUNTIME_INVENTORY.json')
    files={}; changed=[]; excluded=[]
    for p in sorted(AREA.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(AREA).as_posix()
        if p.suffix=='.lock':
            excluded.append(dict(path=rel,reason='Advisory lock, not recovery evidence'));continue
        st=p.stat();digest=sha(p); row=dict(bytes=st.st_size,sha256=digest)
        if rel=='pre-resident-runtime.tar.gz':
            assert digest==base['original_preupgrade_container']['sha256']
            row['storage']='BASE_EXPANDED_MEMBERS_AND_RETAINED_LOCAL_CONTAINER'
        elif base['files'].get(rel)==row:
            row['storage']='BASE_PAUSE_ARCHIVE'
        elif rel in base['external_S034'] and all(base['external_S034'][rel][k]==row[k] for k in ('bytes','sha256')):
            row['storage']='EXTERNAL_S034_ARCHIVE'
        else:
            row['storage']='CLOSEOUT_DELTA';changed.append(p)
        files[rel]=row
    archive=OUT/'runtime-delta.tar.xz'
    assert not archive.exists()
    with tarfile.open(archive,'w:xz',preset=3) as tf:
        for p in changed:tf.add(p,arcname=p.relative_to(AREA).as_posix(),recursive=False)
    # Actual lossless restoration into a fresh root, then per-file hash checks.
    restore=ROOT/'artifacts/tmp'/('S035-closeout-delta-restore-'+str(time.time_ns()))
    restore.mkdir()
    seen=set()
    with tarfile.open(archive,'r:xz') as tf:
        for m in tf:
            assert m.isfile()
            target=(restore/m.name).resolve();assert target.is_relative_to(restore.resolve())
            target.parent.mkdir(parents=True,exist_ok=True)
            with tf.extractfile(m) as src,target.open('wb') as dst:
                for b in iter(lambda:src.read(1024*1024),b''):dst.write(b)
            row=files[m.name];assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256']
            assert sha(AREA/m.name)==row['sha256'];seen.add(m.name)
    assert seen=={p.relative_to(AREA).as_posix() for p in changed}
    write('DELTA_INVENTORY.json',dict(format='S035_CLOSEOUT_DELTA_V1',files=files,excluded_locks=excluded,
        base_inventory='validation/S035/pause/RUNTIME_INVENTORY.json',base_inventory_sha256=sha(ROOT/'validation/S035/pause/RUNTIME_INVENTORY.json'),
        base_archive_receipt=read(ROOT/'validation/S035/pause/ARCHIVE_VERIFICATION.json'),
        S034_archive_sha256=base['external_archive_sha256']))
    write('DELTA_VERIFICATION.json',dict(status='PASS_ACTUAL_RESTORE_ALL_DELTA_FILE_HASHES',archive_bytes=archive.stat().st_size,
        archive_sha256=sha(archive),changed_files=len(seen),current_files=len(files),restored_root=str(restore),
        no_original_deleted=True,ram_state_in_archive=False))
    print('PASS closeout evidence and actual delta restoration',len(seen),archive.stat().st_size,flush=True)

if __name__=='__main__':main()
