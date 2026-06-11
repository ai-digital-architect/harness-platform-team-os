#!/usr/bin/env bash
# PostToolUse hook: if Write/Edit/MultiEdit touched knowledge/** or
# repo-manifest.yaml, run scripts/graph_check.py. On failure emit errors
# to stderr and exit 2 so Claude must fix immediately.
set -euo pipefail

input="$(cat || true)"
file_path="$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    d = json.loads(sys.stdin.read() or "{}")
    ti = d.get("tool_input", {}) or {}
    print(ti.get("file_path") or ti.get("notebook_path") or "")
except Exception:
    print("")
' 2>/dev/null || echo "")"

case "$file_path" in
  *knowledge/*|*repo-manifest.yaml)
    if [ ! -f scripts/graph_check.py ]; then
      # graph_check.py is built in T0.2 — silently pass during bootstrap.
      exit 0
    fi
    if ! python3 scripts/graph_check.py 1>&2; then
      echo "graph_check failed after edit to $file_path — fix before continuing." 1>&2
      exit 2
    fi
    ;;
esac
exit 0
