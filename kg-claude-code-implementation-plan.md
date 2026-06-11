# Harness Platform Knowledge Graph — Claude Code Implementation Plan
## Phased Plan, Task Breakdowns, and the Implementation Harness That Executes Them

**Purpose:** Hand this document to Claude Code to implement the revised knowledge-graph approach (`harness-knowledge-graph-revised-approach.md`). It contains (Part 1) the Claude Code harness — designed per the Claude Code Customization Architecture — that governs the implementation work itself, (Part 2) the phased task breakdown with per-task prompts and acceptance criteria, and (Part 3) the execution protocol.

**How to use:** Bootstrap the harness (Phase 0) by hand or with a single Claude Code session, then execute each task as its own Claude Code session using the task prompts verbatim. Tasks marked **[HUMAN]** require team input and cannot be delegated; tasks marked **[REVIEW]** can be agent-drafted but require named-owner approval before merge.

---

# Part 1 — The Implementation Harness

The harness lives in `harness-platform-team-os` and uses six customization surfaces from the architecture doc: project memory (CLAUDE.md), path-scoped rules, sub-agents, skills, hooks, and settings/permissions. It is itself the first artifact built (Phase 0), so every subsequent task runs under its governance.

## 1.1 Harness file tree

```
harness-platform-team-os/
├── CLAUDE.md                              # H-1: project memory for the build
├── AGENTS.md                              # H-2: cross-harness mirror (Copilot reads this)
├── TASKS.md                               # H-3: living task board (this plan's Part 2, tracked)
├── .claude/
│   ├── settings.json                      # H-4: permissions + hooks
│   ├── rules/
│   │   ├── graph-nodes.md                 # H-5: paths: knowledge/**  — node authoring rules
│   │   ├── scripts.md                     # H-6: paths: scripts/**   — tooling code rules
│   │   └── harness-layer.md               # H-7: paths: harness-layer/** — template rules
│   ├── agents/
│   │   ├── node-author.md                 # H-8: drafts graph nodes
│   │   ├── workflow-miner.md              # H-9: mines workflows from PR/commit history
│   │   ├── graph-validator.md             # H-10: read-only reviewer of graph changes
│   │   └── repo-surveyor.md               # H-11: surveys a code repo to draft its facts
│   ├── skills/
│   │   ├── run-task/SKILL.md              # H-12: executes one TASKS.md task end-to-end
│   │   └── mine-workflow/SKILL.md         # H-13: PR-history → workflow node draft
│   └── hooks/
│       ├── graph-check-on-edit.sh         # H-14: PostToolUse → graph_check on node edits
│       └── task-gate-on-stop.sh           # H-15: Stop → block until task criteria addressed
└── GRAPH-SCHEMA.md                        # built in Phase 1, referenced by rules
```

## 1.2 CLAUDE.md (project memory — keep under 200 lines)

```markdown
# harness-platform-team-os — Knowledge Graph Build

@AGENTS.md

## What this repo is
The single source of truth for the Harness Platform Team: repo-manifest.yaml
(graph backbone), knowledge/ (curated graph), harness-layer/ (distributable
agent config for ~40 code repos), and docs. We are building it per
harness-knowledge-graph-revised-approach.md.

## Operating rules for the build
1. Work ONE task from TASKS.md at a time. Read the task's full entry first.
   Never start a task whose dependencies are not ✅ in TASKS.md.
2. Before writing any graph node, read GRAPH-SCHEMA.md. Validate with
   `python3 scripts/graph_check.py` before finishing (the PostToolUse hook
   also runs it — fix failures immediately, do not defer).
3. Never edit knowledge/INDEX.md or knowledge/graph.json by hand (CI-built).
4. All new knowledge nodes start `status: draft`. Only humans promote to active.
5. Facts about code repos come from the repos or PR history — never invent.
   Use the repo-surveyor sub-agent against a local clone; if a fact is
   unverifiable, write `TODO(verify): <question>` instead of guessing.
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
```

