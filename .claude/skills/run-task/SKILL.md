---
name: run-task
description: >
  Execute one task from TASKS.md end-to-end with full protocol: dependency
  check, branch, implementation, validation, review, PR prep, board update.
  Use at the start of every implementation session: /run-task <TASK-ID>.
---
1. Read TASKS.md; locate $ARGUMENTS. Verify all `depends:` tasks are ✅;
   if not, STOP and report which are missing.
2. Create branch `task/<id>-<slug>`. Restate the task's deliverables and
   acceptance criteria as your TodoWrite list.
3. Implement per the task prompt. Apply CLAUDE.md operating rules.
4. Run every command listed under the task's **Verify** section; all must pass.
5. Invoke the graph-validator sub-agent on the diff (if knowledge/ or the
   manifest changed). Resolve all blocking issues.
6. Update the task's row in TASKS.md (status, PR link placeholder, notes).
7. Commit; summarize for PR: what changed, verification evidence,
   open TODO(verify)/TODO(decide)/[HUMAN] items created.
