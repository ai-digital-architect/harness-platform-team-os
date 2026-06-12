#!/usr/bin/env python3
"""render-templates.py — render the per-repo agent harness from repo-manifest.yaml.

For every non-deprecated repo in the manifest, renders (per revised-approach §6):
  <repo>/AGENTS.md                              identity + deps + graph protocol
  <repo>/CLAUDE.md                              @AGENTS.md + Claude notes
  <repo>/.github/copilot-instructions.md        Copilot pointer + notes
  <repo>/.claude/rules/<n>.md                   tech-matched, from rules/*.rule.md
  <repo>/.github/instructions/<n>.instructions.md   same source, applyTo wrapper
  <repo>/.claude/skills/**                      verbatim copy of harness-layer/skills/

Build/test commands come from harness-layer/surveys/<repo>.md ("## Build & test"
section) when such a survey exists; otherwise TODO(verify) — never guessed.

Usage:
  python3 harness-layer/sync/render-templates.py --out <dir>   # write trees
  python3 harness-layer/sync/render-templates.py --check       # validate only
  (flags combine; --root overrides the team-os root, for tests)

Validation (always, and the only effect of bare --check): manifest parses,
all placeholders resolve, every rendered AGENTS.md is under 100 lines.
Exit 0 success, 1 on any render/validation error. Stdlib-only, deterministic.
"""

import shutil
import sys
from pathlib import Path

TEAM_OS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TEAM_OS / "scripts"))
import graph_check  # noqa: E402

GENERATED_HEADER = "# GENERATED — edit in team-os/harness-layer/"
AGENTS_LINE_BUDGET = 100
TEMPLATES = ("AGENTS.md.tmpl", "CLAUDE.md.tmpl", "copilot-instructions.md.tmpl")
LOCAL_NAMES = {"AGENTS.local.md", "CLAUDE.local.md"}  # never rendered/overwritten


def fail(msg):
    print(f"render-templates: error: {msg}", file=sys.stderr)
    return 1


def load_rules(harness_dir):
    """Parse rules/*.rule.md sources. Returns sorted list of rule dicts."""
    rules = []
    for path in sorted((harness_dir / "rules").glob("*.rule.md")):
        data, _, body_start = graph_check.parse_frontmatter(
            path.read_text(encoding="utf-8"))
        body = "\n".join(path.read_text(encoding="utf-8").split("\n")[body_start - 1:])
        for field in ("name", "tech", "paths"):
            if field not in data:
                raise ValueError(f"{path}: rule source missing {field!r}")
        rules.append({"name": data["name"], "tech": data["tech"],
                      "paths": data["paths"],
                      "description": data.get("description", ""),
                      "body": body.strip("\n")})
    return rules


def bullets(items, empty):
    return "\n".join(f"- {i}" for i in items) if items else f"- {empty}"


def survey_build_test(surveys_dir, repo_name):
    """Extract the '## Build & test' section of a survey report, if present."""
    path = surveys_dir / f"{repo_name}.md"
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").split("\n")
    out, capture = [], False
    for line in lines:
        if line.startswith("## "):
            capture = line.strip().lower() == "## build & test"
            continue
        if capture:
            out.append(line)
    text = "\n".join(out).strip("\n")
    return text or None


def substitute(template, context, source_name):
    text = template
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    if "{{" in text:
        leftover = text[text.index("{{"):].split("}}")[0] + "}}"
        raise ValueError(f"{source_name}: unresolved placeholder {leftover}")
    return text


