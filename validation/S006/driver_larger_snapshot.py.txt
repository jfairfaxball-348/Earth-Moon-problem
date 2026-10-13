#!/usr/bin/env python3
"""CAM-0007 cold replay and supervised fixed construction searches."""
import gzip
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from biplanar_cnf import read_edges
from blowup_graph import blowup
from check_layers import main as check_split
from s005_replay import sha
from s005_search import run_logged, compress
from triangulation_cover import Cover

ROOT = Path('validation/S006')
TMP = Path('artifacts/tmp/S006')
CHECKER = str(Path('artifacts/tmp/S004/drat-trim-mingw.exe').resolve())
SOLVER = str(Path('artifacts/tmp/S004/cadical.exe').resolve())


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=1)+'\n', newline='\n')


def replay():
    import networkx, pysat
    old = json.loads(Path('validation/S005_MANIFEST.json').read_text())
    hashes = {name: sha(Path('artifacts/tmp/S004')/name) for name in old['native_sha256']}
    assert hashes == old['native_sha256']
    sources = {}
    for name in ('cadical', 'drat-trim'):
        p = Path('artifacts/tmp/S004')/name
        commit = subprocess.check_output(['git', '-C', str(p), 'rev-parse', 'HEAD'], text=True).strip()
        status = subprocess.check_output(['git', '-C', str(p), 'status', '--porcelain'], text=True)
        assert commit == old[name.replace('-', '_')+'_source'] and not status
        sources[name] = commit
    save(ROOT/'environment.json', dict(python=sys.version, platform=platform.platform(),
         networkx=networkx.__version__, python_sat=pysat.__version__, native_sha256=hashes,
         native_sources=sources, build='S004 binaries reused, no rebuild'))
    # Exact inherited baseline/control implementation, output paths only changed.
    adapter = TMP/'baseline.py'
    text = Path('tools/s005_replay.py').read_text().replace("'validation/S005'", "'validation/S006'")
    text = text.replace("'artifacts/tmp/S005/replay'", "'artifacts/tmp/S006/replay'")
    text = 'import sys\nsys.path.insert(0, '+repr(str(Path('tools').resolve()))+')\n'+text
    adapter.write_text(text, newline='\n')
    result = run_logged([sys.executable, str(adapter)], 2400, ROOT/'baseline.log')
    save(ROOT/'baseline_command.json', result)
    assert result['returncode'] == 0
    audit = run_logged([sys.executable, 'tools/check_s005_archives.py'], 600, ROOT/'S005-packaging.log')
    assert audit['returncode'] == 0
    rows = []
    for oldrow in json.loads(Path('validation/S005/search_results.json').read_text()):
        assert oldrow['verdict'] == 'NON_BIPLANAR_DRAT_VERIFIED'
        idx = oldrow['target']['index']
        rec = oldrow['certificate']
        dest = TMP/'cold'/f'row{idx}'
        dest.parent.mkdir(parents=True, exist_ok=True)
        src = Path(f'validation/S005/search/cover-row{idx}')
        cnf = Path(str(dest)+'.cnf')
        proof = Path(str(dest)+'.drat')
        cnf.write_bytes(gzip.decompress(Path(str(src)+'.cnf.gz').read_bytes()))
        proof.write_bytes(gzip.decompress(Path(rec['archive']).read_bytes()))
        assert sha(cnf) == rec['cnf_sha256'] and sha(proof) == rec['archive_raw_sha256']
        data = json.loads(Path(str(src)+'.cuts.json').read_text())
        c = Cover(read_edges(oldrow['target']['edgefile']), data['lex'], data.get('short_links', False))
        c.cuts = data['cuts']
        c.write_cnf(Path(str(dest)+'.regenerated.cnf'))
        assert cnf.read_bytes() == Path(str(dest)+'.regenerated.cnf').read_bytes()
        log = ROOT/f'cold-row{idx}.check.log'
        run = run_logged([CHECKER, str(cnf), str(proof), '-t', '1200'], 1220, log)
        assert run['returncode'] == 0 and 's VERIFIED' in log.read_text()
        rows.append(dict(index=idx, command=run, cnf_sha256=sha(cnf), proof_sha256=sha(proof), checker='VERIFIED'))
        save(ROOT/'cold_S005.json', rows)
        print('cold S005', idx, 'VERIFIED', flush=True)
    save(ROOT/'BASELINE_PASS.json', dict(full_archived_S005=len(rows), package_audit=audit,
         controls=23, inherited_baseline='K9, row165, row165 bag; 271 archive/colour audits passed'))


