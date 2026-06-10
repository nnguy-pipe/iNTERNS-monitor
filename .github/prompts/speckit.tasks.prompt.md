---
agent: speckit.tasks
title: "Generate tasks.md"
description: "Create an actionable, dependency-ordered tasks.md from spec or plan artifacts."
slash: "/speckit tasks"
usage: "/speckit tasks [--from <spec|plan|prompt>] [--estimate-units <hours|points>]"
parameters:
  - name: from
    description: Source: spec, plan, or interactive prompt
  - name: estimate-units
    description: Units for estimates (hours or points)
examples:
  - "/speckit tasks --from spec"
---
Read spec.md and plan.md (or accept a user description) and generate tasks.md with goal, milestones, tasks in gerund form, estimates, owners, and dependencies. Return markdown and a short rationale for ordering.