## 1.3 Settings, permissions, hooks (`.claude/settings.json`)

```json
{
  "permissions": {
    "allow": [
      "Read", "Glob", "Grep", "Write", "Edit", "MultiEdit",
      "Bash(python3 scripts/*)", "Bash(yq *)", "Bash(git status*)",
      "Bash(git diff*)", "Bash(git log*)", "Bash(git add *)",
      "Bash(git commit *)", "Bash(git checkout -b task/*)",
      "Bash(bash harness-layer/skills/platform-graph/scripts/pk.sh *)"
    ],
    "ask": [
      "Bash(git push*)",
      "Bash(bash harness-layer/sync/sync-harness.sh*)",
      "Bash(git clone*)"
    ],
    "deny": ["Bash(rm -rf*)", "Bash(git push --force*)", "WebFetch"]
  },
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{ "type": "command",
                  "command": "bash .claude/hooks/graph-check-on-edit.sh" }]
    }],
    "Stop": [{
      "matcher": "",
      "hooks": [{ "type": "command",
                  "command": "bash .claude/hooks/task-gate-on-stop.sh" }]
    }]
  }
}
```

`graph-check-on-edit.sh` (zero-token, deterministic): if the last edit touched `knowledge/**` or `repo-manifest.yaml`, run `graph_check.py`; on failure, emit errors to stderr and exit 2 so Claude fixes them immediately.

`task-gate-on-stop.sh`: if the working tree has changes but the session has not (a) run `graph_check.py` cleanly and (b) updated the current task's checklist in TASKS.md, exit 2 with a reminder listing the unmet acceptance criteria. This makes acceptance criteria self-enforcing per session.

## 1.4 Sub-agents

**`repo-surveyor`** — read-only fact gatherer for a single code repo.

```yaml
---
name: repo-surveyor
description: >
  Surveys one platform code repo (local clone path given in the prompt) and
  returns verified facts: purpose, tech, entry points, build/test commands,
  consumed/published interfaces, terraform outputs/inputs, event topics.
  Use when authoring or verifying manifest entries, dependency nodes, or
  rendered AGENTS.md content. Never guesses — marks unknowns as TODO(verify).
tools: [Read, Glob, Grep, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 15
---
Survey the repo at the path provided. Return a structured report:
PURPOSE / TECH+VERSIONS / ENTRY POINTS / BUILD+TEST COMMANDS (verified by
reading CI config and Makefiles, not guessed) / DEPENDS-ON (imports, terraform
remote state, API clients) / PROVIDES (endpoints, topics, terraform outputs,
published artifacts) / OPEN QUESTIONS as TODO(verify) items.
```

**`workflow-miner`** — reconstructs how the team actually ships a change type.

```yaml
---
name: workflow-miner
description: >
  Mines git history across multiple repo clones to reconstruct the real
  sequence of changes for a recurring change type (e.g., "add a lambda
  integration"). Use when drafting workflow nodes. Read-only.
tools: [Read, Glob, Grep, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 25
memory: project
---
Given a change type and a list of repo clone paths: find 3-5 past examples
(git log --all --grep / file-pattern matching), reconstruct the cross-repo
order of changes from commit timestamps and PR references, extract the files
touched per step and the verification commands used. Return a draft workflow
body with an ORDERED repos list, flagging steps where examples disagree as
TODO(decide) for humans.
```

**`node-author`** — the writer (the main session usually plays this role; the agent exists for parallel batches).

```yaml
---
name: node-author
description: >
  Authors or revises knowledge-graph nodes from survey/mining reports,
  strictly following GRAPH-SCHEMA.md frontmatter and templates. Use for
  batch node creation after surveys complete.
tools: [Read, Glob, Grep, Write, Edit, Bash]
maxTurns: 20
skills: []
---
Author the requested node(s) per GRAPH-SCHEMA.md. status: draft always.
Every edge target must exist. Run `python3 scripts/graph_check.py` and fix
all errors before finishing. No invented facts: only content from the
provided reports; gaps become TODO(verify).
```

