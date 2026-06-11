# Harness Platform Team — File-Based Knowledge Graph for Agentic SDLC
## Revised Approach: Unifying Team-OS, the Six-Memory Architecture, and Dual-Harness (Claude Code + GitHub Copilot) Customization

**Date:** June 2026
**Status:** Proposed — supersedes the standalone `platform-knowledge` repo proposal; builds on `team-struture.md`, `track-a-file-based-guide.md`, `claude-code-customization-architecture-revised.md`, and `ghcopilot-customization-arch.md`.

---

## 1. Feasibility Verdict

**Yes — a file-based knowledge graph that drives both harnesses is feasible, and your existing documents already contain ~80% of the design.** The remaining 20% is unification: the team-structure plan, the six-memory-type spec, and the two harness customization architectures were written as separate efforts and need to be merged into one system with one source of truth.

The feasibility rests on five concrete convergence points verified across your documents:

| Convergence point | Claude Code | GitHub Copilot | Implication |
|---|---|---|---|
| **`AGENTS.md`** (open standard) | Reads it always-on; `@AGENTS.md` importable into CLAUDE.md | Reads it when coding agent operates | One file carries cross-harness instructions per repo |
| **Skills** (Anthropic open standard) | `.claude/skills/<name>/SKILL.md` | Reads `.github/skills/`, **`.claude/skills/`**, and `.agents/skills/` | One skill directory serves both harnesses — write once |
| **Plain markdown + file reads** | Read/Glob/Grep native | `codebase`/`search` tools read repo files | Graph nodes as markdown files are natively traversable by both |
| **Path-scoped rules** | `.claude/rules/*.md` with `paths:` | `.github/instructions/*.instructions.md` with `applyTo:` | Same content, two thin wrapper formats (generatable from one source) |
| **YAML manifest queryable via shell** | Bash tool | terminal tools / CLI | `repo-manifest.yaml` is queryable by both via `yq`/`grep` |

Two constraints surfaced in review that shape the design:

1. **Bitbucket, not GitHub.** The repos live in Bitbucket project HARNESS. This means: CI enforcement uses **Bitbucket Pipelines** (not GitHub Actions), Copilot's GitHub.com-native surfaces (cloud coding agent, org instructions, PR review on GitHub) are unavailable, and Copilot is used through **VS Code / JetBrains / Copilot CLI** against Bitbucket-hosted clones. The `.github/` directory convention still works locally — VS Code reads `.github/copilot-instructions.md` from the working tree regardless of the remote host.
2. **The known gap "no team-level CLAUDE.md" is the central problem to solve.** With ~40 repos, knowledge cannot be duplicated into each repo's CLAUDE.md. The graph must live in one place (team-os) and be *distributed* to every repo's agent sessions by a deliberate mechanism (Section 6).

---

## 2. Unified Architecture — One Repo, Three Layers

**Decision: do not create a separate `platform-knowledge` repo.** The `harness-platform-team-os` repo from `team-struture.md` *is* the knowledge graph repo. Creating a second coordination repo would split the source of truth. Instead, team-os gains a `knowledge/` graph layer, and `repo-manifest.yaml` is promoted from "registry" to **the backbone node-and-edge file of the graph**.

