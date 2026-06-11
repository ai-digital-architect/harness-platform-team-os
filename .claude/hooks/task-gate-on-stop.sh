#!/usr/bin/env bash
# Stop hook: if the working tree has changes, require:
#   (a) python3 scripts/graph_check.py exits 0
#   (b) the current task's row in TASKS.md was updated this session
# Otherwise exit 2 with a reminder so Claude addresses acceptance criteria.
set -euo pipefail

# No changes anywhere? Nothing to enforce.
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null \
    && [ -z "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
  exit 0
fi

problems=()

# (a) Graph check clean — only if the script exists (T0.2+).
if [ -f scripts/graph_check.py ]; then
  if ! python3 scripts/graph_check.py >/dev/null 2>&1; then
    problems+=("graph_check.py is failing — run \`python3 scripts/graph_check.py\` and fix all errors")
  fi
fi

# (b) TASKS.md updated for the current task (inferred from branch task/<ID>-...).
# Accept the update whether it is still uncommitted OR already committed on
# this task branch (diff against the merge-base with main).
branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo "")"
task_id="$(printf '%s' "$branch" | sed -nE 's#^task/([A-Za-z0-9.]+)-.*#\1#p')"
if [ -n "$task_id" ]; then
  updated=0
  if { git diff TASKS.md 2>/dev/null; git diff --cached TASKS.md 2>/dev/null; } \
       | grep -q "$task_id"; then
    updated=1
  else
    base="$(git merge-base main HEAD 2>/dev/null || echo "")"
    if [ -n "$base" ] && git diff "$base"..HEAD -- TASKS.md 2>/dev/null | grep -q "$task_id"; then
      updated=1
    fi
  fi
  if [ "$updated" -eq 0 ]; then
    problems+=("TASKS.md row for $task_id not updated this session — set status and append PR placeholder")
  fi
fi

if [ "${#problems[@]}" -gt 0 ]; then
  {
    echo "Stop blocked — acceptance criteria not yet addressed:"
    for p in "${problems[@]}"; do echo "  - $p"; done
  } 1>&2
  exit 2
fi

exit 0