def certificate(edgefile, prefix):
    row = {'verdict': 'UNKNOWN'}
    gen = run_logged([sys.executable, 'tools/triangulation_cover.py', 'check',
                      str(edgefile), str(prefix)], 120, str(prefix)+'.regen.log')
    assert gen['returncode'] == 0
    proof = str(prefix)+'.drat'
    solve = run_logged([SOLVER, '-q', '--no-binary', str(prefix)+'.cnf', proof],
                       1220, str(prefix)+'.proof-solve.log')
    row.update(regenerate=gen, solve=solve)
    if solve['returncode'] != 20:
        return row
    check = run_logged([CHECKER, str(prefix)+'.cnf', proof, '-t', '1200'],
                       1220, str(prefix)+'.check.log')
    row['check'] = check
    if check['returncode'] != 0 or 's VERIFIED' not in Path(str(prefix)+'.check.log').read_text():
        return row
    row.update(verdict='NON_BIPLANAR_DRAT_VERIFIED', cnf_sha256=sha(str(prefix)+'.cnf'),
               proof_sha256=sha(proof), proof_bytes=Path(proof).stat().st_size)
    core = str(prefix)+'.core.drat'
    trim = run_logged([CHECKER, str(prefix)+'.cnf', proof, '-l', core, '-t', '600'],
                      620, str(prefix)+'.trim.log')
    row['trim'] = trim
    selected = proof
    if trim['returncode'] == 0 and Path(core).exists() and 's VERIFIED' in Path(str(prefix)+'.trim.log').read_text():
        recheck = run_logged([CHECKER, str(prefix)+'.cnf', core, '-t', '600'],
                            620, str(prefix)+'.core.check.log')
        row['core_check'] = recheck
        if recheck['returncode'] == 0 and 's VERIFIED' in Path(str(prefix)+'.core.check.log').read_text():
            selected = core
    dest = ROOT/'search'/prefix.name
    compress(str(prefix)+'.cnf', str(dest)+'.cnf.gz')
    compress(selected, str(dest)+'.drat.gz')
    row.update(archive=str(dest)+'.drat.gz', archive_raw_sha256=sha(selected),
               archive_raw_bytes=Path(selected).stat().st_size, archive_sha256=sha(str(dest)+'.drat.gz'))
    for suffix in ('.regen.log', '.proof-solve.log', '.check.log', '.trim.log', '.core.check.log'):
        p = Path(str(prefix)+suffix)
        if p.exists():
            shutil.copyfile(p, str(dest)+suffix)
    return row


def search():
    assert (ROOT/'BASELINE_PASS.json').is_file()
    source = json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    old = json.loads(Path('validation/S005/SUMMARY.json').read_text())
    excluded = set(old['previously_excluded']+old['S005_new_exclusions'])
    targets = []
    larger='--larger-one' in sys.argv
    if larger:
        previous=json.loads((ROOT/'search_results.json').read_text())
        passed={r['target']['index'] for r in previous if r['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'}
        assert {29,35,46,47,80,81,82,258,260}<=passed
    indices=(197,17,190,195,187,189) if larger else (29,35,46,47,80,81,82,258,260,162,155,157,159)
    tag='larger_' if larger else ''
    for idx in indices:
        assert idx not in excluded
        g6, w, _ = source[idx]
        edges, _ = blowup(g6, w)
        ef = ROOT/'targets'/f'row{idx}.edges'
        ef.parent.mkdir(parents=True, exist_ok=True)
        ef.write_text(''.join(f'{a} {b}\n' for a,b in edges), newline='\n')
        targets.append(dict(index=idx,g6=g6,w=w,n=sum(w),m=len(edges),D=6*sum(w)-12-len(edges),
                            edgefile=str(ef),edge_sha256=sha(ef)))
    save(ROOT/(tag+'targets.json'), targets)
    (ROOT/'search').mkdir(exist_ok=True)
    (TMP/'search').mkdir(exist_ok=True)
    rows = []
    caps = {1:0,2:0}
    for t in targets:
        prefix = TMP/'search'/f"cover-row{t['index']}"
        row = dict(target=t, verdict='UNKNOWN')
        if caps[t['D']] >= 2:
            row['reason'] = 'NOT_RUN after two consecutive lane caps/failures'
        else:
            run = run_logged([sys.executable,'tools/triangulation_cover.py',t['edgefile'],
                              str(prefix),'300','--lex'],320,str(prefix)+'.run.log')
            row['run'] = run
            meta = Path(str(prefix)+'.result.json')
            if run['returncode'] == 0 and meta.exists():
                row['search'] = json.loads(meta.read_text())
                if row['search']['verdict'] == 'UNSAT':
                    row['certificate'] = certificate(t['edgefile'], prefix)
                    row['verdict'] = row['certificate']['verdict']
                elif row['search']['verdict'] == 'SAT_CHECKED':
                    check_split(t['edgefile'],str(prefix)+'.split.json')
                    shutil.copyfile(str(prefix)+'.split.json', ROOT/'search'/f"row{t['index']}.split.json")
                    row['verdict'] = 'BIPLANAR_CHECKED_PENDING_CHROMATIC_REPLAY'
            caps[t['D']] = caps[t['D']]+1 if row['verdict']=='UNKNOWN' else 0
            for suffix in ('.cuts.json','.result.json','.run.log'):
                p = Path(str(prefix)+suffix)
                if p.exists():
                    shutil.copyfile(p,ROOT/'search'/(prefix.name+suffix))
        rows.append(row)
        save(ROOT/(tag+'search_results.json'),rows)
        print(t['index'],row['verdict'],row.get('run',{}).get('seconds','not run'),flush=True)
        if row['verdict'].startswith('BIPLANAR_CHECKED'):
            break


if __name__ == '__main__':
    ROOT.mkdir(parents=True,exist_ok=True)
    TMP.mkdir(parents=True,exist_ok=True)
    {'replay':replay,'search':search}[sys.argv[1]]()