**`graph-validator`** — independent reviewer, invoked before every PR.

```yaml
---
name: graph-validator
description: >
  Reviews graph changes for schema compliance, edge correctness, executability
  of workflows, and consistency with repo-manifest.yaml. Use before opening
  any PR that touches knowledge/ or the manifest. Read-only.
model: opus
effort: high
tools: [Read, Glob, Grep, Bash]
disallowedTools: [Write, Edit, MultiEdit]
maxTurns: 10
---
Review the diff. Score each changed node: (1) schema-valid, (2) edges resolve
and use correct rel types, (3) workflow steps executable by an agent with no
tribal knowledge, (4) no facts duplicated from the manifest, (5) no invented
facts (spot-check 3 claims against the repos/manifest). Return PASS or a
blocking issue list with file/line references. Do not pass if any TODO(decide)
items are unresolved in an `active`-status node.
```

## 1.5 The `run-task` skill (how every session starts)

```markdown
---
name: run-task
description: >
  Execute one task from TASKS.md end-to-end with full protocol: dependency
  check, branch, implementation, validation, review, PR prep, board update.
  Use at the start of every implementation session: /run-task <TASK-ID>.
---
1. Read TASKS.md; locate $ARGUMENTS. Verify all `depends:` tasks are ✅;
   if not, STOP and report which are missing.
2. Create branch `task/<id>-<slug>`. Restate the task's deliverables and
   acceptance criteria as your TodoWrite list.
3. Implement per the task prompt. Apply CLAUDE.md operating rules.
4. Run every command listed under the task's **Verify** section; all must pass.
5. Invoke the graph-validator sub-agent on the diff (if knowledge/ or the
   manifest changed). Resolve all blocking issues.
6. Update the task's row in TASKS.md (status, PR link placeholder, notes).
7. Commit; summarize for PR: what changed, verification evidence,
   open TODO(verify)/TODO(decide)/[HUMAN] items created.
```

---

# Part 2 — Phased Task Breakdown

Conventions: every task has an ID, dependencies, an executable prompt (give it to Claude Code verbatim after `/run-task <ID>` loads context), deliverables, and acceptance criteria (the **Verify** commands the Stop hook enforces). Effort: S = one short session, M = one full session, L = multiple sessions or parallel sub-agents.

## Phase 0 — Bootstrap the Harness (Week 1, days 1–2)

> Phase 0 is the only phase executed without the harness. Run it as one supervised Claude Code session in a fresh clone of team-os (create the empty Bitbucket repo first — [HUMAN], 10 minutes).

**T0.1 — Scaffold harness + repo skeleton** (M) — depends: none
*Prompt:* "Create the repository skeleton and Claude Code harness exactly as specified in Part 1 of kg-claude-code-implementation-plan.md (in this directory): CLAUDE.md, AGENTS.md (mirror of CLAUDE.md's repo description + commands, no Claude-specific content), TASKS.md (transcribe all tasks from Part 2 of the plan as a markdown board: ID | title | status | depends | PR), .claude/settings.json, the two hook scripts, four sub-agent files, two skill directories, three rule files (graph-nodes.md with `paths: ["knowledge/**"]` summarizing schema rules; scripts.md with `paths: ["scripts/**"]` requiring stdlib-only python3 + exit codes + tests; harness-layer.md with `paths: ["harness-layer/**"]` covering template conventions), and empty directories: knowledge/{capabilities,workflows,dependencies,conventions/gotchas,decisions}, harness-layer/{rules,skills,sync}, scripts/. Add bitbucket-pipelines.yml with a placeholder validate step."
*Deliverables:* full tree from §1.1; TASKS.md board.
*Verify:* `find .claude -type f | wc -l` ≥ 10; `python3 -c "import json; json.load(open('.claude/settings.json'))"`; hooks are executable.

**T0.2 — graph_check.py + build_index.py** (M) — depends: T0.1
*Prompt:* "Implement scripts/graph_check.py per the revised-approach doc §7 Layer 2: parse YAML frontmatter from all knowledge/**/*.md (stdlib-only: write a minimal frontmatter parser, no pyyaml dependency), validate: required fields (id,type,title,status), id==path, type in closed set, edges[].rel in closed vocabulary, edges[].to resolves to an existing node id OR a manifest repo name, wikilinks resolve, workflow `repos:` entries exist in repo-manifest.yaml (skip check with warning if manifest absent). Emit knowledge/graph.json (nodes+edges). Exit 1 on errors with file:line reports. Implement scripts/build_index.py generating knowledge/INDEX.md grouped by type with status and last_verified columns plus a graph-health line (% verified <60d). Write scripts/tests/test_graph_check.py with fixture nodes covering each failure mode; runnable via python3 -m unittest discover scripts/tests."
*Verify:* `python3 -m unittest discover scripts/tests` passes; `python3 scripts/graph_check.py` exits 0 on empty graph.

