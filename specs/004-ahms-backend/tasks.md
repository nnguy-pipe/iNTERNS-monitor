# Tasks: Dynamic Dashboard Health Score Calculation Verification & Fix

**Feature**: Verify and fix end-to-end health score calculation pipeline from simulator/dummy server → backend ingestion → reasoning engine → database → frontend display

**Status**: Verification & Fix Phase

**Specification**: `specs/004-ahms-backend/spec.md`

**Plan**: `specs/004-ahms-backend/plan.md`

---

## Overview

The dashboard health score currently appears static and does not update when dummy server or simulator metrics change. This task list focuses on:

1. **Verification**: Confirm backend ingestion, reasoning, and reporting are working
2. **Diagnosis**: Identify where the pipeline breaks (ingestion, reasoning, persistence, or frontend fetch)
3. **Fix**: Ensure the health score is dynamically calculated and displayed

**Expected Data Flow**:
```
Dummy server / simulator metrics
        ↓
Backend POST /api/events (ingestion)
        ↓
Normalization pipeline
        ↓
ReasoningEngine.compute_health_score(...)
        ↓
Health report persisted in database
        ↓
Frontend GET /api/reports/latest
        ↓
Dashboard displays updated score
```

---

## Phase 1: Verification & Instrumentation

**Purpose**: Verify each stage of the pipeline is being called and producing output

**Success Criteria**: All stages log their outputs and can be traced end-to-end

### Logging & Tracing

- [x] T001 Add debug logging to `src/services/ingest.py` to log all received events with timestamp and metrics count
- [x] T002 Add debug logging to `src/services/normalize.py` to log normalized metrics, including source, type, and values
- [x] T003 Add debug logging to `src/services/reasoning.py` to log health score computation with inputs and final score
- [x] T004 Add debug logging to `src/api/routes.py` to log all `/api/reports/latest` requests and returned scores
- [x] T005 [P] Create verification script `tests/verification/verify_pipeline.py` to trace a single metric through all stages

### Ingestion Verification

- [x] T006 [P] Write unit test in `tests/unit/test_ingest.py` to verify `POST /api/events` accepts dummy server payload and stores it
- [x] T007 [P] Write unit test in `tests/unit/test_ingest.py` to verify simulator metrics are extracted and persisted with correct timestamps
- [ ] T008 Implement `GET /api/events/latest` endpoint in `src/api/routes.py` to expose last 10 ingested events (for verification)
- [x] T009 [P] Verify dummy server is actually sending metrics to backend (check network logs, backend logs)

### Normalization Verification

- [x] T010 [P] Write unit test in `tests/unit/test_normalize.py` to verify simulator metrics are normalized to backend model
- [x] T011 [P] Write unit test in `tests/unit/test_normalize.py` to verify lineage and source tags are applied
- [ ] T012 Implement `GET /api/normalized-events` endpoint in `src/api/routes.py` to expose recent normalized records (for verification)
- [x] T013 Manually run normalization against sample simulator payload and verify output structure

### Reasoning Engine Verification

- [x] T014 [P] Write unit test in `tests/unit/test_reasoning.py` to verify `compute_health_score()` is called with normalized metrics
- [x] T015 [P] Write unit test in `tests/unit/test_reasoning.py` to verify health score changes when metric values change
- [x] T016 [P] Write unit test in `tests/unit/test_reasoning.py` to verify primary issue is identified and reasoning is separated
- [x] T017 Create minimal standalone test in `tests/verification/test_reasoning_standalone.py` to call reasoning engine directly with mock metrics
- [x] T018 [P] Ensure reasoning engine is deterministic for the same input (same metrics → same score)

### Persistence Verification

- [x] T019 [P] Write unit test in `tests/unit/test_persistence.py` to verify health reports are persisted to database
- [x] T020 [P] Write unit test in `tests/unit/test_persistence.py` to verify latest report can be retrieved
- [ ] T021 Create query script `tests/verification/query_db.py` to manually inspect database tables and confirm reports exist
- [x] T022 [P] Ensure no mock data is hardcoded in `src/services/persistence.py` or `src/models/health_report.py`

### Frontend Fetch Verification

- [x] T023 [P] Verify `GET /api/reports/latest` endpoint returns actual database data, not mock
- [x] T024 [P] Add response logging to `src/api/routes.py` to log health score returned to frontend
- [ ] T025 Implement `GET /api/reports/history?limit=20` endpoint to view last N health reports
- [x] T026 [P] Write integration test in `tests/integration/test_reports.py` to verify frontend can fetch latest report

