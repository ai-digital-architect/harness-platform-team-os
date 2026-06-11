---
id: workflows/<slug>
type: workflow
title: <Executable playbook name>
status: draft
owners: [<owning-team>]
repos:                          # ORDERED — defines worktree creation & merge order
  - <first-repo-to-change>
  - <second-repo-to-change>
edges:
  - {rel: governed-by, to: conventions/<slug>}
  - {rel: affected-by, to: conventions/gotchas/<slug>}
verify_against:
  - {repo: <manifest-repo-name>, paths: ["<glob>"]}
last_verified: <YYYY-MM-DD>
---

# <Title>

## When to use this workflow

Trigger conditions: the change types / tickets this playbook covers.

## Preconditions

- <access, tooling, or state required before starting>
- TODO(verify): <anything unconfirmed>

## Steps

Steps run in the order of the `repos:` list above. Every step must be
executable; if a step needs tribal knowledge, mark it `[HUMAN]` and stop.

### Step 1 — <action> in <first-repo-to-change>

- **repo:** <first-repo-to-change>
- **files:** `<paths/globs touched>`
- **commands:**
  ```bash
  <exact commands to run>
  ```
- **done when:** <observable definition of done for this step>

### Step 2 — <action> in <second-repo-to-change>

- **repo:** <second-repo-to-change>
- **files:** `<paths/globs touched>`
- **commands:**
  ```bash
  <exact commands to run>
  ```
- **done when:** <observable definition of done for this step>

## Verification

Runnable commands proving the whole workflow succeeded end-to-end:

```bash
<verification commands>
```

- <expected output / observable success criteria>

## Rollback

How to back out if verification fails (or `[HUMAN]` if undocumented).