def render_all(root):
    """Render every non-deprecated repo. Returns {relpath: content} with
    POSIX-style relative paths '<repo>/...'. Raises ValueError on errors."""
    harness = root / "harness-layer"
    manifest = graph_check.load_manifest(root)
    if manifest is None:
        raise ValueError("repo-manifest.yaml not found")
    if manifest["errors"]:
        line, msg = manifest["errors"][0]
        raise ValueError(f"repo-manifest.yaml:{line}: {msg}")
    templates = {}
    for t in TEMPLATES:
        tpath = harness / t
        if not tpath.is_file():
            raise ValueError(f"missing template {tpath}")
        templates[t] = tpath.read_text(encoding="utf-8")
    rules = load_rules(harness)
    surveys_dir = harness / "surveys"

    skills_dir = harness / "skills"
    skill_files = sorted(p for p in skills_dir.rglob("*") if p.is_file()) \
        if skills_dir.is_dir() else []
    skills_list = ", ".join(sorted(p.name for p in skills_dir.iterdir() if p.is_dir())) \
        if skills_dir.is_dir() else "none yet"

    dependents = {}
    for area_repos in manifest["areas"].values():
        for r in area_repos:
            for target in r.get("depends_on", []):
                dependents.setdefault(target, []).append(r["name"])

    out = {}
    for area in sorted(manifest["areas"]):
        meta = manifest.get("area_meta", {}).get(area, {})
        for r in sorted(manifest["areas"][area], key=lambda x: x["name"]):
            name = r["name"]
            tech = r.get("tech", [])
            tech = tech if isinstance(tech, list) else [tech]
            deploy = r.get("deploy_target", "TODO(verify): deploy target not in manifest")
            deploy = ", ".join(deploy) if isinstance(deploy, list) else deploy
            build_test = survey_build_test(surveys_dir, name) or (
                "TODO(verify): build/test commands not yet surveyed — read this "
                "repo's CI config; do not guess. (Filled by repo-surveyor reports "
                "in team-os harness-layer/surveys/.)")
            context = {
                "name": name,
                "area": area,
                "area_description": str(meta.get("description",
                                                 "TODO(verify): area description")),
                "role": str(r.get("role", "TODO(verify): role not in manifest")),
                "tech": ", ".join(tech) if tech else "TODO(verify)",
                "deploy_target": deploy,
                "depends_on_list": bullets(r.get("depends_on", []), "none declared"),
                "dependents_list": bullets(sorted(dependents.get(name, [])),
                                           "none declared"),
                "build_test": build_test,
                "skills_list": skills_list,
            }
            agents = substitute(templates["AGENTS.md.tmpl"], context, "AGENTS.md.tmpl")
            n_lines = agents.count("\n") + 1
            if n_lines >= AGENTS_LINE_BUDGET:
                raise ValueError(
                    f"{name}/AGENTS.md renders to {n_lines} lines "
                    f"(budget < {AGENTS_LINE_BUDGET})")
            out[f"{name}/AGENTS.md"] = agents
            out[f"{name}/CLAUDE.md"] = substitute(
                templates["CLAUDE.md.tmpl"], context, "CLAUDE.md.tmpl")
            out[f"{name}/.github/copilot-instructions.md"] = substitute(
                templates["copilot-instructions.md.tmpl"], context,
                "copilot-instructions.md.tmpl")
            for rule in rules:
                if not set(tech) & set(rule["tech"]):
                    continue
                claude_fm = "---\ndescription: " + rule["description"] + \
                    "\npaths: [" + ", ".join(f'"{g}"' for g in rule["paths"]) + "]\n---"
                out[f"{name}/.claude/rules/{rule['name']}.md"] = "\n".join(
                    [claude_fm, GENERATED_HEADER, "", rule["body"], ""])
                copilot_fm = "---\napplyTo: \"" + ",".join(rule["paths"]) + "\"\n---"
                out[f"{name}/.github/instructions/{rule['name']}.instructions.md"] = \
                    "\n".join([copilot_fm, GENERATED_HEADER, "", rule["body"], ""])
            for sf in skill_files:
                rel = sf.relative_to(skills_dir).as_posix()
                out[f"{name}/.claude/skills/{rel}"] = sf.read_text(encoding="utf-8")
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root, out_dir, check = TEAM_OS, None, False
    while argv:
        arg = argv.pop(0)
        if arg == "--root" and argv:
            root = Path(argv.pop(0))
        elif arg == "--out" and argv:
            out_dir = Path(argv.pop(0))
        elif arg == "--check":
            check = True
        else:
            print("usage: render-templates.py [--check] [--out DIR] [--root DIR]",
                  file=sys.stderr)
            return 1
    if out_dir is None and not check:
        return fail("nothing to do — pass --out <dir> and/or --check")
    try:
        rendered = render_all(root)
    except ValueError as e:
        return fail(str(e))

    repos = sorted({p.split("/", 1)[0] for p in rendered})
    if out_dir is not None:
        changed = 0
        for rel, content in sorted(rendered.items()):
            if Path(rel).name in LOCAL_NAMES:
                continue
            target = out_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            old = target.read_text(encoding="utf-8") if target.is_file() else None
            if old != content:
                target.write_text(content, encoding="utf-8", newline="\n")
                changed += 1
        print(f"render-templates: wrote {out_dir} — {len(repos)} repo(s), "
              f"{len(rendered)} file(s), {changed} changed")
    else:
        print(f"render-templates: check OK — {len(repos)} repo(s), "
              f"{len(rendered)} file(s) render cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
