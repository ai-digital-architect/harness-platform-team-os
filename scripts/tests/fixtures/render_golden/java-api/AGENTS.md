# GENERATED — edit in team-os/harness-layer/ (changes here are overwritten by sync)

# java-api — Harness Platform repo context

## Identity

- **Product area:** fixture-apps — Fixture application area
- **Role:** TODO(verify): role not in manifest
- **Tech:** java, spring-boot
- **Deploys to:** eks

## Dependencies (from team-os repo-manifest.yaml)

Depends on:
- tf-vpc

Depended on by:
- none declared

## Build & test

- `./gradlew build` (verified from bitbucket-pipelines.yml)
- `./gradlew test`

## Platform knowledge graph — use it

This repo is one node of the Harness platform knowledge graph
(`harness-platform-team-os`). Query it with the pk CLI
(`.claude/skills/platform-graph/scripts/pk.sh`). Always begin a task with:

1. `pk repo java-api` — confirm this repo's role and dependencies
2. `pk workflow <task keywords>` then `pk show workflows/<match>` — find and
   FOLLOW the canonical workflow; its `repos:` list defines change order
3. `pk impact java-api` — before changing any interface another repo consumes

If no workflow matches the task, state that explicitly in your summary.

## Knowledge updates

If your change invalidates anything the graph records about this repo
(dependencies, workflows, conventions), your PR description MUST contain
`Knowledge-Update: <team-os PR link>` or `Knowledge-Update: none, because ...`.

Repo-local additions belong in AGENTS.local.md (never overwritten by sync).
