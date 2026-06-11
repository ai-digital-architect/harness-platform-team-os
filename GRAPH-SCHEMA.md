# GRAPH-SCHEMA — Node Types, Edge Types, Frontmatter Spec

Source of truth for the knowledge-graph data model, per section 3
("The Graph Data Model") of `harness-knowledge-graph-revised-approach.md`.
Read this before authoring or editing any node under `knowledge/`.

---

## 1. Node types

| Node type | Lives in | Backed by memory type | Example |
|---|---|---|---|
| `repo` | `repo-manifest.yaml` (entries) — **not** `knowledge/` | Semantic | `harness-api`, `buildi-kaniko` |
| `capability` | `knowledge/capabilities/` | Semantic | `container-builds` |
| `workflow` | `knowledge/workflows/` | Procedural | `eks-infrastructure-upgrade` |
| `dependency` | manifest `depends_on` + `knowledge/dependencies/` for rich edges | Semantic | `harness-api → eks-blue` |
| `convention` | `knowledge/conventions/` | Semantic | `terraform-patterns` |
| `gotcha` | `knowledge/conventions/gotchas/` | Episodic→Semantic | `eks-blue-green-route53` |
| `decision` | `knowledge/decisions/` (indexes `harness-adr`) | Episodic | `0001-blue-green-eks` |

Notes:

- `repo` nodes are entries in `repo-manifest.yaml` (the graph backbone).
  They are never duplicated as markdown files in `knowledge/`; edge targets
  that name a repo resolve against the manifest.
- A `knowledge/dependencies/` node is created **only when an edge needs
  narrative** (contract location, change protocol, deployment ordering,
  failure modes). For most repos the manifest `depends_on` line is enough.

## 2. Edge vocabulary (closed)

The edge vocabulary is **closed** — it is extended only by PR to this file
(GRAPH-SCHEMA.md). Validators reject any other `rel`.

| Edge rel | Direction rule |
|---|---|
| `depends-on` | dependent → dependency |
| `deploys-to` | deployer → deploy target |
| `publishes-to` | publisher → destination |
| `consumes-from` | consumer → source |
| `implements` | repo → capability |
| `touches` | workflow → repo, **ORDERED** — the order drives worktree creation & merge order |
| `governed-by` | any → convention/decision |
| `affected-by` | any → gotcha |
| `supersedes` | decision → decision |
| `subtree-of` | consumer → source (from the manifest's `subtree_plan`) |

`touches` edges are not written in `edges:` — they are derived from a
workflow node's ordered `repos:` list (see §3.3), preserving order.

## 3. Node frontmatter (`knowledge/` files)

### 3.1 Required fields (all node types)

| Field | Spec |
|---|---|
| `id` | Must equal the file's path relative to `knowledge/`, without the `.md` suffix (e.g. `workflows/eks-infrastructure-upgrade`) |
| `type` | One of: `capability`, `workflow`, `dependency`, `convention`, `gotcha`, `decision` |
| `title` | Human-readable title |
| `status` | `draft` \| `active` \| `deprecated`. **All new nodes start `draft`; only humans promote to `active`.** |

### 3.2 Optional fields (all node types)

| Field | Spec |
|---|---|
| `owners` | List of owning teams/people, e.g. `[infra-team]` |
| `edges` | List of `{rel, to}` mappings. `rel` must be in the closed vocabulary (§2); `to` must resolve to a node id or a manifest repo name |
| `verify_against` | Staleness trigger: list of `{repo, paths: ["<glob>", ...]}` mappings — commits in `repo` touching `paths` mark this node stale |
| `last_verified` | `YYYY-MM-DD` date the node was last verified against its `verify_against` sources |

### 3.3 Workflow-only field

| Field | Spec |
|---|---|
| `repos` | **ORDERED** list of manifest repo names — defines worktree creation & merge order. Each entry must exist in `repo-manifest.yaml`. Emitted into `graph.json` as ordered `touches` edges |

### 3.4 Episodic fields (decisions/ and gotchas/ only)

The episodic template from `track-a-file-based-guide.md` is **retained** for
`decisions/` and `gotchas/` nodes; only `id`, `type`, and `edges` are added so
those files participate in the graph.

| Field | Spec |
|---|---|
| `date` | `YYYY-MM-DD` — when the decision was made / the gotcha was hit |
| `category` | Episodic category label |
| `impact` | Impact statement/level |
| `tags` | List of tags |

### 3.5 Reference example

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
verify_against:                 # staleness triggers
  - {repo: harness-terraform-eks-blue, paths: ["*.tf"]}
last_verified: 2026-06-10
---
```

## 4. Rules enforced by `scripts/graph_check.py`

`graph_check.py` runs in CI and in the PostToolUse hook. It validates:

1. **Required fields present:** `id`, `type`, `title`, `status` must exist
   and be non-empty in every node's frontmatter.
2. **id ↔ path:** `id` must equal the node's path relative to `knowledge/`
   with the `.md` suffix stripped.
3. **Closed sets:** `type` must be one of the six knowledge node types
   (§1, excluding `repo`); `status` must be one of `draft`, `active`,
   `deprecated`.
4. **Edge integrity:** every `edges[].rel` must be in the closed vocabulary
   (§2); every `edges[].to` must resolve to an existing node id **or** a
   repo name from `repo-manifest.yaml`.
5. **Wikilinks resolve:** every `[[wikilink]]` in a node body must resolve
   to a node id or a manifest repo name.
6. **Workflow repos exist:** every entry in a workflow node's `repos:` list
   must exist in `repo-manifest.yaml`. (If the manifest is absent, this and
   the repo-target checks above downgrade to warnings.)
7. **Templates excluded:** files named `_template.md` (and the CI-built
   `INDEX.md`) are excluded from all validation.

On success it (re)generates `knowledge/graph.json` deterministically; exit
code 0 = clean, 1 = validation errors (`file:line` diagnostics on stderr).

## 5. Templates

Each `knowledge/` subdirectory contains a `_template.md` skeleton
(excluded from validation). Copy it, rename, set `id` to match the new
path, and keep `status: draft`.
