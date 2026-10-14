"""Freeze S009 public artifact hashes, then verify exact staged Git blob bytes.

Packaging/governance checks only: this does not run a solver or certify mathematics.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "validation/S009_MANIFEST.json"
ENTRY = "7957452c79c2b31088f93fff440783328c78942d"


def git(*args, binary=False):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=not binary)


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def freeze():
    assert git("branch", "--show-current").strip() == "codex/S009-transfer-colours"
    assert git("rev-parse", "HEAD").strip() == ENTRY
    summary = load("validation/S009/SUMMARY.json")
    assert summary["S009_new_exclusions"] == [15, 23, 24, 28, 38, 41, 45]
    assert len(summary["excluded_indices"]) == 52 and summary["remaining_unknown"] == 219
    assert summary["heavy_initial_pipeline"] == "UNKNOWN"
    assert summary["heavy_K7I5_verdict"] == "NON_BIPLANAR_DRAT_VERIFIED"
    command_records = [
        "baseline_driver_command", "final_audit_command", "public_control_command",
        "boundary_control_command", "heavy_extension_command", "full_driver_command",
        "new_discover_command", "new_accept_command", "local_detect_command",
        "local_accept_command",
    ]
    for name in command_records:
        assert load(f"validation/S009/{name}.json")["returncode"] == 0, name
    for name in ("COLD_ARCHIVE_AUDIT_PASS", "EXTENDED_COLD_CNF_AUDIT_PASS", "INDEPENDENT_RECORD_AUDIT_PASS"):
        assert load(f"validation/S009/{name}.json")["verdict"] == "PASS", name
    assert "governance checks: PASS" in (ROOT / "validation/S009/governance.log").read_text()
    unit = (ROOT / "validation/S009/unit.log").read_text()
    assert "Ran 10 tests" in unit and "\nOK" in unit
    paths = set(git("diff", "--name-only", "HEAD").splitlines())
    paths.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    paths.discard(MANIFEST)
    artifacts = {}
    for name in sorted(paths):
        data = (ROOT / name).read_bytes()
        assert len(data) <= 100 * 1024 * 1024, f"GitHub regular-Git size limit: {name}"
        artifacts[name] = {"sha256": digest(data), "bytes": len(data)}
    record = {
        "session": "S009", "date": "2026-10-14", "entry_main": ENTRY,
        "entry_tree": "17611589c3b44454cd8910362306629a15c856ea",
        "branch": "codex/S009-transfer-colours",
        "owner_invocation": "sessions/S009/OWNER_INVOCATION.md",
        "executed_prompt": "sessions/S009/EXECUTED_PROMPT.md",
        "preregistration": "campaigns/CAM-0010.md and prospective amendments A-I",
        "environment": load("validation/S009/environment.json"),
        "summary": summary,
        "checks": {
            "scientific_command_records_returncode_zero": command_records,
            "cold_baseline": "validation/S009/BASELINE_PASS.json",
            "final_independent_audits": [
                "validation/S009/COLD_ARCHIVE_AUDIT_PASS.json",
                "validation/S009/EXTENDED_COLD_CNF_AUDIT_PASS.json",
                "validation/S009/INDEPENDENT_RECORD_AUDIT_PASS.json",
            ],
            "governance": {"command": ".venv/Scripts/python.exe scripts/check_scaffold.py", "returncode": 0, "log": "validation/S009/governance.log"},
            "unit": {"command": ".venv/Scripts/python.exe -m unittest discover -s tests -v", "returncode": 0, "tests": 10, "log": "validation/S009/unit.log"},
            "git_diff_check": "PASS before freeze; staged blob verification required before commit",
            "hosted_checks": "Observe actual postcommit head/main runs and jobs live; not anticipated here",
        },
        "artifact_sha256": artifacts,
        "authority_entry_git_blob_sha256": {
            name: {"sha256": digest(data), "bytes": len(data)}
            for name in ("AGENTS.md", "docs/SESSION_PROTOCOL.md", ".github/workflows/scaffold.yml")
            for data in (git("show", f"{ENTRY}:{name}", binary=True),)
        },
        "byte_provenance": "S009 evidence is exempt from Git text conversion. Observed launch snapshots/hashes are distinct from these final artifact hashes. Manifest excludes its own hash.",
        "heavy_source": {
            "accepted": "validation/S009/heavy_extended/result.json",
            "initial": "validation/S009/heavy/result.json remains UNKNOWN after compact timeout",
            "local_oversize_archive_receipt": "validation/S009/heavy/ARCHIVE_RELOCATION.json",
            "retained_public_proof": "validation/S009/heavy_extended/search/K7-I5.drat.gz",
        },
        "outgoing_integration": "Observe one authored commit/ordinary non-draft PR/non-force two-parent merge/matching tree/head and main jobs after freeze. Save actual evidence in ignored artifacts/tmp/S009/LIVE_EXIT_EVIDENCE.json and final response.",
        "limitations": "Headline remains9..12. No universal colouring improvement, whole-stratum closure, novelty guarantee, external universal review, Lean/formalisation, registration, publication or outreach. Initial UNKNOWNs/caps/misses are not promoted. S010 FUTURE/UNEXECUTED.",
    }
    (ROOT / MANIFEST).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS S009 manifest frozen: {len(artifacts)} public artifacts, {sum(r['bytes'] for r in artifacts.values())} bytes")


def staged():
    record = load(MANIFEST)
    authority = record["authority_entry_git_blob_sha256"]
    paths = list(record["artifact_sha256"]) + list(authority) + [MANIFEST]
    entries = {}
    for line in git("ls-files", "--stage").splitlines():
        meta, path = line.split("\t", 1)
        mode, oid, stage = meta.split()
        assert stage == "0", "Unmerged index"
        entries[path] = oid
    request = "".join(entries[p] + "\n" for p in paths).encode("ascii")
    result = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=request, stdout=subprocess.PIPE, check=True)
    pos = 0
    for path in paths:
        end = result.stdout.index(b"\n", pos)
        oid, kind, size = result.stdout[pos:end].split()
        assert kind == b"blob"
        size = int(size)
        data = result.stdout[end + 1:end + 1 + size]
        assert result.stdout[end + 1 + size:end + 2 + size] == b"\n"
        pos = end + 2 + size
        if path not in authority:
            assert data == (ROOT / path).read_bytes(), f"Staged/work bytes differ: {path}"
        if path != MANIFEST:
            item = authority[path] if path in authority else record["artifact_sha256"][path]
            assert len(data) == item["bytes"] and digest(data) == item["sha256"], path
    assert pos == len(result.stdout)
    print(f"PASS S009 exact staged Git blobs: {len(paths)} files; artifact hashes/working bytes and unchanged entry authority blobs agree")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "staged":
        staged()
    else:
        freeze()
