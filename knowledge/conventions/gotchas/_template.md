---
id: conventions/gotchas/<YYYY-MM>-<slug>
type: gotcha
title: <One-line description of the pitfall>
status: draft
owners: [<owning-team>]
# Episodic fields (retained from the track-a episodic template):
date: <YYYY-MM-DD>
category: <episodic category>
impact: <impact statement/level>
tags: [<tag>, <tag>]
edges:
  # affected nodes point AT this gotcha with affected-by; here, link the
  # convention/decision context:
  - {rel: governed-by, to: conventions/<slug>}
verify_against:
  - {repo: <manifest-repo-name>, paths: ["<glob>"]}
last_verified: <YYYY-MM-DD>
---

# <Title>

## What happened

The incident/discovery, dated and concrete. Facts only — link the repos
involved with wikilinks (e.g. [[<manifest-repo-name>]]).

## Root cause

Why it happened. TODO(verify): if the root cause is unconfirmed.

## How to avoid / detect it

- <concrete avoidance or detection step, with commands where possible>

## If you hit it anyway

Recovery steps, or `[HUMAN]` if recovery needs tribal knowledge.
