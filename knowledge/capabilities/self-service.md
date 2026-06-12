---
id: capabilities/self-service
type: capability
title: Self-service — user-facing APIs and platform services
status: draft
edges:
  # implements is canonically repo→capability (GRAPH-SCHEMA.md §2). Repo nodes
  # live only in repo-manifest.yaml, so the membership edges are recorded here
  # on the capability node; membership = the manifest's `self-service` area.
  - {rel: implements, to: harness-api}
  - {rel: implements, to: harness-platform-api}
  - {rel: implements, to: harness-custom-secrets-mgr}
  - {rel: implements, to: harness-custom-delegate}
  - {rel: implements, to: harness-db-app}
  - {rel: implements, to: harness-ecs-delegate-app}
  - {rel: implements, to: harness-account-resources}
---

# Self-service — user-facing APIs and platform services

## What this capability is

Per `repo-manifest.yaml`, this product area covers "User-facing APIs and
platform services" — the services through which platform users interact
with the Harness platform.

## Repos involved

Membership, tech, deploy targets, dependencies and docs pointers live in
`repo-manifest.yaml` — see the `implements` edges above.

## Cross-area relationships (from the manifest)

- [[harness-api]] and [[harness-platform-api]] declare `depends_on` edges
  into the infrastructure area ([[harness-terraform-eks-blue]]).
- [[harness-db-app]] declares a `depends_on` edge on
  [[harness-terraform-lambda]] (infrastructure area).

## Key entry points

- TODO(verify): which repo is the usual starting point for a self-service
  feature — [[harness-api]] or [[harness-platform-api]], and how do they
  split responsibilities?

## Related workflows

None yet.

## Open questions

- TODO(verify): which team owns the self-service area? (team-structure.md
  is empty — the planned source is unavailable.)