**T0.3 — GRAPH-SCHEMA.md + node templates** (S) — depends: T0.2
*Prompt:* "Author GRAPH-SCHEMA.md from the revised-approach doc §3: node types table, closed edge vocabulary with direction rules, full frontmatter spec including verify_against and the episodic fields (date/category/impact/tags) retained for decisions and gotchas. Add `_template.md` files (excluded by graph_check) in each knowledge/ subdirectory matching the spec, including the workflow template with ordered repos list, per-step commands, and Verification section."
*Verify:* `python3 scripts/graph_check.py` clean; each subdir has `_template.md`.

**T0.4 — CI: validate + index** (S) — depends: T0.2
*Prompt:* "Replace the placeholder bitbucket-pipelines.yml: on PR and main — run unit tests, run graph_check.py, run build_index.py, fail if `git diff --exit-code knowledge/INDEX.md knowledge/graph.json` shows drift."
*Verify:* `python3 -c "import yaml"` unavailable is fine — lint pipeline YAML with yq; local dry-run of each script.

> **Gate G0 [HUMAN]:** team lead reviews the harness PR, merges, confirms a second engineer can clone and run `/run-task` successfully.

## Phase 1 — Backbone + Graph Seeding (Weeks 1–3)

**T1.1 — [HUMAN→REVIEW] Land repo-manifest.yaml** (S) — depends: T0.4
*Prompt:* "Copy the Full Manifest YAML from team-struture.md §3 into repo-manifest.yaml verbatim. Extend graph_check.py to also validate the manifest: unique repo names, depends_on targets exist, deprecated repos not depended on by active repos (warning), every repo belongs to exactly one product area. Report all violations found in the as-is manifest as a checklist in the PR summary — do not fix data yourself."
*Verify:* `python3 scripts/graph_check.py` runs manifest checks; violations listed, not silently fixed.
*[HUMAN]:* team corrects real-world inaccuracies in the manifest (30–60 min review).

**T1.2 — pk CLI + platform-graph skill** (M) — depends: T1.1
*Prompt:* "Implement harness-layer/skills/platform-graph/scripts/pk.sh per revised-approach §5 (repo/deps/workflow/show/impact/search/verify; PK_HOME cache; ff-only sync) plus scripts/impact.py computing the transitive closure of dependents from repo-manifest.yaml + graph.json. Write the SKILL.md exactly per §5. Add scripts/tests/test_impact.py with a fixture manifest reproducing the EKS chain from team-struture.md and asserting impact('harness-terraform-data') includes route53 and both eks repos."
*Verify:* unit tests pass; `bash pk.sh deps 111282-113518-terraform-base` lists ≥4 repos; `bash pk.sh impact harness-terraform-data` matches the documented chain.

