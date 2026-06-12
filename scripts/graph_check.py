#!/usr/bin/env python3
"""graph_check.py — referential-integrity checker for the knowledge graph.

Stdlib-only. Parses YAML frontmatter from knowledge/**/*.md with a minimal
in-repo parser (no pyyaml), validates nodes and edges, and emits
knowledge/graph.json (deterministic). Exit codes: 0 clean, 1 validation
errors (file:line diagnostics on stderr). Warnings go to stderr, exit 0.

Validations:
  - required frontmatter fields: id, type, title, status
  - id must equal the node's path relative to knowledge/ (no .md suffix)
  - type in closed set; status in {draft, active, deprecated}
  - edges[].rel in the closed vocabulary; edges[].to resolves to an
    existing node id OR a repo name from repo-manifest.yaml
  - [[wikilinks]] in the body resolve to node ids or manifest repo names
  - workflow `repos:` entries exist in repo-manifest.yaml
    (skipped with a warning if the manifest is absent)
  - `_template.md` files are excluded from all checks
  - repo-manifest.yaml itself (when present): unique repo names, every repo
    in exactly one product area, depends_on targets exist, active repos
    depending on deprecated repos (warning only)
"""

import json
import re
import sys
from pathlib import Path

NODE_TYPES = {
    "capability", "workflow", "dependency", "convention", "gotcha", "decision",
}
EDGE_RELS = {
    "depends-on", "deploys-to", "publishes-to", "consumes-from", "implements",
    "touches", "governed-by", "affected-by", "supersedes", "subtree-of",
}
STATUSES = {"draft", "active", "deprecated"}
REQUIRED_FIELDS = ("id", "type", "title", "status")
EXCLUDED_NAMES = {"_template.md", "INDEX.md"}
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)")


class FrontmatterError(Exception):
    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message


