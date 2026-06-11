---
id: capabilities/<slug>
type: capability
title: <What the platform DOES — short name>
status: draft
owners: [<owning-team>]
edges:
  # repos implement capabilities: add {rel: implements, to: capabilities/<slug>}
  # edges on the REPO side live in repo-manifest.yaml; here, link governing
  # conventions/decisions and known gotchas:
  - {rel: governed-by, to: conventions/<slug>}
  - {rel: affected-by, to: conventions/gotchas/<slug>}
verify_against:
  - {repo: <manifest-repo-name>, paths: ["<glob>"]}
last_verified: <YYYY-MM-DD>
---

# <Title>

## What this capability is

One or two paragraphs: what the platform does here, for whom, and why it
exists. Maps to a `product_areas` entry in `repo-manifest.yaml`.

## Repos involved

Do not restate manifest facts — name the repos and edge to them with
wikilinks (e.g. [[<manifest-repo-name>]]); their purpose/dependencies live
in `repo-manifest.yaml`.

## Key entry points

Where work on this capability usually starts (repos, services, dashboards).

## Related workflows

- [[workflows/<slug>]]

## Open questions

- TODO(verify): <question that needs a repo or human to answer>
