# Implementation Plan: 007-report

## Objective

Enable report exports directly from the dashboard workflow by wiring **Open report** to the report section and adding timestamped export actions for PDF, simulator JSON, and simulator XML.

## Scope Delivered

1. Health Summary `Open report` now triggers scroll + focus to `#reports`.
2. Report Preview includes export controls for:
   - Download PDF (client-generated current report snapshot)
   - Download JSON (from `/api/simulator/export/json`)
   - Download XML (from `/api/simulator/export/xml`)
3. Export feedback is surfaced in UI with loading/success/error states.
4. Duplicate concurrent export requests are blocked per format.
5. PDF export should read like the dashboard, with clear sections, recent CPU/RAM telemetry, and readable timestamps.
6. Add automated tests for report navigation, export downloads, timestamp formatting, and duplicate-request/error handling.

## Key Technical Notes

- `src/App.jsx` owns report export state and handlers.
- `src/components/dashboard/HealthSummary.jsx` accepts `onOpenReport`.
- `src/components/dashboard/ReportPreview.jsx` accepts export handlers and status.
- `src/utils/api.js` now exports `API_BASE` for consistent endpoint construction.
- Filenames are timestamped as `YYYYMMDD-HHmmss` and include environment context.