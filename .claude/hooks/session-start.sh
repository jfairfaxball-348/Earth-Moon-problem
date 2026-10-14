#!/bin/bash
# SessionStart hook for Claude Code cloud sessions (decision D043).
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
bash "$ROOT/scripts/cloud_setup.sh"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export PATH=\"$ROOT/.venv/bin:$ROOT/artifacts/tmp/native/bin:\$PATH\""
    echo "export VIRTUAL_ENV=\"$ROOT/.venv\""
    echo "export EMP_CADICAL=\"$ROOT/artifacts/tmp/native/bin/cadical\""
    echo "export EMP_DRAT_TRIM=\"$ROOT/artifacts/tmp/native/bin/drat-trim\""
  } >> "$CLAUDE_ENV_FILE"
fi
