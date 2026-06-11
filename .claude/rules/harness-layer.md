---
description: Rules for harness-layer templates, rules, skills, and sync tooling.
paths: ["harness-layer/**"]
---

# harness-layer/ rules

Apply when writing or editing files under `harness-layer/`. This directory is
the **source** for the per-repo agent harness distributed into ~40 code repos
(per revised-approach §6).

1. **Templates render, they don't ship.** Files ending `.tmpl` are inputs to
   `harness-layer/sync/render-templates.py`. Every rendered output starts with
   `# GENERATED — edit in team-os/harness-layer/`.
2. **Manifest-driven only.** Templates read facts from `repo-manifest.yaml`;
   do not hardcode repo names, paths, or tech stacks.
3. **Rendered AGENTS.md must stay under 100 lines** — always-on token budget.
   Push depth into skills (progressive disclosure), not the always-on file.
4. **One rule source, two wrappers.** Each `harness-layer/rules/*.rule.md`
   renders to BOTH `.claude/rules/<n>.md` (with `paths:`) and
   `.github/instructions/<n>.instructions.md` (with `applyTo:`).
5. **Skills are copied verbatim** into target repos under `.claude/skills/`
   so both Claude Code and Copilot discover them. No per-repo skill variants.
6. **Respect local escape hatches.** Never overwrite `AGENTS.local.md` or
   `CLAUDE.local.md` in target repos.
7. **Tech-gated rules.** A target repo only receives the rule files matching
   its manifest `tech:` entries.
8. **Sync scripts are push-gated.** `sync-harness.sh` opens a PR per repo;
   it never force-pushes and never merges.
