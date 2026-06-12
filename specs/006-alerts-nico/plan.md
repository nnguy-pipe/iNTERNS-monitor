# Implementation Plan: Live Alerts and Health Scoring

## Goal

Move the alert experience off static mock data and onto the subsystem telemetry already loaded in `App.jsx`.

## Approach

1. Add shared helpers that turn subsystem CPU, RAM, and active user values into alert objects and a health score.
2. Update `App.jsx` to use those derived values for the alert feed, report preview, and health summary.
3. Keep the existing dashboard layout and detail drawer behavior intact.
4. Document the alert rules and assumptions in the feature spec.

## Risks

- Alert thresholds that are too aggressive could create noise.
- A score formula that is too harsh could make the dashboard feel permanently degraded.
- Live data updates should not clear the selected alert unless that alert is no longer active.

## Validation

- Confirm the app builds after removing the mock alert dependency.
- Confirm the health summary, report preview, and alert feed all reflect the same live telemetry snapshot.