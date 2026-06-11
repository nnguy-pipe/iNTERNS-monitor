# Feature Specification: IMonitor Dashboard

**Feature Directory**: `specs/001-imonitor-dashboard`

**Version**: 1.2.0

**Created**: 2026-06-10

**Updated**: 2026-06-11

**Status**: Review-ready

**Summary**: Preserve the polished enterprise dashboard UX while shifting to backend-driven data for reports and agents. Agent cards must keep all operational details, reintroduce explicit per-agent health display, and align dashboard health score behavior with backend report scoring and fallback rules.

## User Scenarios & UX Flows

The goal is to refine existing flows; we do not add major new features. The UX is laptop-first (desktop baseline ~1200px) with responsive adjustments down to tablet and phone widths.

### P1 — At-a-glance health overview (Primary)

Actor: Site reliability engineer (SRE) or demo audience.

Flow: User opens dashboard → top nav shows product name, CI/PROD toggle, live status and timestamp → health summary is prominent (large score, colored status badge) → alerts feed and metrics provide immediate context.

Acceptance:
- Health summary is visually prominent on page load and readable within 3–5 seconds.
- Status badge uses color semantics: `Healthy`=green, `Degraded`=amber, `Critical`=red.
- Health score is large, with microcopy explaining main contributors (e.g., "Degraded due to memory and API issues").

Success test: Open page at 1366×768 (laptop), confirm top-left quadrant contains health score and badge, and the right column contains report + skills with consistent spacing.

### P2 — Alert investigation (High priority)

Flow: User scans alerts feed → clicks an alert → details drawer opens (focus trapped) showing severity, resource, agent reasoning, suggested actions, confidence, and quick actions (Acknowledge, View Runbook).

Acceptance:
- Drawer opens from the right and overlays content with a dim backdrop.
- Drawer includes: title, time, severity pill (colored), affected resource, source agent, timeline (list of recent events), agent reasoning, suggested remediation steps, related skill link, confidence percentage, and action buttons (`Acknowledge`, `View Runbook`).
- Keyboard: `Esc` closes drawer, `Tab` cycles focus within drawer, initial focus lands on the primary action button.

Success test: Click any alert and verify drawer content, keyboard close, and focus trap behavior.

### P3 — Metrics & trend context (Medium)

Flow: User inspects CPU/memory charts and metric cards which update every few seconds. Cards reflect threshold colors (green/yellow/red) based on configured thresholds and include small trend microcopy.

Acceptance:
- Line charts render with clear axes and muted gridlines; metric cards show last value, unit, and a short trend label.
- Cards change their accent/badge color when values cross warning/critical thresholds.

Success test: Simulate PROD state and observe memory rising; metric cards and health score update and a critical memory alert surfaces.

### P4 — Report and skills preview (Medium)

Flow: Report preview provides a concise executive view (score, summary, areas of concern, suggested improvements). Skills registry highlights operational playbooks and is visually distinct from report cards.

Acceptance:
- Report preview is larger than individual cards and placed left of the skills registry on laptop layouts (8/4 column split).
- Skills cards are vertically stacked on laptop widths to avoid horizontal squashing; on very wide screens they may present multiple columns.

Success test: On laptop width, verify report card width and skills registry alignment match the design baseline and have consistent padding.

### P5 — Backend-aware health consistency (High priority)

Flow: User switches CI/PROD environment → frontend requests latest backend report and agent snapshots → dashboard updates health score, summary, and agent cards using backend values (with fallback to mock data only on API failure).

Acceptance:
- Agent cards retain all card fields currently shown (scope/finding/timestamp + backend telemetry), and display explicit `Health` per card.
- Placeholder backend statuses (for example `default`, `null`) do not show as-is; cards derive a health value from telemetry thresholds when status is not meaningful.
- Dashboard health score mapping from backend report is deterministic and environment changes re-fetch backend data.

Success test: In both CI and PROD, refresh the dashboard and confirm agent card health values and top health score are populated from backend responses when available.

### Edge Cases

- Live feed paused: show a subtle amber banner and continue rendering last values.
- Environment change while drawer open: drawer remains open only if the selected alert exists in the new environment; otherwise the drawer closes with an explanatory toast.
- No alerts: show a friendly empty state with a brief explanation and CTA to view the latest report.


## Requirements *(mandatory)*

### Functional Requirements (refined)

