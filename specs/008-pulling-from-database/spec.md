# Feature Specification: Pulling from Database

**Feature Branch**: `[008-pulling-from-database]`

**Created**: 2026-06-12

**Status**: Draft

**Input**: User description: "I want to be able to have the frontend read from the database itself for values, the ahms.db values instead of the API call. I want this to be implemented to the current code base."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show stored dashboard values (Priority: P1)

As a dashboard user, I want the main report area to show the latest values stored in `ahms.db` so I see the persisted health snapshot rather than a newly computed API response.

**Why this priority**: This is the core value of the feature and the main reason to prefer the database-backed source.

**Independent Test**: Open the dashboard with a stored report available and confirm the health score, status, summary, concerns, and suggestions match the latest persisted record.

**Acceptance Scenarios**:

1. **Given** a persisted report exists for the selected environment, **When** the dashboard loads, **Then** the report cards show the stored score, status, summary, concerns, and suggestions.
2. **Given** the user switches environments, **When** a persisted report exists for the newly selected environment, **Then** the displayed values update to that environment’s stored report.

---

### User Story 2 - Keep the dashboard usable without stored data (Priority: P2)

As a dashboard user, I want the page to still show a useful snapshot when no stored report is available so the experience does not break on empty or fresh data.

**Why this priority**: The dashboard should remain usable even before the database has a saved report.

**Independent Test**: Load the dashboard with no persisted report available and confirm the page still renders a health snapshot based on live telemetry.

**Acceptance Scenarios**:

1. **Given** no persisted report exists for the selected environment, **When** the dashboard loads, **Then** the report area falls back to the live telemetry snapshot.
2. **Given** the persisted report cannot be loaded, **When** the dashboard loads, **Then** the rest of the dashboard still renders and the user can continue using the page.

---

### User Story 3 - Keep exports aligned with the displayed source (Priority: P3)

As a dashboard user, I want exported report content to match what I see on screen so downloaded reports stay consistent with the persisted dashboard values.

**Why this priority**: Exported artifacts must reflect the same source of truth as the visible dashboard.

**Independent Test**: Download the report after loading a persisted report and confirm the export uses the same score, summary, and concern list shown in the UI.

**Acceptance Scenarios**:

1. **Given** a persisted report is displayed, **When** the user exports the report, **Then** the export contains the same score, summary, and concern items.

---

### Edge Cases

- The selected environment has no stored report yet.
- The stored report exists but has an unknown status value.
- The stored report is older than the current live telemetry snapshot.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard MUST use the latest persisted report from `ahms.db` as the primary source for the main report area when one is available.
- **FR-002**: The dashboard MUST display the persisted report’s health score, status, summary, concerns, and improvement suggestions when the report is available.
- **FR-003**: The dashboard MUST fall back to a live telemetry-derived snapshot when no persisted report is available.
- **FR-004**: The dashboard MUST clearly indicate whether the displayed score comes from persisted data or from a fallback snapshot.
- **FR-005**: The dashboard MUST keep the rest of the page usable even when persisted data cannot be loaded.
- **FR-006**: Report exports MUST reflect the same source of truth that is currently shown in the dashboard.
- **FR-007**: Environment changes MUST refresh the displayed report source for the newly selected environment.

### Key Entities *(include if feature involves data)*

- **Persisted health report**: The latest saved dashboard snapshot for an environment, including score, status, summary, concern items, and suggestions.
- **Fallback snapshot**: A live telemetry summary used only when no persisted report is available.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 95% of dashboard loads with stored data available, the main report renders the persisted score and summary within 5 seconds.
- **SC-002**: When a persisted report exists, 100% of dashboard views for that environment show the same score and status as the latest stored report.
- **SC-003**: In fresh or empty environments, users still see a usable fallback report on 100% of page loads.
- **SC-004**: Report exports match the on-screen report source in 100% of verified export checks.

## Assumptions

- The frontend will continue using the backend as the database gateway rather than opening `ahms.db` directly in the browser.
- Live telemetry remains available for fallback and supporting dashboard sections.
- The persisted report already contains the values needed for the main report display.
