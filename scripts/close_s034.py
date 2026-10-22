"""Record stopped S034 and queue the owner-requested Windows S035; no solver."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'validation/S034'
SESSION = ROOT/'sessions/S034'

def write(name, text):
    (ROOT/name).write_text(text, encoding='utf-8')

def append(name, text):
    p = ROOT/name
    if text not in p.read_text():
        p.write_text(p.read_text()+'\n'+text+'\n')

def main():
    result = json.loads((OUT/'SUMMARY.json').read_text())
    assert result['all_recorded_workers_stopped'] and result['mathematical_verdict'] == 'UNKNOWN'
    assert (OUT/'campaign.tar.xz').is_file() and (OUT/'RUNTIME_INVENTORY.json').is_file()
    shutil.copy2(SESSION/'S035_FUTURE_PROMPT.md', ROOT/'authoritative/NEXT_SESSION_PROMPT.md')
    closeout = '''# S034 closeout — phone campaign safety-stopped; Windows continuation queued

S034 is complete. Genuine one-worker guarded solver computation ran from
21 October20:52:22Z to22 October00:01:43Z,11360.862s (3h9m21s). It stopped
cleanly for SAFETY_DISK_RESERVE, before the authorised06:00 UTC/07:00 UK deadline.
No worker remained active and no successor was launched. This was a storage
safety stop, not completion of the finite search or an arbitrary campaign cap.

The256-region ledger records102 visits:16 UNSAT_DRAT_VERIFIED encoded regions,
86 visited UNKNOWN and154 unvisited UNKNOWN. Independently rechecked93047 new
single-layer K5/K33-subdivision clause occurrences; together with2579937 retained
S032 clauses there are2672984 occurrences, not a globally unique count. No saved
SAT candidate, witness, new individual graph decision or whole-stratum proof.
S11m155/156 UNKNOWN; regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN;9<=chi2<=12.

Fresh full271+retained/fresh K9 smoke, native1024n5/K33/positive24, original-rule
and exact mapping audits, actual restart/deadline/claim/proof controls passed.
Final audit independently reconstructed all16 formula hashes and checked proof,
checker-log and pinned-checker identities against the original successful DRAT
receipts. It did not rerun the DRAT checker; prior independent proof receipts
are preserved. All93047 additions were independently subdivision-audited again.
Encoded closures are not16 graph exclusions; baseline/symmetry versus learned
benefit has not been isolated. No percent-to-solution or ETA is justified.

One worker,1GiB sampled RSS visit cap,4GiB disk reserve,384MiB available-memory
floor. Peak observed aggregate RSS1118420KiB includes sampling overshoot; a
capped visit was checkpointed/requeued. Thermal/PSI readings unavailable. Of102
visits,79 ended pending proof,16 proof verified,6 visit quantum,1 RSS capped.
Private CDCL learning was lost between visits; only semantic cuts resume.

Storage inventory shows11200738114 bytes in95 DRAT files, including unfinished
proofs. Archive every runtime file losslessly using interleaved proof chunks;
verify all original file sizes/SHA256 by streaming restoration. See
validation/S034/RUNTIME_INVENTORY.json, campaign.tar.xz and FINAL_MANIFEST.json.
Original frozen S032/S033 evidence remains unchanged. Raw runtime files remain
local; the portable archive carries their exact bytes and original provenance.
See docs/S034_RECOVERY.md. The runtime's absolute POSIX paths, ARM64 binaries
and expired deadlines must never be blindly reused on Windows.

D074 queues S035 on the Windows laptop with multiple workers: fresh Windows
acceptance/port, proof-storage controls, measured1/2/3-worker trials and safe
sustained2-or3-worker continuation (four only if justified). S035 is FUTURE /
UNEXECUTED; this closeout is not its invocation. All parked/scientific/publication
gates remain. Sources unchanged; CLM-0120 records this finite internal audit.

One atomic authored commit on existing main under the existing owner workflow;
no branch/PR or force push. Entry main236d97e8c142b8fdf8d124f02f9c1b754693002f,
treef8ae881e2a9a0f6edbfc4412e5d89ac371ac1b49. Final commit/tree/parent and actual
hosted governance jobs are verified after publication and reported to the owner;
zero hosted checks is not PASS. GitHub connected owner transport may be used
because local CLI credentials are unavailable. D044 fallback permanent details
are preserved in the complete paired S035 prompt. Hosted CI checks integrity,
not mathematical search exhaustion. No new external literature/novelty claim.
'''
    write('sessions/S034/CLOSEOUT.md', closeout)
    write('sessions/S034/RESEARCH.md', '''# S034 research — completed finite computation, UNKNOWN

The registered original S11 domain and256 graph-presence prefixes were retained.
Real one-worker search completed102 visits,16 encoded DRAT closures and93047
independently subdivision-checked new clause occurrences. The unresolved ledger
contains86 visited and154 unvisited regions. All pending proofs stay UNKNOWN.
No SAT candidate, certified individual graph decision, stratum or lower-bound
advance. Baseline/symmetry closure benefit was not separately measured.

Formula recipes normalize CRLF to LF while retaining raw source hashes. A first
closeout hash calculation used raw bytes and failed; registered text reconstruction
reproduced the certified hash exactly and the corrected independent calculation
passed all16. No certificate changed. See validation/S034/SUMMARY.json and
sessions/S034/CLOSEOUT.md. Source/claim attribution and9..12 remain unchanged.
''')
    append('sessions/S034/ADVERSARIAL.md', '''Final audit:102 visits do not imply256-region coverage. Sixteen closed encoded regions are not16 individual graph decisions. No baseline-versus-learned ablation was performed. Ninety-three thousand new clauses are occurrences, not necessarily globally distinct. No candidate or complete stratum. Original DRAT receipts verified by hash and reconstructed formulas; not a fresh second proof replay. Unfinished proofs remain UNKNOWN. Private CDCL checkpoints do not exist. The disk reserve actually stopped the campaign. Lossless interleaved compression preserves unfinished proof bytes as well as successes; the portable restore verifies every byte without expanding all proofs to disk by default.''')
    append('sessions/S034/INPUT.md', 'D074 closeout instruction: close out and commit/push, then install the next session as a Windows laptop run using multiple workers. This queues S035 and does not invoke it on the phone.')
    append('sessions/S034/PLAN.md', 'Final disposition: SAFETY_DISK_RESERVE at00:01:43Z; no restart after the expired06:00Z deadline. Preserve all runtime bytes, audit final ledgers/certificates/cuts, close S034 and queue Windows multiworker S035 under D074.')
    append('sessions/S034/PRIOR_ART.md', 'Closeout: no external theorem, novelty or priority claim was added. S029 landscape/source statuses remain frozen; CLM-0120 is solely a finite internal computation record.')
    write('docs/S034_RECOVERY.md', '''# S034 results and Windows recovery

Read validation/S034/SUMMARY.json and sessions/S034/CLOSEOUT.md first. The
campaign stopped cleanly for disk reserve. No S035 or later computation ran.

The final manifest hashes the immutable entry evidence, final results and archive.
campaign.tar.xz is a lossless tar/xz stream: ordinary metadata lives under runtime/;
large DRAT proofs are interleaved1MiB chunks under proof-chunks/<file-id>/<offset>.
RUNTIME_INVENTORY.json maps original paths to byte sizes/SHA256 and proof IDs.
The archive also contains the identical inventory. This layout shares repeated
proof content efficiently without changing any proof bytes. archive_s034.py
stream-verified every original byte after compression. restore_s034.py is stdlib
and portable, rejects unsafe paths/overwrites and verifies every original file.

From the existing repo on Windows, using its pinned Python environment:

    python scripts/restore_s034.py --output artifacts/tmp/S035/imported-s034

This restores logs, exact recipes, checkpoints and accepted cut blocks, while
stream-verifying but omitting large DRAT files. Append --proofs only if the extra
~11.2GB is wanted. validation/S034/new-geometric.lem.gz separately contains all
93047 additions in recorded chronological block order. The original seed archive
is validation/S032/stopped/learned.lem.gz, with exact hash in the S035 prompt.

JSON absolute paths/PIDs/timestamps are provenance, not a live Windows config.
Import/rebase to the new root, verify each source/hash and clear live claim state;
retain the original archived certificates/recipes unchanged. Rebuild Windows
natives from pinned source, establish fresh deadlines/resource caps, independently
validate formulas/proofs for inherited closures, port POSIX lock/process controls,
and run fresh acceptance before science. Never execute the phone guardian config.
The16 closures concern encoded regions, not16 individual graph decisions.

Proof storage dominated the stop:95 files total11200738114 raw bytes. Do not
repeat this growth at multiple-worker scale. Apply audited lossless compression,
explicit budgets and recovery tests. Do not delete the sole copy of any evidence.
Private CDCL state was not saved. The old scheduled deadline has expired.

D044 fallback: ubuntu-24.04, pinned setup and full271+K9 smoke in the SAME job;
permanent validation/S011/SUMMARY.json and validation/S012 evidence. Historical
runs38623187997,38623722547,38624616691,38635879431 do not validate a fresh
Windows multiworker environment. Current hosted scaffold checks are governance.
''')
    write('campaigns/CAM-0039.md', '# CAM-0039 — S034 COMPLETED_SAFETY_STOP_UNKNOWN\n\n'+closeout.split('\n',2)[2])
    state_path = ROOT/'authoritative/STATE.json'
    state = json.loads(state_path.read_text())
    state['as_of'] = '2026-10-22'
    state['last_completed_session'] = 'S034'
    state['recommended_next_session'] = 'S035'
    state['headline_status'] = 'OPEN_NO_CERTIFIED_CHI10_BIPLANAR_WITNESS_AFTER_S034'
    state['next_session_is_future_unexecuted'] = True
    state['s034_completed_runtime'] = state.pop('active_session', state.get('s034_completed_runtime', {}))
    state['s034_completed_runtime'].update(status=result['status'], stopped_utc=result['stopped_utc'],
        stop_reason=result['stop_reason'], no_automatic_S035=True)
    state['s034_science'] = result
    state['latest_session_entry_main'] = '236d97e8c142b8fdf8d124f02f9c1b754693002f'
    state['latest_session_branch'] = 'main'
    state['latest_session_integration'] = dict(status='VERIFY_FINAL_COMMIT_AND_HOSTED_JOBS_AFTER_PUBLICATION',
        entry_main=state['latest_session_entry_main'], authority='D072 existing main workflow; D074 owner closeout/push',
        transport='Authenticated owner GitHub Git-data API; identical local tree; non-force leased main update',
        hosted_post_session_checks='VERIFY_AFTER_PUBLICATION')
    state['next_session_priority'] = 'S035 FUTURE/UNEXECUTED: Windows laptop multiple-worker continuation of S034; fresh Windows acceptance, portable scheduler, storage fixes, measured1/2/3-worker trials, then safe sustained multiple workers. No phone restart.'
    state['open_obligations'] = [state['next_session_priority'],
        'S11 m155/156 UNKNOWN;240 encoded regions unresolved;16 encoded closures are not individual graph decisions.',
        'Regular154 SOURCE_STATED; S10/S9/S8 NOT_RUN; private CDCL state not saved.',
        'All parked queues/publication/formalisation gates unchanged;9<=chi2<=12.']
    state_path.write_text(json.dumps(state, indent=2)+'\n')
    header = '''# S034 completed — S035 Windows multiple-worker continuation queued (D074)

S034 phone campaign stopped safely at22 October2026,00:01:43 UTC for disk reserve.
102 visits;16 encoded regions proof-closed,240 unresolved;93047 checked new
geometric clause occurrences. No graph/stratum/headline advance;9..12 unchanged.
Results archived losslessly. S035 is FUTURE/UNEXECUTED on the Windows laptop:
fresh Windows acceptance/port, storage controls and measured multiple workers.
Owner's next invocation authorises S035; do not launch it on this phone or run
S036 automatically. See authoritative/NEXT_SESSION_PROMPT.md and D074.

'''
    for name in ('AGENTS.md','authoritative/START_HERE.md'):
        p = ROOT/name
        text = p.read_text()
        if text.startswith('# S034 RUNNING'):
            text = text[text.index('# S033 completed'):] if name.endswith('START_HERE.md') else text[text.index('# D072'):]
        if not text.startswith('# S034 completed'):
            p.write_text(header+text)
    append('docs/SESSION_LEDGER.md', '| S034 | 2026-10-21/22 | CAM0039 completed safety stop (disk) |102 visits;16 encoded DRAT closures;93047 checked additions;240 unresolved; no witness/stratum | S035 Windows multiple workers FUTURE/UNEXECUTED (D074) |')
    append('docs/DECISION_LOG.md', '**D074 (owner,2026-10-22):** close S034 and commit/push; queue S035 as Windows laptop multiple-worker continuation. See docs/D074_S035_WINDOWS_MULTIPLE_WORKERS.md. No S035 invocation or phone restart.')
    append('docs/PHASE_GATE_LEDGER.md', 'S034 COMPLETED_SAFETY_STOP_UNKNOWN:16 encoded region proofs,93047 independently checked added clause occurrences, no witness/whole-stratum proof. Phase1 NOT PASSED;9..12 unchanged. S035 Windows multiple workers queued by D074, not executed.')
    append('docs/FAILURE_LEDGER.md', '| F088 (S034) | Phone storage suffices until the overnight deadline |95 retained DRAT files consumed11200738114 bytes;4GiB reserve stopped computation00:01:43Z after102 visits;79 proofs pending UNKNOWN | Losslessly archive all intermediates; laptop must cap/compress proof storage before scaling; preserve all UNKNOWNs and semantic checkpoints |')
    append('docs/FAILURE_LEDGER.md', '| F089 (S034 closeout) | Raw concatenation reproduces text-mode formula hash | Initial final-audit hash mismatch because Windows seed CRLF is normalized by registered materialise() | Correct independent reconstruction to the same universal-newline input/LF output; all16 exact formula hashes pass; original certificates unchanged |')
    append('campaigns/README.md', '**CAM-0039 / S034 COMPLETED_SAFETY_STOP_UNKNOWN:**102 visits,16 encoded proof closures,93047 checked additions;240 unresolved. Lossless full-runtime archive. S035 Windows multiple workers FUTURE/UNEXECUTED (D074). Earlier RUNNING entry above is historical.')
    claims_path = ROOT/'catalogue/CLAIMS.json'
    claims = json.loads(claims_path.read_text())
    claim = dict(id='CLM-0120', status='COMPUTED_EXACT', sources=['SRC-0055'],
        claim='S034 finite audit checks93047 persisted additional single-layer K5/K33-subdivision clause occurrences and exact256-region partition;16 encoded region formulas match original independently verified DRAT receipts.',
        notes='validation/S034/SUMMARY.json and FINAL_MANIFEST.json.102 visits,240 unresolved, safety disk stop. No fresh second DRAT replay; final audit checks reconstructed formula hashes, proof/log hashes and pinned successful original checker receipts. No individual graph decision, whole stratum, learned-rule benefit, exact projected count, ETA or lower-bound advance. Full runtime bytes archived losslessly. SRC-0055 method attribution only.')
    if not any(x['id']=='CLM-0120' for x in claims):
        claims.append(claim)
        claims_path.write_text(json.dumps(claims,indent=2)+'\n')
        append('catalogue/CLAIMS.md', '## CLM-0120 — COMPUTED_EXACT\n\n'+claim['claim']+'\n\n'+claim['notes'])
    print('Recorded S034 closeout and complete paired S035 Windows multiworker prompt; S035 not executed')

if __name__ == '__main__':
    main()
