# Tasks: IHealth Frontend Implementation

## Goal
Build a polished React + Vite frontend demo for IMonitor that presents mocked CI and PROD health status, live metric simulation, alert investigation, report preview, and skills registry preview using enterprise styling.

## Milestones
- Scaffold the Vite + React + Tailwind project.
- Create mock data files and shared health utilities.
- Build page layout, navigation, and section anchors.
- Implement core dashboard widgets and alerts feed.
- Add live metric simulation, health score recalculation, and environment switching.
- Add alert details drawer and preview sections for reports and skills.
- Polish the UI, accessibility, and responsive styling.

---

## Phase 1: Project setup and theme

- [ ] T001 [P] Initialize Vite React project with JavaScript, Tailwind, Recharts, and Lucide React
  - Files: `package.json`, `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `index.html`, `src/main.jsx`, `src/App.jsx`, `src/index.css`
  - Acceptance: `npm install` succeeds and `npm run dev` starts without errors.
  - Dependencies: none

- [ ] T002 [P] Configure Tailwind CSS and add enterprise base styles
  - Files: `tailwind.config.js`, `src/index.css`, `src/App.jsx`
  - Acceptance: base blue primary palette, light gray background, white cards, rounded corners, subtle shadows, and Tailwind directives are set.
  - Dependencies: T001

- [ ] T003 [P] Create theme-ready UI primitives for badges, pills, and metric cards
  - Files: `src/components/ui/StatusBadge.jsx`, `src/components/ui/SeverityPill.jsx`, `src/components/ui/MetricCard.jsx`
  - Acceptance: each component renders with props and applies enterprise styling.
  - Dependencies: T002

---

## Phase 2: Mock data and utility functions

- [ ] T004 Create mock agent, alert, metric, report, and skill data files
  - Files: `src/data/mockAgents.js`, `src/data/mockAlerts.js`, `src/data/mockMetrics.js`, `src/data/mockReports.js`, `src/data/mockSkills.js`
  - Acceptance: each file exports data for CI and PROD scenarios and contains realistic demo values.
  - Dependencies: T001

- [ ] T005 Create health utility functions for score calculation and alert sorting
  - Files: `src/utils/health.js`
  - Acceptance: exports functions that calculate health score from alerts/metrics and sort alerts by severity.
  - Dependencies: T004

---

## Phase 3: Layout and navigation

- [ ] T006 Implement `PageShell.jsx` and section anchors for Dashboard, Reports, and Skills Registry
  - Files: `src/components/layout/PageShell.jsx`, `src/App.jsx`
  - Acceptance: page layout includes a main container and section anchors for top nav links.
  - Dependencies: T003

- [ ] T007 Implement `TopNav.jsx` with product name, navigation links, environment toggle, live status, and last updated timestamp
  - Files: `src/components/layout/TopNav.jsx`, `src/App.jsx`
  - Acceptance: top nav renders correctly, links scroll to sections, toggle switches CI/PROD state, and timestamp updates on environment change.
  - Dependencies: T006, T004

---

## Phase 4: Dashboard components

- [ ] T008 Implement `HealthSummary.jsx` to display overall status, score, active alerts count, environment, and plain-English summary
  - Files: `src/components/dashboard/HealthSummary.jsx`, `src/App.jsx`
  - Acceptance: component renders all required fields and updates when props change.
  - Dependencies: T005, T007

- [ ] T009 Implement `AgentCard.jsx` and `AgentGrid.jsx` for agent status cards
  - Files: `src/components/dashboard/AgentCard.jsx`, `src/components/dashboard/AgentGrid.jsx`, `src/App.jsx`
  - Acceptance: cards render each monitored resource with status, scope, latest finding, and last checked time.
  - Dependencies: T004, T008

- [ ] T010 Implement `MetricsPanel.jsx` with Recharts line charts and metric cards for CPU, memory, latency, and error rate
  - Files: `src/components/dashboard/MetricsPanel.jsx`, `src/App.jsx`
  - Acceptance: CPU and memory metrics appear in charts/cards and accept dynamic metric data.
  - Dependencies: T004, T005

- [ ] T011 Implement `AlertsFeed.jsx` to show active alerts sorted by severity
  - Files: `src/components/dashboard/AlertsFeed.jsx`, `src/App.jsx`
  - Acceptance: feed displays severity, title, environment, agent, resource, timestamp, and summary; alerts are sorted by severity.
  - Dependencies: T004, T005

- [ ] T012 Integrate dashboard components into `App.jsx` and render the section layout
  - Files: `src/App.jsx`, `src/components/dashboard/HealthSummary.jsx`, `src/components/dashboard/AgentGrid.jsx`, `src/components/dashboard/MetricsPanel.jsx`, `src/components/dashboard/AlertsFeed.jsx`
  - Acceptance: the Dashboard section renders all core widgets using mock data.
  - Dependencies: T008, T009, T010, T011

---

## Phase 5: Metrics simulation

- [ ] T013 Implement live metric simulation with `useEffect` interval updates
  - Files: `src/App.jsx`, `src/utils/healthUtils.js`
  - Acceptance: metrics update every few seconds and can rise toward a critical threshold in PROD.
  - Dependencies: T010, T005

- [ ] T014 Recalculate health score and active alert state based on environment and metrics
  - Files: `src/App.jsx`, `src/utils/healthUtils.js`
  - Acceptance: switching environments or metric updates changes the health score and reflected status.
  - Dependencies: T013

---

## Phase 6: Alerts and alert drawer

- [ ] T015 Implement `AlertDetailsDrawer.jsx` with title, severity, resource, reasoning, suggested actions, related skill, confidence, and status
  - Files: `src/components/dashboard/AlertDetailsDrawer.jsx`, `src/App.jsx`
  - Acceptance: drawer opens and closes cleanly and displays the selected alert details.
  - Dependencies: T011

- [ ] T016 Connect `AlertsFeed.jsx` alert clicks to open the alert details drawer in `App.jsx`
  - Files: `src/App.jsx`, `src/components/dashboard/AlertsFeed.jsx`, `src/components/dashboard/AlertDetailsDrawer.jsx`
  - Acceptance: clicking an alert opens the drawer with the selected alert; closing the drawer clears selection.
  - Dependencies: T015

---

## Phase 7: Reports and skills preview

- [ ] T017 Implement `ReportPreview.jsx` to show latest report score, result, summary, concerns, and improvements by environment
  - Files: `src/components/dashboard/ReportPreview.jsx`, `src/App.jsx`, `src/data/mockReports.js`
  - Acceptance: report preview updates when CI/PROD is toggled and renders required fields.
  - Dependencies: T004, T012

- [ ] T018 Implement `SkillCard.jsx` and `SkillsRegistry.jsx` for the skills registry preview
  - Files: `src/components/skills/SkillCard.jsx`, `src/components/skills/SkillsRegistry.jsx`, `src/App.jsx`, `src/data/mockSkills.js`
  - Acceptance: skills preview displays skills related to active alerts and updates with environment changes.
  - Dependencies: T004, T012

---

## Phase 8: Polish, accessibility, and responsive cleanup

- [ ] T019 Polish styling, spacing, colors, and responsive layout across all sections
  - Files: `src/App.jsx`, `src/index.css`, all component files under `src/components`
  - Acceptance: layout is responsive on desktop and tablet widths, spacing is consistent, and design matches enterprise styling.
  - Dependencies: T012, T013, T016, T018

- [ ] T020 Add accessibility labels, keyboard interaction support, and screen-reader-friendly markup
  - Files: `src/components/layout/TopNav.jsx`, `src/components/dashboard/AlertsFeed.jsx`, `src/components/dashboard/AlertDetailsDrawer.jsx`, `src/components/skills/SkillsRegistry.jsx`
  - Acceptance: navigation links have accessible labels, buttons are keyboard focusable, and drawer markup includes proper ARIA roles.
  - Dependencies: T007, T015, T018

- [ ] T021 Add automated tests for health score calculation and alert drawer interaction
  - Files: `src/utils/health.js`, `src/components/dashboard/AlertDetailsDrawer.jsx`, `src/__tests__/health.test.jsx`, `src/__tests__/AlertDetailsDrawer.test.jsx`
  - Acceptance: automated tests run with `npm test` and verify health score recalculation plus drawer open/close behavior.
  - Dependencies: T005, T015, T020

- [ ] T022 Validate the app build and document how to run the demo
  - Files: `README.md`, `package.json`, `src/App.jsx`
  - Acceptance: `npm run build` succeeds and README includes `npm install` / `npm run dev` instructions.
  - Dependencies: T001, T012, T019

---

## Rationale for Ordering

The tasks are ordered to establish the base project and theme first, then create the mock data and utilities needed for the feature flow. Layout and navigation are built next so dashboard components have a stable structure to mount into. Core dashboard widgets are implemented before live simulation and the alert drawer, ensuring the UI is functional before adding behavior. The preview sections are added afterward, and final polish is reserved until all core interactions are in place.
