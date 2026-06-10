<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0
Bump rationale: MINOR — added Commits subsection under Principle II (Conventional Commits + Jira ticket mandate).

Principles defined:
  I.   Infrastructure as Code First (new)
  II.  Readable, Review-Ready Code (new)
  III. Security & Compliance by Default (new)
  IV.  Tests Are Non-Negotiable (new)
  V.   Controlled, Reproducible Deployments (new)

Sections added:
  - Development Workflow
  - Governance

Deferred TODOs:
  - AI/Model governance: No formal company-wide policy yet.
    Will be revisited when tooling (e.g. SetUpEngine) is available.
  - Team-specific technology standards: Intentionally omitted;
    teams maintain their own stack standards within these bounds.
-->

# iMonitor Constitution

## Purpose

This document defines the non-negotiable engineering principles that apply to all
iPipeline software teams, regardless of language, platform, or domain. Individual
teams may extend these principles with their own standards, but may not contradict them.

---

## Core Principles

### I. Infrastructure as Code First

All cloud and infrastructure resources MUST be defined in code and stored in version
control. No environment — dev, qa, uat, or production — may contain resources that
were created or modified manually outside of a codified deployment process.

- Choose an IaC tool appropriate to the platform (e.g., Terraform, Pulumi, CDK,
  Bicep). The tool is a team decision; the mandate is not.
- Environment-specific configuration MUST be separated from resource definitions
  (e.g., via overlays, workspaces, or parameter files).
- Infrastructure changes MUST go through the same PR and review process as
  application code.
- Drift between environments is a defect and MUST be resolved through code, not
  console fixes.

**Rationale**: Manual infrastructure changes are invisible to reviewers, irreproducible
across environments, and cannot be audited or rolled back reliably. IaC is the baseline
for operational trust.

---

### II. Readable, Review-Ready Code

Code is written once and read many times. Every engineer is responsible for ensuring
their code is clear to a peer reviewer who has no prior context.

**Naming**
- Names MUST be descriptive and unambiguous. Prefer clarity over brevity.
- Avoid abbreviations unless they are universally understood in the domain
  (e.g., `id`, `url`, `api`).
- Follow the naming convention of the language and team: `snake_case` for Python,
  `camelCase` for JavaScript/TypeScript, `PascalCase` for types and classes across
  most languages. Be consistent within a codebase.

**Structure**
- Functions and methods MUST do one thing. If you cannot describe a function's
  purpose in a single sentence, it SHOULD be split.
- Files and modules MUST have a clear, singular purpose. Avoid "utils" or "helpers"
  files that become catch-alls.
- Keep functions short. A function that does not fit on one screen warrants
  scrutiny and likely refactoring.

**Clarity**
- Code MUST be self-explanatory. Comments explain *why*, not *what*. If a comment
  is needed to explain what the code does, consider rewriting the code.
- Dead code, commented-out blocks, and unused imports MUST NOT be merged.
- Magic numbers and strings MUST be extracted into named constants.

