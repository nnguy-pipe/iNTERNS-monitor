# Feature Specification: Report Export and Download Controls

**Feature Branch**: `007-report-export-controls`  
**Created**: 2026-06-10  
**Status**: Implemented  
**Input**: User description: "Open report downloads timestamped PDF of current report and simulator XML/JSON exports."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open report from dashboard and export (Priority: P1)

As a dashboard user, I can use the **Open report** control in Health Summary to open the report and immediately export the current report view.

**Why this priority**: Enables core report workflow from the existing command center CTA.

**Independent Test**: Click **Open report** and verify report section opens and export actions are visible.

**Acceptance Scenarios**:

1. **Given** the dashboard has a current report, **When** the user clicks **Open report**, **Then** the report section is scrolled into view and focused.
2. **Given** the report is open, **When** export is triggered, **Then** a PDF file is downloaded containing the current report snapshot and timestamp.

---

### User Story 2 - Download simulator exports from report controls (Priority: P1)

As a dashboard user, I can download the current simulator XML and JSON exports from the report controls.

**Why this priority**: Required for operations handoff and offline diagnostics.

**Independent Test**: Trigger each download and validate files are delivered with current simulator content.

**Acceptance Scenarios**:

1. **Given** simulator export APIs are available, **When** user clicks **Download JSON**, **Then** the browser downloads a `.json` file from current simulator export.
2. **Given** simulator export APIs are available, **When** user clicks **Download XML**, **Then** the browser downloads a `.xml` file from current simulator export.

---

### User Story 3 - Time-stamped report artifacts (Priority: P2)

As a user exporting artifacts, I get time-stamped filenames so reports are traceable.

**Why this priority**: Improves auditability and avoids overwrite confusion.

**Independent Test**: Perform exports twice and confirm filenames include timestamp and are unique.

**Acceptance Scenarios**:

1. **Given** the user exports any artifact, **When** download starts, **Then** filename includes environment and timestamp.
2. **Given** two exports happen at different times, **When** files are saved, **Then** names are distinct.

## Edge Cases

- Simulator API unavailable: show clear failure feedback and do not trigger empty download.
- Export endpoint returns malformed payload: block download and surface error.
- Rapid repeated clicks: avoid duplicate in-flight requests for same artifact.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Health Summary **Open report** control MUST navigate/scroll/focus to the report section and expose export actions.
- **FR-002**: The dashboard MUST support downloading a timestamped PDF artifact of the current report state from the UI.
- **FR-003**: The dashboard MUST support downloading current simulator JSON export using `/api/simulator/export/json`.
- **FR-004**: The dashboard MUST support downloading current simulator XML export using `/api/simulator/export/xml`.
- **FR-005**: All exported files MUST include timestamped filenames with environment context.
- **FR-006**: The UI MUST provide visible success/failure state for each export attempt.
- **FR-007**: Export actions MUST prevent duplicate concurrent requests per format.

### Key Entities

- **Report Artifact**: A downloadable file representing current report state (PDF/JSON/XML) plus metadata (format, timestamp, environment).
- **Export Job State**: UI state for each format (idle, loading, success, error) used to control button status and feedback.

## Assumptions

- Current report data is available in frontend state (health score, result, summary, concerns, improvements).
- A client-side PDF artifact can be generated without backend rendering.
- Simulator export endpoints return current snapshot at request time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of **Open report** clicks move users to report section in a single interaction.
- **SC-002**: 95% of successful export actions start a file download in under 3 seconds on a healthy local environment.
- **SC-003**: 100% of exported filenames include timestamp and environment tag.
- **SC-004**: 0 empty-file downloads occur when simulator export endpoints return errors.