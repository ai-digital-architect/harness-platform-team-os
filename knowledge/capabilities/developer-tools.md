---
id: capabilities/developer-tools
type: capability
title: Developer tools — CLIs, AI tooling, pipeline utilities
status: draft
edges:
  # implements is canonically repo→capability (GRAPH-SCHEMA.md §2). Repo nodes
  # live only in repo-manifest.yaml, so the membership edges are recorded here
  # on the capability node; membership = the manifest's `developer-tools` area.
  - {rel: implements, to: harness-cli}
  - {rel: implements, to: harness-actions}
  - {rel: implements, to: harness-templates}
  - {rel: implements, to: harness-pipeline-ops}
  - {rel: implements, to: harness-rewrite-recipes}
  - {rel: implements, to: harness-utilities}
  - {rel: implements, to: company-mcp-server}
  - {rel: implements, to: harness-managed-pipeline-schema}
  - {rel: implements, to: harness-ai-toolkit}
  - {rel: implements, to: harness-marketplace}
---

# Developer tools — CLIs, AI tooling, pipeline utilities

## What this capability is

Per `repo-manifest.yaml`, this product area covers "CLIs, AI tooling,
pipeline utilities" — the tooling developers use to work with the platform
rather than services the platform runs.

## Repos involved

Membership, tech, deploy targets and dependencies (including the
intra-area dependency order) live in `repo-manifest.yaml` — see the
`implements` edges above.

## Cross-area relationships (from the manifest)

- The manifest `subtree_plan` (shared_python_libs) names
  [[harness-utilities]] as the source of common Python utilities for
  lambdas in the integrations area ([[lambda-harness-event-handler]],
  [[lambda-cve-data-sync]], [[lambda-privileged-access-mgmt]]).

## Key entry points

- TODO(verify): which tool is the primary developer entry point —
  [[harness-cli]], [[harness-actions]], or [[company-mcp-server]]?

## Related workflows

None yet.

## Open questions

- TODO(verify): which team owns the developer-tools area?
  (team-structure.md is empty — the planned source is unavailable.)
- TODO(verify): what does [[harness-ai-toolkit]] contain and how is it
  consumed?
