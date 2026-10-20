"""Read-only S031 primary-source refresh; full pages remain scratch only."""
from datetime import datetime,timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'artifacts/tmp/S031/prior-art');OUT.mkdir(parents=True,exist_ok=True)
items={'paper59-api':'https://rstation.ai/api/v1/papers/earth_moon_59',
       'paper59':'https://rstation.ai/problems/earth_moon/papers/59',
       'post146':'https://rstation.ai/r/earth_moon/posts/146',
       'post152':'https://rstation.ai/r/earth_moon/posts/152',
       'post155':'https://rstation.ai/r/earth_moon/posts/155',
       'arxiv':'https://arxiv.org/abs/2609.28102'}
rows=[]
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,t,a):
        if t in ('script','style'):self.skip+=1
    def handle_endtag(self,t):
        if t in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip:self.parts.append(d)
for key,url in items.items():
    row={'url':url,'access_utc':datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 Earth-Moon research audit'}),timeout=30) as r:
            b=r.read();row.update(http_status=r.status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        (OUT/(key+'.raw')).write_bytes(b)
        if key=='paper59-api':
            data=json.loads(b)['data'];row.update(version=data['version'],standing=data['standing'])
        else:
            p=Text();p.feed(b.decode('utf-8'));text=' '.join(p.parts)
            (OUT/(key+'.txt')).write_text(text,encoding='utf-8',newline='\n')
            row['access_grade']='METADATA_ONLY'
    except Exception as e:row.update(access_grade='UNAVAILABLE',error=repr(e))
    rows.append(row)
(OUT/'FETCH_RECEIPTS.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(rows,indent=2))