**Commits**
- Commit messages MUST follow the [Conventional Commits](https://www.conventionalcommits.org/)
  standard (Angular convention):
  ```
  <type>(<scope>): <short description>

  [optional body]
  ```
  Valid types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `style`, `perf`, `ci`, `build`, `revert`.
- Every commit message MUST reference the associated Jira ticket in the scope or
  body, e.g.:
  ```
  feat(EMRGTC-1234): add bearer token validation to utilities API
  fix(AIML-567): correct prompt template variable substitution
  ```
- The short description MUST be written in the imperative mood ("add", "fix",
  "remove") and MUST NOT end with a period.
- Breaking changes MUST be noted with a `!` after the type or a `BREAKING CHANGE:`
  footer in the commit body.

**Pull Requests**
- PRs MUST be focused and small enough to review in a single sitting. A PR that
  touches unrelated concerns SHOULD be split.
- Every PR MUST include a clear description of what changed and why, along with
  the Jira ticket link.
- All PRs MUST receive at least **1 approving review** from a qualified team member
  before merge.
- Reviewers SHOULD flag any code that violates these standards, not just bugs.

**Rationale**: Readable code reduces onboarding time, makes bugs easier to spot in
review, and lowers the cost of future changes. Code that is hard to read is a
maintenance liability regardless of whether it works today.

---

### III. Security & Compliance by Default

Security is not a phase or a checklist item — it is a continuous responsibility
embedded in every change.

- Secrets, credentials, API keys, and tokens MUST NEVER be committed to source
  control or hardcoded in application code. Use secrets management tooling
  appropriate to the platform (e.g., AWS SSM Parameter Store, Azure Key Vault,
  HashiCorp Vault).
- All user-facing services MUST enforce authentication and authorization. The
  mechanism is a team decision; the requirement is not.
- Every PR MUST pass automated security scanning (Checkmarx SAST and Black Duck
  for dependency risk) before merge. Any finding rated High or Critical blocks
  merge until resolved or formally risk-accepted with documented justification.
- Code MUST be free of OWASP Top 10 vulnerabilities. Engineers are responsible
  for understanding common vulnerability classes relevant to their stack.
- Third-party dependencies MUST be reviewed before adoption. Prefer well-maintained
  packages with active security patching histories.

**Rationale**: iPipeline operates in a regulated insurance industry. Security
vulnerabilities carry compliance, legal, and reputational consequences. Catching
issues at PR time is orders of magnitude cheaper than remediating them in production.

---

### IV. Tests Are Non-Negotiable

Every service, library, and non-trivial function MUST have automated tests that
verify its intended behavior. Tests are a first-class deliverable, not an afterthought.

- Use the testing framework standard for the team's language (e.g., pytest for
  Python, Jest for JavaScript/TypeScript, JUnit for Java, xUnit for C#).
- Tests MUST run and pass in CI on every PR. A PR that breaks existing tests MUST
  NOT be merged until the tests are fixed or the change is confirmed intentional
  and the tests updated accordingly.
- New features MUST be accompanied by tests that cover the new behavior.
- Bug fixes MUST be accompanied by a regression test that would have caught the bug.
- There is no company-wide coverage floor — each team defines its own target
  appropriate to the risk profile of their service — but the absence of tests for
  changed behavior is not acceptable.

**Rationale**: Automated tests are the primary mechanism for preventing regressions
and enabling engineers to refactor with confidence. In AI/ML, financial, and
integration-heavy systems, silent failures are particularly costly and often
invisible without automated verification.

---

### V. Controlled, Reproducible Deployments

Deployments to any environment MUST be performed through an automated, auditable
pipeline. No engineer should be able to deploy to uat or production by running a
command locally.

- GitHub Actions is the standard CI/CD platform at iPipeline. Teams may use
  additional or alternative tooling where justified, but the deployment process
  MUST remain pipeline-driven, not manual.
- All deployment pipelines MUST be defined in code and version-controlled alongside
  the application they deploy.
- Environments (dev, qa, uat, prod) represent stages of confidence and maturity.
  Teams may promote to environments in the order that makes sense for their
  workflow, but MUST NOT deploy untested or unreviewed code to uat or production.
- Build artifacts MUST be deterministic: the same source commit MUST produce the
  same artifact on every build. Environment differences are configuration, not code.
- Rollback MUST be possible. Every production deployment MUST have a documented
  rollback path.

**Rationale**: Manual deployments are error-prone, untraceable, and impossible to
audit. Automated pipelines enforce consistency, create an audit trail, and allow
teams to move fast without sacrificing safety.

---

## Development Workflow

This workflow applies to all teams. Steps may be adapted to team tooling, but the
structure MUST be preserved.

1. **Branch** off the main branch using a descriptive branch name tied to the
   work item (e.g., `feat/TICKET-123-short-description`, `fix/TICKET-456-bug-name`).
2. **Develop locally** against a non-production environment. Do not develop directly
   against shared or production resources.
3. **Test locally** — all tests MUST pass before opening a PR.
4. **Open a PR** against the main branch with a clear description of the change
   and its rationale.
5. **Automated gates** — security scans and CI tests run automatically. Address
   any failures before requesting review.
6. **Peer review** — at least 1 approving review is required. Reviewers verify
   correctness, readability, security, and constitution compliance.
7. **Merge** — squash or merge per team convention. The main branch MUST always
   be in a deployable state.
8. **Deploy** via the automated pipeline. Do not deploy manually.

---

## Governance

This constitution applies to all iPipeline engineering teams and supersedes informal
team-level practices where they conflict. Teams SHOULD maintain their own supplementary
standards that extend (not contradict) these principles.

**Amendment process**:
- Amendments require a PR with at least 1 approving review from an engineering lead.
- The version MUST be incremented following semantic versioning:
  - **MAJOR**: A principle is removed, fundamentally redefined, or governance structure changes.
  - **MINOR**: A new principle or section is added, or existing guidance is materially expanded.
  - **PATCH**: Clarifications, wording improvements, or non-semantic refinements.
- `Last Amended` MUST be updated to the merge date of the amendment PR.
- The Sync Impact Report comment at the top of this file MUST be updated with
  each amendment to record what changed.

**Compliance**:
- All PRs SHOULD be reviewed with these principles in mind.
- Exceptions to any principle require explicit, documented justification in the PR
  description and sign-off from an engineering lead.
- Repeated non-compliance is a team health issue and SHOULD be raised in retrospectives
  and engineering leadership reviews.

**Version**: 1.1.0 | **Ratified**: 2026-03-27 | **Last Amended**: 2026-03-27
