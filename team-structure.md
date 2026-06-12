
Knowledge graph
I want look at an efficient way to create and manage knowledge graph for a technology platform . The platform has many repositories , some infrastructure and some platform functionality.I want to create and manage the knowledge graph so that it can be given to coding harnesses for Claude code and / or GitHub copilot for sdlc to maintain , enhance , troubleshoot and add new features and functionality to the platform. A lot of the platform features existing or new will touch multiple repositories .
Show more



Type / for skills


Clarifying project goals and objectives
Last message 3 hours ago
Memory
Only you
Project memory will show here after a few chats.

Instructions
Add instructions to tailor Claude’s responses

Files
4% of project capacity used
Search mode

team-struture.md
1,572 lines

md



CLAUDE.md
110 lines

md



README.md
80 lines

md



memory-type-mapping.md
211 lines

md



known-gaps.md
71 lines

md



trade-offs.md
48 lines

md



claude-memory.instructions.md
176 lines

md



track-a-file-based-guide.md
553 lines

md



claude-code-customization-architecture-revised.md
2,331 lines

md



ghcopilot-customization-arch.md
1,534 lines

md



team-struture.md


raw
# Harness Platform Team: Team-OS Structure & Developer Guide

 

> **Last updated:** May 2026

> **Purpose:** Reference guide covering team-os repo structure, the repo manifest pattern, git subtrees for code sharing, and trunk-based development with git worktrees.

 

---

 

## Table of Contents

 

