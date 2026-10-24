"""Bounded-memory replay of the immutable first S045 slice and schema controls."""
import gzip
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from s045_search import instance,journal,sha,atomic

def main():
    initial=json.loads((ROOT/'validation/S045/INITIAL_SLICE.json').read_text())
    expected='f792a7273a18768d83ce69c78a002f58243113f961aeca2a6163b2bf73ad685b'
    started=time.monotonic();p=psutil.Process();before=p.memory_info().private
    with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/tmp/S045') as temp:
        temp=Path(temp);records=temp/'records.jsonl'
        with gzip.open(ROOT/initial['files']['CANDIDATES.jsonl']['archive'],'rb') as src,records.open('wb') as dst:
            shutil.copyfileobj(src,dst,1024*1024)
        assert sha(records)==initial['files']['CANDIDATES.jsonl']['raw_sha256']
        count=sum(1 for _ in journal(records));assert count==initial['candidates']==38042
        target=temp/'BASE.inst'
        instance(target,50,journal(records),record_count=count,target_k=9,target_mode='partition')
        assert sha(target)==expected
        after=p.memory_info().private
        row=next(journal(records));rejected=[]
        for key,value in [('k',10),('n',51),('mode','block')]:
            bad=dict(row);bad[key]=value
            try:instance(target,50,[bad],record_count=1,target_k=9,target_mode='partition')
            except AssertionError:rejected.append(key)
            else:raise AssertionError('invalid checkpoint admitted: '+key)
        partial=temp/'partial.jsonl';partial.write_text('{"n":50',encoding='ascii')
        try:list(journal(partial))
        except ValueError:rejected.append('partial')
        else:raise AssertionError('incomplete record admitted')
    atomic(ROOT/'validation/S045/STREAMING_ACCEPTANCE.json',dict(status='PASS',rows=count,
        exact_cnf_byte_match=True,cnf_sha256=expected,wall_seconds=time.monotonic()-started,
        private_before=before,private_after=after,rejected_schema_fields=rejected))
    print('S045 streaming/checkpoint acceptance PASS',flush=True)

if __name__=='__main__':main()
