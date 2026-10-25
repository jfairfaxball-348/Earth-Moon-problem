"""Audit all archive bytes, new graph records, geometric clauses and native leftovers."""
import gzip,hashlib,itertools,json,sqlite3,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'validation/S045/final'
sys.path.insert(0,str(ROOT/'tools'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,v):Path(p).write_text(json.dumps(v,indent=1)+'\n',encoding='utf-8',newline='\n')
from s045_verify import check_pair,check_colouring,partition_clause,geometric_journal

def audit(portable=False):
    reg=json.loads((V/'REGISTRATION.json').read_text());index=json.loads((V/'ARCHIVE_INDEX.json').read_text())
    smoke=json.loads((V/'SMOKE.json').read_text());assert smoke['verdict']=='PASS'
    started=time.monotonic();pairs=list(itertools.combinations(range(50),2));rows=0;fresh=0;native_rows=0;unsat=[];orphans=[]
    out=ROOT/'artifacts/tmp/S045/final-audit';out.mkdir(parents=True,exist_ok=True)
    database=out/('portable.sqlite' if portable else 'audit.sqlite');database.unlink(missing_ok=True)
    db=sqlite3.connect(database);db.execute('PRAGMA cache_size=-8192');db.execute('CREATE TABLE seen(h BLOB PRIMARY KEY) WITHOUT ROWID')
    seals=[]
    for item in index['journals']:
        archive=ROOT/item['archive'];assert sha(archive)==item['archive_sha256']
        receipt=json.loads(Path(str(archive)+'.seal.json').read_text());raw=hashlib.sha256();size=0
        with gzip.open(archive,'rb') as f:
            for line in f:
                raw.update(line);size+=len(line);assert line.endswith(b'\n')
                r=json.loads(line);assert (r['n'],r['k'],r['mode'])==(50,9,'partition')
                bits=r['bits'];assert len(bits)==2450 and not set(bits)-{'0','1'}
                if rows>=reg['inherited_independently_checked_prefix_records']:
                    check_pair(50,r['layers'],r['rotations']);check_colouring(50,r['layers'],r['colours'],9)
                    assert all([list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1']==r['layers'][j] for j in (0,1))
                    clause=partition_clause(50,r['colours']);assert clause and all(bits[v-1]=='0' for v in clause);fresh+=1
                db.execute('INSERT OR IGNORE INTO seen VALUES (?)',(hashlib.sha256(bits.encode()).digest(),));rows+=1
                if rows%10000==0:db.commit()
        db.commit();assert raw.hexdigest()==receipt['raw_sha256'] and size==receipt['raw_bytes'];seals.append(dict(archive=item['archive'],raw_sha256=raw.hexdigest(),raw_bytes=size))
        print('Candidate archive checked:',rows,flush=True)
    assert rows==reg['expected_candidate_records'] and fresh==reg['fresh_check_delta_records']
    prefix=json.loads((ROOT/reg['prefix_receipt']).read_text());assert prefix['input_candidates']==reg['inherited_independently_checked_prefix_records'] and prefix['status']=='PASS'
    # The inherited prefix is pinned to the actual previously audited gzip bytes.
    for source,h in prefix['source_journals'].items():
        found=[x for x in index['journals'] if x['runtime_source'].replace('\\','/')==source.replace('\\','/')]
        assert len(found)==1 and found[0]['archive_sha256']==h
    geometry=index['geometry'];archive=ROOT/'validation/S045/final/PLANARITY.lem.gz';assert sha(archive)==geometry['archive_sha256']
    lem=out/'PLANARITY.lem';raw=hashlib.sha256();size=0
    with gzip.open(archive,'rb') as src,lem.open('wb') as dst:
        for block in iter(lambda:src.read(1024*1024),b''):raw.update(block);size+=len(block);dst.write(block)
    assert raw.hexdigest()==geometry['raw_sha256'] and size==geometry['raw_bytes']
    count=geometric_journal(lem,50);assert count==reg['expected_geometric_occurrences'];print('All geometric occurrences freshly checked:',count,flush=True)
    orphan_seen=set()
    for item in index['native_traces']:
        archive=ROOT/item['archive'];assert sha(archive)==item['archive_sha256']
        with gzip.open(archive,'rt',encoding='utf-8') as f:
            for number,line in enumerate(f,1):
                if line.startswith('END 20'):unsat.append(dict(archive=item['archive'],line=number))
                if not line.startswith('CAND '):continue
                fields=line.split();assert len(fields)==3;bits=fields[2];assert len(bits)==2450 and not set(bits)-{'0','1'};native_rows+=1
                h=hashlib.sha256(bits.encode()).digest()
                if db.execute('SELECT 1 FROM seen WHERE h=?',(h,)).fetchone() or h in orphan_seen:continue
                orphan_seen.add(h);orphans.append(dict(bits=bits,source=item['archive'],line=number))
        print('Native trace rows scanned:',native_rows,'unmatched:',len(orphans),flush=True)
    assert len(orphans)<=reg['orphan_cap']
    if portable:
        saved=[json.loads(line) for line in gzip.open(V/'ORPHANS.jsonl.gz','rt',encoding='utf-8')]
        assert {r['bits'] for r in saved}=={r['bits'] for r in orphans}
        for r in saved:check_pair(50,r['layers'],r['rotations']);check_colouring(50,r['layers'],r['colours'],9)
    else:
        import networkx as nx
        import s045_search as search
        saved=[]
        for item in orphans:
            bits=item['bits'];layers=[[list(e) for i,e in enumerate(pairs) if bits[2*i+j]=='1'] for j in (0,1)];rotations=[]
            for layer in layers:
                g=nx.Graph();g.add_nodes_from(range(50));g.add_edges_from(layer);ok,embedding=nx.check_planarity(g);assert ok;rotations.append(embedding.get_data())
            check_pair(50,layers,rotations);answer,colours=search.colouring(50,layers,9,reg['orphan_colouring_seconds'])
            if answer is not True:
                write_json(V/'PENDING_SCIENTIFIC_ALERT.json',dict(source=item,layers=layers,rotations=rotations,result=answer,proof_verified=False));raise AssertionError('Unjournalled native candidate needs scientific review')
            check_colouring(50,layers,colours,9);saved.append(dict(n=50,k=9,layers=layers,rotations=rotations,colours=colours,**item))
        with gzip.open(V/'ORPHANS.jsonl.gz','wt',encoding='utf-8') as f:
            for row in saved:f.write(json.dumps(row,separators=(',',':'))+'\n')
    assert not unsat,unsat
    result=dict(status='PASS',candidate_records=rows,prefix_inherited_checked_records=reg['inherited_independently_checked_prefix_records'],freshly_checked_candidate_records=fresh,geometric_occurrences_freshly_checked=count,native_trace_candidate_occurrences=native_rows,previously_unjournalled_distinct_layer_assignments=len(orphans),all_unjournalled_candidates_checked_nine_colourable=True,retained_native_unsat_signals=unsat,all_archive_bytes_checked=True,partial_final_count_not_claimed_as_native_slice=True,proof_backed_projected_coverage=None,witness=False,domain_excluded=False,elapsed_seconds=time.monotonic()-started,journal_seals=seals)
    db.close()
    if not portable:write_json(V/'AUDIT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='journal_seals'}),flush=True)
    return result

if __name__=='__main__':audit('--portable' in sys.argv)