- **FR-001**: The dashboard MUST display a top navigation bar with the product name, three in-page sections (Dashboard, Reports, Skills), a CI/PROD environment toggle, a live status indicator, and a last-updated timestamp.
- **FR-002**: The health summary MUST be visually prominent (large numeric score and an accessible status badge) and include the primary contributors to the current score in short plain-English copy.
- **FR-003**: Agent cards MUST display `name`, explicit `health`, and all available context fields (`scope`, `latestFinding`, `lastChecked`, and telemetry such as CPU/RAM/active users/external load/event spike). Cards should be equal-height within a responsive grid.
- **FR-004**: Metrics panel MUST include line charts and metric cards for CPU, memory, API latency, and error rate. Metric cards MUST use threshold-based color accents and short trend copy.
- **FR-005**: Alerts feed MUST be severity-sorted, show clear severity pills (color-coded), and visually emphasize critical alerts (left accent, stronger shadow).
- **FR-006**: Alert details drawer MUST present: title, timestamp, severity pill, affected resource, source agent, short timeline of events, agent reasoning, suggested actions (bulleted), related skill link, confidence score, and primary actions (`Acknowledge`, `View Runbook`).
- **FR-007**: Drawer accessibility: focus trap when open, `Esc` closes, initial focus on the primary action, and all interactive elements keyboard navigable.
- **FR-008**: The dashboard MUST maintain a laptop-first 8/4 column layout for Report/Skills at ~1200px and collapse cleanly to single-column on small screens.
- **FR-009**: Styling MUST follow the iPipeline-inspired theme: primary blue accents, white cards, light-gray background, and color semantics (green/amber/red) for health indicators.
- **FR-010**: The app MUST use backend endpoints as the primary source for report and agent data, with mock datasets used only as controlled fallback when backend calls fail.
- **FR-011**: Backend report `health_score` MUST be mapped to a 0-100 integer for display and remain consistent across the Health Summary and Report panels.
- **FR-012**: Backend health score/status MUST be authoritative when present; frontend severity logic is allowed only as a temporary UI fallback when backend score/status are missing.
- **FR-013**: The frontend fallback health algorithm MUST be rule-based, deterministic, and documented (alerts + agent status + telemetry penalties) for explainability.

### Key Entities (refined)

- `AgentStatus`: `{ name, scope, status, health, latestFinding, lastChecked, confidenceScore, cpu, ram, active_users, external_load, event_spike }`
- `Alert`: `{ id, severity, title, environment, sourceAgent, affectedResource, timestamp, summary, reasoning, suggestedActions, relatedSkill, status, acknowledged }`
- `LiveMetricSeries`: `{ cpuUsage: number[], memoryUsage: number[], apiLatency: number[], errorRate: number[] }`
- `ReportPreview`: `{ healthScore, result, summary, areasOfConcern: string[], suggestedImprovements: string[], backendStatus?, suggestions?, createdAt? }`
- `SkillPreview`: `{ name, description, category, relatedAlerts: string[] }`
- `BackendAgentResponse`: `{ agents: AgentStatus[] }`
- `BackendReportResponse`: `{ health_score: number, status: string, primary_issue: string, suggestions: string[], created_at: string }`

## API Contracts

- `GET /health`
	- Purpose: verify backend availability before data fetch.
	- Success: service health object.
	- Failure: frontend shows non-blocking backend connection banner.
- `GET /api/reports/latest?system_name=iMonitor&environment=<ci|production>`
	- Purpose: fetch latest health report for selected environment.
	- Success: `BackendReportResponse`.
	- Failure behavior: frontend attempts `POST /api/reports/generate` for recovery.
- `POST /api/reports/generate`
	- Purpose: generate report if latest report does not exist.
	- Body: `{ system_name: "iMonitor", environment: <ci|production>, lookback_minutes: 60 }`
	- Success: generated `BackendReportResponse`.
- `GET /api/agents/check`
	- Purpose: fetch latest agent snapshot values.
	- Success: `BackendAgentResponse` with card-ready telemetry fields.
- `GET /api/simulator/metrics`
	- Purpose: retrieve simulator metrics for trend and validation use.
- `POST /api/simulator/ingest?system_name=iMonitor&environment=<ci|production>`
	- Purpose: ingest simulator output into report-generation pipeline.


## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On laptop width (≥1200px), a user identifies overall system health and the selected environment within 5 seconds of opening the dashboard.
- **SC-002**: Metrics update on a regular interval (configurable, default ≤5s) and metric cards reflect real-time-like changes.
- **SC-003**: When simulated memory crosses the critical threshold in PROD, a critical alert is created, the alerts feed highlights it, and the health score adjusts appropriately.
- **SC-004**: Alerts feed presents at least 3 alerts (across environments) in the demo data set with complete details.
- **SC-005**: The alert details drawer presents all required fields, supports keyboard interactions, and the primary actions are usable by keyboard and mouse.
- **SC-006**: Report preview and skills registry are visible and read comfortably without horizontal overflow on the laptop baseline.
- **SC-007**: For a given backend report, the displayed health score is identical in all UI locations and equals `round(health_score * 100)`.
- **SC-008**: Every rendered agent card shows an explicit `Health` value and does not surface placeholder statuses such as `default` or `null`.


## Assumptions

- Backend is expected to be available locally and is the primary data source for reports and agent checks.
- The laptop-first layout (≥1200px) is the primary design target; tablet/phone use is supported via responsive collapse rules.
- Threshold values for warning/critical are configurable constants used by metric cards and alert generation.
- Accessibility (ARIA roles, keyboard focus management) is implemented as part of polishing; the app remains a demo, not a fully certified accessibility product.
- Implementation stack: React + Vite (JavaScript), Tailwind CSS, Recharts. No TypeScript.

## Health Score Decision

- Backend is the single source of truth for dashboard health score and health status.
- Frontend rule-based computation is temporary fallback only, used when backend score/status are missing or invalid.
- Frontend fallback must never override a valid backend health score/status.

## Open Questions

1. What exact weighting model should be used for score derivation when backend score is unavailable (for example: memory 35%, API errors 30%, CPU 20%, infra latency 15%)?
2. For placeholder agent status values (`default`, `null`, `unknown`), do we standardize threshold derivation in backend only, or keep a mirrored frontend fallback for resiliency?
