# TASKS — Knowledge Graph Build

Living board. Update the row of the task you're working on in the same PR.
Status legend: ⬜ todo · 🟡 in-progress · ✅ done · ⛔ blocked.

## Phase 0 — Bootstrap the Harness

| ID   | Title                                   | Status | Depends | PR |
|------|-----------------------------------------|--------|---------|----|
| T0.1 | Scaffold harness + repo skeleton        | ✅     | —       |    |
| T0.2 | graph_check.py + build_index.py         | ✅     | T0.1    | task/T0.2-graph-check-build-index (PR pending) |
| T0.3 | GRAPH-SCHEMA.md + node templates        | ✅     | T0.2    | task/T0.3-graph-schema-templates (PR pending) |
| T0.4 | CI: validate + index                    | ✅     | T0.2    | task/T0.4-ci-validate-index (PR pending) |

**Gate G0 [HUMAN]:** team lead reviews + merges harness PR.

## Phase 1 — Backbone + Graph Seeding

| ID   | Title                                   | Status | Depends     | PR |
|------|-----------------------------------------|--------|-------------|----|
| T1.1 | Land repo-manifest.yaml [HUMAN→REVIEW]  | ✅     | T0.4        | task/T1.1-land-repo-manifest (PR pending) |
| T1.2 | pk CLI + platform-graph skill           | ⬜     | T1.1        |    |
| T1.3 | Capability nodes ×6                     | ⬜     | T1.1        |    |
| T1.4 | Rich dependency nodes                   | ⬜     | T1.2        |    |
| T1.5 | Decisions index                         | ⬜     | T1.1        |    |

**Gate G1 [HUMAN]:** owners review capability + dependency PRs; promote to active.

## Phase 2 — Workflows + Conventions

| ID   | Title                                   | Status | Depends       | PR |
|------|-----------------------------------------|--------|---------------|----|
| T2.1 | Pick top 5 workflows [HUMAN]            | ✅     | —             | task/T2.1-pick-workflows (PR pending) |
| T2.2 | Mine + author workflow nodes ×5         | ⬜     | T2.1, T1.4    |    |
| T2.3 | Convention nodes ×3 + gotcha skill      | ⬜     | T1.4          |    |
| T2.4 | Graph-driven worktree scripts           | ⬜     | T2.2          |    |

**T2.1 selection (2026-06-11, utpal):** the 5 workflow nodes for T2.2 are
`eks-infrastructure-upgrade`, `cross-repo-feature`, `add-lambda-integration`,
`add-harness-api-endpoint`, `new-buildi-image`.
[HUMAN] still owed for T2.2: 2–3 exemplar past changes (PR links or commits)
per workflow — provide together with `$CLONES_DIR` when T1.4/T2.2 start.

**Gate G2 [HUMAN]:** workflow owners resolve TODO(decide); one real ticket executed.

## Phase 3 — Harness Layer Distribution

| ID   | Title                                   | Status | Depends     | PR |
|------|-----------------------------------------|--------|-------------|----|
| T3.1 | Template renderer                       | ⬜     | T1.2        |    |
| T3.2 | sync-harness.sh + pilot to 3 repos      | ⬜     | T3.1        |    |
| T3.3 | knowledge-gate CI for code repos        | ⬜     | T3.1        |    |
| T3.4 | Claude Stop-hook for code repos         | ⬜     | T3.2        |    |

**Gate G3 [HUMAN]:** pilot engineers run real tickets; approve rollout.

## Phase 4 — Living-Graph Automation

| ID   | Title                                   | Status | Depends     | PR |
|------|-----------------------------------------|--------|-------------|----|
| T4.1 | Staleness detector                      | ⬜     | T3.3        |    |
| T4.2 | Gardening workflow + rotation           | ⬜     | T4.1        |    |
| T4.3 | Capture-loop proof [HUMAN-led]          | ⬜     | T3.4        |    |
| T4.4 | Exit review [HUMAN]                     | ⬜     | T4.3        |    |
