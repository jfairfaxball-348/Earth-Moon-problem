"""Current S045 operational handover after accepted memory-stop recovery."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'validation/S045/memory_recycle'
def put(p,text):(ROOT/p).write_text(text,encoding='utf-8',newline='\n')
def main():
    a=json.loads((V/'ACCEPTANCE.json').read_text(encoding='utf-8'));assert a['status']=='PASS'
    note=f'''\n\nS045 memory-limit recovery, 24 October 2026: the 20:22 UTC safe stop was\nPRIVATE_MEMORY_LIMIT, native rc0; no owner STOP, alert or uncertified UNSAT.\nFour completed slices preceded it. All 453656 candidate records and 1570940\ngeometric rule occurrences were preserved; the pending final 72775-rule\ngeometric tail was independently checked during recovery. Private CDCL ended\nwith its process. Fresh full 271+K9 smoke, all 1024 native fixed n5 cases,\nprotocol/DRAT controls, timing controls and real-child memory regressions PASS.\n\nResource policy now ends a native slice cooperatively at 2.5 GiB aggregate\nprivate memory; after independent audit the next slice reloads ALL semantic\nrecords. The existing 3 GiB hard cap, 1.5 GiB available floor and 10 GiB disk\nreserve remain. A local SLICE_STOP is distinct from durable campaign STOP.\nOwner/scientific/hard-resource/deadline stops remain latched. An already-too-large\ncheckpoint producing zero new candidates stops CHECKPOINT_MEMORY_NO_PROGRESS;\nno endless zero-progress restart. No increase to the machine's resource limits.\n\nCurrent acceptance: validation/S045/memory_recycle/ACCEPTANCE.json; seed\n{a['seed_candidates']} candidate records / {a['seed_geometric_rules']} geometric\nrule occurrences includes the independently checked restart benchmark additions.\nThe native binary and mathematical checks are unchanged; source pins include\nthe recycling driver. Original watchdog evidence stays frozen and is replayed\nwith scripts/s045_replay_watchdog.py against its exact 673d4a6 context.\n\nTwo-hour check-ins remain ACTIVE. Hard stop remains 25 October 2026 07:30\nEurope/London = UTC/GMT. S045 continues, S036 stays stopped, no S046 invocation.\nCounts are activity, not projected coverage; no witness; 9<=chi_2<=12.\n'''
    top='''# S045 memory recovery accepted — 24 October 2026\n\nRead validation/S045/memory_recycle/ACCEPTANCE.json and the current execution\nprompt. A 2.5 GiB soft threshold recycles completed, audited native slices\nbefore the unchanged 3 GiB hard cap. All semantic journals are retained and\nreplayed. Hard stop remains 25 October 07:30 UK/GMT. Two-hour checks ACTIVE.\nS036 stopped; no automatic S046. Historical handover follows.\n\n'''
    put('sessions/S045/RUNNING.md',top+(ROOT/'sessions/S045/RUNNING.md').read_text(encoding='utf-8')+note)
    prompt=(ROOT/'sessions/S045/EXECUTION_PROMPT.md').read_text(encoding='utf-8')+note
    put('sessions/S045/EXECUTION_PROMPT.md',prompt);put('authoritative/NEXT_SESSION_PROMPT.md',prompt)
    for p in ('sessions/S045/RESEARCH.md','sessions/S045/ADVERSARIAL.md','docs/SESSION_LEDGER.md','docs/FAILURE_LEDGER.md','campaigns/CAM-0049.md'):
        put(p,(ROOT/p).read_text(encoding='utf-8')+note)
    for p in ('AGENTS.md','authoritative/START_HERE.md'):put(p,top+(ROOT/p).read_text(encoding='utf-8'))
    state=json.loads((ROOT/'authoritative/STATE.json').read_text(encoding='utf-8'))
    state['current_computation']='RUNNING'
    state['active_session']['stage']='SUSTAINED_SEARCH_MEMORY_RECYCLE'
    state['s045_memory_recycle']=dict(status='ACCEPTED_RESTARTED',acceptance='validation/S045/memory_recycle/ACCEPTANCE.json',deadline_epoch=1792913400,soft_private_bytes=a['soft_private_bytes'],hard_private_bytes=a['hard_private_bytes'],seed_candidates=a['seed_candidates'],seed_geometric_rules=a['seed_geometric_rules'],old_stop='PRIVATE_MEMORY_LIMIT',all_semantic_rules_preserved=True,checkin_status='ACTIVE',witness=False)
    put('authoritative/STATE.json',json.dumps(state,indent=2)+'\n')
    (V/'FAILURES.json').write_text(json.dumps(dict(environment_invocation='Initial smoke used default Linux binary path on Windows; rerun with existing pinned EMP_DRAT_TRIM/EMP_CADICAL passed full smoke.',historical_wrapper='Path.open wrapper initially received Python locale encoding token; explicit utf-8 fallback fixed wrapper, historical receipts unchanged.',proof_status='No mathematical claim from operational acceptance'),indent=1)+'\n',encoding='utf-8',newline='\n')
if __name__=='__main__':main()
