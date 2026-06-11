---
id: decisions/<NNNN>-<slug>
type: decision
title: <ADR title>
status: draft
owners: [<owning-team>]
# Episodic fields (retained from the track-a episodic template):
date: <YYYY-MM-DD>
category: <episodic category>
impact: <impact statement/level>
tags: [<tag>, <tag>]
edges:
  # if this ADR replaces an earlier one:
  - {rel: supersedes, to: decisions/<NNNN>-<old-slug>}
verify_against:
  - {repo: <manifest-repo-name>, paths: ["<glob>"]}
last_verified: <YYYY-MM-DD>
---

# <NNNN>. <Title>

> Indexes the canonical ADR in `harness-adr` where applicable —
> source: TODO(verify): <link/path to the ADR in harness-adr>

## Context

The forces at play: what problem demanded a decision.

## Decision

What was decided, stated as a single unambiguous sentence, then detail.

## Consequences

- <what becomes easier>
- <what becomes harder / what is now forbidden>

## Affected repos / nodes

- [[<manifest-repo-name>]]
- [[conventions/<slug>]]
