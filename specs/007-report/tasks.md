# Tasks: 007-report

- [x] Wire `Open report` action in Health Summary to report section navigation.
- [x] Add report export controls to report preview panel.
- [x] Implement client-side timestamped PDF generation for current report snapshot.
- [x] Implement simulator JSON export download (`/api/simulator/export/json`).
- [x] Implement simulator XML export download (`/api/simulator/export/xml`).
- [x] Add UI export status messaging and per-format in-flight request guarding.
- [x] Document implemented behavior in `specs/007-report/`.
- [X] Redesign the PDF export to match the dashboard's visual layout.
- [X] Include the latest CPU and RAM telemetry snapshot in the PDF export.
- [X] Format export timestamps in a human-readable date/time style.
- [X] Add automated tests for Open report navigation and report focus behavior.
- [X] Add automated tests for PDF export content, including dashboard-style sections and human-readable timestamps.
- [X] Add automated tests for simulator JSON/XML download flows and duplicate-request/error handling.
- [X] Add a performance-oriented check for export start time against SC-002.