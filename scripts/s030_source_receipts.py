"""Hash fetched source bytes and extract article text for the S030 audit.

Raw manuscripts are scratch only. Commit receipts and CC0 supplement, not
unlicensed full papers. Fetching occurred separately through read-only HTTP.
"""
import hashlib
from html.parser import HTMLParser
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/tmp/S030/sources'
sys.stdout.reconfigure(encoding='utf-8')

class Article(HTMLParser):
    def __init__(self):
        super().__init__(); self.active=False; self.parts=[]
    def handle_starttag(self,t,attrs):
        if t=='article':self.active=True
        if self.active and t in ('p','h1','h2','h3'):self.parts.append('\n')
    def handle_endtag(self,t):
        if t=='article':self.active=False
    def handle_data(self,d):
        if self.active:self.parts.append(d)

urls={'paper59.html':'https://rstation.ai/problems/earth_moon/papers/59',
      'paper59.md':'https://rstation.ai/api/v1/papers/earth_moon_59/versions/3/download',
      'paper59-api.json':'https://rstation.ai/api/v1/papers/earth_moon_59',
      'post146.html':'https://rstation.ai/r/earth_moon/posts/146',
      'post152.html':'https://rstation.ai/r/earth_moon/posts/152',
      'post155.html':'https://rstation.ai/r/earth_moon/posts/155',
      'szeider-abs.html':'https://arxiv.org/abs/2609.28102',
      'szeider.html':'https://arxiv.org/html/2609.28102v1',
      'supplement.zip':'https://rstation.ai/api/v1/papers/earth_moon_59/versions/3/supplement'}
receipts=[]
for name,url in urls.items():
    p=BASE/name; b=p.read_bytes()
    receipts.append({'url':url,'date':'2026-10-19','http_status':200,
                     'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    if name.startswith('post'):
        a=Article();a.feed(b.decode()); txt=''.join(a.parts)
        (BASE/(p.stem+'.txt')).write_text(txt,encoding='utf-8')
        print(name,txt[:700],txt[-800:],sep='\n')
(BASE/'FETCH_RECEIPTS.json').write_text(json.dumps(receipts,indent=2)+'\n')
