# GENERATED — edit in team-os/harness-layer/ (changes here are overwritten by sync)

Read `AGENTS.md` at the repo root first — it defines this repo's identity,
dependencies, build/test commands, and the platform knowledge-graph protocol.

## Copilot notes

- Skills live in `.claude/skills/` (platform-graph) — Copilot's skill loader
  reads that directory; use platform-graph before cross-repo work.
- Path-scoped instructions are generated into `.github/instructions/`
  from the repo's manifest `tech:` field.
- Every PR description MUST contain a `Knowledge-Update:` line
  (team-os PR link, or `none, because ...`) — CI's knowledge-gate enforces it.
- Repo-local additions belong in `AGENTS.local.md` (never overwritten by sync).
