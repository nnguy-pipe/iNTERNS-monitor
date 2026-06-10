---
agent: speckit.implement
title: "Implement tasks from tasks.md"
description: "Produce implementation plans, patch snippets, and commit sequences for tasks."
slash: "/speckit implement"
usage: "/speckit implement [--task <task-id>] [--dry-run]"
parameters:
  - name: task
    description: Specific task id from tasks.md to implement (optional)
  - name: dry-run
    description: Output patches/commands without applying changes
examples:
  - "/speckit implement --task user-auth"
---
Given tasks.md or a task id, produce file diffs, patch snippets, and a suggested commit sequence. Include tests or test plans. If --dry-run, do not apply edits.
