---
id: capabilities/policy-and-governance
type: capability
title: Policy and governance — OPA policies, ADRs, monitoring
status: draft
edges:
  # implements is canonically repo→capability (GRAPH-SCHEMA.md §2). Repo nodes
  # live only in repo-manifest.yaml, so the membership edges are recorded here
  # on the capability node; membership = the manifest's `policy-and-governance`
  # area.
  - {rel: implements, to: harness-policy}
  - {rel: implements, to: harness-adr}
  - {rel: implements, to: harness-dynatrace-cloudwatch}
  - {rel: implements, to: harness-eks-extension-dynatrace}
---

# Policy and governance — OPA policies, ADRs, monitoring

## What this capability is

Per `repo-manifest.yaml`, this product area covers "OPA policies, ADRs,
monitoring" — the repos that govern how the platform is used and observed.

## Repos involved

Membership, tech and dependencies live in `repo-manifest.yaml` — see the
`implements` edges above.

## Cross-area relationships (from the manifest)

- The manifest records no cross-area `depends_on` edges for this area.
- TODO(verify): do [[harness-dynatrace-cloudwatch]] and
  [[harness-eks-extension-dynatrace]] monitor resources provisioned by the
  infrastructure area repos?

## Key entry points

- TODO(verify): where are [[harness-policy]] OPA policies enforced
  (CI, runtime, both)?

## Related workflows

None yet.

## Open questions

- TODO(verify): which team owns the policy-and-governance area?
  (team-structure.md is empty — the planned source is unavailable.)
