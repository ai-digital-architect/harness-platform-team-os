---
id: capabilities/container-builds
type: capability
title: Container builds — Buildi container build system
status: draft
edges:
  # implements is canonically repo→capability (GRAPH-SCHEMA.md §2). Repo nodes
  # live only in repo-manifest.yaml, so the membership edges are recorded here
  # on the capability node; membership = the manifest's `container-builds` area.
  - {rel: implements, to: buildi}
  - {rel: implements, to: buildi-cli}
  - {rel: implements, to: buildi-kaniko}
  - {rel: implements, to: buildi-kaniko-arm64}
  - {rel: implements, to: buildi-kaniko-images}
  - {rel: implements, to: buildi-terraform-data}
  - {rel: implements, to: buildi-terraform-ecs}
  - {rel: implements, to: buildi-terraform-roles}
  - {rel: implements, to: buildi-terraform-connect}
---

# Container builds — Buildi container build system

## What this capability is

Per `repo-manifest.yaml`, this product area is the "Buildi container build
system": the service, CLI, Kaniko build images and the Terraform that
provisions Buildi's own infrastructure.

## Repos involved

Membership, tech, deploy targets and dependencies (including the
intra-area dependency order) live in `repo-manifest.yaml` — see the
`implements` edges above.

## Cross-area relationships (from the manifest)

- [[buildi-terraform-data]], [[buildi-terraform-ecs]] and
  [[buildi-terraform-roles]] declare `depends_on` edges on
  [[111282-113518-terraform-base]] (infrastructure area).
- The manifest `subtree_plan` (shared_terraform_modules) lists
  [[buildi-terraform-data]] as a planned consumer of shared modules
  sourced from [[111282-113518-terraform-base]].

## Key entry points

- TODO(verify): is [[buildi]] (the service) or [[buildi-cli]] the usual
  entry point for users of the build system?

## Related workflows

None yet.

## Open questions

- TODO(verify): which team owns the container-builds area?
  (team-structure.md is empty — the planned source is unavailable.)
- TODO(verify): how do [[buildi-kaniko]], [[buildi-kaniko-arm64]] and
  [[buildi-kaniko-images]] relate at build/publish time?
