# Feature Specification: Live Alerts and Health Score

## Overview

Replace the static alert feed with alerts generated from the live subsystem telemetry already loaded in `App.jsx`. The dashboard should surface CPU, RAM, and active user pressure per subsystem, then combine those values into one overall health score so users can quickly understand the current operating state.

## User Scenarios

1. An operator opens the dashboard and sees alerts only when one or more subsystems exceed safe CPU, RAM, or user thresholds.
2. An operator clicks an alert and can inspect the affected subsystem, what triggered the alert, and what to do next.
3. An operator reviews the health summary and sees a single score that reflects the combined live telemetry across all subsystems.
4. When subsystem telemetry returns to safe ranges, active alerts disappear and the health summary improves automatically.

## Functional Requirements

1. Alerts must be derived from the current subsystem telemetry already available in the app.
2. Alerts must use live CPU, RAM, and active user values from each subsystem, not mock alert fixtures.
3. Each generated alert must include a severity, title, summary, reasoning, suggested actions, source subsystem, and affected resource.
4. A subsystem must produce an alert when any monitored metric crosses the warning threshold.
5. A subsystem must produce a critical alert when any monitored metric crosses the critical threshold.
6. The dashboard must calculate an overall health score from the same live CPU, RAM, and active user values.
7. The health summary must map the score and current alerts to a clear status such as Healthy, Degraded, or Critical.
8. The report card must reflect the live health score and the current areas of concern.
9. Alert details must stay in sync with the selected live alert.

## Alert and Score Rules

- CPU warning threshold: 75%
- CPU critical threshold: 90%
- RAM warning threshold: 3500 MB
- RAM critical threshold: 6000 MB
- Active user warning threshold: 250
- Active user critical threshold: 600
- Health score weighting: CPU 45%, RAM 35%, users 20%

## Assumptions

- Subsystem telemetry is already fetched into `App.jsx` and is the source of truth for alerts.
- Alert generation is per subsystem, with the highest-severity metric driving the alert severity.
- A subsystem with no threshold breaches produces no alert.
- The report card should summarize the same live health snapshot used by the summary and alerts.

## Success Criteria

1. Users see alerts update within one polling cycle after subsystem values change.
2. The health score always falls between 0 and 100.
3. The alert feed shows no mock-only alert content.
4. At least one alert appears whenever a subsystem exceeds a defined warning threshold.
5. The report and health summary match the same live telemetry snapshot.