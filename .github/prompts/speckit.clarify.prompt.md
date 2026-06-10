---
agent: speckit.clarify
title: "Ask targeted clarification questions"
description: "Identify underspecified areas and generate focused clarification questions."
slash: "/speckit clarify"
usage: "/speckit clarify [--limit <n>]"
parameters:
  - name: limit
    description: Maximum number of clarification questions (default: 5)
examples:
  - "/speckit clarify --limit 3"
---
Analyze a spec or feature description and list up to five high-impact clarification questions. Explain why each matters and how to encode answers into the spec.
