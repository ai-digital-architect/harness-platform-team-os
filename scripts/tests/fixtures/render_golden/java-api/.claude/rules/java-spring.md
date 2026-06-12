---
description: Java/Kotlin Spring change rules for Harness platform repos.
paths: ["**/*.java", "**/*.kt", "**/pom.xml", "**/build.gradle*"]
---
# GENERATED — edit in team-os/harness-layer/

# Java / Spring rules (Harness platform)

1. **Deployment is graph-coupled.** These services deploy onto infrastructure
   owned by terraform repos (see `depends_on` in AGENTS.md). API or contract
   changes that other repos consume require `pk impact <this-repo>` first,
   and endpoint work should follow `pk workflow api-endpoint` when one exists.
2. **Follow the team convention node** once it lands:
   `pk show conventions/java-spring-standards`.
   TODO(verify): node pending (team-os T2.3) — until then, match the patterns
   already present in this repo.
3. TODO(verify): per-repo build/test commands (to be filled from repo
   surveys — read this repo's CI config or build files, do not guess).