---

## Phase 2: Diagnosis & Root Cause Analysis

**Purpose**: Identify which stage of the pipeline is failing or producing stale data

**Success Criteria**: Clear documentation of where the pipeline breaks

### Metrics Collection & Inspection

- [x] T027 Run verification script T005 against live simulator and document output at each stage
- [x] T028 Check backend logs to confirm ingestion endpoint is being called (use `tail -f` on log file)
- [x] T029 Query database directly to confirm events table has recent records with current timestamps
- [x] T030 Query database to confirm health_report table has recent entries that differ from each other
- [x] T031 [P] Manually call `GET /api/reports/latest` and compare timestamp with current time (should be recent)

### Identify Mock/Fallback Data Usage

- [ ] T032 Search frontend code for hardcoded health scores or mock report data in `src/data/mockReports.js`
- [ ] T033 Verify frontend fetch logic in `src/utils/api.js` is actually calling backend, not returning cached mock
- [ ] T034 Check if `HealthSummary.jsx` or other dashboard components are using mock data as primary source
- [ ] T035 [P] Search backend for any hardcoded fallback health scores that might be returned when ingestion is empty
- [ ] T036 [P] Verify no stale cached data is being returned from previous request (check response headers)

### Timing & Frequency Issues

- [ ] T037 Check if health score computation frequency matches simulator metric generation frequency
- [ ] T038 [P] Verify frontend refresh rate vs backend update rate (is frontend polling too infrequently?)
- [ ] T039 Ensure simulator/dummy server is actually running and sending metrics (not just accepting connections)
- [ ] T040 [P] Check if there's a database transaction isolation issue preventing fresh reads

### Data Flow Inspection

- [x] T041 Add breakpoint or print statement in reasoning engine and manually trigger a health score computation
- [x] T042 Manually insert test metrics into database and trigger `GET /api/reports/latest` to see if score changes
- [x] T043 [P] Trace one metric payload from dummy server through ALL logs: ingest, normalize, reason, persist, fetch
- [ ] T044 Create end-to-end trace document: `specs/004-ahms-backend/TRACE_LOG.md` recording each stage's inputs/outputs

---

## Phase 3: Fix & Implementation

**Purpose**: Fix identified issues and ensure health score is always fresh and backend-authoritative

**Success Criteria**: Health score updates dynamically when metrics change; no mock or stale data

### Backend Fixes

#### Ingestion Pipeline

- [x] T045 [US1] Ensure `POST /api/events` endpoint is enabled and accepts metrics from simulator
- [x] T046 [US1] Verify ingestion handler in `src/services/ingest.py` commits transactions immediately (no buffering)
- [x] T047 [US1] Implement request validation to reject malformed payloads with clear error messages
- [ ] T048 [US1] Add timestamp normalization so all ingested events use backend server time, not client time

#### Normalization & Persistence

- [x] T049 [US1] Ensure normalized records are committed to database within seconds of ingestion (check transaction log)
- [ ] T050 [US1] Implement deduplication logic to prevent duplicate metrics from inflating health scores
- [ ] T051 [US1] Add index on event timestamp to ensure fast retrieval of recent events
- [ ] T052 [US1] [P] Verify no in-memory cache is stalling updates (if cache exists, implement TTL or invalidation)

#### Reasoning Engine

- [x] T053 [US2] Ensure `compute_health_score()` is called on EVERY new ingestion event, not just periodically
- [x] T054 [US2] Verify reasoning engine uses latest normalized metrics, not cached or older versions
- [ ] T055 [US2] Implement result caching with very short TTL (e.g., 5 seconds) to avoid redundant computation
- [x] T056 [US2] Ensure health report generation timestamp matches computation time (not stale)
- [x] T057 [US2] Add validation that health score is always recalculated from current data, never returned from fallback

#### Reporting & Frontend API

- [x] T058 [US2] Implement `GET /api/reports/latest` to return most recent health report with computed timestamp
- [ ] T059 [US2] Add `X-Report-Age` header to response showing how fresh the report is (e.g., "5 seconds old")
- [ ] T060 [US2] Ensure no mock data is ever returned from `/api/reports/latest` (raise error if no data available)
- [ ] T061 [US2] Implement `GET /api/health/status` to show pipeline health (ingestion working? reasoning running? DB up?)

#### Audit & Debugging Endpoints

