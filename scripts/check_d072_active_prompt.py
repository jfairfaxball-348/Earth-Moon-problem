"""D072 active phone prompt and immutable S032 history integrity checker.

The old S032 checker expects its historical S033 prompt to be active.
Temporarily substitute that immutable archived prompt only for that checker,
restoring the current prompt on any error. D071 historic directive is unedited.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "sessions/S032/S033_FUTURE_PROMPT.md"
ACTIVE = ROOT / "authoritative/NEXT_SESSION_PROMPT.md"
D071 = ROOT / "docs/D071_S033_PARALLEL_DIRECTIVE.json"
D072 = ROOT / "docs/D072_S033_PHONE_TEST_DIRECTIVE.json"

def blob_sha(path):
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

def main():
    old = json.loads(D071.read_text(encoding="utf-8"))
    new = json.loads(D072.read_text(encoding="utf-8"))
    state = json.loads((ROOT / "authoritative/STATE.json").read_text(encoding="utf-8"))
    assert old["decision"] == "D071"
    assert new["decision"] == "D072" and new["scope"] == "ACTIVE_S033_PHONE_OVERRIDE"
    assert old["active_prompt_git_blob_sha"] == new["previous_active_prompt_sha"]
    assert old["archived_prompt_git_blob_sha"] == new["archived_s032_prompt_sha"]
    assert new["preserves_s032_archive"] and new["does_not_invoke_s033"]
    assert blob_sha(ARCHIVE) == new["archived_s032_prompt_sha"]
    original = ACTIVE.read_bytes()
    if state["last_completed_session"] == "S032":
        assert state["recommended_next_session"] == "S033"
        assert blob_sha(ACTIVE) == new["active_prompt_git_blob_sha"]
        assert original.decode("utf-8").startswith("# S033 — Samsung Galaxy S24 ARM64")
        assert "S034" in original.decode("utf-8")
    try:
        ACTIVE.write_bytes(ARCHIVE.read_bytes())
        subprocess.run([sys.executable, str(ROOT / "scripts/check_s032_records.py")],
                       cwd=ROOT, check=True)
    finally:
        ACTIVE.write_bytes(original)
    assert ACTIVE.read_bytes() == original
    print("PASS D072 mobile override and historical S032 preservation")

if __name__ == "__main__":
    main()
