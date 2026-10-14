#!/bin/bash
# Reproducible Linux/cloud environment for EMP sessions (decision D043).
# Builds the S004-pinned native SAT tools from source, installs the pinned
# Python packages into .venv, and records the realised environment.
# Idempotent and non-interactive. Governance/infrastructure only: running it
# proves nothing mathematical.
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

# Pins (S004 native sources; package versions recorded in S004-S010 manifests).
CADICAL_URL="https://github.com/arminbiere/cadical"
CADICAL_SHA="c60730422e758ef1cebe7aeddf2dda31c996bf04"
DRATTRIM_URL="https://github.com/marijnheule/drat-trim"
DRATTRIM_SHA="2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
PY_PACKAGES=("python-sat==1.9.dev15" "networkx==3.5")
PY_OPTIONAL=("numpy==2.5.4" "pymupdf==1.26.6")

NATIVE="$ROOT/artifacts/tmp/native"
SRC="$NATIVE/src"
BIN="$NATIVE/bin"
LOG="$NATIVE/setup.log"
mkdir -p "$SRC" "$BIN"
: > "$LOG"
say() { echo "[cloud_setup] $*" | tee -a "$LOG" >&2; }

fetch_pin() {  # url sha dest
  local url="$1" sha="$2" dest="$3"
  if [ -d "$dest/.git" ] && [ "$(git -C "$dest" rev-parse HEAD 2>/dev/null)" = "$sha" ]; then
    return 0
  fi
  rm -rf "$dest"
  git init -q "$dest"
  git -C "$dest" remote add origin "$url"
  git -C "$dest" fetch -q --depth 1 origin "$sha"
  git -C "$dest" checkout -q --detach FETCH_HEAD
  [ "$(git -C "$dest" rev-parse HEAD)" = "$sha" ] || { say "pin mismatch for $url"; exit 1; }
}

# --- Python environment -----------------------------------------------------
PY="$(command -v python3.12 || command -v python3)"
if [ ! -x .venv/bin/python ]; then
  say "creating .venv with $PY"
  "$PY" -m venv .venv
fi
.venv/bin/python -m pip install -q --disable-pip-version-check "${PY_PACKAGES[@]}" >>"$LOG" 2>&1
for pkg in "${PY_OPTIONAL[@]}"; do
  .venv/bin/python -m pip install -q --disable-pip-version-check "$pkg" >>"$LOG" 2>&1 \
    || say "optional package $pkg not installed (only needed by census/figure tools)"
done

# --- Native tools -------------------------------------------------------------
if [ ! -x "$BIN/cadical" ] || [ "$(cat "$BIN/cadical.pin" 2>/dev/null)" != "$CADICAL_SHA" ]; then
  say "building CaDiCaL $CADICAL_SHA"
  fetch_pin "$CADICAL_URL" "$CADICAL_SHA" "$SRC/cadical"
  (cd "$SRC/cadical" && ./configure >>"$LOG" 2>&1 && make -j"$(nproc)" >>"$LOG" 2>&1)
  cp "$SRC/cadical/build/cadical" "$BIN/cadical"
  echo "$CADICAL_SHA" > "$BIN/cadical.pin"
fi
if [ ! -x "$BIN/drat-trim" ] || [ "$(cat "$BIN/drat-trim.pin" 2>/dev/null)" != "$DRATTRIM_SHA" ]; then
  say "building drat-trim $DRATTRIM_SHA"
  fetch_pin "$DRATTRIM_URL" "$DRATTRIM_SHA" "$SRC/drat-trim"
  gcc -O2 -o "$BIN/drat-trim" "$SRC/drat-trim/drat-trim.c" >>"$LOG" 2>&1
  echo "$DRATTRIM_SHA" > "$BIN/drat-trim.pin"
fi

# Historical S004-S010 tools hard-code the Windows binary names. Point those
# paths at the Linux builds instead of editing preserved scientific scripts.
LEGACY="$ROOT/artifacts/tmp/S004"
mkdir -p "$LEGACY"
ln -sf "$BIN/cadical" "$LEGACY/cadical.exe"
ln -sf "$BIN/drat-trim" "$LEGACY/drat-trim-mingw.exe"

# --- Environment record -----------------------------------------------------
.venv/bin/python - "$NATIVE/ENVIRONMENT.json" "$CADICAL_SHA" "$DRATTRIM_SHA" <<'EOF'
import hashlib, json, os, platform, subprocess, sys
from importlib import metadata
out, cad_sha, dt_sha = sys.argv[1:4]
bindir = os.path.join(os.path.dirname(out), "bin")
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
def ver(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None
gcc = subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
record = {
    "purpose": "Realised cloud environment (D043); a new environment, not a byte reproduction of the Windows S004-S010 binaries",
    "platform": platform.platform(),
    "python": sys.version,
    "packages": {k: ver(k) for k in ("python-sat", "networkx", "numpy", "pymupdf")},
    "compiler": gcc,
    "native_sources": {"cadical": cad_sha, "drat-trim": dt_sha},
    "native_sha256": {b: sha(os.path.join(bindir, b)) for b in ("cadical", "drat-trim")},
    "cpus": os.cpu_count(),
    "mem_total_kib": next((int(l.split()[1]) for l in open("/proc/meminfo") if l.startswith("MemTotal")), None),
}
json.dump(record, open(out, "w"), indent=1)
EOF

say "ready: .venv ($(.venv/bin/python --version 2>&1)), $BIN/cadical, $BIN/drat-trim; record $NATIVE/ENVIRONMENT.json"