def _strip_quotes(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    return s


def _split_flow_items(s, line):
    """Split a flow-collection body on top-level commas."""
    items, depth, start = [], 0, 0
    in_quote = None
    for i, ch in enumerate(s):
        if in_quote:
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ("'", '"'):
            in_quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
            if depth < 0:
                raise FrontmatterError(line, "unbalanced brackets in flow value")
        elif ch == "," and depth == 0:
            items.append(s[start:i])
            start = i + 1
    if depth != 0 or in_quote:
        raise FrontmatterError(line, "unbalanced brackets or quotes in flow value")
    items.append(s[start:])
    return [i for i in (x.strip() for x in items) if i != ""]


def _parse_value(s, line):
    """Parse a scalar or flow collection ({...} / [...])."""
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        return [_parse_value(x, line) for x in _split_flow_items(s[1:-1], line)]
    if s.startswith("{") and s.endswith("}"):
        out = {}
        for item in _split_flow_items(s[1:-1], line):
            if ":" not in item:
                raise FrontmatterError(line, f"expected 'key: value' in flow mapping, got {item!r}")
            k, v = item.split(":", 1)
            out[_strip_quotes(k)] = _parse_value(v, line)
        return out
    return _strip_quotes(s)


def parse_frontmatter(text):
    """Parse YAML frontmatter. Returns (dict, key_lines, body_start_line).

    key_lines maps top-level keys to their 1-based line number in the file.
    Supports: scalars, flow lists/maps, and block lists of scalars or flow
    maps. Raises FrontmatterError on anything else.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError(1, "missing frontmatter (file must start with ---)")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise FrontmatterError(1, "unterminated frontmatter (no closing ---)")

    data, key_lines = {}, {}
    current_key = None
    for i in range(1, end):
        raw = lines[i]
        lineno = i + 1
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            if ":" not in stripped:
                raise FrontmatterError(lineno, f"expected 'key:' or 'key: value', got {stripped!r}")
            key, rest = stripped.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            key_lines[key] = lineno
            if rest == "":
                data[key] = []        # block list expected
                current_key = key
            else:
                data[key] = _parse_value(rest, lineno)
                current_key = None
        else:
            if current_key is None:
                raise FrontmatterError(lineno, f"unexpected indented line: {stripped!r}")
            if not stripped.startswith("- "):
                raise FrontmatterError(
                    lineno, "only block lists are supported under a key (expected '- item')")
            data[current_key].append(_parse_value(stripped[2:], lineno))
    return data, key_lines, end + 2


def parse_manifest(path):
    """Parse repo-manifest.yaml (stdlib, targeted at its known shape).

    Returns {"areas": {area: [repo, ...]}, "area_meta": {area: {field: value}},
    "deprecated": [entry, ...], "errors": [(line, message), ...]} where repo
    dicts carry name, depends_on, area, the 1-based source line, and every
    other scalar/flow field of the entry (role, tech, deploy_target, docs, …).
    Shape: product_areas is a map of area -> {description, repos: [- name: …]},
    deprecated and subtree_plan are top-level; list fields are flow style.
    """
    lines = path.read_text(encoding="utf-8").split("\n")
    areas, area_meta, deprecated, errors = {}, {}, [], []
    section = None
    area, area_indent = None, None
    repo = None

    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            section, area, area_indent, repo = None, None, None, None
            key = s.split(":", 1)[0].strip()
            if key in ("product_areas", "deprecated", "subtree_plan"):
                section = key
            continue

        if section == "product_areas":
            if s.startswith("- "):
                if not s.startswith("- name:"):
                    if repo is None:
                        errors.append((i, f"repo entry must start with 'name:': {s!r}"))
                    continue
                name = _strip_quotes(s.split(":", 1)[1])
                repo = {"name": name, "depends_on": [], "area": area, "line": i}
                areas.setdefault(area, []).append(repo)
            elif s.endswith(":") and (area_indent is None or indent <= area_indent):
                area, area_indent, repo = s[:-1].strip(), indent, None
                areas.setdefault(area, [])
                area_meta.setdefault(area, {})
            elif ":" in s:
                key, val = s.split(":", 1)
                key = key.strip()
                if not val.strip():
                    continue  # block keys (repos:) and empty values
                try:
                    parsed = _parse_value(val, i)
                except FrontmatterError as e:
                    errors.append((e.line, e.message))
                    continue
                if repo is not None:
                    if key == "depends_on":
                        repo[key] = parsed if isinstance(parsed, list) else [parsed]
                    elif key not in repo:
                        repo[key] = parsed
                elif area is not None:
                    area_meta.setdefault(area, {})[key] = parsed
        elif section == "deprecated":
            if s.startswith("- name:"):
                deprecated.append({"name": _strip_quotes(s.split(":", 1)[1]), "line": i})
    return {"areas": areas, "area_meta": area_meta, "deprecated": deprecated,
            "errors": errors}


def validate_manifest(manifest, path):
    """T1.1 manifest checks. Returns (errors, warnings) as (path, line, msg)."""
    errors = [(path, line, msg) for line, msg in manifest["errors"]]
    warnings = []
    seen = {}  # name -> (area, line)
    for area, repos in manifest["areas"].items():
        for r in repos:
            if r["name"] in seen:
                prev_area, prev_line = seen[r["name"]]
                if prev_area == area:
                    errors.append((path, r["line"],
                                   f"duplicate repo name {r['name']!r} in product area "
                                   f"{area!r} (first at line {prev_line})"))
                else:
                    errors.append((path, r["line"],
                                   f"repo {r['name']!r} belongs to more than one product "
                                   f"area: {prev_area!r} (line {prev_line}) and {area!r}"))
            else:
                seen[r["name"]] = (area, r["line"])
    dep_names = {}
    for d in manifest["deprecated"]:
        if d["name"] in seen:
            errors.append((path, d["line"],
                           f"repo {d['name']!r} is listed both as active and deprecated"))
        dep_names[d["name"]] = d["line"]
    for area, repos in manifest["areas"].items():
        for r in repos:
            for target in r["depends_on"]:
                if target in seen:
                    continue
                if target in dep_names:
                    warnings.append((path, r["line"],
                                     f"active repo {r['name']!r} depends on deprecated "
                                     f"repo {target!r}"))
                else:
                    errors.append((path, r["line"],
                                   f"depends_on target {target!r} of repo {r['name']!r} "
                                   "not found in repo-manifest.yaml"))
    return errors, warnings


def load_manifest(root):
    """Parse repo-manifest.yaml if present. Returns parsed dict or None."""
    manifest_path = root / "repo-manifest.yaml"
    if not manifest_path.is_file():
        return None
    return parse_manifest(manifest_path)


def manifest_repo_names(manifest):
    """All repo names (active + deprecated) usable as edge/wikilink targets."""
    names = {d["name"] for d in manifest["deprecated"]}
    for repos in manifest["areas"].values():
        names.update(r["name"] for r in repos)
    return names


def load_nodes(root):
    """Parse all knowledge/**/*.md nodes. Returns (nodes, errors).

    Each node: {path, rel_id, data, key_lines, body, body_start}.
    """
    knowledge = root / "knowledge"
    nodes, errors = [], []
    if not knowledge.is_dir():
        return nodes, errors
    for path in sorted(knowledge.rglob("*.md")):
        if path.name in EXCLUDED_NAMES:
            continue
        rel = path.relative_to(knowledge).as_posix()
        text = path.read_text(encoding="utf-8")
        try:
            data, key_lines, body_start = parse_frontmatter(text)
        except FrontmatterError as e:
            errors.append((path, e.line, e.message))
            continue
        body = "\n".join(text.split("\n")[body_start - 1:])
        nodes.append({
            "path": path,
            "rel_id": rel[:-3],  # strip .md
            "data": data,
            "key_lines": key_lines,
            "body": body,
            "body_start": body_start,
        })
    return nodes, errors


def validate(nodes, manifest_repos, root):
    """Return (errors, warnings) as lists of (path, line, message)."""
    errors, warnings = [], []
    node_ids = {n["data"].get("id") for n in nodes if n["data"].get("id")}

    def resolvable(target):
        return target in node_ids or (manifest_repos is not None and target in manifest_repos)

    for n in nodes:
        path, data, kl = n["path"], n["data"], n["key_lines"]

        for field in REQUIRED_FIELDS:
            if field not in data or data[field] in ("", [], None):
                errors.append((path, 1, f"missing required field: {field}"))
        nid = data.get("id")
        if nid and nid != n["rel_id"]:
            errors.append((path, kl.get("id", 1),
                           f"id {nid!r} does not match path-derived id {n['rel_id']!r}"))
        ntype = data.get("type")
        if ntype and ntype not in NODE_TYPES:
            errors.append((path, kl.get("type", 1),
                           f"type {ntype!r} not in {sorted(NODE_TYPES)}"))
        status = data.get("status")
        if status and status not in STATUSES:
            errors.append((path, kl.get("status", 1),
                           f"status {status!r} not in {sorted(STATUSES)}"))

        edges = data.get("edges", [])
        if not isinstance(edges, list):
            errors.append((path, kl.get("edges", 1), "edges must be a list"))
            edges = []
        for edge in edges:
            eline = kl.get("edges", 1)
            if not isinstance(edge, dict) or "rel" not in edge or "to" not in edge:
                errors.append((path, eline, f"edge must be a mapping with rel and to: {edge!r}"))
                continue
            if edge["rel"] not in EDGE_RELS:
                errors.append((path, eline,
                               f"edge rel {edge['rel']!r} not in closed vocabulary {sorted(EDGE_RELS)}"))
            target = edge["to"]
            if not resolvable(target):
                if manifest_repos is None and target not in node_ids:
                    warnings.append((path, eline,
                                     f"edge target {target!r} is not a node id; cannot check "
                                     "against repo-manifest.yaml (manifest absent)"))
                else:
                    errors.append((path, eline,
                                   f"edge target {target!r} resolves to neither a node id "
                                   "nor a manifest repo name"))

        if ntype == "workflow":
            repos = data.get("repos", [])
            if not isinstance(repos, list):
                errors.append((path, kl.get("repos", 1), "repos must be an ordered list"))
                repos = []
            if manifest_repos is None:
                if repos:
                    warnings.append((path, kl.get("repos", 1),
                                     "repo-manifest.yaml absent — skipping workflow repos check"))
            else:
                for r in repos:
                    if r not in manifest_repos:
                        errors.append((path, kl.get("repos", 1),
                                       f"workflow repo {r!r} not found in repo-manifest.yaml"))

        body_offset = n["body_start"]
        for j, line in enumerate(n["body"].split("\n")):
            for m in WIKILINK_RE.finditer(line):
                target = m.group(1).strip()
                if not resolvable(target):
                    lineno = body_offset + j
                    if manifest_repos is None and target not in node_ids:
                        warnings.append((path, lineno,
                                         f"wikilink [[{target}]] is not a node id; cannot check "
                                         "against repo-manifest.yaml (manifest absent)"))
                    else:
                        errors.append((path, lineno,
                                       f"wikilink [[{target}]] resolves to neither a node id "
                                       "nor a manifest repo name"))
    return errors, warnings


def build_graph_json(nodes):
    out_nodes, out_edges = [], []
    for n in sorted(nodes, key=lambda x: x["data"].get("id") or x["rel_id"]):
        data = n["data"]
        node = {"id": data.get("id"), "type": data.get("type"),
                "title": data.get("title"), "status": data.get("status")}
        for opt in ("owners", "repos", "verify_against", "last_verified"):
            if opt in data:
                node[opt] = data[opt]
        out_nodes.append(node)
        for edge in data.get("edges", []) or []:
            if isinstance(edge, dict) and "rel" in edge and "to" in edge:
                out_edges.append({"from": data.get("id"), "rel": edge["rel"], "to": edge["to"]})
        # workflow repos are 'touches' edges, ordered
        if data.get("type") == "workflow":
            for i, r in enumerate(data.get("repos", []) or []):
                out_edges.append({"from": data.get("id"), "rel": "touches", "to": r, "order": i})
    out_edges.sort(key=lambda e: (e["from"] or "", e["rel"], e["to"], e.get("order", -1)))
    return {"nodes": out_nodes, "edges": out_edges}


def run(root, write=True):
    """Run all checks. Returns exit code."""
    root = Path(root)
    manifest = load_manifest(root)
    manifest_repos = manifest_repo_names(manifest) if manifest else None
    errors, warnings = [], []
    if manifest is not None:
        errors, warnings = validate_manifest(manifest, root / "repo-manifest.yaml")
    nodes, nerrors = load_nodes(root)
    verrors, vwarnings = validate(nodes, manifest_repos, root)
    errors = errors + nerrors + verrors
    warnings = warnings + vwarnings

    for path, line, msg in warnings:
        print(f"{path}:{line}: warning: {msg}", file=sys.stderr)
    for path, line, msg in errors:
        print(f"{path}:{line}: error: {msg}", file=sys.stderr)

    if errors:
        print(f"graph_check: {len(errors)} error(s)", file=sys.stderr)
        return 1

    if write and (root / "knowledge").is_dir():
        graph = build_graph_json(nodes)
        out = root / "knowledge" / "graph.json"
        out.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8", newline="\n")
    print(f"graph_check: OK ({len(nodes)} node(s), "
          f"{len(build_graph_json(nodes)['edges'])} edge(s))")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = "."
    write = True
    while argv:
        arg = argv.pop(0)
        if arg == "--root" and argv:
            root = argv.pop(0)
        elif arg == "--no-write":
            write = False
        else:
            print(f"usage: graph_check.py [--root DIR] [--no-write]", file=sys.stderr)
            return 1
    return run(root, write=write)


if __name__ == "__main__":
    sys.exit(main())
