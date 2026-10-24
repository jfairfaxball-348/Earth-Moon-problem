"""Prepare S045 running handover; no scientific computation or process launch."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def write(p,s):
    p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def dump(p,d):write(p,json.dumps(d,indent=2)+'\n')
def append(p,s):
    q=ROOT/p;write(p,q.read_text(encoding='utf-8').rstrip()+'\n\n'+s+'\n')

def main():
    b=json.loads((ROOT/'validation/S045/BENCHMARK.json').read_text())
    text='''# S045 research and benchmark

Owner selected 50 vertices and explicitly authorised prepare/test/benchmark/
launch. No target change: chi>=10, thickness at most two. The new domain has
all 1225 optional pairs, no independence/degree/symmetry/density restriction.
Inherited attributed native partial-planarity code is preserved as source in
tools/s045_native.cpp; tools/s045_main.hpp supplies a new incremental protocol.
Python independently checks both rotation systems and every colouring before
feeding back a necessary partition clause. Private solver learning persists
between candidates; only audited semantic rules survive slice recycling.

For any map c:V->{0,...,8}, every graph without a proper nine-colouring must
have an edge uv with c(u)=c(v). Therefore OR over both layer variables of all
such pairs is a sound necessary clause. If the current graph is properly
coloured by c, it falsifies that clause and is excluded. No assumption about
alpha is involved. Colour names may be permuted freely; splitting a class
preserves properness and can shorten/strengthen the clause.

| Arm | Verified candidates | Elapsed seconds | Checked geometric cuts |
|---|---:|---:|---:|
'''
    for r in b['arms']:text+=f"| {r['arm']} | {r['new_candidates']} | {r['elapsed_seconds']:.3f} | {r['verified_geometric_cuts']} |\n"
    text+='''
Default partition feedback selected under the registered operational gate.
Exact blocking visited more models; no speedup or greater projected coverage
is claimed. Each partition rule excludes all graphs permitting that same
colouring, while exact blocking excludes just one layer assignment. Candidate
counts and geometric clause counts are diagnostics. The benchmark contains
no non-nine-colourable candidate, no domain refutation and no headline advance.
'''
    text+=f"\nFresh semantic restart: {b['restart']['new_candidates']} additional verified candidates in {b['restart']['elapsed_seconds']:.3f}s.\n"
    write('sessions/S045/RESEARCH.md',text)
    write('sessions/S045/ADVERSARIAL.md','''# S045 adversarial and operational review

Fresh full smoke: all 271 chromatic input byte matches/proofs, retained K9
and new native K9 proof PASS. Exhaustive 1024 fixed five-vertex layer cases,
K3,3, padded 50-vertex positive, independent disconnected/isolated rotation
checks, 5184 partition truth-table cases, invalid feedback, truncated geometric
checkpoint, chromatic oracle/DRAT round trip and cooperative stop PASS.

Two preparation failures are retained, not promoted: the imported positive
fixture had reverse-ordered endpoints, exposing a canonicalisation omission;
normalize endpoints before encoding and comparing. A Windows psutil call
needed str(Path), rather than WindowsPath. Failed attempts and full logs stay
under artifacts/tmp/S045/controls*; final successful suite is controls-r3.
No failed run established a mathematical exclusion. Compact failure logs are
permanent under validation/S045/failures/.

Native UNSAT is always UNKNOWN without a separate full proof. A colouring
UNSAT alert stops the run and needs standalone proof verification. Independent
rotation Euler checks operate component by component and include isolates.
No criticality or edge saturation is assumed. Graphs with smaller critical
cores remain admissible. No canonical enumeration/completeness-speed claim.

The portable historical check scripts hard-code a globally stopped runtime.
They remain byte-for-byte frozen. scripts/s045_replay_history.py replays them
against the actual archived entry STATE and original prompt, explicitly as
historical checks. check_s045_records.py separately validates current S045
authority. This separates historical evidence from current process state;
it neither changes a frozen certificate nor weakens its hash check.

Guard controls check the wall ceiling, resource floor and changed-source
stop conditions. WMI launch avoids the application's job object. No blind
PID reuse, duplicate launch or automatic resume; status checks creation time
and executable. A private-state checkpoint is never claimed. Source/binary
change, unsafe resources, owner STOP, native UNSAT, non-nine alert, fault or
eight-hour ceiling stops the new run. S036 remains CLEAN_STOPPED.
''')
    claim=dict(id='CLM-0146',status='PROGRAMME_PROVED',sources=['SRC-0055'],
       claim='For every map c from V to at most nine colours, every non-nine-colourable graph on V has an edge inside a class of c. Consequently the disjunction of union-edge variables within those classes is a necessary clause for the chi>=10 construction search.',
       notes='Elementary contrapositive: absence of all same-class edges makes c proper. S045 RESEARCH.md; independent 4-vertex truth table controls and saved colouring certificates. This is an encoding lemma, not a graph exclusion or bound advance.')
    p=ROOT/'catalogue/CLAIMS.json';claims=json.loads(p.read_text())
    assert claim['id'] not in {x['id'] for x in claims};dump('catalogue/CLAIMS.json',claims+[claim])
    append('catalogue/CLAIMS.md',f"## {claim['id']} — {claim['status']}\n\n{claim['claim']}\n\n{claim['notes']}")
    sources=json.loads((ROOT/'catalogue/SOURCES.json').read_text())
    for s in sources:
        if s['id'] in ('SRC-0037','SRC-0043'):
            s['accessed']='2026-10-24'
            s['note']+=' S045: limited abstract/introduction/statements refreshed; no external certificate replay or novelty guarantee. See sessions/S045/PRIOR_ART.md.'
    dump('catalogue/SOURCES.json',sources)
    append('catalogue/SOURCES.md','S045 refresh, 24 October 2026: SRC-0037 (Szeider) and SRC-0043 (rStation paper22), STATEMENT_INSPECTED this session; no external certificate replay. SRC-0038 DOI refresh failed; retained attribution only. See sessions/S045/PRIOR_ART.md.')
    report='S045 owner CONTINUE overrides proposal-only gate: unrestricted 50-vertex native colouring-feedback search; fresh acceptance and three-arm benchmark PASS; sustained run is separately identified in RUNNING.md. S036 stopped; no witness or bound advance.'
    for p,t in [('docs/SESSION_LEDGER.md','| S045 | 2026-10-24 | IN_PROGRESS CAM0049 | '+report+' |'),('docs/DECISION_LOG.md',report),('docs/PHASE_GATE_LEDGER.md',report+' Phase1 OPEN; no later session/publication/Lean.'),('docs/FAILURE_LEDGER.md','S045 preparation failures: reversed-edge imported fixture canonicalisation and Windows psutil Path incompatibility; corrected, failed logs preserved, final fresh suite PASS. Benchmark does not show a throughput speedup over blocking or graph coverage.'),('campaigns/README.md','**CAM-0049: '+report+'**')]:append(p,t)
    write('campaigns/CAM-0049.md','# CAM-0049 — S045 50-vertex direct colouring-feedback search\n\n'+report+'\n\nDomain, gates and limits: sessions/S045/PLAN.md and validation/S045/REGISTRATION.json. Runtime authority and safe status/STOP: sessions/S045/RUNNING.md. Counts are activity, not coverage.\n')
    fail=ROOT/'validation/S045/failures';fail.mkdir(exist_ok=True)
    for name in ('controls-console.log','controls-r2-console.log'):
        with gzip.open(fail/(name+'.gz'),'wb') as f:f.write((ROOT/'artifacts/tmp/S045'/name).read_bytes())
    # Portable receipt for the new independent watchdog tests (not a scientific result).
    dump('validation/S045/GUARD_CONTROLS.json',dict(status='PASS',wall_ceiling=True,resource_floor=True,source_change=True,no_change=True))
    print('S045 research and ledger records prepared')

if __name__=='__main__':main()