**T1.3 — Capability nodes ×6** (M) — depends: T1.1
*Prompt:* "Author one capability node per product area in the manifest (infrastructure, self-service, container-builds, integrations, developer-tools, policy-and-governance): narrative purpose, `implements` edges from member repos (derive membership from the manifest; do not restate per-repo facts), key cross-area relationships. Source narrative ONLY from team-struture.md descriptions and manifest fields; everything else is TODO(verify). status: draft."
*Verify:* graph_check clean; 6 nodes; every manifest repo reachable from exactly one capability via `implements`.

**T1.4 — Rich dependency nodes** (L, parallelizable) — depends: T1.2; needs local clones [HUMAN: provide clone dir]
*Prompt:* "For each of these high-value edges, dispatch the repo-surveyor sub-agent against both sides (clones under $CLONES_DIR) and author a knowledge/dependencies/ node: (1) the terraform chain data→integration→{eks-blue,eks-green,route53}; (2) harness-api→eks-blue; (3) lambda-harness-event-handler→harness-terraform-lambda; (4) buildi→buildi-terraform-ecs; (5) each subtree_plan entry as `subtree-of` edges with the update protocol from team-struture.md §4. Each node: nature, contract location (real file paths from surveys), change protocol, failure modes. Unverifiable claims → TODO(verify)."
*Verify:* graph_check clean; ≥8 dependency nodes; zero invented paths (validator spot-check passes).

**T1.5 — Decisions index** (S) — depends: T1.1; [HUMAN: provide harness-adr clone or export]
*Prompt:* "Create knowledge/decisions/ nodes indexing each ADR in the harness-adr clone: id, title, status, one-paragraph summary, `governed-by`-able id, link to the source ADR file. Do not copy full ADR bodies — harness-adr stays the ADR system of record; these nodes make ADRs graph-addressable."
*Verify:* graph_check clean; node count == ADR count; each node links a real source path.

> **Gate G1 [HUMAN]:** owners review/correct capability + dependency PRs; resolve TODO(verify) items or convert to tickets; promote accurate nodes to `status: active`.

## Phase 2 — Workflows + Conventions (Weeks 2–4, overlaps)

**T2.1 — [HUMAN] Pick the top 5 workflows** (30 min): from the candidate list (cross-repo-feature, eks-infrastructure-upgrade, add-lambda-integration, add-harness-api-endpoint, new-buildi-image, terraform-module-subtree-update, deprecate-a-repo) the team picks 5 by frequency and names 2–3 exemplar past changes for each.

**T2.2 — Mine + author workflow nodes ×5** (L) — depends: T2.1, T1.4
*Prompt:* "For each selected workflow: run the workflow-miner sub-agent over the exemplar changes (clones in $CLONES_DIR), then author the node from the mining report using the workflow template: ordered repos list, per-step repo/files/commands/done-definition, Verification section with runnable commands, edges to governing conventions and known gotchas, verify_against globs per touched repo. Disagreements between exemplars → TODO(decide). The eks-infrastructure-upgrade node must reproduce and formalize the worked example in team-struture.md §5. status: draft."
*Verify:* graph_check clean; every step has a command or an explicit [HUMAN] marker; `pk.sh show workflows/<each>` renders.

**T2.3 — Convention nodes ×3 + gotcha capture loop** (M) — depends: T1.4
*Prompt:* "Author terraform-patterns, lambda-python-standards, java-spring-standards convention nodes: extract candidate standards by surveying 2–3 repos per tech (repo-surveyor) and looking for consistent patterns; every rule gets a `source:` citation (file path) or TODO(verify) — never invent a standard. Then implement the record-gotcha skill (harness-layer/skills/record-gotcha/SKILL.md): from the current session's discovery, draft a gotcha node using the episodic frontmatter template, print the full file content and the team-os PR steps."
*Verify:* graph_check clean; every convention rule carries a source citation; skill file lints against schema.

