# Implementation Plan: IHealth Frontend

## Problem Statement

Create a polished frontend demo for IMonitor that presents CI and production system health in a single-page, enterprise-style dashboard. The app should feel realistic with live metric simulation, agent intelligence, alert investigation, and environment-specific mocked states.

## Goals

- Build a React + Vite frontend using JavaScript, Tailwind CSS, Recharts, and Lucide React.
- Implement a mostly single-page layout with Dashboard, Reports, and Skills Registry sections.
- Provide a CI / PROD toggle that swaps between two mocked state profiles.
- Simulate live CPU, memory, latency, and error rate metrics.
- Recalculate the health score and active alerts when data changes.
- Show an alerts feed sorted by severity and open an alert details drawer on click.
- Display a report preview and a skills registry preview tied to active alerts.
- Apply an iPipeline-inspired enterprise visual theme with accessible labels.

## Non-Goals

- No authentication.
- No backend integration or real API calls.
- No complex routing; section links may scroll to page anchors.
- No global state library such as Redux or MobX.
- No TypeScript.
- No production-grade backend services or CI integration.

## Architecture

Use a simple component-based React app:

- `src/main.jsx` — app entry point.
- `src/App.jsx` — top-level state and environment toggle.
- `src/components/layout/TopNav.jsx` — product name, nav links, environment toggle, live status, timestamp.
- `src/components/layout/PageShell.jsx` — layout container, spacing, section anchors.
- `src/components/dashboard/HealthSummary.jsx` — status badge, score, alert count, summary.
- `src/components/dashboard/AgentCard.jsx` — individual agent status card.
- `src/components/dashboard/AgentGrid.jsx` — grid of agents.
- `src/components/dashboard/MetricsPanel.jsx` — charts and metric cards using Recharts.
- `src/components/dashboard/AlertsFeed.jsx` — severity-sorted alert list.
- `src/components/dashboard/AlertDetailsDrawer.jsx` — slide-over drawer with alert reasoning and actions.
- `src/components/dashboard/ReportPreview.jsx` — latest report card.
- `src/components/skills/SkillCard.jsx` — skill preview card.
- `src/components/skills/SkillsRegistry.jsx` — skills registry section.
- `src/components/ui/StatusBadge.jsx`, `SeverityPill.jsx`, `MetricCard.jsx`, `SectionHeader.jsx` — reusable UI elements.

State is managed in `App.jsx` with React `useState` and `useEffect`:

- `environment` — `CI` or `PROD`.
- `mockData` — selected from the environment-specific mock files.
- `metrics` — updated on an interval.
- `selectedAlert` — currently open alert in the drawer.

## Data Model

Use mock JavaScript files that export arrays/objects:

- `src/data/mockAgents.js`
  - `name`, `scope`, `status`, `latestFinding`, `lastChecked`, `confidenceScore`
- `src/data/mockAlerts.js`
  - `severity`, `title`, `environment`, `sourceAgent`, `affectedResource`, `timestamp`, `summary`, `reasoning`, `suggestedActions`, `relatedSkill`, `status`
- `src/data/mockMetrics.js`
  - time-series for `cpuUsage`, `memoryUsage`, `apiLatency`, `errorRate`
- `src/data/mockReports.js`
  - `healthScore`, `result`, `summary`, `areasOfConcern`, `suggestedImprovements`
- `src/data/mockSkills.js`
  - `name`, `description`, `category`, `relatedAlerts`

The environment toggle selects the appropriate mock dataset and determines the health summary state.

## API Surface

No external API surface is required. Expose a clean internal component props interface:

- `TopNav` props: `{ environment, onToggleEnvironment, liveStatus, lastUpdated }`
- `HealthSummary` props: `{ status, score, alertCount, environment, summary }`
- `AgentGrid` props: `{ agents }`
- `MetricsPanel` props: `{ metrics }`
- `AlertsFeed` props: `{ alerts, onSelectAlert }`
- `AlertDetailsDrawer` props: `{ alert, isOpen, onClose }`
- `ReportPreview` props: `{ report }`
- `SkillsRegistry` props: `{ skills }`
- `SkillCard` props: `{ skill }`
- `StatusBadge` and `SeverityPill` props: `{ value, level }`
- `MetricCard` props: `{ label, value, trend }`

## Milestones

1. Scaffold the Vite React project and install Tailwind, Recharts, Lucide React.
2. Build layout components: `PageShell`, `TopNav`, and section anchors.
3. Create mock data modules for CI and PROD states.
4. Implement `HealthSummary`, `AgentGrid`, `MetricsPanel`, and `AlertsFeed`.
5. Add environment toggle behavior and mocked state switching.
6. Implement metric simulation with `useEffect` interval updates.
7. Add `AlertDetailsDrawer` with the click-to-open interaction.
8. Add `ReportPreview` and `SkillsRegistry` sections.
9. Polish styling, spacing, responsive layout, and accessibility labels.
10. Validate with build and manual UI checks.

## Success Criteria

- `App.jsx` loads with mock CI state by default and supports PROD toggle.
- The top nav shows environment state, live status, and last updated timestamp.
- Health summary displays status, score, alert count, selected environment, and plain-English summary.
- At least one alert opens the details drawer when clicked.
- Metrics update periodically and reflect rising CPU/memory values in the PROD scenario.
- Alerts remain sorted by severity and update the health score when active.
- Report preview and skills registry are visible and change with the selected environment.
- UI uses a blue enterprise theme, white cards, gray background, rounded corners, and subtle shadows.
- The app builds successfully with Vite.

## Validation Commands

Once scaffolded, use:

- `npm install`
- `npm run dev`
- `npm run build`

Manual validation:

- View the page in the browser and toggle CI / PROD.
- Click an alert and verify the details drawer opens.
- Confirm metrics update every few seconds and a critical memory alert appears in PROD.