```
harness-platform-team-os/                  (Bitbucket — single source of truth)
│
├── repo-manifest.yaml                     # GRAPH BACKBONE: repo nodes + depends_on edges
│                                          # (already designed in team-struture.md — unchanged)
├── GRAPH-SCHEMA.md                        # Node types, edge types, frontmatter spec
├── CLAUDE.md                              # Team context for Claude sessions in this repo
├── AGENTS.md                              # Cross-harness context (Copilot reads this too)
├── .github/copilot-instructions.md       # Copilot-specific pointer to the graph
│
├── knowledge/                             # THE KNOWLEDGE GRAPH (curated layer)
│   ├── INDEX.md                           # Auto-generated node index (CI-built)
│   ├── graph.json                         # Auto-generated machine-readable edges (CI-built)
│   ├── capabilities/                      # What the platform DOES (maps to product_areas)
│   │   ├── self-service.md
│   │   ├── container-builds.md            # buildi ecosystem narrative
│   │   ├── integrations.md
│   │   ├── developer-tools.md
│   │   ├── infrastructure.md
│   │   └── policy-and-governance.md
│   ├── workflows/                         # PROCEDURAL memory — executable playbooks
│   │   ├── cross-repo-feature.md          # worktree workflow from team-struture.md §5
│   │   ├── eks-infrastructure-upgrade.md  # the blue/green chain example, formalized
│   │   ├── add-lambda-integration.md
│   │   ├── add-harness-api-endpoint.md
│   │   ├── new-buildi-image.md
│   │   ├── terraform-module-subtree-update.md
│   │   └── deprecate-a-repo.md
│   ├── dependencies/                      # Cross-repo edges TOO RICH for the manifest
│   │   ├── harness-api--harness-terraform-eks-blue.md
│   │   └── lambda-event-handler--harness-terraform-lambda.md
│   ├── conventions/                       # SEMANTIC memory — standards + gotchas
│   │   ├── terraform-patterns.md
│   │   ├── lambda-python-standards.md
│   │   ├── java-spring-standards.md
│   │   └── gotchas/
│   │       └── 2026-06-eks-blue-green-route53.md
│   └── decisions/                         # EPISODIC memory — ADRs (indexes harness-adr)
│       └── 0001-blue-green-eks.md
│
├── harness-layer/                         # DISTRIBUTABLE per-repo agent harness (Section 6)
│   ├── AGENTS.md.tmpl                     # Template: rendered per-repo from manifest
│   ├── CLAUDE.md.tmpl
│   ├── copilot-instructions.md.tmpl
│   ├── rules/                             # Source of truth for path-scoped rules
│   │   ├── terraform.rule.md              #   → .claude/rules/ + .github/instructions/
│   │   ├── python-lambda.rule.md
│   │   └── java-spring.rule.md
│   ├── skills/                            # Shared skills (work in BOTH harnesses)
│   │   ├── platform-graph/
│   │   │   ├── SKILL.md                   # "Query the platform knowledge graph"
│   │   │   └── scripts/pk.sh              # The graph CLI (Section 5)
│   │   ├── cross-repo-feature/
│   │   │   └── SKILL.md                   # Drives the worktree workflow
│   │   └── record-gotcha/
│   │       └── SKILL.md                   # Capture loop (Section 7)
│   └── sync/
│       ├── sync-harness.sh                # Pushes harness-layer into each code repo
│       └── render-templates.py            # Manifest-driven template rendering
│
├── product-development/                   # (unchanged from team-struture.md)
│   ├── product/ …  engineering/ …  analytics/ …  infrastructure/ …
├── team/                                  # (unchanged)
└── scripts/
    ├── graph_check.py                     # Referential integrity (CI)
    ├── build_index.py                     # INDEX.md + graph.json generation
    └── setup-feature-worktrees.sh         # (from team-struture.md, now graph-aware)
```

The three layers:

1. **Backbone layer** — `repo-manifest.yaml`. Already designed. Repo nodes, `depends_on`/`deploy_target`/`tech` edges, deprecation status, subtree plan. *Machine-authoritative*: CI validates it; scripts and agents query it with `yq`.
2. **Curated layer** — `knowledge/`. Markdown nodes with YAML frontmatter following the six-memory-type spec (Section 4). *Human-authoritative*: PR-reviewed, owned, versioned.
3. **Harness layer** — `harness-layer/`. The thin, generated agent configuration distributed into every code repo so that both Claude Code and Copilot sessions are *born knowing* the graph exists and how to query it.

---

## 3. The Graph Data Model

### 3.1 Node and edge types

| Node type | Lives in | Backed by memory type | Example |
|---|---|---|---|
| `repo` | `repo-manifest.yaml` (entries) | Semantic | `harness-api`, `buildi-kaniko` |
| `capability` | `knowledge/capabilities/` | Semantic | `container-builds` |
| `workflow` | `knowledge/workflows/` | Procedural | `eks-infrastructure-upgrade` |
| `dependency` | manifest `depends_on` + `knowledge/dependencies/` for rich edges | Semantic | `harness-api → eks-blue` |
| `convention` | `knowledge/conventions/` | Semantic | `terraform-patterns` |
| `gotcha` | `knowledge/conventions/gotchas/` | Episodic→Semantic | `eks-blue-green-route53` |
| `decision` | `knowledge/decisions/` (indexes `harness-adr`) | Episodic | `0001-blue-green-eks` |

