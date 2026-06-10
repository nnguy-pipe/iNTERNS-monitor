---
agent: speckit.constitution
title: "Generate or update project constitution"
description: "Create or update a concise project constitution and list impacted templates."
slash: "/speckit constitution"
usage: "/speckit constitution [--update] [--format <md|txt>]"
parameters:
  - name: update
    description: Update existing constitution instead of creating new
  - name: format
    description: Output format (md or txt)
examples:
  - "/speckit constitution --update --format md"
---
Produce a project constitution covering principles, governance, decision-making, and contributor expectations. Show diffs when updating.