- [ ] T062 [US2] Implement `GET /api/debug/last-report` returning full health report JSON with all fields
- [ ] T063 [US2] Implement `GET /api/debug/event-count` returning count of events in last 1/5/10 minutes
- [ ] T064 [US2] Implement `GET /api/debug/reasoning-trace` returning the reasoning chain that led to current score

### Frontend Fixes

#### Data Fetching

- [ ] T065 [P] Update `src/utils/api.js` to ensure `getHealthReport()` always fetches fresh data, not cached
- [ ] T066 [P] Remove any mock report data from being used as primary source in `HealthSummary.jsx`
- [ ] T067 [P] Implement fallback to mock only when backend returns 5xx error or connection fails
- [ ] T068 [P] Add response validation to reject stale reports (older than 1 minute)

#### Display & Refresh

- [ ] T069 [P] Ensure dashboard health score is fetched every 10 seconds (or user-configurable)
- [ ] T070 [P] Add visual indicator in `HealthSummary.jsx` showing when score was last updated
- [ ] T071 [P] Implement smooth transition animation when health score changes
- [ ] T072 [P] Add debug mode to `src/utils/api.js` that logs all backend responses to console

#### Error Handling

- [ ] T073 [P] Implement retry logic for failed backend fetches with exponential backoff
- [ ] T074 [P] Display clear error message if backend health score cannot be fetched
- [ ] T075 [P] Add fallback to agent card metrics if health report fetch fails (not mock data)

---

## Phase 4: Integration Testing & Validation

**Purpose**: Verify end-to-end pipeline works with real simulator data

**Success Criteria**: Health score updates within 2 seconds of simulator metric change

### End-to-End Tests

- [ ] T076 [P] Write integration test in `tests/integration/test_e2e_health_score.py` that:
  - Starts backend server
  - Sends test metrics via `POST /api/events`
  - Calls `GET /api/reports/latest`
  - Verifies score changed from baseline
  
- [ ] T077 [P] Write integration test that sends 5 different metric payloads and verifies score changes each time

- [ ] T078 [US2] Write test that verifies health score determinism (same metrics → same score)

- [ ] T079 [US2] Write test that verifies health report persistence (report can be retrieved from database)

### Live System Tests

- [ ] T080 Start backend server: `python3 -m uvicorn src.api.main:app --reload`
- [ ] T081 Start simulator or dummy server and verify it's sending metrics
- [ ] T082 Manually call backend endpoints and record responses:
  - `GET /api/health` (should show all systems green)
  - `GET /api/reports/latest` (should show recent report)
  - `GET /api/debug/last-report` (should show detailed report)
  
- [ ] T083 Check logs for any errors or warnings related to ingestion or reasoning

- [ ] T084 [P] Monitor backend CPU and memory usage while simulator sends metrics (should be stable)

### Frontend Validation

- [ ] T085 Start frontend: `npm run dev`
- [ ] T086 Open dashboard and note current health score and timestamp
- [ ] T087 Wait 10 seconds and verify health score updates (even if value stays same, timestamp should change)
- [ ] T088 Stop simulator and verify dashboard eventually shows degraded health (within 30 seconds)
- [ ] T089 Restart simulator and verify dashboard recovers to healthy state within 30 seconds
- [ ] T090 [P] Check browser console for any errors or warnings

---

## Phase 5: Documentation & Hardening

**Purpose**: Document the health score flow and add safeguards against regression

**Success Criteria**: Architecture documented; safeguards in place

### Documentation

- [ ] T091 Create `specs/004-ahms-backend/HEALTH_SCORE_FLOW.md` documenting the complete end-to-end flow with diagrams
- [ ] T092 Add comments to `src/services/reasoning.py` explaining the health score algorithm and key decision points
- [ ] T093 Document all new debugging endpoints in `specs/004-ahms-backend/DEBUG_ENDPOINTS.md`
- [ ] T094 Create troubleshooting guide: `specs/004-ahms-backend/TROUBLESHOOTING_HEALTH_SCORE.md`
- [ ] T095 [P] Add architecture decision record: `specs/004-ahms-backend/adr/ADR-001-HEALTH_SCORE_FRESHNESS.md`

### Safeguards & Regression Prevention

- [ ] T096 [P] Add assertion in `src/services/reasoning.py` that health score is never stale (timestamp check)
- [ ] T097 [P] Add assertion in `src/api/routes.py` that reported data always comes from database, not memory
- [ ] T098 [P] Implement health check that fails if ingestion pipeline hasn't processed events in last 5 minutes
- [ ] T099 [P] Add CI test that verifies end-to-end pipeline completes in < 2 seconds
- [ ] T100 Create `tests/integration/test_regression_stale_scores.py` to prevent health score staleness regression

