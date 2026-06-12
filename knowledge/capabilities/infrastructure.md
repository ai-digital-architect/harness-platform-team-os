---
id: capabilities/infrastructure
type: capability
title: Infrastructure — Terraform modules, EKS, networking, IAM
status: draft
edges:
  # implements is canonically repo→capability (GRAPH-SCHEMA.md §2). Repo nodes
  # live only in repo-manifest.yaml, so the membership edges are recorded here
  # on the capability node; membership = the manifest's `infrastructure` area.
  - {rel: implements, to: 111282-113518-terraform-base}
  - {rel: implements, to: harness-terraform-data}
  - {rel: implements, to: harness-terraform-integration}
  - {rel: implements, to: harness-terraform-eks-blue}
  - {rel: implements, to: harness-terraform-eks-green}
  - {rel: implements, to: harness-terraform-lambda}
  - {rel: implements, to: harness-terraform-route53}
  - {rel: implements, to: harness-terraform-secrets}
  - {rel: implements, to: harness-ecs-delegate-terraform-ecs}
  - {rel: implements, to: 111282-113518-terraform-cosign}
  - {rel: implements, to: harness-terraform-magpie-consumer-lambda}
---

# Infrastructure — Terraform modules, EKS, networking, IAM

## What this capability is

The platform's foundation layer. Per `repo-manifest.yaml`, this product area
covers "Terraform modules, EKS, networking, IAM": the Terraform repos that
provision the AWS estate every other product area deploys onto.

## Repos involved

Membership, roles, tech, deploy targets and dependency order live in
`repo-manifest.yaml` — see the `implements` edges above.

## Cross-area relationships (from the manifest)

- Repos in self-service ([[harness-api]], [[harness-platform-api]],
  [[harness-db-app]]), container-builds ([[buildi-terraform-data]],
  [[buildi-terraform-ecs]], [[buildi-terraform-roles]]) and integrations
  ([[lambda-harness-event-handler]], [[harness-magpie-consumer-lambda]])
  declare `depends_on` edges into this area's repos.
- The manifest `subtree_plan` (shared_terraform_modules) names
  [[111282-113518-terraform-base]] as the source for shared Terraform
  patterns, with [[buildi-terraform-data]] among the planned consumers.
- The manifest deprecates [[harness-terraform-eks2]] and
  [[harness-terraform-eks3]] as "Replaced by eks-blue/green".

## Key entry points

- TODO(verify): where does a typical infrastructure change start — the root
  module [[111282-113518-terraform-base]] or a leaf repo?

## Related workflows

None yet.

## Open questions

- TODO(verify): which team owns the infrastructure area? (team-structure.md
  is empty — the planned source is unavailable.)
- TODO(verify): what is the operational relationship between
  [[harness-terraform-eks-blue]] and [[harness-terraform-eks-green]]
  (blue/green cutover procedure)?
