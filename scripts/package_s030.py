"""Freeze completed bounded S030 evidence. No verdict inference from logs."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'artifacts/tmp/S030'
DEST=ROOT/'validation/S030'


def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def put(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if src.suffix in ('.cnf','.log'):
        dst=dst.with_suffix(dst.suffix+'.gz')
        with src.open('rb') as inp, dst.open('wb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as out:
                shutil.copyfileobj(inp,out)
    else:shutil.copy2(src,dst)


def main():
    DEST.mkdir(exist_ok=True,parents=True)
    for name in ('ENVIRONMENT.json','GATE.json','JOURNAL.jsonl','SMOKE.json','smoke.log',
                 'CONTROLS.json','EXTRA_CONTROLS.json','INDEPENDENT.json','POSITIVE24.json','SEARCH_REPLAY.json'):
        put(TMP/name,DEST/name)
    put(TMP/'sources/FETCH_RECEIPTS.json',DEST/'prior_art/FETCH_RECEIPTS.json')
    supp=TMP/'sources/supplement'
    for p in supp.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            put(p,DEST/'prior_art/paper59'/p.relative_to(supp))
    results=[]; proof_receipts=[]
    for name in ('pilot','strong','sorted'):
        base=TMP/name
        r=json.loads((base/'RESULT.json').read_text()); results.append(r)
        for p in base.iterdir():
            if p.is_file() and (p.suffix in ('.json','.jsonl','.log','.py') or p.name=='final.cnf'):
                put(p,DEST/name/p.name)
        proof=(TMP/'current.drat') if name=='pilot' else base/'current.drat'
        if proof.exists():
            proof_receipts.append({'stage':name,'raw_bytes':proof.stat().st_size,'sha256':digest(proof),
              'status':'INCOMPLETE_SEARCH_TRACE_NOT_A_CERTIFICATE','retained':False,
              'reason':'UNKNOWN search; final CNF, semantic cuts and native logs retained instead'})
    (DEST/'INCOMPLETE_PROOF_RECEIPTS.json').write_text(json.dumps(proof_receipts,indent=2)+'\n')
    summary={'session':'S030','executor':'Codex desktop local Windows','smoke':'PASS_FULL_271_PLUS_K9',
             'S11_m155_156':results[-1]['verdict'],'S11_m154_regular':'SOURCE_STATED_NOT_PROGRAMME_DECIDED',
             'S10':'NOT_RUN','S9':'NOT_RUN','S8_unconditional_fallback':'NOT_RUN',
             'witness':None,'certified_strata':[],
             'seconds':round(sum(r['seconds'] for r in results),3),
             'sat_models':sum(sum(i['returncode']==10 for i in r['iterations']) for r in results),
             'search_segments':[{k:v for k,v in r.items() if k!='iterations'} for r in results],
             'peak_private_kib':max(i['peak_tree_rss_kib'] for r in results for i in r['iterations']),
             'regular_packet':'THREE_FINITE_BRANCHES_RUP_VERIFIED; HAND_COVERAGE_NOT_REPROVED',
             'range':{'lower':9,'upper':12}}
    assert summary['S11_m155_156']=='UNKNOWN' and not summary['certified_strata'] and summary['witness'] is None
    (DEST/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    manifest={}
    for p in DEST.rglob('*'):
        if p.is_file() and p.name!='PACKAGE.json':
            manifest[p.relative_to(ROOT).as_posix()]={'bytes':p.stat().st_size,'sha256':digest(p)}
    (DEST/'PACKAGE.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),
                                               'files':manifest},indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='search_segments'},indent=2))


if __name__=='__main__':main()
