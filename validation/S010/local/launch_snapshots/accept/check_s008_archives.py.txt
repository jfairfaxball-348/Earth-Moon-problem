"""Cold S008 partial/full CNFs, exact labels and finite-control accounting."""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from blowup_graph import blowup
from biplanar_cnf import read_edges
from s008_cover import FullCover
from s005_search import compress
from s005_replay import sha
from s007_run import save

ROOT=Path('validation/S008');TMP=Path('artifacts/tmp/S008')


def main():
    baseline=Path('validation/S008')
    assert json.loads((baseline/'BASELINE_PASS.json').read_text())['cold_full_proofs']==40
    assert json.loads((baseline/'supervised_controls_command.json').read_text())['returncode']==0
    assert len(json.loads((baseline/'independent_cut_enumeration.json').read_text()))==23
    assert len(json.loads((baseline/'new_clause_controls.json').read_text()))==27
    if ROOT!=baseline:
        assert json.loads((ROOT/'controls_command.json').read_text())['returncode']==0
        assert json.loads((ROOT/'counter_semantics.json').read_text())['auxiliary_extension_checks']==2304
    source=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    rows=json.loads((ROOT/'search_results.json').read_text());new=[];pack=[]
    for row in rows:
        t=row['target'];idx=t['index'];g,w,_=source[idx];edges,_=blowup(g,w)
        assert t['g6']==g and t['w']==w and read_edges(t['edgefile'])==edges
        assert sha(t['edgefile'])==t['edge_sha256'] and t['D']==2
        assert all(t['ten_colouring'][a]!=t['ten_colouring'][b] for a,b in edges)
        assert 's VERIFIED' in (baseline/f'chi-row{idx}.check.log').read_text()
        prefix=TMP/'search'/f'cover-row{idx}';dest=ROOT/'search'/prefix.name
        data=Path(str(dest)+'.cuts.json')
        if data.exists():
            d=json.loads(data.read_text());c=FullCover(edges,d['lex'],d.get('short_links',False))
            assert c.static==d['static'];c.cuts=d['cuts']
            regen=Path(str(prefix)+'.audit.cnf');c.write_cnf(regen)
            initial=Path(str(prefix)+'.initial.cnf')
            # Cold regeneration of the actual pre-solve file, separately from lazy-cut CNF.
            c.cuts=[];fresh=Path(str(prefix)+'.initial.audit.cnf');c.write_cnf(fresh)
            assert initial.read_bytes()==fresh.read_bytes()
            full=row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED'
            archive=str(dest)+('.cnf.gz' if full else '.partial.cnf.gz')
            if full:assert regen.read_bytes()==gzip.decompress(Path(archive).read_bytes())
            else:compress(regen,archive)
            initial_archive=archive if sha(initial)==sha(regen) else str(dest)+'.initial.cnf.gz'
            if initial_archive!=archive:compress(initial,initial_archive)
            p=dict(index=idx,grade='FULL_CNF_WITH_SEPARATE_DRAT' if full else 'PARTIAL_NECESSARY_CNF_NOT_A_REFUTATION',cuts=len(d['cuts']),
                static=d['static'],raw_sha256=sha(regen),archive=archive,archive_sha256=sha(archive),
                initial_raw_sha256=sha(initial),initial_archive=initial_archive,initial_archive_sha256=sha(initial_archive),
                identical_initial_and_last_cut_archive_shared=initial_archive==archive)
            pack.append(p)
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
            rec=row['certificate'];raw=gzip.decompress(Path(rec['archive']).read_bytes())
            assert regen.read_bytes()==gzip.decompress(Path(str(dest)+'.cnf.gz').read_bytes())
            assert sha(regen)==rec['cnf_sha256']
            assert hashlib.sha256(raw).hexdigest()==rec['archive_raw_sha256']
            assert sha(rec['archive'])==rec['archive_sha256']
            assert rec['cold_retained_check']['returncode']==0
            assert 's VERIFIED' in Path(str(dest)+'.cold.check.log').read_text()
            new.append(idx)
        elif row['verdict']=='BIPLANAR_CHECKED_CHI10':
            from check_layers import main as check_split
            check_split(t['edgefile'],str(ROOT/'search'/f'row{idx}.split.json'))
        else:assert row['verdict']=='UNKNOWN'
        if row['verdict']=='UNKNOWN' and row.get('certificate'):
            partial=Path(str(prefix)+'.drat')
            if partial.exists():
                row['unverified_native_export']=dict(path=str(partial.resolve()),sha256=sha(partial),bytes=partial.stat().st_size,
                    grade='POST_WORKER_CAPTURE_UNVERIFIED_EXPORT_NOT_AN_EXCLUSION')
                row['certificate'].setdefault('verdict','UNKNOWN')
    save(ROOT/'search_results.json',rows)
    save(ROOT/'partial_cnf_audit.json',pack)
    old=json.loads(Path('validation/S007/SUMMARY.json').read_text())
    summary=dict(old)
    summary.pop('S007_new_exclusions');summary['S008_new_exclusions']=sorted(new)
    summary['excluded_indices']=sorted(set(old['excluded_indices'])|set(new))
    summary['remaining_unknown_indices']=sorted(set(range(271))-set(summary['excluded_indices']))
    summary['remaining_unknown']=len(summary['remaining_unknown_indices'])
    summary['registered_unknown']=[r['target']['index'] for r in rows if r['verdict']=='UNKNOWN']
    summary['registered_not_run']=[r['target']['index'] for r in rows if 'NOT_RUN' in r.get('reason','')]
    summary['wall_capped']=[r['target']['index'] for r in rows if r.get('run',{}).get('reason')=='external wall cap']
    summary['D2_remaining_unknown']=sorted(set(old['D2_remaining_unknown'])-set(new))
    summary['stratum_remaining_counts']['2']=len(summary['D2_remaining_unknown'])
    summary['new_full_encoding']='completion-K5-input-K33-v1'
    summary['prior_relaxation_verdicts']=summary.pop('global_relaxation_verdicts')
    summary['prior_heavy_cover_verdicts']=summary.pop('heavy_cover_verdicts')
    summary['prior_heavy_K7I5_cegar_verdict']=summary.pop('heavy_K7I5_cegar_verdict')
    summary['headline_advance']=any(r['verdict']=='BIPLANAR_CHECKED_CHI10' for r in rows)
    summary_name='sequential_SUMMARY.json' if '--verify-only' in sys.argv and ROOT==baseline else 'SUMMARY.json'
    save(ROOT/summary_name,summary)
    print('PASS exact target labels/lower proofs; cold partial/full CNFs;',len(new),'new checked exclusions;',summary['remaining_unknown'],'UNKNOWN')


if __name__=='__main__':
    if '--tree' in sys.argv:
        from s008_tree import TreeFullCover
        FullCover=TreeFullCover
        ROOT=ROOT/'tree';TMP=TMP/'tree'
    main()
