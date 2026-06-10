# Tasks: Multi-Agent Telemetry Collectors

**Feature**: Multi-Agent Telemetry Collectors | **Spec**: `specs/005-multi-agent-collectors/spec.md` | **Plan**: `specs/005-multi-agent-collectors/plan.md`

## Implementation Strategy

**MVP Scope**: Phase 1-4 (agents fully functional + API endpoints)  
**Nice-to-Have**: Phase 5-6 (correlation + advanced tests)  
**Test Approach**: Unit tests per agent, integration tests for registry and API

## Phase 1: Agent Abstraction Layer & Foundation

**Goal**: Create reusable agent base class and ORM models for storing agent findings.

**Independent Test Criteria**:
- Base agent class defines interface contract
- All methods are mockable and testable
- ORM models persist agent findings and state
- Database schema supports multi-agent queries

### Tasks

- [ ] T001 Create agent base class with interface in `src/agents/base.py`
- [ ] T002 [P] Create `AgentFinding` ORM model in `src/models/agent_finding.py`
- [ ] T003 [P] Create `AgentState` ORM model in `src/models/agent_state.py`
- [ ] T004 Add ORM model to database initialization in `src/store/sqlite.py`
- [ ] T005 Create persistence service methods for agent findings in `src/services/persistence.py`
- [ ] T006 Add unit tests for base agent class in `tests/unit/test_agent_base.py`
- [ ] T007 [P] Add unit tests for ORM models in `tests/unit/test_agent_models.py`

---

## Phase 2: Implement 5 Specialized Agents

**Goal**: Implement Infrastructure, Memory, CPU, CI/CD, and API agents.

**Independent Test Criteria**:
- Each agent independently reports health status
- Each agent tracks latest finding and check timestamp
- Each agent can be queried via `get_status()` method
- All agents reuse base class interface

### Infrastructure Agent (US1)

- [ ] T008 [P] [US1] Implement Infrastructure agent in `src/agents/infrastructure.py`
- [ ] T009 [US1] Add infrastructure metrics collection (zone, DNS, network)
- [ ] T010 [US1] Add health scoring logic (0.0-1.0 scale with thresholds)
- [ ] T011 [US1] Add finding generation (issue detection + recommendations)
- [ ] T012 [US1] Add unit tests for Infrastructure agent in `tests/unit/test_infrastructure_agent.py`

### Memory Agent (US2)

- [ ] T013 [P] [US2] Implement Memory agent in `src/agents/memory.py`
- [ ] T014 [US2] Add memory metrics collection (heap, GC, OOM risk)
- [ ] T015 [US2] Add health scoring logic (0.0-1.0 scale with thresholds)
- [ ] T016 [US2] Add finding generation (issue detection + recommendations)
- [ ] T017 [US2] Add unit tests for Memory agent in `tests/unit/test_memory_agent.py`

### CPU Agent (US3)

- [ ] T018 [P] [US3] Implement CPU agent in `src/agents/cpu.py`
- [ ] T019 [US3] Add CPU metrics collection (load, saturation, context switches)
- [ ] T020 [US3] Add health scoring logic (0.0-1.0 scale with thresholds)
- [ ] T021 [US3] Add finding generation (issue detection + recommendations)
- [ ] T022 [US3] Add unit tests for CPU agent in `tests/unit/test_cpu_agent.py`

### CI/CD Agent (US4)

- [ ] T023 [P] [US4] Implement CI/CD agent in `src/agents/cicd.py`
- [ ] T024 [US4] Add pipeline metrics collection (job failures, queue, flakiness)
- [ ] T025 [US4] Add health scoring logic (0.0-1.0 scale with thresholds)
- [ ] T026 [US4] Add finding generation (issue detection + recommendations)
- [ ] T027 [US4] Add unit tests for CI/CD agent in `tests/unit/test_cicd_agent.py`

### API Agent (US5)

- [ ] T028 [P] [US5] Implement API agent in `src/agents/api.py`
- [ ] T029 [US5] Add endpoint metrics collection (latency, availability, errors)
- [ ] T030 [US5] Add health scoring logic (0.0-1.0 scale with thresholds)
- [ ] T031 [US5] Add finding generation (issue detection + recommendations)
- [ ] T032 [US5] Add unit tests for API agent in `tests/unit/test_api_agent.py`

---

## Phase 3: Agent Registry & Discovery

**Goal**: Create registry service to discover and query all agents.

**Independent Test Criteria**:
- Registry lists all registered agents
- Registry returns agent status and findings
- Registry supports agent lookup by ID
- Registry can aggregate health across all agents

### Tasks

