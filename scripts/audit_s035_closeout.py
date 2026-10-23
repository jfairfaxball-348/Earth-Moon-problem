"""Read-only scientific audit at owner pause; no solver/proof-checker launch."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'scripts')]
from s035_windows import read_json,atomic_json,live_identity,tree_sample
from s035_regions import sha,validate_partition
from audit_s033_fast import subdivision
AREA=ROOT/'artifacts/tmp/S035';CAMP=AREA/'campaign';OUT=ROOT/'validation/S035/closeout'

def resolve(original):
    prefix='/root/Earth-Moon-problem/'
    if original.startswith(prefix+'artifacts/tmp/S034/campaign/'):
        return AREA/'imported-s034'/original.removeprefix(prefix+'artifacts/tmp/S034/campaign/')
    if original.startswith(prefix):return ROOT/original.removeprefix(prefix)
    return Path(original)

def logic(log):
    rows=[]
    for match in re.finditer(r'^c S032_LOGIC conflicts=(\d+) decisions=(\d+) propagations=(\d+)',log,re.M):
        rows.append(dict(zip(('conflicts','decisions','propagations'),map(int,match.groups()))))
    return rows

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    pause=read_json(CAMP/'OWNER_PAUSE.json');cfg=read_json(CAMP/'CONFIG.json');data=read_json(CAMP/'REGIONS.json');contexts=pause['contexts']['contexts']
    assert validate_partition(cfg,data['cells'])
    import psutil
    for p in pause['processes']:
        assert live_identity(p['pid'],p['start_ticks'])
        __import__('s035_thread_policy').validate(p,read_json(CAMP/'RESUME_CONTROL/THREAD_POLICY.json'),paused=True)
    # Search actual scientific logs and native results, including imported S034.
    # Acceptance controls deliberately have SAT outputs and are classified apart.
    sat=[];scanned=0;controls=[]
    scientific=('campaign','benchmark-1','benchmark-2','benchmark-3','imported-s034','phase-diagnostic','phase-diagnostic-overlap-aborted')
    for name in scientific:
        for p in (AREA/name).rglob('*'):
            if p.suffix not in ('.log','.json','.jsonl'):continue
            text=p.read_text(errors='replace');scanned+=1
            if re.search(r'^s SATISFIABLE\s*$',text,re.M) or re.search(r'"returncode"\s*:\s*10\b',text) or p.name=='CANDIDATE.json':
                # Worker-control fixtures only, never a scientific candidate.
                row=dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
                if name=='imported-s034' and ('control' in str(p).lower()):controls.append(row)
                else:sat.append(row)
    atomic_json(OUT/'SAT_AUDIT.json',dict(status='NO_SCIENTIFIC_SAT_OR_CANDIDATE_FOUND' if not sat else 'SAT_REQUIRES_IMMEDIATE_REVIEW',scanned_files=scanned,hits=sat,classified_control_hits=controls,scope=scientific,not_claimed='No inference of SAT or UNSAT from difficulty'))
    assert not sat, 'Prominent SAT review required; see SAT_AUDIT.json'
    rows=[]
    for cell in data['cells']:
        if cell['status']=='UNSAT_DRAT_VERIFIED':continue
        ident=str(cell['id']);context=contexts.get(ident);attempts=sorted((CAMP/'attempts'/f'cell-{cell["id"]:04d}').glob('*'))
        history=[];native_pids=set();results=collections.Counter();proofs=[];best=None
        for directory in attempts:
            lp=directory/'native.log'
            if lp.exists():
                text=lp.read_text(errors='replace');counter=logic(text)
                if counter and 'S035_RESIDENT_ORIGIN' not in text:
                    history.append(dict(directory=str(directory),first=counter[0],last=counter[-1],samples=len(counter),conflicts_monotone=all(a['conflicts']<=b['conflicts'] for a,b in zip(counter,counter[1:]))))
                    if best is None or counter[-1]['conflicts']>best['conflicts']:best=counter[-1]
            for result in directory.glob('*RESULT.json'):
                v=read_json(result);results[str(v.get('reason') or v.get('last_outcome') or v.get('returncode') or v.get('status'))]+=1
                if v.get('worker'):native_pids.add((v['worker'].get('pid'),v['worker'].get('start_ticks')))
            if (directory/'PROOF_INPUT.json').exists():proofs.append(read_json(directory/'PROOF_INPUT.json'))
        evictions=[]
        for line in (CAMP/'JOURNAL.jsonl').read_text().splitlines():
            v=json.loads(line)
            if v['kind']=='resident_memory_eviction' and v.get('cell')==cell['id']:evictions.append(v)
        current=logic((Path(context['directory'])/'native.log').read_text())[-1] if context else None
        summary=dict(id=cell['id'],status='UNKNOWN',pause_state='NATIVE_SUSPENDED_RAM_RETAINED' if context else 'COLD_QUEUED_SEMANTIC_RECOVERY',pending_unsat_proof=bool(cell.get('pending_proof')),verification_backlog=False,visits=cell['visits'],completed_visit_seconds=cell['seconds'],native_process_identities=len(native_pids),resident_turns=context.get('turns') if context else None,current_counters=current,largest_recorded_conflicts=best,history=history,outcomes=dict(results),proof_attempts=len(proofs),evictions=evictions,stale_private_cdcl_flag=bool(cell.get('private_cdcl_retained_in_ram')) and not bool(context),bottleneck='Algorithmic search unresolved; original congruence stalls and cold restarts were operational losses. No mathematical obstruction inferred.',recommendation='Retain current context if identity survives; add cooperative pause and SAT-first supervisor before authorized resume.' if context else 'Cold semantic restore only after SAT audit and capacity opens; prioritize a registered region-specific comparison, never short identical blind restarts.')
        rows.append(summary)
    assert [x['id'] for x in rows]==[0,1,3,7,15,31,63,127,255]
    atomic_json(OUT/'NINE_REGIONS.json',dict(regions=rows,no_pending_unsat_proofs=not any(x['pending_unsat_proof'] for x in rows),proof_checks_not_replayed=True))
    # Re-audit every S035 accepted clause; inherited seed/S034 hashes stay pinned.
    accepted=0
    for row in data['accepted_cuts']:
        p=Path(row['path']);assert sha(p)==row['sha256'];n=0
        if 'S035' not in str(p) or 'imported-s034' in str(p):continue
        for line in p.read_bytes().splitlines():
            xs=list(map(int,line.split()));assert xs.pop()==0 and xs and len(xs)==len(set(xs));assert all(-756<=x<0 for x in xs) and len({(-x-1)%2 for x in xs})==1
            subdivision([tuple(cfg['pairs'][(-x-1)//2]) for x in xs]);n+=1
        assert n==row['count'];accepted+=n
    print('CUT_AUDIT_PASS',accepted,flush=True)
    for p,h in cfg['source_sha256'].items():assert sha(ROOT/p)==h
    assert sha(cfg['native'])==cfg['native_sha256']
    certificates=[]
    for cell in data['cells']:
        if cell['status']!='UNSAT_DRAT_VERIFIED':continue
        cert=read_json(cell['certificate']);recipe=cert['formula_recipe'];assert cert['cell']==cell['id'] and cert['assumptions']==cell['assumptions']==recipe['assumptions'];assert cert['mapping_sha256']==cfg['mapping_sha256']
        sources=recipe['sources'];clauses=recipe['base_clauses']+sum(s['count'] for s in sources)+len(recipe['assumptions'])
        h=hashlib.sha256(f'p cnf {recipe["variables"]} {clauses}\n'.encode())
        for index,p in enumerate([recipe['base'],*[s['path'] for s in sources]]):
            with resolve(p).open() as f:
                if index==0:next(f)
                for block in iter(lambda:f.read(1024*1024),''):h.update(block.encode())
        for lit in recipe['assumptions']:h.update(f'{lit} 0\n'.encode())
        assert h.hexdigest()==cert['formula_sha256'],cell['id']
        assert sha(resolve(cert['checker_log']))==cert['checker_log_sha256'];assert 's VERIFIED' in resolve(cert['checker_log']).read_text()
        proof=resolve(cert['proof']);receipt=proof.with_suffix('.ARCHIVE.json')
        if receipt.exists():
            v=read_json(receipt);assert sha(v['archive'])==v['archive_sha256'] and v['raw_sha256']==cert['proof_sha256']
        else:assert sha(proof)==cert['proof_sha256']
        certificates.append(dict(cell=cell['id'],formula_sha256=cert['formula_sha256'],proof_sha256=cert['proof_sha256'],checker_log_sha256=cert['checker_log_sha256']))
        if len(certificates)%25==0:print('FORMULA_RECEIPTS',len(certificates),flush=True)
    atomic_json(OUT/'AUDIT.json',dict(status='PASS_PAUSE_AUDIT_NO_NEW_MATHEMATICAL_CLAIM',proof_closed_regions=len(certificates),unresolved_regions=len(rows),S035_accepted_clause_occurrences=accepted,total_accepted_occurrences=sum(s['count'] for s in data['accepted_cuts']),certificates=certificates,formula_hashes_reconstructed=True,fresh_DRAT_replay=False,source_native_hashes='PASS',all_processes_suspended=True,processes_exited=False,ram_CDCL_serialized=False,mathematical_verdict='UNKNOWN',whole_stratum_certified=False,bounds=[9,12],recorded_epoch=time.time()))
    print('PASS SAT scan, nine diagnostics, clauses, formulas and original proof receipts',flush=True)

if __name__=='__main__':main()
