---
agent: speckit.specify
title: "Create or update feature spec.md"
description: "Produce a clear, testable feature specification from a description."
slash: "/speckit specify"
usage: "/speckit specify [--from <description|notes>] [--version <v1.0>]"
parameters:
  - name: from
    description: Source content for the spec
  - name: version
    description: Version tag for the spec output
examples:
  - "/speckit specify --from description --version v1.0"
---
Write or refine spec.md including user stories, acceptance criteria, UX flows, data model changes, API contracts, and edge cases. Output a versioned spec and list open questions.