### Monitoring & Alerting

- [ ] T101 Add Prometheus metric for "health score age" (how fresh is current report?)
- [ ] T102 Add Prometheus metric for "events processed per minute" to detect ingestion slowdown
- [ ] T103 Add Prometheus metric for "reasoning computation time" to detect performance degradation
- [ ] T104 [P] Document alerting thresholds in `specs/004-ahms-backend/MONITORING.md`

---

## Phase 6: Polish & Documentation Completion

**Purpose**: Final validation and cleanup

**Success Criteria**: All tasks complete; documentation updated; no regressions

### Final Validation

- [ ] T105 Run full test suite: `pytest tests/ -v` (should pass 100%)
- [ ] T106 Run integration tests specifically: `pytest tests/integration/ -v`
- [ ] T107 Run verification script against live system: `python tests/verification/verify_pipeline.py`
- [ ] T108 Manually verify dashboard health score updates 5 consecutive times

### Code Quality

- [ ] T109 Format code: `black src/ tests/`
- [ ] T110 Lint code: `flake8 src/ tests/`
- [ ] T111 Type check: `mypy src/ --ignore-missing-imports`
- [ ] T112 [P] Remove debug logging statements (or make them debug-level only)

### Final Documentation

- [ ] T113 Update `BACKEND_README.md` with health score flow overview
- [ ] T114 Update main `README.md` with links to health score documentation
- [ ] T115 Create `CHANGELOG.md` entry for this verification and fix phase
- [ ] T116 [P] Verify all new endpoints are documented in `specs/004-ahms-backend/contracts/`

---

## Dependencies & Execution Strategy

### Critical Path

```
T001-T004 (add logging)
    ↓
T006-T009 (verify ingestion)
    ↓
T010-T013 (verify normalization)
    ↓
T014-T018 (verify reasoning)
    ↓
T019-T022 (verify persistence)
    ↓
T045-T064 (implement fixes)
    ↓
T076-T090 (integration testing)
    ↓
T105-T116 (polish & documentation)
```

### Parallel Opportunities

Tasks marked `[P]` can run in parallel:
- **Logging phase**: T001-T004 all parallelizable
- **Unit tests**: T006-T007, T010-T011, T014-T016, T019-T020 can run in parallel
- **Fixes**: T045-T064 mostly independent per subsystem (ingestion, normalization, reasoning, reporting, frontend)
- **Integration tests**: T076-T079 can run in parallel
- **Documentation**: T091-T104 mostly parallelizable

### MVP Scope (Minimum Viable Fix)

For quick validation of the core issue:
1. T001-T005 (add logging and create verification script)
2. T006-T009 (verify ingestion endpoint is working)
3. T014-T018 (verify reasoning engine is being called)
4. T027-T030 (run diagnostics and inspect database)
5. T045-T061 (implement core backend fixes)
6. T076-T084 (end-to-end testing)

**Estimated MVP Time**: 4-6 hours

### Full Implementation

Complete all phases for production-ready health score pipeline.

**Estimated Full Time**: 24-32 hours

---

## Success Criteria Checklist

- [ ] Backend ingestion endpoint receives metrics from simulator/dummy server within 1 second
- [ ] Normalized metrics are persisted to database within 1 second of ingestion
- [ ] Reasoning engine computes health score within 500ms of receiving metrics
- [ ] Health report is persisted to database with current timestamp
- [ ] Frontend fetches latest report via `GET /api/reports/latest`
- [ ] Dashboard displays health score with update timestamp
- [ ] Health score changes within 2 seconds of simulator metric change
- [ ] No mock or stale data is used as primary source
- [ ] All new endpoints have debug/verification capability
- [ ] End-to-end pipeline is documented and tested
- [ ] CI passes 100% of tests including new regression tests

---

## Testing Strategy

**Unit Tests** (Phase 1-2): Isolated component testing for ingestion, normalization, reasoning, persistence

**Integration Tests** (Phase 4): Full pipeline from ingestion → reasoning → reporting

**Live System Tests** (Phase 4): Real simulator metrics flowing through real backend and frontend

**Regression Tests** (Phase 5): Prevent health score staleness from happening again

**Performance Tests** (Phase 5): Verify < 2 second end-to-end latency for health score updates