**T2.4 — Graph-driven worktree scripts** (M) — depends: T2.2
*Prompt:* "Implement scripts/setup-feature-worktrees.sh and scripts/merge-feature.sh per revised-approach §8: read the ordered repos list from a workflow node (via pk.sh show + frontmatter parse), create worktrees in order, and merge in the same order; sibling steps (eks-blue/eks-green) flagged parallelizable. Implement the cross-repo-feature skill SKILL.md orchestrating: find workflow → worktrees → per-step implement+verify → PRs in order → Knowledge-Update reminder. Add a dry-run mode used in tests."
*Verify:* dry-run against workflows/eks-infrastructure-upgrade prints the 5-repo order from team-struture.md exactly; unit test for the frontmatter-order parser passes.

> **Gate G2 [HUMAN]:** workflow owners resolve TODO(decide) items; one engineer executes one real ticket following a workflow node and files gaps as issues; accurate workflows promoted to active.

## Phase 3 — Harness Layer Distribution (Weeks 4–8)

**T3.1 — Template renderer** (L) — depends: T1.2
*Prompt:* "Implement harness-layer/sync/render-templates.py per revised-approach §6: for each non-deprecated manifest repo render AGENTS.md (<100 lines: identity/tech/deploy_target/dependencies from its manifest entry, build/test commands token left as TODO(verify) unless a survey report exists, graph protocol referencing pk), CLAUDE.md (`@AGENTS.md` + Claude-specific notes incl. platform-graph + cross-repo-feature + record-gotcha skills), .github/copilot-instructions.md, and tech-matched rules: harness-layer/rules/*.rule.md (write the three sources: terraform, python-lambda, java-spring) rendered to BOTH .claude/rules/<n>.md with `paths:` and .github/instructions/<n>.instructions.md with `applyTo:`, selected by the repo's tech field. Copy .claude/skills/ verbatim. Every generated file starts with `# GENERATED — edit in team-os/harness-layer/`. Support --check (diff only) and --out <dir>. Unit tests render a fixture manifest of 3 repos (one per tech) and snapshot-compare."
*Verify:* tests pass; `--check --out /tmp/render` produces per-repo trees; generated AGENTS.md for harness-api < 100 lines.

**T3.2 — sync-harness.sh + pilot to 3 repos** (M) — depends: T3.1; [HUMAN: pick pilots — suggest harness-terraform-data, lambda-harness-event-handler, harness-api]
*Prompt:* "Implement harness-layer/sync/sync-harness.sh: for each target repo clone, render, diff, and if changed create branch chore/harness-sync, commit, push (push is permission-gated — request approval per repo), and print the Bitbucket PR URL to open. Respect AGENTS.local.md/CLAUDE.local.md by never writing those names. Run it for the 3 pilot repos only."
*Verify:* 3 PRs prepared; in a pilot clone, `claude` session shows rendered CLAUDE.md loaded and `/platform-graph` available; in VS Code, Copilot lists the platform-graph skill.

**T3.3 — knowledge-gate CI for code repos** (M) — depends: T3.1
*Prompt:* "Write harness-layer/ci/knowledge-gate.sh + a bitbucket-pipelines.yml snippet for code repos: fetch team-os graph.json (raw URL or shallow clone), intersect the PR's changed files with verify_against globs for this repo, and fail unless the PR description (Bitbucket API, $BITBUCKET_PR_ID) contains `Knowledge-Update:` with a link or a 'none, because' justification; print the affected node ids on failure. Include the snippet in the renderer output for pilot repos. Unit-test the glob-intersection logic with fixtures."
*Verify:* tests pass; simulated run with a changed `*.tf` path against the eks workflow's verify_against fails without the PR field and passes with it.

