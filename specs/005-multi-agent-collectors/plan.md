# Implementation Plan: Multi-Agent Telemetry Collectors

**Branch**: `feature/multi-agent-collectors` | **Date**: 2026-06-10 | **Spec**: `specs/005-multi-agent-collectors/spec.md`

## Summary

Extend the AHMS backend with a modular multi-agent architecture where each agent (Infrastructure, Memory, CPU, CI/CD, API) independently monitors a CI component. Each agent reports health status, latest finding, and check timestamp. Agents integrate with the existing reasoning and persistence services for correlation and cross-system pattern detection.

## Technical Context

**Language/Version**: Python 3.12 (existing)

**Additional Dependencies**: None required (reuse existing FastAPI, SQLAlchemy, Pydantic)

**Storage**: Leverage existing SQLite (dev) / Postgres (prod)

**Testing**: pytest (existing)

**Architecture**: Agent abstraction layer + 5 concrete agents + agent registry

## Reuse Strategy

1. **Persistence Service**: Use existing CRUD for agent findings
2. **Reasoning Engine**: Reuse health scoring logic for agent evaluation
3. **Correlation Engine**: Enhance to correlate across agent findings
4. **API Routes**: Add new `/api/agents/*` endpoints
5. **Models**: Extend ORM with new tables for agent state and findings

## Project Structure (additions)

```text
src/
├── agents/
│   ├── __init__.py
│   ├── base.py              # Abstract Agent base class
│   ├── infrastructure.py    # Infrastructure agent
│   ├── memory.py            # Memory agent
│   ├── cpu.py               # CPU agent
│   ├── cicd.py              # CI/CD agent
│   ├── api.py               # API agent
│   └── registry.py          # Agent registry / discovery
├── models/
│   ├── agent_finding.py     # New ORM model for agent findings
│   └── agent_state.py       # New ORM model for agent state
└── api/
    └── agents_routes.py     # New routes for agent endpoints
```

## Key Design Decisions

1. **Agent Base Class**: Abstract interface with `check()`, `report()`, `get_status()` methods
2. **Finding Model**: Stores `agent_id`, `status`, `latest_finding`, `last_check_time`, `metadata`
3. **Registry**: Central lookup service for all agents; returns agent info + current status
4. **Mock Data**: Agents use realistic but simulated metrics (no external dependencies for MVP)
5. **Correlation**: Extend existing correlation engine to detect agent-to-agent patterns
6. **Backward Compatibility**: New endpoints don't break existing API; existing tests pass

## Implementation Strategy

1. **Phase 1**: Create agent abstraction layer (base class, interfaces)
2. **Phase 2**: Implement 5 concrete agents (each independent)
3. **Phase 3**: Create agent registry and discovery service
4. **Phase 4**: Add agent API endpoints (`/api/agents/*`)
5. **Phase 5**: Extend correlation engine for agent findings
6. **Phase 6**: Create comprehensive tests and documentation

## Deliverables

- Agent base class with interface contract
- 5 fully functional agents
- Agent finding and state ORM models
- Agent registry service
- 11 new API endpoints (list agents, query agent, get agent findings, etc.)
- 5 new database tables (one per agent type + generic findings table)
- 25+ unit tests covering all agents and edge cases
- Updated API documentation
- Integration with existing reasoning engine
