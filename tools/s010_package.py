"""Freeze S010 public artifact hashes and verify exact staged Git blobs."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENTRY='8626b6419f12d706f3ba567f6733d26d6e4dd7be';MANIFEST='validation/S010_MANIFEST.json'

def git(*args,binary=False):return subprocess.check_output(['git',*args],cwd=ROOT,text=not binary)
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def digest(b):return hashlib.sha256(b).hexdigest()

def freeze():
    assert git('rev-parse','HEAD').strip()==ENTRY and git('branch','--show-current').strip()=='codex/S010-strategic-reset'
    summary=load('validation/S010/SUMMARY.json')
    assert summary['S010_new_exclusions']==[] and summary['remaining_unknown']==219
    assert load('validation/S010/INDEPENDENT_RECORD_AUDIT_PASS.json')['verdict']=='PASS'
    assert 'governance checks: PASS' in (ROOT/'validation/S010/governance.log').read_text()
    unit=(ROOT/'validation/S010/unit.log').read_text();assert 'Ran 10 tests' in unit and '\nOK' in unit
    paths=set(git('diff','--name-only','HEAD').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    paths.discard(MANIFEST);artifacts={}
    for name in sorted(paths):
        raw=(ROOT/name).read_bytes();assert len(raw)<=100*1024**2,name
        artifacts[name]=dict(sha256=digest(raw),bytes=len(raw))
    record=dict(session='S010',date='2026-10-14',entry_main=ENTRY,entry_tree='defbef2531504b868642c5f21b5dd1ee40b0bf17',
        branch='codex/S010-strategic-reset',owner_invocation='sessions/S010/OWNER_INVOCATION.md',executed_prompt='sessions/S010/EXECUTED_PROMPT.md',
        preregistration='campaigns/CAM-0011.md with prospectiveA-E',environment=load('validation/S010/environment.json'),summary=summary,
        artifact_sha256=artifacts,authority_entry_git_blob_sha256={
            name:dict(sha256=digest(raw),bytes=len(raw)) for name in ('AGENTS.md','docs/SESSION_PROTOCOL.md','.github/workflows/scaffold.yml')
            for raw in (git('show',ENTRY+':'+name,binary=True),)},
        checks=dict(cold50='validation/S010/cold_replay.json',chromatic271='validation/S010/chromatic_cold_replay.json',
            scientific_audit='validation/S010/INDEPENDENT_RECORD_AUDIT_PASS.json',
            governance=dict(command='.venv/Scripts/python.exe scripts/check_scaffold.py',returncode=0,log='validation/S010/governance.log'),
            unit=dict(command='.venv/Scripts/python.exe -m unittest discover -s tests -v',returncode=0,tests=10,log='validation/S010/unit.log'),
            hosted='Observe actual postcommit head/main runs/jobs; not anticipated here'),
        byte_provenance='S010 evidence exempt from Git text conversion. Observed launch snapshots remain immutable and distinct from final hashes. Manifest excludes itself.',
        outgoing_integration='Observe one authored commit/ordinary PR/non-force two-parent merge/main/parents/matching trees/jobs after freeze; ignored artifacts/tmp/S010/LIVE_EXIT_EVIDENCE.json and final response.',
        limitations='Headline9..12 unchanged;52 rows excluded/219 UNKNOWN. No new row exclusion/whole-census/minimality/novelty/external universal review/formalisation/registration/publication/outreach. S011 FUTURE/UNEXECUTED.')
    (ROOT/MANIFEST).write_text(json.dumps(record,indent=1)+'\n',encoding='utf-8',newline='\n')
    print('PASS frozen S010',len(artifacts),'artifacts;',sum(r['bytes'] for r in artifacts.values()),'bytes')

def staged():
    rec=load(MANIFEST);authority=rec['authority_entry_git_blob_sha256'];paths=list(rec['artifact_sha256'])+list(authority)+[MANIFEST]
    entries={}
    for line in git('ls-files','--stage').splitlines():
        meta,path=line.split('\t',1);mode,oid,stage=meta.split();assert stage=='0';entries[path]=oid
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for p in paths:
        proc.stdin.write((entries[p]+'\n').encode());proc.stdin.flush()
        oid,kind,size=proc.stdout.readline().split();assert kind==b'blob';raw=proc.stdout.read(int(size));assert proc.stdout.read(1)==b'\n'
        if p not in authority:assert raw==(ROOT/p).read_bytes(),p
        if p!=MANIFEST:
            exp=authority[p] if p in authority else rec['artifact_sha256'][p]
            assert len(raw)==exp['bytes'] and digest(raw)==exp['sha256'],p
    proc.stdin.close();assert proc.wait()==0
    print('PASS exact staged S010 blobs:',len(paths))

if __name__=='__main__':staged() if len(sys.argv)>1 else freeze()
