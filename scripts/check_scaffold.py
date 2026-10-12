#!/usr/bin/env python3
"""Stdlib-only governance sanity checks; never a mathematical proof."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "AGENTS.md", "authoritative/START_HERE.md",
    "authoritative/STATE.json", "authoritative/NEXT_SESSION_PROMPT.md",
    "docs/SESSION_PROTOCOL.md", "docs/PHASE_GATE_LEDGER.md",
    "docs/SESSION_LEDGER.md", "docs/DECISION_LOG.md",
    "docs/FAILURE_LEDGER.md", "research/PROBLEM_STATEMENT.md",
    "catalogue/SOURCES.md", "catalogue/SOURCES.json",
    "catalogue/CLAIMS.md", "catalogue/CLAIMS.json",
    "sessions/S001/CLOSEOUT.md", "tools/check_submission.py"
]
for item in REQUIRED:
    assert (ROOT / item).is_file(), "Missing: " + item
state = json.loads((ROOT / "authoritative/STATE.json").read_text())
sources = json.loads((ROOT / "catalogue/SOURCES.json").read_text())
claims = json.loads((ROOT / "catalogue/CLAIMS.json").read_text())
assert state["last_completed_session"] == "S001"
assert state["recommended_next_session"] == "S002"
assert state["next_session_is_future_unexecuted"] is True
assert state["phases"][0]["status"] == "PASS_ADMIN_ONLY"
assert len({s["id"] for s in sources}) == len(sources)
assert len({c["id"] for c in claims}) == len(claims)
assert all(c["status"] in {
    "SOURCE_STATED", "PROGRAMME_PROVED", "COMPUTED_EXACT",
    "HEURISTIC", "FORMALLY_CERTIFIED", "INHERITED_UNVERIFIED"
} for c in claims)
source_ids = {s["id"] for s in sources}
assert all(set(c["sources"]) <= source_ids for c in claims)
print("S001 scaffold governance checks: PASS (not proof, not hosted CI)")
