"""S028 variant of scripts/replay_s027_certificates.py. Cold replay of every S027-style non-biplanarity / domain certificate (local, pinned).

For each certified item: regenerate the CNF from the stored lemma/learned record in
a fresh process, require its SHA-256 to equal the certificate's cnf_sha256,
decompress the stored DRAT, require its SHA-256, and re-check with the pinned
drat-trim. Writes validation/S028/REPLAY.json. Not a new search.
Usage: python scripts/replay_s027_certificates.py ROOTDIR(validation/S027/local)
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
CHECKER = os.environ.get('EMP_DRAT_TRIM', str(ROOT / 'artifacts/tmp/S004/drat-trim-mingw.exe'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(cnf, cert, gzproof, td):
    proof = Path(td) / 'p.drat'
    proof.write_bytes(gzip.decompress(Path(gzproof).read_bytes()))
    rec = {'cnf_sha256_match': sha(cnf) == cert['cnf_sha256'], 'drat_sha256_match': sha(proof) == cert['drat_sha256']}
    if rec['cnf_sha256_match'] and rec['drat_sha256_match']:
        r = subprocess.run([CHECKER, str(cnf), str(proof), '-t', '3600'], capture_output=True, text=True, timeout=4000)
        rec['drat_trim'] = 'VERIFIED' if 's VERIFIED' in r.stdout else 'FAIL'
    rec['ok'] = rec.get('drat_trim') == 'VERIFIED'
    return rec


def minor(d, two, td):
    cert = json.loads((d / 'minor.certificate.json').read_text())
    prefix = Path(td) / 'minor'
    Path(str(prefix) + '.lemmas.json').write_bytes(gzip.decompress((d / 'lemmas.json.gz').read_bytes()))
    out = Path(td) / 'regen.cnf'
    if two:
        # s027 regen requires an existing PREFIX.cnf to compare; write via its class directly.
        code = ('import sys,json;sys.path.insert(0,r"%s");from s027_two_branch import TwoBranchK;'
                'from biplanar_cnf import read_edges;d=json.load(open(r"%s"));'
                's=int(d["flags"][d["flags"].index("--two-branch")+1]);c=TwoBranchK(read_edges(r"%s"),s);'
                'g=json.loads(json.dumps(c.data()));assert all(g[k]==d[k] for k in g if k!="lemmas");'
                'c.lemmas=[[tuple(e) for e in K] for K in d["lemmas"]];cl=c.clauses();'
                'open(r"%s","w",newline="\\n").write(f"p cnf {c.nv} {len(cl)}\\n"+"".join(" ".join(map(str,x))+" 0\\n" for x in cl))'
                % (ROOT / 'tools', str(prefix) + '.lemmas.json', d / 'graph.edges', out))
        subprocess.run([PY, '-c', code], check=True, timeout=3600)
    else:
        subprocess.run([PY, str(ROOT / 'tools/s025_regen_cnf.py'), str(d / 'graph.edges'),
                        str(prefix) + '.lemmas.json', str(out)], check=True, timeout=3600, capture_output=True)
    return check(out, cert, d / 'minor.drat.gz', td)


def domain(d, td):
    cert = json.loads((d / 'domain.certificate.json').read_text())
    sys.path.insert(0, str(ROOT / 'tools'))
    from s027_check_learned import regen
    out = Path(td) / 'domain.cnf'
    out.write_bytes(regen(json.load(gzip.open(d / 'LEARNED.json.gz', 'rt'))))
    return check(out, cert, d / 'domain.drat.gz', td)


def main(base):
    base = Path(base)
    os.environ['EMP_S027_EXTRA_OBSTRUCTIONS'] = str(base / 'EXTRA_OBSTRUCTIONS.json')
    rows = []
    items = [(p.parent.name, p.parent, False) for p in sorted((base / 'descent').glob('D*/minor.certificate.json'))]
    for name, d, two in items:
        with tempfile.TemporaryDirectory() as td:
            r = minor(d, two, td)
        r['item'] = name
        rows.append(r)
        print(name, r, flush=True)
    for p in sorted((base / 'source').glob('profile*/domain.certificate.json')):
        with tempfile.TemporaryDirectory() as td:
            r = domain(p.parent, td)
        r['item'] = p.parent.name
        rows.append(r)
        print(p.parent.name, r, flush=True)
    res = {'items': len(rows), 'all_verified': all(r['ok'] for r in rows), 'rows': rows,
           'checker': CHECKER, 'checker_sha256': sha(CHECKER)}
    (ROOT / 'validation/S028/REPLAY.json').write_text(json.dumps(res, indent=1), newline='\n')
    print('REPLAY', res['items'], 'all_verified', res['all_verified'])


if __name__ == '__main__':
    main(sys.argv[1])