Edge vocabulary (closed; extended only by PR to GRAPH-SCHEMA.md): `depends-on`, `deploys-to`, `publishes-to`, `consumes-from`, `implements` (repo→capability), `touches` (workflow→repo, **ordered** — this drives worktree merge order), `governed-by` (any→convention/decision), `affected-by` (any→gotcha), `supersedes` (decision→decision), `subtree-of` (consumer→source, from the manifest's `subtree_plan`).

### 3.2 Node frontmatter (knowledge/ files)

```yaml
---
id: workflows/eks-infrastructure-upgrade
type: workflow
title: EKS version upgrade across blue/green clusters
status: active                  # draft | active | deprecated
owners: [infra-team]
repos:                          # ORDERED — defines worktree creation & merge order
  - harness-terraform-data
  - harness-terraform-integration
  - harness-terraform-eks-blue
  - harness-terraform-eks-green
  - harness-terraform-route53
edges:
  - {rel: governed-by, to: conventions/terraform-patterns}
  - {rel: affected-by, to: conventions/gotchas/2026-06-eks-blue-green-route53}
verify_against:                 # staleness triggers (Section 7)
  - {repo: harness-terraform-eks-blue, paths: ["*.tf"]}
last_verified: 2026-06-10
---
```

Note the deliberate reuse: the episodic template from `track-a-file-based-guide.md` (date/category/impact/tags frontmatter) is kept for `decisions/` and `gotchas/`; only `id`, `type`, and `edges` fields are added so those files participate in the graph.

### 3.3 What the manifest keeps vs what knowledge/ adds

The manifest answers *what exists and what depends on what* — keep it lean exactly as designed. A `knowledge/dependencies/` node is created **only when an edge needs narrative**: the contract location, the change protocol, deployment ordering, failure modes. For most of the ~40 repos, the manifest line is enough; expect only 10–20 rich dependency nodes (the EKS chain, harness-api↔terraform, lambda↔terraform-lambda, the subtree relationships).

---

## 4. Mapping the Six-Memory Architecture onto the Graph and Both Harnesses

This is the unification of `memory-type-mapping.md` with the two customization architectures. Each memory type gets exactly one **team-shared** home in the graph and one **per-developer** home in the native harness — they complement rather than duplicate.

| Memory type | Team-shared (in team-os graph, git) | Claude Code native (per dev) | Copilot native (per dev) |
|---|---|---|---|
| **Semantic** | `repo-manifest.yaml`, `capabilities/`, `conventions/`, `dependencies/` | Repo `CLAUDE.md` (rendered) + `.claude/rules/` | `copilot-instructions.md` + `.instructions.md` |
| **Procedural** | `knowledge/workflows/` | Skills (`.claude/skills/`) | Same skills (read from `.claude/skills/`) |
| **Episodic** | `knowledge/decisions/`, `gotchas/` (+ `harness-adr` repo) | Auto-memory observations promoted via PR | PR-template capture |
| **Working** | — (session-only by design) | Conversation + TodoWrite | Conversation + todos |
| **Short-term** | — (session-only) | Conversation (auto-compressed) | Conversation |
| **Long-term** | — (personal by design) | `~/.claude/` MEMORY.md, `~/.claude/CLAUDE.md` | VS Code personal instructions |

Three rules fall out of this table and resolve ambiguities in the source documents:

1. **Team knowledge never lives in personal memory.** Auto-memory (`~/.claude/projects/*/memory/`) and personal instructions are *staging areas*. The promotion rules from the memory spec ("episodic pattern observed 3+ times → semantic rule") are redirected: promotion targets are graph nodes in team-os, reached via PR — never a bigger personal MEMORY.md. This directly addresses the known gap "no multi-user memory coordination."
2. **Per-repo `.claude/memory/` directories are retired in favor of the central graph** for anything cross-repo. The Track A `.claude/memory/{episodic,semantic,procedural}` structure remains valid *inside a single repo* for knowledge that genuinely concerns only that repo (e.g., buildi's internal debugging notes), but anything touching two or more repos, any workflow, and any ADR goes to team-os. Rule of thumb: *if another repo's agent would benefit, it belongs in the graph.*
3. **Procedural memory ships as skills, not prose.** Because Copilot reads `.claude/skills/` natively, a workflow node in the graph is paired with a thin skill whose SKILL.md says "fetch and follow `knowledge/workflows/<name>.md` from team-os" — progressive disclosure keeps the always-on token cost near zero in both harnesses (Tier 1 metadata only, ~50–100 tokens per skill).

---

## 5. How Agents Query the Graph — the `pk` CLI (Harness-Neutral)

Per the non-MCP decision discussed previously: the graph is queried through a **committed shell/Python CLI**, not an MCP server. Both harnesses execute terminal commands natively; the CLI is lazy-loaded (zero idle token cost) and works identically in Claude Code, Copilot CLI, Copilot agent mode, and plain human terminals. An MCP shim can be added later as a ~50-line adapter if discoverability problems are observed — MCP becomes an optional transport, not the architecture.

`harness-layer/skills/platform-graph/scripts/pk.sh` (distributed into every repo):

```bash
#!/usr/bin/env bash
# pk — query the Harness platform knowledge graph
# Requires: yq, git. Graph cached at ${PK_HOME:-$HOME/.pk-cache/team-os}.
set -euo pipefail
PK_HOME="${PK_HOME:-$HOME/.pk-cache/team-os}"
TEAM_OS_URL="ssh://git@bitbucket.example.com/HARNESS/harness-platform-team-os.git"

sync() {  # shallow clone or fast-forward; called implicitly by every command
  if [ -d "$PK_HOME/.git" ]; then git -C "$PK_HOME" pull -q --ff-only || true
  else git clone -q --depth 1 "$TEAM_OS_URL" "$PK_HOME"; fi
}

case "${1:-help}" in
  repo)        sync; yq ".product_areas[].repos[] | select(.name == \"$2\")" \
                 "$PK_HOME/repo-manifest.yaml" ;;
  deps)        sync; yq ".product_areas[].repos[] | select(.depends_on[]? == \"$2\") | .name" \
                 "$PK_HOME/repo-manifest.yaml" ;;            # who depends ON $2
  workflow)    sync; ls "$PK_HOME/knowledge/workflows/" | grep -i "${2:-.}" ;;
  show)        sync; cat "$PK_HOME/knowledge/$2.md" ;;
  impact)      sync; python3 "$PK_HOME/scripts/impact.py" "$2" ;;  # transitive closure
  search)      sync; grep -ril "$2" "$PK_HOME/knowledge/" "$PK_HOME/repo-manifest.yaml" ;;
  verify)      sync; python3 "$PK_HOME/scripts/graph_check.py" ;;
  *) echo "pk repo|deps|workflow|show|impact|search|verify" ;;
esac
```

The paired skill (one copy, both harnesses):

```markdown
# harness-layer/skills/platform-graph/SKILL.md
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
```

Why this satisfies both customization architectures: in Claude Code, the skill is auto-invoked by description match or `/platform-graph`; in Copilot, the identical files in `.claude/skills/` are discovered through its skill loader with the same progressive-disclosure tiering. One artifact, two harnesses, zero duplication.

---

## 6. Distribution — Solving "No Team-Level CLAUDE.md" Across ~40 Repos

The known-gaps document already names the workaround family (submodules / shared directory sync); the team-structure document already establishes subtree tooling and discipline. The revised approach uses **manifest-driven sync of a generated harness layer**, which fits trunk-based development better than 40 submodule pointers:

1. `render-templates.py` reads `repo-manifest.yaml` and, for each repo, renders:
   - `AGENTS.md` — repo purpose, tech, deploy target, dependencies (pulled from its manifest entry), build/test commands, and the graph protocol. *This single file serves both harnesses* per the convergence table.
   - `CLAUDE.md` — `@AGENTS.md` import + Claude-specific notes (sub-agent and skill references).
   - `.github/copilot-instructions.md` — pointer to AGENTS.md content + Copilot-specific notes.
   - `.claude/rules/*.md` and `.github/instructions/*.instructions.md` — generated from the single `harness-layer/rules/*.rule.md` sources, with `paths:`/`applyTo:` globs derived from the repo's `tech:` field (terraform rules only land in terraform repos, etc.).
   - `.claude/skills/` — copied verbatim (platform-graph, cross-repo-feature, record-gotcha).
2. `sync-harness.sh` opens a PR per code repo when the rendered output differs (run weekly by Bitbucket Pipelines in team-os, or on every harness-layer change). Repos accept these PRs like any dependency bump.
3. A `# GENERATED — edit in team-os/harness-layer/` header plus a repo-local `AGENTS.local.md` / `CLAUDE.local.md` escape hatch keeps repo-specific additions from being overwritten.

Result: every Claude Code or Copilot session, in any of the ~40 repos, starts with (a) the repo's identity and dependencies already in context, (b) the graph protocol in its instructions, and (c) the `pk` skill available — at a fixed, small always-on token cost (the rendered AGENTS.md targets < 100 lines; everything else is lazy).

---

## 7. The Update Loop — Keeping the Graph Alive (Bitbucket Edition)

Adapted from the earlier plan's enforcement design, retargeted from GitHub Actions to Bitbucket Pipelines, and wired to the harnesses' native hook systems.

**Layer 1 — at creation time (agent hooks).**
- Claude Code: a `Stop` hook (in the distributed `.claude/settings.json`) checks whether the session modified files matching any graph node's `verify_against` globs and, if so, blocks completion (exit 2) until the agent states which workflow it followed and whether a graph update is needed. A `SessionStart` hook warms the `pk` cache.
- Copilot: hooks are event-scoped and weaker here; instead, the rendered `copilot-instructions.md` requires a "Knowledge graph updates needed: …" section in every PR description, and Layer 2 enforces it.

**Layer 2 — at PR time (CI gates).**
- In team-os: `graph_check.py` (schema validity, dangling edges, manifest↔knowledge consistency — every `repos:` entry in a workflow must exist in the manifest; every manifest repo should be reachable from a capability node) + regeneration of INDEX.md/graph.json, failing on drift.
- In each code repo: a `knowledge-gate` Bitbucket Pipelines step fetches team-os `graph.json`, intersects the PR's changed files with `verify_against` triggers, and fails unless the PR description contains `Knowledge-Update: <team-os PR link | none, because …>`. This is the load-bearing rule: **a code PR cannot merge while silently invalidating the graph**, regardless of which harness (or human) authored it.

**Layer 3 — over time (staleness + capture).**
- Weekly Pipelines job in team-os: for each node, compare `last_verified` against commits touching `verify_against` paths (Bitbucket REST API); open a task/issue per stale node; report graph health (% nodes verified < 60 days) in INDEX.md. A monthly gardening rotation (~2h) triages — typically by pointing Claude Code at the stale node and letting it propose the update PR.
- Capture loop: the `record-gotcha` skill turns in-session discoveries into ready-to-PR gotcha/decision nodes using the episodic frontmatter template from the memory spec. The Claude-side auto-memory remains personal scratch; anything recurring gets promoted to the graph via this skill, never accumulated privately.

---

## 8. Powering the Cross-Repo Worktree Workflow from the Graph

This is where the graph pays for itself. The team-structure document's worktree workflow currently requires a human to know the dependency chain. With workflow nodes carrying an **ordered `repos:` list**, the manifest-driven script becomes graph-driven:

```bash
# scripts/setup-feature-worktrees.sh <workflow-id> <feature-slug>
REPOS=$(yq '.repos[]' <(pk show "workflows/$1" | sed -n '/^---$/,/^---$/p'))
for repo in $REPOS; do
  git -C "$repo" worktree add "../wt-$2/$repo" "feature/$2"
done
# merge-feature.sh later merges in the SAME order — topological order is now
# versioned knowledge, not tribal knowledge.
```

The `cross-repo-feature` skill orchestrates the full loop in either harness: find workflow → create worktrees in `repos:` order → implement per step → run each step's verification → open PRs in order → remind about Knowledge-Update. In Claude Code, large parallelizable workflows can additionally use sub-agents with `isolation: worktree` (one slice per worktree, per the Claude architecture doc §3.6) — the graph's ordered list tells the lead agent what can parallelize (siblings in the dependency tree: eks-blue ∥ eks-green) and what cannot (data → integration must be sequential).

---

## 9. Gaps from `known-gaps.md` — Disposition

| Known gap | Disposition in this design |
|---|---|
| No team-level CLAUDE.md | Solved: rendered harness layer synced from team-os (Section 6) |
| MEMORY.md 200-line truncation | Sidestepped: team knowledge lives in the graph, not MEMORY.md |
| No multi-user memory coordination | Solved: PR-reviewed graph is the coordination mechanism |
| No event-triggered memory writes | Solved: Bitbucket Pipelines staleness job + knowledge-gate |
| No memory search API | `pk search` (grep over graph) now; vector layer later if needed |
| No structured metadata | Solved: YAML frontmatter + graph.json (already in the Track A spec) |
| No memory versioning | Solved: the graph is git; personal memory stays personal |
| Concurrent session conflicts | Reduced: graph writes go through PRs; merge conflicts are git's job |

Scale check against `trade-offs.md`: the file-based track is rated "good" for 50–500 entries. Expected graph size here: ~40 repo entries (manifest) + ~6 capabilities + ~10–15 workflows + ~15 dependency nodes + ~20 conventions/gotchas + ADR index ≈ **under 120 nodes** — comfortably inside Track A's sweet spot, with `pk search` (grep) adequate for retrieval. The Track B vector store remains the documented escape hatch if the gotcha/decision corpus grows past several hundred nodes; nothing in this design blocks adding it, because all nodes carry structured frontmatter ready for indexing.

---

## 10. Implementation Roadmap (Merged with the Team-Structure Phases)

The team-structure roadmap (team-os creation, manifest, subtrees, worktrees) proceeds as written; the knowledge-graph work threads into it:

| Weeks | Team-structure phase (as planned) | Knowledge-graph additions |
|---|---|---|
| 1–2 | Create team-os, scaffold dirs, write repo-manifest.yaml, CLAUDE.md files | Add `knowledge/` + GRAPH-SCHEMA.md + templates; write all 6 capability nodes; `graph_check.py` + Pipelines in team-os; draft `pk.sh` |
| 2–4 | Migrate ADRs, runbooks, feature-index, topology.md | ADRs become `decisions/` nodes (or indexed); topology.md content becomes rich `dependencies/` nodes; draft top 5 workflows by mining recent PRs (incl. the EKS upgrade example); build `render-templates.py` |
| 4–8 | Subtree pilot (terraform-base → 2–3 consumers) | Pilot harness sync into the same 2–3 repos first; `subtree-of` edges in graph; 2–3 engineers run real tickets agent-first via `pk` in both harnesses, logging every graph gap |
| 6–10 | Worktree workflow adoption + team demo | Demo runs from a workflow node via graph-driven `setup-feature-worktrees.sh`; knowledge-gate Pipelines rolled to all active repos; capture loop (`record-gotcha`) proven with ≥5 real nodes |
| 10+ | Automation phase (manifest validation, dep visualization) | Staleness job + gardening rotation; graph health metric in INDEX.md; evaluate (only if grep retrieval visibly strains) Track B vector search or an MCP shim over `pk` |

**Exit criteria for "the graph is real":** every active repo has a synced harness layer; every recurring change type has an active workflow node; one cross-repo feature has shipped agent-first in *each* harness following a workflow node; the knowledge-gate has blocked (and thereby corrected) at least one PR; graph health ≥ 80% verified.

---

## 11. Deltas from the Source Documents (What This Revision Changes)

1. **One repo, not two.** The earlier `platform-knowledge` proposal is merged into `harness-platform-team-os`; `repo-manifest.yaml` is promoted to graph backbone rather than duplicated into `repos/*.md` nodes.
2. **Bitbucket-native enforcement.** All CI examples move from GitHub Actions to Bitbucket Pipelines; Copilot usage is scoped to VS Code/JetBrains/CLI surfaces (its GitHub.com cloud agent is out of scope).
3. **CLI-first, MCP-as-optional-adapter** for graph queries, per the non-MCP analysis — replacing the earlier plan's Phase 3 MCP servers as the primary interface.
4. **The six-memory spec is re-scoped:** team-shared memory types (semantic, procedural, episodic) live in the graph; per-repo `.claude/memory/` is for single-repo knowledge only; personal surfaces (auto-memory, MEMORY.md) are staging areas with PR-based promotion to the graph.
5. **Skills are the cross-harness procedural carrier** (single `.claude/skills/` copy read by both tools), replacing duplicated slash-commands + prompt files.
6. **Workflows carry ordered `repos:` lists** that mechanically drive the worktree scripts — converting team-struture.md's manually-known merge order into versioned, agent-executable knowledge.
