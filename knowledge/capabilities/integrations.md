---
id: capabilities/integrations
type: capability
title: Integrations — Lambda-based event processing and integrations
status: draft
edges:
  # implements is canonically repo→capability (GRAPH-SCHEMA.md §2). Repo nodes
  # live only in repo-manifest.yaml, so the membership edges are recorded here
  # on the capability node; membership = the manifest's `integrations` area.
  - {rel: implements, to: lambda-harness-event-handler}
  - {rel: implements, to: lambda-cve-data-sync}
  - {rel: implements, to: lambda-harness-grc}
  - {rel: implements, to: lambda-jet-evidence-integration}
  - {rel: implements, to: lambda-privileged-access-mgmt}
  - {rel: implements, to: harness-magpie-consumer-lambda}
---

# Integrations — Lambda-based event processing and integrations

## What this capability is

Per `repo-manifest.yaml`, this product area covers "Lambda-based event
processing and integrations" — the Lambda functions that connect the
platform to surrounding systems.

## Repos involved

Membership, tech, deploy targets and dependencies live in
`repo-manifest.yaml` — see the `implements` edges above.

## Cross-area relationships (from the manifest)

- [[lambda-harness-event-handler]] declares a `depends_on` edge on
  [[harness-terraform-lambda]] (infrastructure area).
- [[harness-magpie-consumer-lambda]] declares a `depends_on` edge on
  [[harness-terraform-magpie-consumer-lambda]] (infrastructure area).
- The manifest `subtree_plan` (shared_python_libs) lists
  [[lambda-harness-event-handler]], [[lambda-cve-data-sync]] and
  [[lambda-privileged-access-mgmt]] as planned consumers of common Python
  utilities sourced from [[harness-utilities]] (developer-tools area).

## Key entry points

- TODO(verify): which events/sources trigger each lambda, and where is the
  event routing configured?

## Related workflows

None yet.

## Open questions

- TODO(verify): which team owns the integrations area? (team-structure.md
  is empty — the planned source is unavailable.)