**T3.4 — Claude Stop-hook for code repos** (S) — depends: T3.2
*Prompt:* "Add to the rendered .claude/settings.json for code repos: a SessionStart hook warming the pk cache and a Stop hook (knowledge-reminder.sh, shipped via harness-layer) that exits 2 when the session modified files matching this repo's verify_against globs (read from cached graph.json) and the transcript flag file ~/.pk-consulted-$REPO is absent — message instructs the agent to state which workflow it followed and whether a graph update is needed."
*Verify:* renderer includes hooks; manual test in a pilot clone: edit a watched file, attempt to stop, observe block then release.

> **Gate G3 [HUMAN]:** pilot engineers run 2–3 real tickets per harness (Claude Code AND Copilot) in pilot repos; gaps filed; team approves rollout of sync + gate to all active repos (then rerun T3.2/T3.3 unrestricted — agent task, push-gated).

## Phase 4 — Living-Graph Automation (Weeks 8–12)

**T4.1 — Staleness detector** (M) — depends: T3.3
*Prompt:* "Implement scripts/staleness.py + a scheduled Bitbucket Pipelines job in team-os: for each active node, query the Bitbucket API for commits in verify_against repos/paths since last_verified; emit a stale-nodes report, update the graph-health metric inputs, and create/refresh one Bitbucket task or issue per stale node titled '<id> may be stale — N commits since <date>'. Dry-run mode with fixture API responses for tests."
*Verify:* tests pass with fixtures; dry-run produces a correct report for a synthetic stale node.

**T4.2 — Gardening workflow node + rotation** (S) — depends: T4.1
*Prompt:* "Author knowledge/workflows/graph-gardening.md: monthly rotation procedure — triage stale-node issues, dispatch node-author to draft updates, graph-validator review, bump last_verified, archive resolved gotchas older than 1 year per the memory-spec maintenance rules. Include the pk and script commands for each step."
*Verify:* graph_check clean; every step has a command.

**T4.3 — Capture-loop proof** (ongoing) — depends: T3.4
*[HUMAN-led]:* over 4 weeks, ≥5 gotcha/convention nodes must originate from real agent sessions via /record-gotcha (either harness). If the rate is lower, treat as a defect: agent investigates whether the skill description, hook nagging, or PR template is the failure point and proposes a fix PR.

**T4.4 — Exit review [HUMAN]:** all active repos synced + gated; ≥50% of eligible changes shipped following a workflow node; graph health ≥80%; knowledge-gate has blocked-and-corrected ≥1 real PR; decision recorded (as a graph decision node) on whether Track B vector search or an MCP shim over pk is warranted — default no.

---

# Part 3 — Execution Protocol

**Session discipline.** One task = one session = one branch = one PR. Start every session with `/run-task <ID>`. If a task exceeds the context comfortably (T1.4, T2.2, T3.1), use the documented sub-agents for the read-heavy halves; their isolated contexts keep the main session lean (per the customization architecture's token strategy).

**Order and parallelism.** Phases gate sequentially at G0–G3, but within phases the dependency fields permit parallel sessions (e.g., T1.3 ∥ T1.4 ∥ T1.5 after T1.2). Two engineers can run parallel sessions safely because every task owns disjoint paths; TASKS.md conflicts are the merge signal that two sessions collided.

**Human touchpoints are load-bearing.** [HUMAN] tasks (manifest correction, workflow selection, TODO(decide) resolution, gate reviews, status promotion to active) are where tribal knowledge enters the graph. Budget them: G0 ~1h, G1 ~3h across owners, G2 ~4h including the live ticket, G3 ~1 week of pilot usage, T4.4 ~1h.

**Failure handling.** Any task whose Verify step cannot pass is finished as a draft PR with a FAILED section: what passed, what didn't, hypothesis, and the exact command output — never silently weakened acceptance criteria. The graph-validator's blocking issues are resolved before requesting human review, not bundled into it.

**What Claude Code must never do in this build** (enforced by permissions + rules): force-push; edit generated files (INDEX.md, graph.json, rendered harness files in code repos) by hand; promote a node to active; invent repo facts, commands, or standards; merge its own PRs.
