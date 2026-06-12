#!/usr/bin/env python3
"""impact.py — transitive closure of DEPENDENTS of a repo.

Stdlib-only. Reads dependency edges from repo-manifest.yaml (depends_on)
and, when knowledge/graph.json exists, its `depends-on` edges. Prints each
repo/node impacted by a change to <repo> — i.e. everything that directly or
transitively depends ON it — one per line, sorted (deterministic).

Usage: python3 scripts/impact.py <repo> [--root DIR]
Exit codes: 0 success (even when nothing depends on <repo>),
            1 unknown repo or missing/invalid inputs (file:line on stderr).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graph_check  # noqa: E402


def load_edges(root):
    """Return (known_names, reverse) for the graph rooted at `root`.

    known_names: every name a query may target (manifest repos, active and
    deprecated, plus graph.json node ids and edge endpoints).
    reverse: dependency -> set of direct dependents.
    """
    root = Path(root)
    known, reverse = set(), {}

    manifest = graph_check.load_manifest(root)
    if manifest is not None:
        known |= graph_check.manifest_repo_names(manifest)
        for repos in manifest["areas"].values():
            for r in repos:
                for dep in r["depends_on"]:
                    reverse.setdefault(dep, set()).add(r["name"])

    graph_path = root / "knowledge" / "graph.json"
    if graph_path.is_file():
        try:
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise ValueError(f"{graph_path}:1: error: cannot read graph.json: {e}")
        for node in graph.get("nodes", []):
            if node.get("id"):
                known.add(node["id"])
        for edge in graph.get("edges", []):
            if edge.get("rel") == "depends-on" and edge.get("from") and edge.get("to"):
                known.add(edge["from"])
                known.add(edge["to"])
                reverse.setdefault(edge["to"], set()).add(edge["from"])
    return known, reverse


def impact(target, reverse):
    """Sorted transitive closure of dependents of `target` (cycle-safe)."""
    seen, stack = set(), [target]
    while stack:
        current = stack.pop()
        for dependent in reverse.get(current, ()):
            if dependent not in seen:
                seen.add(dependent)
                stack.append(dependent)
    seen.discard(target)
    return sorted(seen)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root, target = ".", None
    while argv:
        arg = argv.pop(0)
        if arg == "--root" and argv:
            root = argv.pop(0)
        elif target is None and not arg.startswith("-"):
            target = arg
        else:
            print("usage: impact.py <repo> [--root DIR]", file=sys.stderr)
            return 1
    if target is None:
        print("usage: impact.py <repo> [--root DIR]", file=sys.stderr)
        return 1

    root = Path(root)
    manifest_path = root / "repo-manifest.yaml"
    if not manifest_path.is_file():
        print(f"{manifest_path}:1: error: repo-manifest.yaml not found", file=sys.stderr)
        return 1
    try:
        known, reverse = load_edges(root)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    if target not in known:
        print(f"{manifest_path}:1: error: unknown repo {target!r} "
              "(not in repo-manifest.yaml or knowledge/graph.json)", file=sys.stderr)
        return 1
    for name in impact(target, reverse):
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
