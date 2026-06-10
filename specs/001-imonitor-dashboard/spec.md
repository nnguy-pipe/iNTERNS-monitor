# Feature Specification: IMonitor Dashboard

**Feature Directory**: `specs/001-imonitor-dashboard`

**Version**: 1.1.0

**Created**: 2026-06-10

**Status**: Review-ready

**Summary**: Polish and refine the IMonitor frontend so it reads and behaves like a professional enterprise monitoring product. Preserve existing functionality and mock-data-driven CI/PROD toggle, but tighten visual hierarchy, spacing, colors, and UX copy to feel simple, credible, and demo-ready.

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

### Edge Cases

- Live feed paused: show a subtle amber banner and continue rendering last values.
- Environment change while drawer open: drawer remains open only if the selected alert exists in the new environment; otherwise the drawer closes with an explanatory toast.
- No alerts: show a friendly empty state with a brief explanation and CTA to view the latest report.


## Requirements *(mandatory)*

### Functional Requirements (refined)

- **FR-001**: The dashboard MUST display a top navigation bar with the product name, three in-page sections (Dashboard, Reports, Skills), a CI/PROD environment toggle, a live status indicator, and a last-updated timestamp.
- **FR-002**: The health summary MUST be visually prominent (large numeric score and an accessible status badge) and include the primary contributors to the current score in short plain-English copy.
- **FR-003**: Agent cards MUST display `name`, `scope`, `status` (with color badge), `latestFinding`, and `lastChecked`. Cards should be equal-height within a responsive grid.
- **FR-004**: Metrics panel MUST include line charts and metric cards for CPU, memory, API latency, and error rate. Metric cards MUST use threshold-based color accents and short trend copy.
- **FR-005**: Alerts feed MUST be severity-sorted, show clear severity pills (color-coded), and visually emphasize critical alerts (left accent, stronger shadow).
- **FR-006**: Alert details drawer MUST present: title, timestamp, severity pill, affected resource, source agent, short timeline of events, agent reasoning, suggested actions (bulleted), related skill link, confidence score, and primary actions (`Acknowledge`, `View Runbook`).
- **FR-007**: Drawer accessibility: focus trap when open, `Esc` closes, initial focus on the primary action, and all interactive elements keyboard navigable.
- **FR-008**: The dashboard MUST maintain a laptop-first 8/4 column layout for Report/Skills at ~1200px and collapse cleanly to single-column on small screens.
- **FR-009**: Styling MUST follow the iPipeline-inspired theme: primary blue accents, white cards, light-gray background, and color semantics (green/amber/red) for health indicators.
- **FR-010**: The app MUST remain frontend-only using mock datasets for CI and PROD and simulate live metric updates on a timed interval.

### Key Entities (refined)

- `AgentStatus`: `{ name, scope, status, latestFinding, lastChecked, confidenceScore }`
- `Alert`: `{ id, severity, title, environment, sourceAgent, affectedResource, timestamp, summary, reasoning, suggestedActions, relatedSkill, status, acknowledged }`
- `LiveMetricSeries`: `{ cpuUsage: number[], memoryUsage: number[], apiLatency: number[], errorRate: number[] }`
- `ReportPreview`: `{ healthScore, result, summary, areasOfConcern: string[], suggestedImprovements: string[] }`
- `SkillPreview`: `{ name, description, category, relatedAlerts: string[] }`


## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On laptop width (≥1200px), a user identifies overall system health and the selected environment within 5 seconds of opening the dashboard.
- **SC-002**: Metrics update on a regular interval (configurable, default ≤5s) and metric cards reflect real-time-like changes.
- **SC-003**: When simulated memory crosses the critical threshold in PROD, a critical alert is created, the alerts feed highlights it, and the health score adjusts appropriately.
- **SC-004**: Alerts feed presents at least 3 alerts (across environments) in the demo data set with complete details.
- **SC-005**: The alert details drawer presents all required fields, supports keyboard interactions, and the primary actions are usable by keyboard and mouse.
- **SC-006**: Report preview and skills registry are visible and read comfortably without horizontal overflow on the laptop baseline.


## Assumptions

- Demo remains frontend-only with all data mocked in `src/data/` and no backend integrations.
- The laptop-first layout (≥1200px) is the primary design target; tablet/phone use is supported via responsive collapse rules.
- Threshold values for warning/critical are configurable constants used by metric cards and alert generation.
- Accessibility (ARIA roles, keyboard focus management) is implemented as part of polishing; the app remains a demo, not a fully certified accessibility product.
- Implementation stack: React + Vite (JavaScript), Tailwind CSS, Recharts. No TypeScript.
