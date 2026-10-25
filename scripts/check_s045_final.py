"""Portable full closeout replay, immutable provenance and successor boundary."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'validation/S045/final'
sys.path.insert(0,str(ROOT/'scripts'))
from audit_s045_final import audit
def main():
    saved=json.loads((V/'AUDIT.json').read_text());records_only='--records-only' in sys.argv
    fresh=saved if records_only else audit(portable=True)
    for key in ('candidate_records','freshly_checked_candidate_records','geometric_occurrences_freshly_checked','native_trace_candidate_occurrences','previously_unjournalled_distinct_layer_assignments'):
        assert saved[key]==fresh[key],key
    reg=json.loads((V/'REGISTRATION.json').read_text());entry=json.loads((V/'ENTRY.json').read_text())
    assert reg['deadline_epoch']==1792913400 and reg['observed_stop_epoch']>=1792913400
    assert reg['observed_stop_epoch']-1792913400<1 and entry['all_recorded_identities_exited']
    assert not reg['search_restarted'] and not reg['private_cdcl_serialized']
    state=json.loads((ROOT/'authoritative/STATE.json').read_text())
    assert state['last_completed_session']=='S045' and state['recommended_next_session']=='S046'
    assert not state.get('active_session') and state['next_session_is_future_unexecuted']
    assert state['s045_result']['status']=='CLOSED_OWNER_DEADLINE_UNKNOWN'
    assert state['s036_closeout']['computation']=='STOPPED'
    assert (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_bytes()==(ROOT/'sessions/S045/S046_FUTURE_PROMPT.md').read_bytes()
    assert 'FUTURE / UNEXECUTED' in (ROOT/'authoritative/NEXT_SESSION_PROMPT.md').read_text()
    initial=json.loads((V/'INITIAL_SOURCES.json').read_text())
    assert initial['commit']=='307399a7ce471f722181098a93c8378d5b2f5824'
    for item in initial['files'].values():assert hashlib.sha256((ROOT/item['archive']).read_bytes()).hexdigest()==item['sha256']
    manifest=json.loads((V/'MANIFEST.json').read_text())
    for p,h in manifest['sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    print('S045 final records PASS (mathematical audit not rerun)' if records_only else 'S045 final deadline, evidence and S046 FUTURE boundary PASS; no witness or finite-domain exclusion')
if __name__=='__main__':main()
