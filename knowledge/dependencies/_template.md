---
id: dependencies/<consumer-repo>--<provider-repo>
type: dependency
title: <consumer-repo> → <provider-repo>
status: draft
owners: [<owning-team>]
edges:
  # The bare depends_on fact lives in repo-manifest.yaml — this node exists
  # only because the edge needs narrative. Typical edges:
  - {rel: depends-on, to: <provider-repo>}
  - {rel: governed-by, to: conventions/<slug>}
  - {rel: affected-by, to: conventions/gotchas/<slug>}
verify_against:
  - {repo: <consumer-repo>, paths: ["<glob of contract files>"]}
  - {repo: <provider-repo>, paths: ["<glob of contract files>"]}
last_verified: <YYYY-MM-DD>
---

# <consumer-repo> → <provider-repo>

## Nature of the dependency

What the consumer actually uses from the provider (API, module, image,
event, state), and why. Keep manifest facts in the manifest — this is the
narrative the manifest line cannot carry.

## Contract location

Real file paths on both sides of the contract:

- `<consumer-repo>/<path/to/consuming-code-or-config>`
- `<provider-repo>/<path/to/interface-definition>`
- TODO(verify): <unconfirmed path>

## Change protocol

How a change to the provider safely reaches the consumer — ordering,
versioning, deployment sequence, who must review:

1. <step>
2. <step>

## Failure modes

What breaks when this edge is violated, and how it manifests:

- <symptom> — <cause> — <where to look>
