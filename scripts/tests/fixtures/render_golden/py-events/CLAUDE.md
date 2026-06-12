# GENERATED — edit in team-os/harness-layer/ (changes here are overwritten by sync)

@AGENTS.md

## Claude-specific notes

- Skills in `.claude/skills/` (shared with Copilot): platform-graph.
  Invoke `platform-graph` BEFORE implementing features or planning any
  cross-repo change.
- Path-scoped rules are generated into `.claude/rules/` from the repo's
  manifest `tech:` field — they apply automatically.
- Personal/per-repo overrides go in `CLAUDE.local.md` (never synced,
  never overwritten).
