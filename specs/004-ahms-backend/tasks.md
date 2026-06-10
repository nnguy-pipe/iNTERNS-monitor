# Tasks for AHMS Backend (specs/004-ahms-backend)

## Phase 1: Setup

- [ ] T001 Create Python project scaffold and directory layout at `src/` and `tests/`
- [ ] T002 Add `requirements.txt` and `requirements-dev.txt` with FastAPI, SQLAlchemy, Pydantic, Uvicorn, pytest
- [ ] T003 Initialize a minimal FastAPI app in `src/api/main.py` with `/health` endpoint
- [ ] T004 Add database initialization and SQLite configuration in `src/store/sqlite.py`
- [ ] T005 Add CI workflow stub in `.github/workflows/ci.yml` to run tests

## Phase 2: Foundational

- [ ] T006 [P] Define data models: `src/models/ci_event.py`, `src/models/health_report.py`, `src/models/suggestion.py`
- [ ] T007 Implement persistence layer `src/services/persistence.py` and migrations plan (Alembic)
- [ ] T008 Create API routes shell `src/api/routes.py` for events, reports, hooks
- [ ] T009 Add logging, config management, and basic telemetry ingestion harness `src/services/ingest.py`

## Phase 3: [US1] Ingestion & Normalization (Priority: P1)

- [ ] T010 [US1] Implement `POST /api/events` ingestion endpoint in `src/api/routes.py` and handler in `src/services/ingest.py`
- [ ] T011 [US1] Implement normalization pipeline for metrics/logs/traces/events in `src/services/normalize.py`
- [ ] T012 [US1] Persist normalized records to ledger in `src/services/persistence.py`
- [ ] T013 [US1] Implement schema validation and lineage tagging in `src/services/normalize.py`
- [ ] T014 [P] [US1] Add unit tests for ingestion and normalization in `tests/unit/test_ingest.py`

## Phase 4: [US2] Agentic Reasoning & Detection (Priority: P2)

- [ ] T015 [US2] Prototype reasoning engine in `src/services/reasoning.py` that returns: objective issue, reasoning, suggestions, confidence
- [ ] T016 [US2] Implement correlation engine `src/services/correlation.py` to link events across sources
- [ ] T017 [US2] Implement anomaly detectors in `src/services/anomaly.py` (statistical + rule-based hooks)
- [ ] T018 [US2] Integrate reasoning outputs into health reports and persist in `src/models/health_report.py`
- [ ] T019 [US2] Add tests for reasoning, correlation, and anomaly detection in `tests/unit/`

## Phase 5: [US3] Orchestration, Governance & CI Verdicts (Priority: P3)

- [ ] T020 [US3] Implement action orchestration skeleton in `src/services/orchestrator.py` (approve/execute/rollback)
- [ ] T021 [US3] Implement governance rules and approvals storage in `src/services/governance.py`
- [ ] T022 [US3] Implement audit ledger writes for all decisions in `src/services/audit.py`
- [ ] T023 [US3] Expose CI evaluation API `POST /api/ci/evaluate` in `src/api/routes.py` returning `pass|warn|fail` with machine-readable rationale
- [ ] T024 [P] [US3] Add integration tests for orchestration and CI evaluation in `tests/integration/`

## Final Phase: Polish & Handoff

- [ ] T025 Create `specs/004-ahms-backend/contracts/report-api.md` hook contract and ensure routes are documented
- [ ] T026 Write `specs/004-ahms-backend/quickstart.md` with run instructions and example CI call
- [ ] T027 Security review and add SAST/secret-scan to CI

## Dependencies

- Phases 3 depends on Phases 1 and 2 completion.
- Phase 4 depends on Phase 3 ingestion and persistence.
- Phase 5 depends on Phase 4 and must enforce governance rules before any orchestration task executes.

## Parallel Opportunities

- Tasks marked `[P]` are safe to run in parallel (model definitions, tests, some services) as they operate on different files.

## Implementation Strategy

- MVP: deliver a runnable backend with `/health`, `POST /api/events`, `GET /api/reports/latest`, and `POST /api/ci/evaluate` returning deterministic verdicts. Start with SQLite and unit tests.
- Incrementally add reasoning, correlation, and orchestration with tests and audit trails.

