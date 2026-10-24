"""Record the accepted streaming revision and live running handover."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

def put(name,text): (ROOT/name).write_text(text,encoding='utf-8',newline='\n')

def main():
    b=json.loads((ROOT/'validation/S045/BENCHMARK.json').read_text())
    snap=json.loads((ROOT/'validation/S045/LAUNCH_SNAPSHOT.json').read_text());obs=snap['observed_status']
    table='| Arm | Candidates | Seconds | Geometric rules |\n|---|---:|---:|---:|\n'
    for row in b['arms']:
        table+=f"| {row['arm']} | {row['new_candidates']} | {row['elapsed_seconds']:.3f} | {row['verified_geometric_cuts']} |\n"
    put('sessions/S045/RUNNING.md',f'''# S045 sustained 50-vertex search — IN PROGRESS

Owner authorises preparation, testing, benchmarking and search. S036 remains
CLEAN_STOPPED. No witness or domain exclusion; 9<=chi_2<=12 unchanged.

Current accepted configuration: {b['selected_arm']}. Positive edge preferences
are a heuristic, not a restriction. Domain: all 1225 optional pairs on 50
vertices, two disjoint planar layers, direct non-nine-colourability; no alpha,
degree, symmetry or exact-density restriction. Fresh full 271+K9 acceptance,
exhaustive native controls, independent rotations/colourings, DRAT round trip,
cooperative STOP and semantic restart PASS. Repeated final benchmark:

{table}
Semantic restart added {b['restart']['new_candidates']} candidates. Counts are activity,
not graph coverage, speedup or an ETA. Certificates: validation/S045/benchmark-streaming.
Original benchmark/source receipts remain under benchmark and before-streaming.

## Runtime authority

Root artifacts/tmp/S045/campaign. CAMPAIGN.json identifies the controller;
STATUS.json the slice; IDENTITY.json the generator; LAUNCH.json WMI dispatch.
ERROR.json / GUARD_STOP.json override stale labels. Match PID, creation time
and executable. Never remove a lock, duplicate a run or automatically resume
a STOP/error. No S035/S036 controls. Read-only status and cooperative STOP:

    .venv/Scripts/python.exe scripts/s045_campaign.py status
    .venv/Scripts/python.exe scripts/s045_campaign.py stop

One generator with serial oracle, 3 GiB solver/controller private-memory cap,
1.5 GiB available-RAM floor and 10 GiB disk reserve. Eight-hour wall ceiling
from original start 16:23:36 UTC on 24 October 2026, including maintenance.
WMI launch avoids the desktop app job. Watchdog latches STOP on resource
breach, changed source/binary or ceiling. POWER.json records a bounded Windows
keep-awake request, released when the exact controller exits or ceiling arrives;
the display is not kept on. No recurring task or unattended successor session.

600-second slices retain all audited semantic rules and discard private CDCL.
Learning persists between candidates inside a slice; no private-state checkpoint.
After owner STOP verify actual exits and retain every journal, log and receipt.

## Preserved work and maintenance

First slice completed 38042 checked nine-colourable candidates and 111073
checked geometric rule occurrences. All data are permanently compressed under
validation/S045/initial-slice. Memory buffering grew; cooperative maintenance
retired the old processes and preserved all rules. Streaming replays exactly
the same CNF from all 38042 rows with about 33 MB replay-process memory.
Wrong vertex count, colour target, feedback mode and partial rows are rejected.
Full native controls and the three-arm benchmark were repeated after the change.

Operator-directed resume-maintenance requires accepted byte hashes, exact old
identities exited, no owner STOP and preserved control files. The SAME campaign
resumes every rule under the original ceiling; this is not automatic recovery.
Maintenance evidence and initial source/benchmark are permanent.

Latest permanent launch observation: {obs['candidates']} total candidates,
{obs['new_candidates']} new since restart, controller PID {obs['controller']['pid']},
generator PID {obs['generator']['pid']}, about {obs['elapsed_seconds']:.1f}s into that slice.
Controller private memory {snap['controller_private_bytes']/2**20:.1f} MiB. Exact identity
and increasing native CPU checked. These are historical observations; read
runtime files for current identities. Receipt: validation/S045/LAUNCH_SNAPSHOT.json.

## Reproduction and eventual closeout

Build recipe scripts/build_s045_native.py and validation/S045/BUILD.json pin
source and executable bytes. Existing accepted packages/compiler were reused.
Portable replay: python scripts/check_s045_records.py. Immutable historical
checks use the actual archived entry state; current S045 is checked separately.
Native scientific replay requires fresh full cloud_smoke.py. Alternate Actions
runner: docs/CLOUD_ENVIRONMENT.md and validation/S011/SUMMARY.json, setup and
full smoke in the SAME job.

Bare native UNSAT or a non-nine alert stops with UNKNOWN until full independent
proofs pass. A witness needs labelled V,E1,E2, independently checked planar
rotations, standalone chromatic DRAT, and a proper ten-colouring for chi=10.
After this campaign ends, reconcile/retain final evidence and close S045;
install identical full S046 FUTURE/UNEXECUTED prompts in authoritative/ and
sessions/S045/, print the full prompt and verified GitHub links, then stop
before S046. There is no S045 closeout verdict yet. No publication/Lean authority.
''')
    revision=f'''\n## Streaming revision and repeated benchmark

38042 candidates and 111073 geometric rule occurrences from the first slice
are preserved. Exact regenerated CNF bytes from all rows match; replay private
memory about 33 MB. Wrong n/k/mode and partial checkpoint rows rejected.
Fresh native acceptance repeated after the streaming change.

{table}
Selected {b['selected_arm']}; fresh restart added {b['restart']['new_candidates']} candidates
in {b['restart']['elapsed_seconds']:.3f}s. This operational selection does not
establish a statistical speedup. Original source/receipts and both benchmarks
remain archived. Same campaign resumes all saved rules, original ceiling.
'''
    p=ROOT/'sessions/S045/RESEARCH.md';put(str(p.relative_to(ROOT)),p.read_text(encoding='utf-8')+revision)
    p=ROOT/'sessions/S045/ADVERSARIAL.md'
    put(str(p.relative_to(ROOT)),p.read_text(encoding='utf-8')+'''
Streaming revision: final acceptance suite controls-streaming-r2 PASS; original
controls-r3/source/benchmark receipts retained under before-streaming. Initial
slice fully archived. Maintenance stopped cooperatively; exact former process
identities exited. The pre-stop second-slice entry has zero new candidates and
no generator, and is not counted as new scientific execution. Explicit operator
resume checks old identities and owner STOP, preserves controls and all journals,
and retains the original ceiling. This is current owner-authorised preparation
and search, not automatic recovery of an owner stop. Runtime guard/keep-awake
helpers are newly scoped to S045 only. No historical process was touched.
''')
    p=ROOT/'authoritative/STATE.json';s=json.loads(p.read_text())
    s['current_computation']='RUNNING';s['active_session']['stage']='SUSTAINED_SEARCH_STREAMING'
    s['s045_preparation'].update(status='STREAMING_ACCEPTED_AND_RESUMED',selected=b['selected_arm'],
        initial_slice_candidates=38042,initial_slice_geometric_rules=111073,original_ceiling_preserved=True)
    put(str(p.relative_to(ROOT)),json.dumps(s,indent=2)+'\n')
    report='S045 streaming maintenance: 38042 candidate records / 111073 geometric rule occurrences preserved; exact bounded-memory CNF replay PASS; fresh controls/benchmark PASS; '+b['selected_arm']+' selected; same campaign resumed under original ceiling. No witness or coverage claim.'
    for name in ('docs/SESSION_LEDGER.md','docs/DECISION_LOG.md','docs/FAILURE_LEDGER.md','campaigns/CAM-0049.md'):
        p=ROOT/name;put(name,p.read_text(encoding='utf-8').rstrip()+'\n\n'+report+'\n')
    sys.path.insert(0,str(ROOT/'scripts'))
    from s045_runtime import guard_reason
    assert guard_reason(0,28800,{},None)=='EIGHT_HOUR_WALL_CEILING'
    assert guard_reason(0,1,{},'DISK_RESERVE')=='DISK_RESERVE'
    assert guard_reason(0,1,{'tools/s045_search.py':'wrong'},None).startswith('SOURCE_OR_BINARY_CHANGED')
    assert guard_reason(0,1,{},None) is None
    print('S045 final running handover and guard checks PASS')

if __name__=='__main__':main()
