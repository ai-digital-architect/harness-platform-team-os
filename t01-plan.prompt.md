
You are bootstrapping the Claude Code implementation harness for the knowledge-graph build.

Your task is T0.1 from kg-claude-code-implementation-plan.md Part 2.



DELIVERABLES — you will plan (not yet write) the complete file tree:



1. CLAUDE.md — 200-line project memory per Part 1 §1.2

2. AGENTS.md — cross-harness mirror (Copilot-readable)

3. TASKS.md — markdown board transcribed from this plan's Part 2

4. .claude/settings.json — permissions + hooks per Part 1 §1.3

5. .claude/hooks/graph-check-on-edit.sh — validation hook

6. .claude/hooks/task-gate-on-stop.sh — acceptance-criteria gate

7. .claude/agents/repo-surveyor.md — Part 1 §1.4

8. .claude/agents/workflow-miner.md — Part 1 §1.4

9. .claude/agents/node-author.md — Part 1 §1.4

10. .claude/agents/graph-validator.md — Part 1 §1.4

11. .claude/skills/run-task/SKILL.md — Part 1 §1.5

12. .claude/skills/mine-workflow/SKILL.md — (placeholder, detail in T2.2)

13. .claude/rules/graph-nodes.md — `paths: ["knowledge/**"]`

14. .claude/rules/scripts.md — `paths: ["scripts/**"]`

15. .claude/rules/harness-layer.md — `paths: ["harness-layer/**"]`

16. bitbucket-pipelines.yml — placeholder validate step

17. Empty directories:

    - knowledge/{capabilities,workflows,dependencies,conventions/gotchas,decisions}

    - harness-layer/{rules,skills,sync}

    - scripts/

18. GRAPH-SCHEMA.md — placeholder (built in T0.3)



PLAN MODE CHECKLIST (do not write yet):



Step 1: List all 18 deliverables with their sizes (estimate lines of code/config).

Step 2: For each of the 16 files, provide a PREVIEW of the full content:

  - Copy the exact content from Part 1 of kg-claude-code-implementation-plan.md where specified

  - For scripts (hooks), provide the exact bash code

  - For JSON/YAML, format clearly and validate structure

  - For markdown (CLAUDE.md, AGENTS.md, TASKS.md), provide the full text

Step 3: For empty directories, list the exact paths.

Step 4: Verify the tree structure by drawing it (cd .; find . -type f -o -type d | head -50).

Step 5: Call out any ambiguities or decisions you made (there should be none — everything is specified).

Step 6: Summarize the total LOC and file count.



ACCEPTANCE CHECKLIST (approval gates for you to review):



□ All file previews match the spec exactly (especially .claude/settings.json — any JSON syntax error blocks you)

□ All 18 deliverables accounted for

□ Directory structure complete

□ No files invented beyond the spec

□ Total LOC estimate < 2000 (harness is intentionally lean)



ONLY AFTER YOU RECEIVE APPROVAL on all checkboxes should you:

- Create all directories with `Bash(mkdir -p <path>)`

- Write all files with `Write(<path>, <content>)`

- Verify with `Bash(find . -type f | wc -l)` == 16 files

- Validate JSON: `Bash(python3 -c "import json; json.load(open('.claude/settings.json'))")`

- Mark Task T0.1 ✅ in TASKS.md and commit (chore: bootstrap harness)



BEGIN PLAN MODE NOW.