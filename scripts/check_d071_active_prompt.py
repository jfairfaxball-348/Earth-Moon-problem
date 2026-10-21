"""Validate current D071 S033 prompt and frozen S032 records without rewriting history.

S032's checker and archived S033 handoff are hash-pinned in its immutable
MANIFEST. The live NEXT_SESSION_PROMPT can legitimately change on owner command.
Run the immutable historical checker with a temporary, exactly archived view of
that one path; restore it even on checker failure. Git-tracked bytes are unchanged.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "sessions/S032/S033_FUTURE_PROMPT.md"
ACTIVE = ROOT / "authoritative/NEXT_SESSION_PROMPT.md"
DIRECTIVE = ROOT / "docs/D071_S033_PARALLEL_DIRECTIVE.json"

def git_blob_sha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def main():
    d = json.loads(DIRECTIVE.read_text(encoding="utf-8"))
    state = json.loads((ROOT / "authoritative/STATE.json").read_text(encoding="utf-8"))
    assert d["decision"] == "D071" and d["scope"] == "ACTIVE_S033_PROMPT_ONLY"
    assert d["preserves_s032_archive"] and d["does_not_invoke_s033"]
    assert git_blob_sha(ARCHIVE) == d["archived_prompt_git_blob_sha"]
    prior_active = ACTIVE.read_bytes()
    if state["last_completed_session"] == "S032":
        assert state["recommended_next_session"] == "S033"
        assert git_blob_sha(ACTIVE) == d["active_prompt_git_blob_sha"]
        assert ACTIVE.read_text(encoding="utf-8").startswith("# S033 — build")
    try:
        ACTIVE.write_bytes(ARCHIVE.read_bytes())
        subprocess.run([sys.executable, str(ROOT / "scripts/check_s032_records.py")],
                       cwd=ROOT, check=True)
    finally:
        ACTIVE.write_bytes(prior_active)
    assert ACTIVE.read_bytes() == prior_active
    print("PASS D071 active S033 amendment with frozen S032 archive and historical checker")

if __name__ == "__main__":
    main()
