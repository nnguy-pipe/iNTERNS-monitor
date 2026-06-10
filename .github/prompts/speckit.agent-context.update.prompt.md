---
agent: speckit.agent-context.update
title: "Refresh agent context for Spec Kit"
description: "Update the managed Spec Kit section in the coding agent context file."
slash: "/speckit agent-context.update"
usage: "/speckit agent-context.update [--files spec.md,plan.md,tasks.md]"
parameters:
  - name: files
    description: Comma-separated list of files to refresh in the agent context
examples:
  - "/speckit agent-context.update --files spec.md,plan.md"
---
Locate Spec Kit artifacts and refresh the agent context snippet used by coding agents. Output the updated block and verification checklist.
