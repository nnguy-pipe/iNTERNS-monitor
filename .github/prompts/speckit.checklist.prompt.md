---
agent: speckit.checklist
title: "Generate a release or feature checklist"
description: "Create a checklist for a feature or release based on repo practices."
slash: "/speckit checklist"
usage: "/speckit checklist [--for <feature|release>] [--include-tests]"
parameters:
  - name: for
    description: Target: feature or release (default: feature)
  - name: include-tests
    description: Include detailed test steps
examples:
  - "/speckit checklist --for release --include-tests"
---
Produce a concise checklist covering design, implementation, testing, security, deployment, and monitoring. Include owners and validation commands.
