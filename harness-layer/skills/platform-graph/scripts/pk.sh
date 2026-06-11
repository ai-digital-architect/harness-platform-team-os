#!/usr/bin/env bash
# pk — query the Harness platform knowledge graph
# Requires: git, and yq OR python3. Graph cached at ${PK_HOME:-$HOME/.pk-cache/team-os}.
#
# Source spec: harness-knowledge-graph-revised-approach.md §5.
# Documented adaptations (T1.2):
#   1. yq fallback — if `yq` is not on PATH, `repo` and `deps` fall back to a
#      small embedded python3 reader (reusing scripts/graph_check.py's
#      manifest parser from the cached team-os checkout). The yq path stays
#      primary per the spec.
#   2. sync() skip — if PK_HOME already exists as a directory without .git,
#      cloning is skipped, so PK_HOME can point at a local team-os checkout
#      for tests/offline use.
#   3. impact/verify pass --root "$PK_HOME" explicitly (and verify adds
#      --no-write) so they operate on the cache regardless of the caller's
#      cwd and never rewrite the cached graph.json.
#   4. in-checkout default — when PK_HOME is unset AND this script lives
#      inside a team-os checkout (repo-manifest.yaml four levels up),
#      PK_HOME defaults to that checkout instead of the clone cache, so pk
#      works offline inside team-os itself. Explicit PK_HOME always wins;
#      distributed copies in code repos still default to the cache.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "${PK_HOME:-}" ] && [ -f "$SCRIPT_DIR/../../../../repo-manifest.yaml" ]; then
  PK_HOME="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
fi
PK_HOME="${PK_HOME:-$HOME/.pk-cache/team-os}"
TEAM_OS_URL="ssh://git@bitbucket.example.com/HARNESS/harness-platform-team-os.git"

sync() {  # shallow clone or fast-forward; called implicitly by every command
  if [ -d "$PK_HOME/.git" ]; then git -C "$PK_HOME" pull -q --ff-only || true
  elif [ -d "$PK_HOME" ]; then :  # local checkout / pre-seeded cache — leave as-is
  else git clone -q --depth 1 "$TEAM_OS_URL" "$PK_HOME"; fi
}

have_yq() { command -v yq >/dev/null 2>&1; }

py_repo() {  # fallback for `repo`: print the raw manifest block for repo $1
  python3 - "$PK_HOME/repo-manifest.yaml" "$1" <<'PYEOF'
import sys
path, name = sys.argv[1], sys.argv[2]
lines = open(path, encoding="utf-8").read().split("\n")
out, indent = [], None
for line in lines:
    s = line.strip()
    if indent is None:
        if s.startswith("- name:") and s.split(":", 1)[1].strip().strip("'\"") == name:
            indent = len(line) - len(line.lstrip(" "))
            out.append(line)
        continue
    if s == "":
        out.append(line)
        continue
    if len(line) - len(line.lstrip(" ")) <= indent:
        break
    out.append(line)
print("\n".join(out).rstrip())
PYEOF
}

py_deps() {  # fallback for `deps`: names of repos whose depends_on contains $1
  python3 - "$PK_HOME" "$1" <<'PYEOF'
import sys
from pathlib import Path
root, name = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(root / "scripts"))
import graph_check
manifest = graph_check.parse_manifest(root / "repo-manifest.yaml")
for repos in manifest["areas"].values():
    for r in repos:
        if name in r["depends_on"]:
            print(r["name"])
PYEOF
}

case "${1:-help}" in
  repo)        sync
               if have_yq; then
                 yq ".product_areas[].repos[] | select(.name == \"$2\")" \
                   "$PK_HOME/repo-manifest.yaml"
               else py_repo "$2"; fi ;;
  deps)        sync                                          # who depends ON $2
               if have_yq; then
                 yq ".product_areas[].repos[] | select(.depends_on[]? == \"$2\") | .name" \
                   "$PK_HOME/repo-manifest.yaml"
               else py_deps "$2"; fi ;;
  workflow)    sync; ls "$PK_HOME/knowledge/workflows/" | grep -i "${2:-.}" ;;
  show)        sync; cat "$PK_HOME/knowledge/$2.md" ;;
  impact)      sync; python3 "$PK_HOME/scripts/impact.py" "$2" --root "$PK_HOME" ;;  # transitive closure
  search)      sync; grep -ril "$2" "$PK_HOME/knowledge/" "$PK_HOME/repo-manifest.yaml" ;;
  verify)      sync; python3 "$PK_HOME/scripts/graph_check.py" --root "$PK_HOME" --no-write ;;
  *) echo "pk repo|deps|workflow|show|impact|search|verify" ;;
esac
