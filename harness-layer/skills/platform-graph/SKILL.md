---
name: platform-graph
description: >
  Query the Harness platform knowledge graph: repo purposes, cross-repo
  dependencies, change-impact analysis, implementation workflows, conventions,
  gotchas, and ADRs across all ~40 platform repos. Use BEFORE implementing any
  feature, planning cross-repo changes, or answering "what depends on X /
  what breaks if I change Y" questions.
---
Run `scripts/pk.sh` (alias `pk`). Always begin a task with:
1. `pk repo <this-repo>` — confirm this repo's role and dependencies
2. `pk workflow <task keywords>` then `pk show workflows/<match>` — find and
   FOLLOW the canonical workflow; its `repos:` list defines change order
3. `pk impact <repo>` before changing any interface another repo consumes
If no workflow matches the task, state that explicitly in your summary.
