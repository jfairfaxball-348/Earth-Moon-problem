#!/usr/bin/env python3
"""Cloud environment acceptance check (decision D043).

Re-checks retained programme proofs with the Linux builds made by
scripts/cloud_setup.sh, writing only under artifacts/tmp/cloud_smoke/:

  * all 271 S004 non-9-colourability proofs (validation/S004/chi10): the CNF is
    regenerated from the corpus and must match the recorded SHA-256 byte for
    byte, then the retained DRAT is checked by the Linux drat-trim;
  * a fresh CaDiCaL solve of the K9 CNF whose new DRAT proof is checked;
  * the K9 non-biplanarity control: Cover CNF regenerated in a fresh process
    (sequential representation only, see F045) and its retained DRAT checked.

A PASS means the cloud toolchain reproduces recorded inputs and accepts recorded
proofs. It is an environment check, not new mathematics.
Usage: .venv/bin/python scripts/cloud_smoke.py [--rows N]
"""
import argparse, gzip, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "tools"))
OUT = ROOT / "artifacts/tmp/cloud_smoke"
CHECKER = os.environ.get("EMP_DRAT_TRIM", str(ROOT / "artifacts/tmp/native/bin/drat-trim"))
SOLVER = os.environ.get("EMP_CADICAL", str(ROOT / "artifacts/tmp/native/bin/cadical"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(cnf, proof, cap):
    start = time.time()
    run = subprocess.run([CHECKER, str(cnf), str(proof), "-t", str(cap)],
                         capture_output=True, text=True, timeout=cap + 60)
    ok = run.returncode == 0 and "s VERIFIED" in run.stdout
    return ok, round(time.time() - start, 3)


def chromatic(limit):
    from blowup_chi_cnf import bag_cnf
    from s004_certify import write_cnf
    corpus = json.loads(Path("validation/S003/survivors_alpha_ge3.json").read_text())
    chi = json.loads(Path("validation/S004/chi10_results.json").read_text())
    rows = []
    for i, r in enumerate(corpus[:limit]):
        cnf, proof = OUT / "chi.cnf", OUT / "chi.drat"
        write_cnf(cnf, *bag_cnf(*r[:2], 9))
        rec = chi[i]["bag"]
        proof.write_bytes(gzip.decompress(Path(rec["archive"]).read_bytes()))
        cnf_match = sha(cnf) == rec["cnf_sha256"]
        proof_match = sha(proof) == rec["drat_sha256"]
        ok, secs = check(cnf, proof, 600) if cnf_match and proof_match else (False, 0)
        rows.append(dict(index=i, cnf_sha256_match=cnf_match, proof_sha256_match=proof_match,
                         verified=ok, seconds=secs))
        if not ok:
            print(f"chi row {i}: FAIL {rows[-1]}", flush=True)
    return rows


def k9():
    cnf, proof = OUT / "K9.cnf", OUT / "K9.drat"
    rec = next(x for x in json.loads(Path("validation/S010/cold_replay.json").read_text())
               if x["archive"].endswith("cover-K9.drat.gz"))
    regen = subprocess.run([sys.executable, "tools/s010_regenerate.py", "Cover",
                            "validation/S003/K9.edges", "validation/S004/controls/cover-K9", str(cnf)],
                           capture_output=True, text=True, timeout=600)
    cnf_match = regen.returncode == 0 and sha(cnf) == rec["cnf_sha256"]
    proof.write_bytes(gzip.decompress(Path(rec["archive"]).read_bytes()))
    proof_match = sha(proof) == rec["archive_raw_sha256"]
    ok, secs = check(cnf, proof, 1200) if cnf_match and proof_match else (False, 0)
    return dict(cnf_sha256_match=cnf_match, proof_sha256_match=proof_match, verified=ok,
                seconds=secs, regenerate_returncode=regen.returncode,
                regenerate_stderr_tail=regen.stderr[-500:])


def solver_roundtrip():
    cnf, proof = OUT / "K9.cnf", OUT / "K9.fresh.drat"
    start = time.time()
    run = subprocess.run([SOLVER, "-q", "--no-binary", str(cnf), str(proof)],
                         capture_output=True, text=True, timeout=1800)
    unsat = run.returncode == 20
    ok, secs = check(cnf, proof, 1200) if unsat else (False, 0)
    return dict(solver_returncode=run.returncode, solve_seconds=round(time.time() - start, 3),
                fresh_proof_verified=ok, check_seconds=secs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=271, help="chromatic rows to check (default all 271)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    assert Path(CHECKER).exists(), f"missing checker {CHECKER}; run scripts/cloud_setup.sh"
    rows = chromatic(args.rows)
    k9_result = k9()
    solver = solver_roundtrip()
    passed = all(r["verified"] for r in rows) and k9_result["verified"] and solver["fresh_proof_verified"]
    result = dict(
        verdict="PASS" if passed else "FAIL",
        scope="environment acceptance only; no new mathematical claim",
        platform=platform.platform(), python=sys.version, checker=CHECKER, checker_sha256=sha(CHECKER),
        chromatic_rows_checked=len(rows), chromatic_rows_verified=sum(r["verified"] for r in rows),
        chromatic_cnf_byte_matches=sum(r["cnf_sha256_match"] for r in rows),
        solver=SOLVER, solver_sha256=sha(SOLVER), k9=k9_result, solver_roundtrip=solver, rows=rows,
    )
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=1))
    print(f"cloud smoke {result['verdict']}: chromatic {result['chromatic_rows_verified']}/{len(rows)} verified, "
          f"{result['chromatic_cnf_byte_matches']}/{len(rows)} CNF byte matches; "
          f"K9 cnf_match={k9_result['cnf_sha256_match']} verified={k9_result['verified']}; "
          f"fresh CaDiCaL K9 proof verified={solver['fresh_proof_verified']}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
