---
agent: speckit.taskstoissues
title: "Convert tasks.md into GitHub issues"
description: "Create GitHub issues from tasks.md with labels, assignees, and dependencies."
slash: "/speckit taskstoissues"
usage: "/speckit taskstoissues [--assignee <user>] [--label <label>] [--dry-run]"
parameters:
  - name: assignee
    description: Assign created issues to this GitHub username (optional)
  - name: label
    description: Add a label to all created issues (optional)
  - name: dry-run
    description: Output commands without creating issues
examples:
  - "/speckit taskstoissues --dry-run"
  - "/speckit taskstoissues --assignee @alice --label backlog"
---
Parse tasks.md and produce GitHub issues in JSON or gh CLI command form. Include title, body, labels, assignees, and dependency links. If --dry-run, return commands without making API calls.
