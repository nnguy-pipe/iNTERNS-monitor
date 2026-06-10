---
agent: speckit.analyze
title: "Cross-artifact spec/plan/tasks analysis"
description: "Analyze spec.md, plan.md, and tasks.md for consistency and quality."
slash: "/speckit analyze"
usage: "/speckit analyze [--files spec.md,plan.md,tasks.md] [--format <summary|detailed>]"
parameters:
  - name: files
    description: Comma-separated files to analyze (defaults to spec.md,plan.md,tasks.md)
  - name: format
    description: Output verbosity: summary or detailed
examples:
  - "/speckit analyze --format summary"
---
Compare artifacts and report inconsistencies, missing details, and conflicting acceptance criteria. Provide prioritized recommendations and concrete edits.