- [ ] T033 [P] Create Agent Registry in `src/agents/registry.py`
- [ ] T034 Register all 5 agents with registry
- [ ] T035 Add registry query methods: list agents, get agent by ID, aggregate health
- [ ] T036 Add registry persistence (fetch/update agent state from database)
- [ ] T037 [P] Add unit tests for registry in `tests/unit/test_agent_registry.py`

---

## Phase 4: Agent API Endpoints

**Goal**: Expose agent status and findings via REST API.

**Independent Test Criteria**:
- Endpoints accept HTTP requests and return JSON
- Endpoints integrate with registry service
- Endpoints support filtering and pagination
- All endpoints documented in OpenAPI

### Tasks

- [ ] T038 Create agent routes in `src/api/agents_routes.py`
- [ ] T039 Implement `GET /api/agents` - list all agents with current status
- [ ] T040 Implement `GET /api/agents/{agent_id}` - query single agent
- [ ] T041 Implement `GET /api/agents/{agent_id}/findings` - list agent findings
- [ ] T042 Implement `GET /api/health/agents` - aggregate health status
- [ ] T043 Implement `POST /api/agents/{agent_id}/check` - trigger manual check
- [ ] T044 [P] Add integration tests for agent endpoints in `tests/integration/test_agent_endpoints.py`
- [ ] T045 Update API documentation in `docs/API.md` with agent endpoints

---

## Phase 5: Cross-Agent Correlation

**Goal**: Enhance correlation engine to detect patterns across agent findings.

**Independent Test Criteria**:
- Correlation engine processes agent findings
- Correlation engine detects multi-agent patterns
- Correlation engine generates causal narratives
- Findings stored with correlation IDs

### Tasks

- [ ] T046 Extend correlation engine in `src/services/correlation.py` to ingest agent findings
- [ ] T047 Implement pattern detection (e.g., memory surge → API latency)
- [ ] T048 Implement causal narrative generation for multi-agent patterns
- [ ] T049 [P] Add unit tests for cross-agent correlation in `tests/unit/test_agent_correlation.py`

---

## Phase 6: Polish & Documentation

**Goal**: Comprehensive tests, documentation, and performance optimization.

**Independent Test Criteria**:
- All tests pass (>80% coverage)
- All agents properly documented
- No regressions in existing API
- Performance acceptable under load

### Tasks

- [ ] T050 Run full test suite and fix failures
- [ ] T051 Add performance tests for agent checks in `tests/performance/test_agent_perf.py`
- [ ] T052 Create agent developer guide in `docs/AGENTS.md`
- [ ] T053 Update DEPLOYMENT.md with agent environment variables
- [ ] T054 Update BACKEND_README.md with multi-agent architecture overview
- [ ] T055 Create agent extension guide for adding custom agents
- [ ] T056 Performance optimization: cache agent findings for 30-60 seconds
- [ ] T057 Final validation: all endpoints working, no broken tests

---

## Dependencies

**No external dependencies on other user stories.**

All agents can be implemented in parallel (tasks T008-T032 are all independent).  
Agents are fully independent and can operate without correlation (Phase 5).

## Parallel Execution Example

**Example: Implement all 5 agents in parallel (1 team per agent)**:

```bash
# Agent 1: Infrastructure (tasks T008-T012)
git checkout -b feat/agent-infrastructure
# Complete T008-T012 → PR

# Agent 2: Memory (tasks T013-T017) — parallel
git checkout -b feat/agent-memory
# Complete T013-T017 → PR

# Agent 3: CPU (tasks T018-T022) — parallel
# Agent 4: CI/CD (tasks T023-T027) — parallel
# Agent 5: API (tasks T028-T032) — parallel

# After all PRs merged:
# Complete Phase 3-6 sequentially (registry depends on all agents)
```

## Estimated Effort

- **Phase 1** (Foundation): 4-5 hours
- **Phase 2** (5 Agents): 8-10 hours (highly parallelizable)
- **Phase 3** (Registry): 2-3 hours
- **Phase 4** (API): 3-4 hours
- **Phase 5** (Correlation): 2-3 hours
- **Phase 6** (Polish): 2-3 hours

**Total**: ~21-28 hours (or ~5-7 hours with full parallelization)

## MVP Definition

**Minimal Viable Multi-Agent System**:
- ✅ 5 agents fully implemented
- ✅ Each agent tracks: status, latest_finding, last_check_time
- ✅ Agent registry discoverable
- ✅ API endpoints: list agents, get agent, get findings
- ✅ Basic unit tests per agent
- ✅ Backward compatible with existing API

**Nice-to-Have (Phase 5-6)**:
- Cross-agent correlation
- Advanced pattern detection
- Performance optimization
- Comprehensive documentation
