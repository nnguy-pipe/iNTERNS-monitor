# Feature Specification: IMonitor Dashboard

**Feature Branch**: `001-imonitor-dashboard`

**Created**: 2026-06-10

**Status**: Draft

**Input**: User description: "Build the frontend for IMonitor, an intelligent live monitoring dashboard for life insurance software systems."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Monitor system health at a glance (Priority: P1)

An engineer needs to evaluate the current health of CI and production systems quickly, using a polished dashboard that surfaces overall status, live metrics, active alerts, and agent findings.

**Why this priority**: This is the core demo experience for IMonitor and delivers the highest value to the engineer user by making system health immediately visible.

**Independent Test**: Load the dashboard and verify that the top navigation, health summary, agent cards, live metrics, alerts feed, report preview, and skills registry preview are all visible and updated with mock data.

**Acceptance Scenarios**:

1. **Given** the user opens the dashboard, **When** the dashboard loads, **Then** the top navigation shows IHealth, the environment toggle, live status indicator, and last updated timestamp.
2. **Given** the dashboard is visible, **When** the mock data is displayed, **Then** the health summary shows overall status, health score, active alerts count, selected environment, and a plain-English summary.

---

### User Story 2 - Inspect active alerts and alert details (Priority: P2)

An engineer needs to review active alerts sorted by severity and open details for any alert to understand the impacted resource, suggested remediation, and agent reasoning.

**Why this priority**: Alert investigation is essential for operational monitoring and showcases the demo’s interactive value.

**Independent Test**: Click an alert in the alerts feed and confirm that an alert details drawer opens with title, severity, affected resource, reasoning, suggested actions, related skill, confidence score, and status.

**Acceptance Scenarios**:

1. **Given** active alerts are displayed, **When** the user clicks an alert, **Then** a side drawer opens showing the alert details and suggested next steps.
2. **Given** the alert details drawer is open, **When** the user reviews the information, **Then** they can see the associated agent and the alert confidence score.

---

### User Story 3 - Review live system metrics and trend behavior (Priority: P3)

An engineer wants to see simulated live metrics for CPU usage, memory usage, API latency, and error rate so they can understand system trends and anticipate potential issues.

**Why this priority**: Live metrics support the status summary and provide context for alerts, making the demo feel responsive and realistic.

**Independent Test**: Observe the metrics section for simulated updates every few seconds and confirm that CPU, memory, API latency, and error rate values change over time.

**Acceptance Scenarios**:

1. **Given** the dashboard is active, **When** the live simulation runs, **Then** CPU and memory metrics update periodically and may rise toward a critical threshold.
2. **Given** memory usage crosses a threshold, **When** the simulated state changes, **Then** a critical memory alert appears and the health score updates accordingly.

---

### User Story 4 - Preview recent system health report and skills registry (Priority: P3)

An engineer wants a quick summary of the latest merge or production health report and a preview of agent-discovered operational skills.

**Why this priority**: This completes the demo experience by showing both historical reporting and intelligence driven by monitoring agents.

**Independent Test**: Verify the report preview card displays a health score, result, summary, concerns, and suggested improvements, and confirm the skills registry preview lists discovered skills.

**Acceptance Scenarios**:

1. **Given** the report preview is visible, **When** the user scans the card, **Then** they see the latest health score, result, summary, areas of concern, and suggested improvements.
2. **Given** the skills registry preview is visible, **When** the user reads the card, **Then** they see operational skills like Memory Leak Detection, High CPU Usage Investigation, CI Health Gate Review, and New Relic Metric Interpretation.

---

### Edge Cases

