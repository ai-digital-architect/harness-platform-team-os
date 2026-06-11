# harness-platform-team-os — Knowledge Graph Build

## What this repo is
The single source of truth for the Harness Platform Team: repo-manifest.yaml
(graph backbone), knowledge/ (curated graph), harness-layer/ (distributable
agent config for ~40 code repos), and docs. We are building it per
harness-knowledge-graph-revised-approach.md.

## Operating rules for the build
1. Work ONE task from TASKS.md at a time. Read the task's full entry first.
   Never start a task whose dependencies are not ✅ in TASKS.md.
2. Before writing any graph node, read GRAPH-SCHEMA.md. Validate with
   `python3 scripts/graph_check.py` before finishing.
3. Never edit knowledge/INDEX.md or knowledge/graph.json by hand (CI-built).
4. All new knowledge nodes start `status: draft`. Only humans promote to active.
5. Facts about code repos come from the repos or PR history — never invent.
   If a fact is unverifiable, write `TODO(verify): <question>` instead of guessing.
6. Workflow nodes must be executable: explicit repos in order, commands,
   verification steps. If a step needs tribal knowledge, mark [HUMAN] and stop.
7. Commits: conventional (`feat(knowledge): add eks-upgrade workflow`).
   One task = one branch `task/<TASK-ID>-slug` = one PR. Update TASKS.md
   status in the same PR.
8. Bitbucket, not GitHub: CI is bitbucket-pipelines.yml; PR via `git push`
   + Bitbucket URL in summary (no `gh` CLI).

## Commands
- Validate graph:        python3 scripts/graph_check.py
- Rebuild index:         python3 scripts/build_index.py
- Render harness layer:  python3 harness-layer/sync/render-templates.py --check
- Query graph:           bash harness-layer/skills/platform-graph/scripts/pk.sh <cmd>

## Where things go
- Repo facts/edges → repo-manifest.yaml ONLY (never duplicate into knowledge/)
- Rich cross-repo narrative → knowledge/dependencies/
- Playbooks → knowledge/workflows/   Standards → knowledge/conventions/
- ADRs → knowledge/decisions/        Pitfalls → knowledge/conventions/gotchas/
