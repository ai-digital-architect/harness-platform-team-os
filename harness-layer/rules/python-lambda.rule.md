---
name: python-lambda
description: Python lambda change rules for Harness platform repos.
tech: [python]
paths: ["**/*.py"]
---

# Python / Lambda rules (Harness platform)

1. **Infra lives elsewhere.** Lambda runtime config and event wiring are
   defined in the terraform repos (see this repo's `depends_on` in AGENTS.md).
   Changing handler signatures, env vars, or event contracts usually needs a
   paired terraform change — run `pk impact <this-repo>` and
   `pk workflow lambda` first.
2. **Follow the team convention node** once it lands:
   `pk show conventions/lambda-python-standards`.
   TODO(verify): node pending (team-os T2.3) — until then, match the patterns
   already present in this repo.
3. **Shared code is subtree-planned.** Common utilities are slated to come
   from harness-utilities via git subtree (manifest `subtree_plan`); do not
   copy-paste utility code between lambda repos.
4. TODO(verify): per-repo test/package commands (to be filled from repo
   surveys — read this repo's CI config, do not guess).
