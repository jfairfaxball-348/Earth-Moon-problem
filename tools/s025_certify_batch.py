#!/usr/bin/env python3
"""S025: for every minor-CEGAR UNSAT prefix, independently re-justify the CNF clauses,
then re-solve natively with DRAT and check with drat-trim.  Records one JSON per graph
and a combined summary.  Usage: s025_certify_batch.py DIR OUTDIR TAG1 TAG2 ...
(each TAG names DIR/C5-TAG.edges and DIR/mC_TAG.{cnf,lemmas.json,result.json})
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from s025_certify import certify, sha   # noqa: E402

if __name__ == '__main__':
    d, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for tag in sys.argv[3:]:
        res = json.loads((d / f'mC_{tag}.result.json').read_text())
        rec = {'tag': tag, 'cegar': res, 'edges_sha256': sha(d / f'C5-{tag}.edges')}
        if res['verdict'] == 'UNSAT':
            chk = subprocess.run([sys.executable, str(ROOT / 'tools/s025_check_minor_cert.py'),
                                  str(d / f'C5-{tag}.edges'), str(d / f'mC_{tag}')],
                                 capture_output=True, text=True, timeout=3600)
            rec['justification'] = json.loads(chk.stdout.strip().splitlines()[-1]) if chk.returncode == 0 \
                else {'verdict': 'FAILED', 'stderr': chk.stderr[-1500:]}
            rec['drat'] = certify(d / f'mC_{tag}.cnf', out, 36000, 36000)
            rec['lemmas_sha256'] = sha(d / f'mC_{tag}.lemmas.json')
        rec['certified'] = (res['verdict'] == 'UNSAT' and
                            rec.get('justification', {}).get('verdict') == 'ALL_CLAUSES_JUSTIFIED' and
                            rec.get('drat', {}).get('verdict') == 'UNSAT_DRAT_VERIFIED')
        (out / f'C5-{tag}.certificate.json').write_text(json.dumps(rec, indent=1))
        summary.append({'tag': tag, 'certified': rec['certified'],
                        'cegar_seconds': res.get('seconds'),
                        'drat_verdict': rec.get('drat', {}).get('verdict')})
        print(json.dumps(summary[-1]), flush=True)
    (out / f'batch_{sys.argv[3]}_{len(sys.argv)-3}.json').write_text(json.dumps(summary, indent=1))