- If the simulated live feed pauses or fails, the dashboard should continue showing the last known values and display a subtle warning that live updates are paused.
- If the environment toggle changes, the dashboard should update the status indicators, health summary, and alerts feed to match the selected CI or PROD context.
- If no active alerts remain, the alerts feed should show a friendly message such as "No active issues" and the health summary should reflect a healthy state.
- If the user opens an alert detail and then changes the environment, the drawer should either preserve the selected alert context or close gracefully with a message.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST display a top navigation bar with the IHealth product name, sections for Dashboard, Reports, and Skills Registry, a CI / PROD environment toggle, a live status indicator, and a last updated timestamp.
- **FR-002**: The dashboard MUST show a health summary that includes overall system status (Healthy, Degraded, or Critical), a health score from 0 to 100, the number of active alerts, the selected environment, and a short plain-English summary.
- **FR-003**: The dashboard MUST show agent status cards for monitored resources, including name, monitoring scope, status, latest finding, and last checked time.
- **FR-004**: The dashboard MUST show live metrics for CPU usage, memory usage, API latency, and error rate, with CPU and memory displayed using line charts or clear metric cards.
- **FR-005**: The dashboard MUST display an alerts feed sorted by severity, with each alert including severity, title, environment, source agent, affected resource, timestamp, and a short summary.
- **FR-006**: When a user clicks an alert, the dashboard MUST open an alert details drawer showing alert title, severity, affected resource, agent reasoning, suggested actions, related skill, confidence score, and status.
- **FR-007**: The dashboard MUST display a report preview card showing the latest merge or production health report with health score, result, summary, areas of concern, and suggested improvements.
- **FR-008**: The dashboard MUST show a skills registry preview with operational skills discovered by agents.
- **FR-009**: The dashboard MUST use an enterprise theme with primary blue, white cards, light gray background, green/yellow/red status colors, rounded cards, subtle shadows, and clean spacing.
- **FR-010**: The dashboard MUST simulate live monitoring by updating metrics every few seconds, allowing CPU and memory to rise, showing a critical memory alert when memory crosses a threshold, and updating the health score based on active alerts.
- **FR-011**: The dashboard MUST avoid backend integrations and complex routing, using mock data for the demo.
- **FR-012**: The frontend implementation MUST use React, Node.js, Tailwind CSS, and Recharts.
- **FR-013**: Navigation links in the top nav MAY scroll to in-page sections for Dashboard, Reports, and Skills Registry instead of using full route transitions.
- **FR-014**: The CI / PROD toggle MUST switch the dashboard between two mocked data states; CI should present a mostly healthy scenario with a merge warning, and PROD should present a degraded or critical scenario.
- **FR-015**: The dashboard MUST use accessible labels, readable headings, and enterprise-friendly UI text.

### Key Entities *(include if feature involves data)*

- **DashboardView**: Represents the main monitoring experience, including environment selection, summary widgets, agent cards, live metrics, alerts feed, report preview, and skills registry.
- **AgentStatus**: Represents a monitoring agent with attributes: `name`, `scope`, `status`, `latestFinding`, `lastChecked`, and `confidenceScore`.
- **Alert**: Represents an active issue with attributes: `severity`, `title`, `environment`, `sourceAgent`, `affectedResource`, `timestamp`, `summary`, `reasoning`, `suggestedActions`, `relatedSkill`, and `status`.
- **LiveMetric**: Represents simulated data for `cpuUsage`, `memoryUsage`, `apiLatency`, and `errorRate`, including trends over time.
- **ReportPreview**: Represents the latest health report with `healthScore`, `result`, `summary`, `areasOfConcern`, and `suggestedImprovements`.
- **SkillPreview**: Represents an operational skill with `name`, `description`, and `category`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can identify overall system health and the selected environment within 5 seconds of opening the dashboard.
- **SC-002**: The dashboard updates metrics at least once every 5 seconds and reflects changing CPU, memory, API latency, or error rate values.
- **SC-003**: At least one critical memory alert appears automatically when simulated memory usage crosses the threshold during the demo.
- **SC-004**: The alerts feed is sortable by severity and shows at least 3 active alerts with complete details on the dashboard.
- **SC-005**: The alert details drawer displays all required fields and is accessible by clicking any active alert.
- **SC-006**: The report preview and skills registry preview are visible on the dashboard and include the required summary and skill names.

## Assumptions

- The demo is a frontend-only experience with mocked live data; no backend API or authentication is implemented.
- The initial environment state and all dashboard data are predefined by the demo and may switch between CI and PROD without real backend context.
- The dashboard is designed as a polished hackathon demo rather than a production-grade monitoring product.
- The MVP is mostly single-page with sections for Dashboard, Reports, and Skills Registry.
- Navigation links can scroll to sections instead of using full routing.
- The CI / PROD toggle switches between two mocked data states.
- The CI scenario is mostly healthy with a merge warning, and the PROD scenario demonstrates degraded or critical health.
- The app is implemented using React, Node.js, Tailwind CSS, and Recharts.
- Accessibility and readable labels are required throughout the UI.
- Real-time data is simulated in the browser, with metric updates every few seconds and a predictable threshold-based alert behavior.
- Complex routing, deep navigation, and user management are out of scope for this frontend demo.
