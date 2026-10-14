#!/usr/bin/env python3
"""CAM-0007 packaging/label/hash audit; proof replay is a separate command."""
import gzip
import json
from pathlib import Path
from biplanar_cnf import read_edges
from blowup_graph import blowup
from s005_replay import sha
from triangulation_cover import Cover


def main():
    src=json.loads(Path('validation/S003/survivors_alpha_ge3.json').read_text())
    rows=json.loads(Path('validation/S006/search_results.json').read_text())
    extra=Path('validation/S006/larger_search_results.json')
    if extra.exists():
        rows+=json.loads(extra.read_text())
    known=json.loads(Path('validation/S005/SUMMARY.json').read_text())
    before=set(known['previously_excluded']+known['S005_new_exclusions'])
    chi=json.loads(Path('validation/S006/chromatic/results.json').read_text())
    chi_extra=Path('validation/S006/chromatic/larger_results.json')
    if chi_extra.exists():
        chi+=json.loads(chi_extra.read_text())
    lower={r['index']:r for r in chi}
    seen=set();new=set()
    for row in rows:
        t=row['target'];idx=t['index']
        assert idx not in seen and idx not in before
        seen.add(idx)
        g,w,_=src[idx]
        edges,_=blowup(g,w)
        assert t['g6']==g and t['w']==w and read_edges(t['edgefile'])==edges
        assert t['n']==sum(w) and t['m']==len(edges) and t['D']==6*sum(w)-12-len(edges)
        assert sha(t['edgefile'])==t['edge_sha256']
        ch=lower[idx]
        assert ch['checker']=='VERIFIED' and ch['chi']==10
        assert all(ch['ten_colouring'][a]!=ch['ten_colouring'][b] for a,b in edges)
        assert 's VERIFIED' in Path(f'validation/S006/chromatic/row{idx}.check.log').read_text()
        if row['verdict']=='NON_BIPLANAR_DRAT_VERIFIED':
            r=row['certificate']
            prefix=Path(f'validation/S006/search/cover-row{idx}')
            cnf=gzip.decompress(Path(str(prefix)+'.cnf.gz').read_bytes())
            data=json.loads(Path(str(prefix)+'.cuts.json').read_text())
            c=Cover(edges,data['lex'],data.get('short_links',False));c.cuts=data['cuts']
            regen=Path(f'artifacts/tmp/S006/audit-row{idx}.cnf');c.write_cnf(regen)
            assert regen.read_bytes()==cnf and sha(regen)==r['cnf_sha256']
            import hashlib
            raw=gzip.decompress(Path(r['archive']).read_bytes())
            assert hashlib.sha256(raw).hexdigest()==r['archive_raw_sha256']
            assert len(raw)==r['archive_raw_bytes'] and sha(r['archive'])==r['archive_sha256']
            suffix='.core.check.log' if 'core_check' in r and r['core_check']['returncode']==0 else '.check.log'
            assert 's VERIFIED' in Path(str(prefix)+suffix).read_text()
            new.add(idx)
        else:
            assert row['verdict']=='UNKNOWN', 'Positive requires separate chromatic replay before closeout'
    summary=json.loads(Path('validation/S006/SUMMARY.json').read_text())
    assert summary['S006_new_exclusions']==sorted(new)
    assert summary['excluded_indices']==sorted(before|new)
    assert summary['remaining_unknown_indices']==sorted(set(range(271))-before-new)
    assert summary['remaining_unknown']==271-len(before|new)
    print('PASS S006 fixed labels, regenerated CNFs, compact raw/archive hashes and exact frontier;',len(new),'new exclusions')


if __name__=='__main__':
    main()
