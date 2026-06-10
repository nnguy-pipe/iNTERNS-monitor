---
agent: speckit.plan
title: "Create a design plan (plan.md)"
description: "Generate a structured plan.md from a feature description or spec."
slash: "/speckit plan"
usage: "/speckit plan [--from <spec|description>] [--concise]"
parameters:
  - name: from
    description: Source for the plan: spec or natural-language description
  - name: concise
    description: Produce a shorter plan
examples:
  - "/speckit plan --from spec"
---
Produce plan.md with problem statement, goals, non-goals, architecture, data model, API surface, milestones, and success criteria. Keep it concise and reference validation commands.