- [Harness Platform Team: Team-OS Structure \& Developer Guide](#harness-platform-team-team-os-structure--developer-guide)
  - [Table of Contents](#table-of-contents)
  - [1. Analysis: The Team-OS Pattern](#1-analysis-the-team-os-pattern)
  - [2. Recommended Architecture](#2-recommended-architecture)
    - [Structure: Hybrid Docs-Repo + Manifest](#structure-hybrid-docs-repo--manifest)
    - [Why NOT Embed Code Repos into Team-OS](#why-not-embed-code-repos-into-team-os)
  - [3. The Repo Manifest](#3-the-repo-manifest)
    - [What It Is and Why It Helps](#what-it-is-and-why-it-helps)
    - [Full Manifest YAML](#full-manifest-yaml)
    - [Query Examples](#query-examples)
  - [4. Git Subtrees for Code Sharing](#4-git-subtrees-for-code-sharing)
    - [How Subtrees Work](#how-subtrees-work)
    - [Why Subtrees Are Compatible With Trunk-Based Development](#why-subtrees-are-compatible-with-trunk-based-development)
    - [Git Aliases for Subtree Operations](#git-aliases-for-subtree-operations)
  - [5. Trunk-Based Development with Git Worktrees](#5-trunk-based-development-with-git-worktrees)
    - [The Problem](#the-problem)
    - [Worktree Workflow: Cross-Repo Feature](#worktree-workflow-cross-repo-feature)
    - [Manifest-Driven Worktree Script](#manifest-driven-worktree-script)
    - [Trunk-Based Benefits Summary](#trunk-based-benefits-summary)
    - [Example: EKS Infrastructure Upgrade](#example-eks-infrastructure-upgrade)
    - [Pro Tips](#pro-tips)
  - [6. Implementation Roadmap](#6-implementation-roadmap)
    - [Phase 1: Create the Team-OS Repo (Week 1–2)](#phase-1-create-the-team-os-repo-week-12)
    - [Phase 2: Populate with Existing Knowledge (Week 2–4)](#phase-2-populate-with-existing-knowledge-week-24)
    - [Phase 3: Git Subtree Pilot in Code Repos (Week 4–8)](#phase-3-git-subtree-pilot-in-code-repos-week-48)
    - [Phase 4: Worktree Workflow Adoption (Week 6–10, overlaps Phase 3)](#phase-4-worktree-workflow-adoption-week-610-overlaps-phase-3)
    - [Phase 5: Automation (Optional / Ongoing)](#phase-5-automation-optional--ongoing)
  - [7. Summary](#7-summary)

 

---

 

## 1. Analysis: The Team-OS Pattern

 

The `team-os-example-repo` pattern is a **documentation & coordination repo** — not a code repo. It contains:

 

- PRDs, RFCs, engineering plans, analytics artifacts

- A `feature-index.yaml` as a master lookup tying features to all related artifacts

- `CLAUDE.md` context files at every level for AI-agent discoverability

- Organized by **function** (product, engineering, analytics) then by **product area**

 

The Harness Platform Team has ~40+ individual **code repos** — a fundamentally different artifact type. The challenge is applying the same organizational clarity to a polyrepo landscape.

 

**Key distinction:**

 

| team-os-example-repo | Harness Platform Team |

| -------------------- | --------------------- |

| One repo, all docs | ~40 code repos, scattered docs |

| Product areas = feature areas | Product areas = technical subsystems |

| `feature-index.yaml` ties artifacts together | No single source of truth across repos |

| `CLAUDE.md` provides AI-navigable context | Knowledge lives in people's heads |

 

---

 

## 2. Recommended Architecture

 

### Structure: Hybrid Docs-Repo + Manifest

 

A new `harness-platform-team-os` Bitbucket repo serves as the documentation and coordination hub. Individual code repos remain fully independent.

 

```text

harness-platform-team-os (NEW Bitbucket repo — documentation & coordination)

├── CLAUDE.md                          # Team context, doc index

├── README.md

├── repo-manifest.yaml                 # Master registry of ALL repos + relationships

├── product-development/

│   ├── CLAUDE.md

│   ├── feature-index.yaml             # Features → PRDs, RFCs, plans, tickets

│   ├── product/

│   │   ├── CLAUDE.md

│   │   ├── PRDs/

│   │   │   ├── self-service/          # harness-api related

│   │   │   ├── container-builds/      # buildi related

│   │   │   ├── pipeline-tooling/      # harness-actions, harness-templates

│   │   │   ├── integrations/          # lambda integrations

│   │   │   └── developer-tools/       # CLI, MCP, AI toolkit

│   │   ├── strategy/

│   │   ├── customers/

│   │   ├── competitive-research/

│   │   ├── launch-emails/

│   │   ├── meetings/

│   │   └── processes/

│   ├── engineering/

│   │   ├── CLAUDE.md

│   │   ├── rfcs/

│   │   │   ├── infrastructure/        # Terraform base, EKS, networking

│   │   │   ├── self-service/          # harness-api, platform-api

│   │   │   ├── container-builds/      # buildi ecosystem

│   │   │   ├── integrations/          # lambdas, event handlers

│   │   │   └── developer-tools/       # CLI, MCP, pipeline-ops

│   │   ├── plans/

│   │   │   └── (same product areas)

│   │   ├── bug-investigations/

│   │   │   └── (same product areas)

│   │   └── adrs/                      # Mirror/index of harness-adr

│   ├── analytics/

│   │   ├── CLAUDE.md

│   │   ├── dashboards/

│   │   ├── metrics/

│   │   ├── schemas/

│   │   └── queries/

│   ├── data-engineering/

│   │   ├── CLAUDE.md

│   │   ├── plans/

│   │   └── rfcs/

│   └── infrastructure/                # Infra-specific docs

│       ├── CLAUDE.md

│       ├── topology.md                # Dependency graph narrative

│       ├── runbooks/

│       └── terraform-patterns/

├── team/

│   ├── CLAUDE.md

│   ├── onboarding-guides/

│   │   ├── onboarding-general.md

│   │   ├── onboarding-engineering.md

│   │   ├── onboarding-infrastructure.md

│   │   └── onboarding-tools.md

│   └── retros/

└── policies/                          # Index/mirror of harness-policy

    └── CLAUDE.md

```

 

### Why NOT Embed Code Repos into Team-OS

 

| Approach | Verdict | Reason |

| -------- | ------- | ------ |

| Git subtrees of code repos INTO team-os | **Not viable** | team-os is docs, not code. Mixing 40+ code repos bloats it and conflates concerns |

| Git submodules pointing to code repos | **Not recommended** | DX friction: detached HEAD, init ceremony, adds no value for a docs repo |

| Repo manifest (YAML) | **Recommended** | Lightweight, queryable, no git coupling, supports automation |

 

---

 

## 3. The Repo Manifest

 

### What It Is and Why It Helps

 

A `repo-manifest.yaml` is a **declarative inventory** — a version-controlled, queryable, automation-friendly single source of truth about your entire repository landscape.

 

Think of it as a "registry" rather than documentation: structured enough to query programmatically, yet readable enough to onboard from.

 

| Problem | How Manifest Solves It |

| ------- | ---------------------- |

| "What repos exist?" | `grep -r "name:" repo-manifest.yaml` — instant list |

| "What does repo X depend on?" | Read `depends_on:` field — clear dependency graph |

| "Where are the docs for this repo?" | `docs:` field links to PRDs, RFCs, runbooks in team-os |

| "Which repos use Python?" | `grep "python" repo-manifest.yaml` |

| "What's deployed where?" | `deploy_target:` maps repos to AWS targets |

| "Which repos are deprecated?" | `deprecated:` section with reason + migration path |

| "What repos are safe to merge in what order?" | `depends_on:` gives you a topological sort for CI and worktree merges |

 

**Why not a wiki or Confluence page?**

 

| Format | Search | Version Control | Automation | Link Validity |

| ------ | ------ | --------------- | ---------- | ------------- |

| Wiki page | Hard (free text) | No | No | Breaks easily |

| **repo-manifest.yaml** | Easy (structured) | **Yes (git)** | **Yes (CI can validate)** | Linked in git |

 

### Full Manifest YAML

 

```yaml

# repo-manifest.yaml

# Master registry of all Harness Platform Team repositories

# Used for: discovery, dependency mapping, onboarding, CI/CD orchestration

 

version: "1.0"

bitbucket_project: "HARNESS"

default_branch: main

 

product_areas:

 

  infrastructure:

    description: "Terraform modules, EKS, networking, IAM"

    repos:

      - name: 111282-113518-terraform-base

        role: root-module

        tech: [terraform]

        deploy_target: aws

        depends_on: []

        subtree_candidates: []

 

      - name: harness-terraform-data

        role: data-infrastructure

        tech: [terraform]

        deploy_target: [kms, s3, dynamodb]

        depends_on: [111282-113518-terraform-base]

 

      - name: harness-terraform-integration

        role: integration-infra

        tech: [terraform]

        deploy_target: [sns]

        depends_on: [harness-terraform-data]

 

      - name: harness-terraform-eks-blue

        role: compute

        tech: [terraform]

        deploy_target: eks

        depends_on: [harness-terraform-integration]

 

      - name: harness-terraform-eks-green

        role: compute

        tech: [terraform]

        deploy_target: eks

        depends_on: [harness-terraform-integration]

 

      - name: harness-terraform-lambda

        role: compute

        tech: [terraform]

        deploy_target: lambda

        depends_on: [harness-terraform-integration]

 

      - name: harness-terraform-route53

        role: networking

        tech: [terraform]

        deploy_target: route53

        depends_on: [harness-terraform-data, harness-terraform-eks-blue]

 

      - name: harness-terraform-secrets

        role: security

        tech: [terraform]

        depends_on: [harness-terraform-data]

 

      - name: harness-ecs-delegate-terraform-ecs

        role: compute

        tech: [terraform]

        deploy_target: ecs

        depends_on: [111282-113518-terraform-base]

 

      - name: 111282-113518-terraform-cosign

        tech: [terraform]

        depends_on: [harness-terraform-integration]

 

  self-service:

    description: "User-facing APIs and platform services"

    repos:

      - name: harness-api

        tech: [java, spring-boot]

        deploy_target: eks

        depends_on: [harness-terraform-eks-blue]

        docs: product-development/engineering/plans/self-service/

 

      - name: harness-platform-api

        tech: [java]

        deploy_target: eks

        depends_on: [harness-terraform-eks-blue]

 

      - name: harness-custom-secrets-mgr

        tech: [java]

        deploy_target: jar

 

      - name: harness-custom-delegate

        tech: [docker]

        deploy_target: docker

 

      - name: harness-db-app

        tech: [java]

        deploy_target: lambda

        depends_on: [harness-terraform-lambda]

 

      - name: harness-ecs-delegate-app

        tech: [terraform]

        deploy_target: ecs

 

      - name: harness-account-resources

        tech: [terraform]

        deploy_target: harness-saas

 

  container-builds:

    description: "Buildi container build system"

    repos:

      - name: buildi

        tech: [kotlin, spring-boot]

        deploy_target: ecs

        depends_on: [buildi-terraform-ecs]

 

      - name: buildi-cli

        tech: [go]

        deploy_target: cli

 

      - name: buildi-kaniko

        tech: [docker]

        deploy_target: ecs-task

 

      - name: buildi-kaniko-arm64

        tech: [docker]

        deploy_target: ecs-task

 

      - name: buildi-kaniko-images

        tech: [docker]

        deploy_target: ecr

 

      - name: buildi-terraform-data

        tech: [terraform]

        depends_on: [111282-113518-terraform-base]

 

      - name: buildi-terraform-ecs

        tech: [terraform]

        depends_on: [111282-113518-terraform-base]

 

      - name: buildi-terraform-roles

        tech: [terraform]

        depends_on: [111282-113518-terraform-base]

 

      - name: buildi-terraform-connect

        tech: [terraform]

        depends_on: [buildi-terraform-roles]

 

  integrations:

    description: "Lambda-based event processing and integrations"

    repos:

      - name: lambda-harness-event-handler

        tech: [python]

        deploy_target: lambda

        depends_on: [harness-terraform-lambda]

 

      - name: lambda-cve-data-sync

        tech: [python]

        deploy_target: lambda

 

      - name: lambda-harness-grc

        tech: [java]

        deploy_target: lambda

 

      - name: lambda-jet-evidence-integration

        tech: [python]

        deploy_target: lambda

 

      - name: lambda-privileged-access-mgmt

        tech: [python]

        deploy_target: lambda

 

      - name: harness-magpie-consumer-lambda

        tech: [python]

        deploy_target: lambda

        depends_on: [harness-terraform-magpie-consumer-lambda]

 

  developer-tools:

    description: "CLIs, AI tooling, pipeline utilities"

    repos:

      - name: harness-cli

        tech: [python]

        deploy_target: cli

 

      - name: harness-actions

        tech: [go, python]

        deploy_target: cli

 

      - name: harness-templates

        tech: [python]

        deploy_target: docker

 

      - name: harness-pipeline-ops

        tech: [python]

        depends_on: [harness-rewrite-recipes]

 

      - name: harness-rewrite-recipes

        tech: [java]

 

      - name: harness-utilities

        tech: [python]

 

      - name: company-mcp-server

        tech: [python]

        deploy_target: server

 

      - name: harness-managed-pipeline-schema

        tech: [pydantic]

 

      - name: harness-ai-toolkit

        tech: [manifest]

 

      - name: harness-marketplace

        tech: [config]

 

  policy-and-governance:

    description: "OPA policies, ADRs, monitoring"

    repos:

      - name: harness-policy

        tech: [rego]

 

      - name: harness-adr

        tech: [markdown]

 

      - name: harness-dynatrace-cloudwatch

        tech: [terraform]

 

      - name: harness-eks-extension-dynatrace

        tech: [terraform]

 

# Repos flagged for deprecation/deletion

deprecated:

  - name: harness-terraform-eks2

    reason: "Replaced by eks-blue/green"

  - name: harness-terraform-eks3

    reason: "Replaced by eks-blue/green"

  - name: 111282-113518-terraform-gremlin

    reason: "Deletable"

  - name: 111282-113518-terraform-purge

    reason: "Deletable"

  - name: swiss-terraform-eks

    reason: "Deletable"

 

# Git subtree plan — for future shared-code extraction

subtree_plan:

  shared_terraform_modules:

    description: "Extract common TF patterns into subtrees consumable by downstream repos"

    source: 111282-113518-terraform-base

    consumers: [harness-terraform-data, harness-terraform-integration, buildi-terraform-data]

    prefix: modules/shared-base

    strategy: squash

 

  shared_python_libs:

    description: "Common Python utilities across lambdas"

    source: harness-utilities

    consumers: [lambda-harness-event-handler, lambda-cve-data-sync, lambda-privileged-access-mgmt]

    prefix: libs/harness-common

    strategy: squash

```

 

### Query Examples

 

Using [`yq`](https://github.com/mikefarah/yq) to query the manifest:

 

```bash

# What repos deploy to Lambda?

yq '.product_areas[].repos[] | select(.deploy_target | contains("lambda"))' repo-manifest.yaml

 

# What depends on terraform-base?

yq '.product_areas[].repos[] | select(.depends_on | contains("111282-113518-terraform-base"))' repo-manifest.yaml

 

# List all Python repos

yq '.product_areas[].repos[] | select(.tech | contains("python"))' repo-manifest.yaml

 

# Find all deprecated repos

yq '.deprecated[].name' repo-manifest.yaml

 

# What product area is buildi-cli in?

yq '.product_areas | to_entries[] | select(.value.repos[].name == "buildi-cli") | .key' repo-manifest.yaml

```

 

**Example onboarding flow:**

 

```text

"What does buildi-cli depend on?"

  → grep buildi-cli repo-manifest.yaml

  → tech: [go], deploy_target: cli, depends_on: [buildi]

  → docs: product-development/engineering/plans/container-builds/buildi-cli.md

  → Engineer reads that RFC, understands the full buildi subsystem in minutes

```

 

---

 

## 4. Git Subtrees for Code Sharing

 

Git subtrees belong **between code repos** — not between team-os and code repos. The team-os connects via YAML pointers only.

 

```text

┌─────────────────────────────────────────────┐

│          harness-platform-team-os           │

│  repo-manifest.yaml → references all repos  │

└─────────────────────────────────────────────┘

              │ (YAML pointers only — no git link)

              ▼

┌─────────────────────────────────────────────┐

│           Individual Code Repos             │

│                                             │

│  terraform-base ──subtree──► terraform-data │

│  terraform-base ──subtree──► buildi-tf-*    │

│  harness-utilities ──subtree──► lambdas     │

└─────────────────────────────────────────────┘

```

 

### How Subtrees Work

 

1. `terraform-base` contains shared Terraform modules

2. A consumer repo (e.g. `harness-terraform-data`) pulls them in:

 

   ```bash

   git subtree add --prefix modules/base \

     git@bitbucket.org:harness/111282-113518-terraform-base.git main --squash

   ```

 

3. The consumer has **all code at rest** — no extra init steps for new cloners

4. Updates flow downstream: `git subtree pull --prefix modules/base <remote> main --squash`

5. Fixes flow upstream: `git subtree push --prefix modules/base <remote> main` (then open a PR)

 

### Why Subtrees Are Compatible With Trunk-Based Development

 

| Concern | Resolution |

| ------- | ---------- |

| Each repo stays independent | Subtree is just a directory inside the consumer; maintains its own commit history |

| No detached HEAD | Unlike submodules, the working tree stays on the correct branch |

| Explicit update history | `--squash` creates a single merge commit per update — no history noise |

| New cloner DX | `git clone` — done. No `submodule init` ceremony |

| Fixes upstream | `git subtree push` opens a contribution path back to the source repo |

 

### Git Aliases for Subtree Operations

 

```bash

git config alias.stpull '!f() { git subtree pull --prefix=$1 $2 main --squash; }; f'

git config alias.stpush '!f() { git subtree push --prefix=$1 $2 main; }; f'

 

# Usage:

git stpull modules/base git@bitbucket.org:harness/111282-113518-terraform-base.git

git stpush modules/base git@bitbucket.org:harness/111282-113518-terraform-base.git

```

 

---

 

## 5. Trunk-Based Development with Git Worktrees

 

### The Problem

 

In trunk-based development across multiple interdependent repos, you often need to:

 

1. Work on a feature across **multiple repos simultaneously**

2. Test them together **before** merging to `main`

3. Switch contexts without losing work state

4. Coordinate merges in the right dependency order

 

**Without worktrees:** Repeated `git checkout` / `git stash` across repos — noisy, error-prone, slow context switching.

 

**With worktrees + manifest:** Each repo has multiple checked-out branches at once in isolated directories. The manifest tells you *which repos* to coordinate and in *what order* to merge.

 

---

 

### Worktree Workflow: Cross-Repo Feature

 

**Scenario:** Adding a new PAM Lambda integration that touches three repos.

 

The manifest shows the dependency chain:

 

```yaml

integrations:

  - name: lambda-privileged-access-mgmt

    tech: [python]

    depends_on: [harness-terraform-lambda, harness-utilities]

```

 

**Merge order derived from `depends_on`:** `harness-utilities` → `harness-terraform-lambda` → `lambda-privileged-access-mgmt`

 

```bash

# 1. Create worktrees for only the repos in your dependency chain

 

cd harness-utilities

git worktree add ../wt-pam-feature feature/pam-logging

 

cd ../harness-terraform-lambda

git worktree add ../wt-terraform feature/pam-iam-role

 

cd ../lambda-privileged-access-mgmt

git worktree add ../wt-lambda feature/pam-handler

 

# You now have parallel working trees:

# wt-pam-feature/     ← harness-utilities on feature/pam-logging

# wt-terraform/       ← harness-terraform-lambda on feature/pam-iam-role

# wt-lambda/          ← lambda-privileged-access-mgmt on feature/pam-handler

# (original dirs)     ← all three repos still on main, untouched

 

# 2. Develop in each worktree independently

cd wt-pam-feature && vim src/logger.py && git add . && git commit -m "Add structured logging helper"

cd ../wt-terraform && vim iam.tf && git add . && git commit -m "Add PAM execution role"

cd ../wt-lambda && vim handler.py && git add . && git commit -m "Add PAM event handler"

 

# 3. Test the full stack together (all three repos in feature state)

python -m pytest tests/integration/lambda_pam_test.py

terraform plan  # uses the new IAM role from wt-terraform

 

# 4. Merge in dependency order (manifest gives you this sequence)

cd ../wt-pam-feature && git push && gh pr create  # utilities first

cd ../wt-terraform  && git push && gh pr create   # then infra

cd ../wt-lambda     && git push && gh pr create   # then the lambda

 

# 5. Clean up worktrees

git worktree remove wt-pam-feature

git worktree remove wt-terraform

git worktree remove wt-lambda

```

 

**Quick context switching without stash noise:**

 

```bash

# Switch back to main (stable) without disrupting feature work

cd ../harness-utilities/     # still on main — work on a hotfix, commit, push

 

# Return to feature (state fully preserved)

cd ../wt-pam-feature/        # still on feature/pam-logging exactly where you left it

```

 

---

 

### Manifest-Driven Worktree Script

 

Store in `scripts/setup-feature-worktrees.sh` in the team-os repo:

 

```bash

#!/bin/bash

# Usage: ./scripts/setup-feature-worktrees.sh <product-area> <feature-name>

# Example: ./scripts/setup-feature-worktrees.sh integrations pam-logging

 

AREA=$1

FEATURE=$2

 

REPOS=$(yq ".product_areas.${AREA}.repos[].name" repo-manifest.yaml)

 

for repo in $REPOS; do

  BRANCH="feature/${FEATURE}"

  echo "Creating worktree for $repo → $BRANCH"

  git -C "../$repo" worktree add "../../wt-${FEATURE}/${repo}" "$BRANCH" 2>/dev/null \

    || git -C "../$repo" worktree add -b "$BRANCH" "../../wt-${FEATURE}/${repo}" main

done

 

echo ""

echo "Worktrees ready at: wt-${FEATURE}/"

echo "Merge order (from depends_on):"

yq ".product_areas.${AREA}.repos[] | .name + \" depends_on: \" + (.depends_on // [] | join(\", \"))" repo-manifest.yaml

```

 

Store in `scripts/merge-feature.sh`:

 

```bash

#!/bin/bash

# Merges repos in topological order based on depends_on in the manifest

# Usage: ./scripts/merge-feature.sh <feature-name>

 

FEATURE=$1

 

yq '.product_areas[].repos[] | .name' repo-manifest.yaml | while read repo; do

  BRANCH="feature/${FEATURE}"

  if git -C "../$repo" rev-parse "$BRANCH" &>/dev/null; then

    echo "Merging $repo ($BRANCH → main)..."

    cd "../$repo"

    gh pr merge --squash --auto

    cd - > /dev/null

  fi

done

```

 

---

 

### Trunk-Based Benefits Summary

 

| TBD Practice | Enabled By Manifest + Worktrees |

| ------------ | ------------------------------- |

| **Small, frequent PRs** | Worktrees isolate changes; manifest shows merge order so each PR stays focused |

| **Main always deployable** | Dependencies are explicit; validate full stack in feature worktrees before merging |

| **No long-lived branches** | Parallel worktrees = multiple features in flight without diverging `main` |

| **Fast code review** | Each PR is small and focused; reviewers see the dependency chain in the manifest |

| **Easy rollback** | Manifest identifies which repos were part of a feature; revert in reverse order |

| **Onboarding** | New dev reads manifest, learns the graph, runs `setup-feature-worktrees.sh` |

 

---

 

### Example: EKS Infrastructure Upgrade

 

**Scenario:** Upgrading EKS version across all clusters.

 

Manifest shows the dependency chain:

 

```text

harness-terraform-data

  └── harness-terraform-integration

        ├── harness-terraform-eks-blue

        ├── harness-terraform-eks-green

        └── harness-terraform-route53  (also depends on eks-blue)

```

 

```bash

# Create worktrees for the full dependency chain

for repo in harness-terraform-data harness-terraform-integration \

            harness-terraform-eks-blue harness-terraform-eks-green \

            harness-terraform-route53; do

  git -C $repo worktree add ../wt-eks-upgrade/$repo feature/eks-1.30-upgrade

done

 

# Dev work in dependency order

cd wt-eks-upgrade/harness-terraform-data       && vim main.tf && git commit -am "Bump EKS data sources"

cd ../harness-terraform-integration             && vim main.tf && git commit -am "Update integration endpoints"

cd ../harness-terraform-eks-blue                && vim main.tf && terraform plan && git commit -am "Upgrade to EKS 1.30 (blue)"

cd ../harness-terraform-eks-green               && vim main.tf && terraform plan && git commit -am "Upgrade to EKS 1.30 (green)"

cd ../harness-terraform-route53                 && vim main.tf && terraform plan && git commit -am "Update Route53 health checks"

 

# Validate full stack across all worktrees before merging

terraform plan -chdir=wt-eks-upgrade/harness-terraform-route53

 

# Merge in dependency order — manifest defines the sequence

for repo in data integration eks-blue eks-green route53; do

  cd wt-eks-upgrade/harness-terraform-$repo

  git push && gh pr create --title "EKS 1.30 upgrade ($repo)" && gh pr merge --auto

  cd -

done

```

 

---

 

### Pro Tips

 

**1. Keep worktree dirs out of repos:**

 

```bash

# Add to .gitignore in each code repo

wt-*/

```

 

**2. Validate the manifest in CI:**

 

```yaml

# .bitbucket-pipelines.yml step in team-os

- step:

    name: Validate repo-manifest.yaml

    script:

      - yq eval-all repo-manifest.yaml > /dev/null   # valid YAML

      - yq '.product_areas[].repos[].name' repo-manifest.yaml | sort | uniq -d  # no duplicates

```

 

**3. Use manifest as CI change trigger:**

 

```bash

# Only test repos affected by a commit + their dependents

CHANGED_REPO=$(git diff --name-only HEAD~1 | head -1 | cut -d/ -f1)

DEPENDENT_REPOS=$(yq ".product_areas[].repos[] | select(.depends_on[] == \"$CHANGED_REPO\") | .name" repo-manifest.yaml)

# Trigger pipelines for CHANGED_REPO and all DEPENDENT_REPOS

```

 

**4. Auto-populate PR descriptions from manifest:**

 

```markdown

<!-- PR template — referencing manifest cross-links -->

**Related repos** (from `repo-manifest.yaml`):

- [ ] harness-utilities#__ — shared logging lib

- [ ] harness-terraform-lambda#__ — IAM role

```

 

**5. Git aliases for common operations:**

 

```bash

git config alias.supdate 'submodule update --remote --merge'

git config alias.spush   'push --recurse-submodules=on-demand'

git config alias.stpull  '!f() { git subtree pull --prefix=$1 $2 main --squash; }; f'

git config alias.stpush  '!f() { git subtree push --prefix=$1 $2 main; }; f'

```

 

---

 

## 6. Implementation Roadmap

 

### Phase 1: Create the Team-OS Repo (Week 1–2)

 

- Create `harness-platform-team-os` in Bitbucket

- Scaffold the directory structure from [Section 2](#2-recommended-architecture)

- Write `repo-manifest.yaml` with all ~40 repos mapped (use the YAML in [Section 3](#full-manifest-yaml) as the starting point)

- Add `CLAUDE.md` context files at each directory level

- Write onboarding guides in `team/onboarding-guides/`

 

### Phase 2: Populate with Existing Knowledge (Week 2–4)

 

- Migrate existing ADRs from `harness-adr` into `product-development/engineering/adrs/` (or index them with links)

- Migrate any existing runbooks into `product-development/infrastructure/runbooks/`

- Create `feature-index.yaml` mapping current features/initiatives to repos and artifacts

- Write `infrastructure/topology.md` documenting the Terraform dependency graph as a narrative

 

### Phase 3: Git Subtree Pilot in Code Repos (Week 4–8)

 

- Identify shared Terraform modules in `111282-113518-terraform-base`

- Add subtrees to 2–3 consumer repos as a pilot (e.g., `harness-terraform-data`, `buildi-terraform-data`)

- Validate the pattern works with existing CI pipelines

- Document the workflow in `product-development/engineering/rfcs/infrastructure/shared-modules-subtree-rfc.md`

- Add `scripts/subtree-update.sh` helper to consumer repos

 

### Phase 4: Worktree Workflow Adoption (Week 6–10, overlaps Phase 3)

 

- Add `scripts/setup-feature-worktrees.sh` and `scripts/merge-feature.sh` to team-os

- Run a cross-repo feature using the worktree workflow as a team demo

- Document lessons learned back in `team/retros/`

 

### Phase 5: Automation (Optional / Ongoing)

 

- CI validation of `repo-manifest.yaml` against actual Bitbucket project (confirm all named repos exist)

- Dependency graph visualization generated from manifest

- PR templates in code repos that auto-link to team-os docs via the `docs:` field in the manifest

 

---

 

## 7. Summary

 

| Component | Where | Type |

| --------- | ----- | ---- |

| Documentation, PRDs, RFCs, plans | `harness-platform-team-os` (new Bitbucket repo) | Standalone docs repo |

| Repo registry + dependency graph | `repo-manifest.yaml` in team-os | YAML manifest — no git coupling to code repos |

| Shared Terraform modules | `git subtree` in consumer repos, sourced from `terraform-base` | `git subtree --squash` |

| Shared Python utilities | `git subtree` in lambda repos, sourced from `harness-utilities` | `git subtree --squash` |

| Cross-repo feature development | Git worktrees + manifest merge order | `git worktree add` per dependent repo |

| Individual code repos | Existing Bitbucket repos, fully independent | Independent trunk-based repos |
