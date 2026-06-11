---
id: conventions/<slug>
type: convention
title: <Standard name, e.g. terraform-patterns>
status: draft
owners: [<owning-team>]
edges:
  # nodes/repos governed by this convention point AT it with governed-by;
  # here, link related decisions and known gotchas:
  - {rel: governed-by, to: decisions/<slug>}
  - {rel: affected-by, to: conventions/gotchas/<slug>}
verify_against:
  - {repo: <manifest-repo-name>, paths: ["<glob>"]}
last_verified: <YYYY-MM-DD>
---

# <Title>

## Scope

Which repos / file types / change types this standard applies to.

## The standard

The rules themselves — concrete, checkable statements:

- <rule>
- <rule>

## Rationale

Why these rules exist (link decisions with [[decisions/<slug>]] rather than
restating them).

## Examples

```text
<good example>
```

## Exceptions

Known, sanctioned deviations and where they live.
