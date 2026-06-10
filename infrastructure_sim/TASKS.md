# Infrastructure Simulator — Actionable Tasks

Status: **29 tasks** across 5 phases  
Last Updated: 2026-06-10  
Priority Order: P1 (Blocking) → P2 (Important) → P3 (Nice-to-have)

---

## Phase 1: Testing & Validation (8 tasks, 7 P1 + 1 P2)

**Goal**: Validate preset accuracy, export formats, and end-to-end correctness.

### Ready to Start (No Dependencies)

- [ ] **TEST-001** (P1) — Validate high_cpu preset accuracy
  - Run high_cpu preset for 300s, verify sustained CPU 70-90% across all subsystems
  - Log min/max/avg per subsystem
  - Expected output: CSV showing CPU ranges and conformance

- [ ] **TEST-002** (P1) — Validate high_ram preset growth
  - Run high_ram preset for 300s, verify linear RAM growth at ~0.5%/s
  - Calculate growth rate, confirm no decline
  - Expected output: RAM vs time plot (in JSON metrics)

- [ ] **TEST-003** (P1) — Validate low_ram preset decay
  - Run low_ram preset for 300s, verify RAM decay at ~0.2%/s
  - Confirm monotonic decline until floor (base_ram)
  - Expected output: RAM vs time plot showing decay

- [ ] **TEST-004** (P1) — Validate active_users metric consistency
  - Run high_users and low_users presets
  - Verify active_users ranges match spec (web 500-800, app 400-700, db 50-150, cache 100-300)
  - Expected output: Active user histogram per subsystem per preset

- [ ] **TEST-005** (P1) — Test SQL-JSON export completeness
  - Export to sql-json format, verify schema.subsystem_metrics contains all 11 columns
  - Validate data types: metric_id (string), cpu_percent (float), etc.
  - Expected output: JSON schema validation report

- [ ] **TEST-006** (P1) — Test SQL-XML export parsing
  - Export to sql-xml, parse with XML parser
  - Verify metric_id uniqueness and FK relationships valid
  - Expected output: XML parse success + uniqueness report

- [ ] **TEST-007** (P1) — Test both-format simultaneous export
  - Run `--out-format both`, verify both .json and .xml files created
  - Check file sizes reasonable, no corruption
  - Expected output: Size/checksum comparison

- [ ] **TEST-008** (P2) — Load test: long-duration simulation
  - Run 3600s (1hr) simulation, measure memory/CPU usage of simulator itself
  - Verify no memory leaks in simulator process
  - Export to JSON/XML, verify file sizes manageable
  - Expected output: Resource utilization metrics + files

---

## Phase 2: SQL Import & Database Setup (6 tasks, 3 P1 + 3 P2)

**Goal**: Set up SQL infrastructure for data persistence and analytics.

### Blocking on TEST-005 & TEST-006

- [ ] **DB-001** (P1) — Create PostgreSQL schema
  - Execute DDL from SQL_IMPORT_GUIDE.md
  - Create tables: simulations, ticks, subsystem_metrics with PKs, FKs, indexes
  - Expected output: Schema DDL script + verification queries

- [ ] **DB-002** (P1) — Create PostgreSQL import script
  - Write Python script to parse sql-json, batch-insert to tables
  - Handle ON CONFLICT for duplicate simulation_ids
  - Expected output: import_postgres.py with error handling

- [ ] **DB-003** (P1) — Test PostgreSQL import
  - Generate 5 different preset runs (high_cpu, low_cpu, high_ram, low_ram, high_users)
  - Import each to test DB, verify row counts match expected
  - Expected: ticks = duration, metrics = ticks × 4 subsystems
  - Expected output: Import log + verification queries

### Blocking on DB-003

- [ ] **DB-004** (P2) — Create SQLite schema
  - Create SQLite equivalent DDL (adapt from PostgreSQL)
  - Test import script with SQLite backend
  - Expected output: SQLite DDL + import_sqlite.py

- [ ] **DB-005** (P2) — Create MySQL schema
  - Create MySQL 5.7+ DDL with JSON functions support
  - Test import via both Python and native SQL LOAD
  - Expected output: MySQL DDL + import_mysql.py

- [ ] **DB-006** (P2) — Add query indexes for analytics
  - Create composite index on (simulation_id, subsystem, timestamp) in subsystem_metrics
  - Verify query performance improvements (benchmark before/after)
  - Expected output: Index DDL + performance test results

---

## Phase 3: Integration & Deployment (5 tasks, 1 P1 + 2 P2 + 2 P3)

**Goal**: Make simulator data accessible across systems.

### Blocking on DB-003 / TEST-007 / INT-001

- [ ] **INT-001** (P1) — Create demo import script
  - Write standalone Python script (import_simulator_data.py)
  - Support reading .json/.xml, configurable SQL backend (postgres/sqlite/mysql)
  - Expected output: Standalone script with config file support

- [ ] **INT-002** (P2) — Add CSV export option
  - Extend simulator to support `--out-format csv`
  - Export subsystem_metrics to CSV (flat, SQL-compatible)
  - Expected output: CSV export code + CSV sample file

- [ ] **INT-003** (P2) — Create example Dockerfile
  - Containerize simulator + import workflow
  - Base: python:3.9, install dependencies, mount volume for output
  - Expected output: Dockerfile + docker-compose.yml for test

### Blocking on INT-001

- [ ] **INT-004** (P3) — Add --continuous-export mode
  - Allow simulator to export partial results every N ticks
  - Useful for streaming import (not just final output)
  - Expected output: Streaming export mode with append logic

- [ ] **INT-005** (P3) — Integrate with monitoring dashboard
  - Document how to query simulator output and feed to Grafana/Prometheus
  - Create example dashboard JSON
  - Expected output: Integration guide + example queries

---

## Phase 4: Documentation & Examples (5 tasks, 2 P1 + 3 P2)

**Goal**: Make it easy for users to adopt the simulator.

### Blocking on DB-003 / TEST-001/002

- [ ] **DOC-001** (P1) — Create full example workflow
  - Write end-to-end example: generate data → export JSON → create tables → import → run 5 queries → save results
  - Include expected output for each step
  - Expected output: tutorial.md with step-by-step commands

- [ ] **DOC-002** (P1) — Create preset tuning guide
  - Document how to customize leak_rate, cpu_volatility, base_cpu per subsystem
  - Provide 3 real-world example scenarios (e.g., overloaded web, memory-heavy app)
  - Expected output: tuning_guide.md + 3 preset examples

- [ ] **DOC-003** (P1) — Create SQL query cookbook
  - Provide 10 useful queries: anomaly detection, performance trends, user correlation, memory leaks, load patterns
  - Include expected output for each
  - Expected output: queries.md + query examples

- [ ] **DOC-004** (P2) — Create troubleshooting guide
  - Document common issues: file not found, JSON parse errors, FK constraint violations, missing timestamps
  - Provide resolution steps for each
  - Expected output: troubleshooting.md

- [ ] **DOC-005** (P2) — Add inline code comments
  - Add docstrings to all functions
  - Explain complex logic (RAM modes, preset patterns)
  - Ensure code is self-documenting
  - Expected output: Updated infrastructure_simulator.py with 95%+ documented

---

## Phase 5: Enhancements & Future Work (5 tasks, all P3)

**Goal**: Advanced features for power users.

### Blocking on DB-003 / INT-001 / DOC-002

- [ ] **ENH-001** (P3) — Add anomaly detection module
  - Detect sudden CPU spikes, memory leaks, user load anomalies
  - Output anomaly scores in JSON/SQL
  - Expected output: anomaly_detector.py module + example alerts

- [ ] **ENH-002** (P3) — Add performance baseline comparison
  - Allow comparing two simulation runs (before/after optimization)
  - Output delta metrics (CPU delta, RAM delta, user load delta)
  - Expected output: compare.py + comparison report example

- [ ] **ENH-003** (P3) — Add --replay mode
  - Read from JSON/XML, replay metrics into live database in real-time
  - Useful for testing dashboards/alerting systems
  - Expected output: replay.py + usage example

- [ ] **ENH-004** (P3) — Create preset builder UI (CLI)
  - Interactive CLI tool to design custom presets (not web UI)
  - Interactively set base_cpu, base_ram, volatility, leak_rate per subsystem
  - Save/load preset configurations
  - Expected output: preset_builder.py + example presets

- [ ] **ENH-005** (P3) — Add multi-subsystem correlation analysis
  - Detect correlated failures (e.g., app CPU spike → db CPU spike 1s later)
  - Output correlation matrix + time-lag analysis
  - Expected output: correlation_analyzer.py + example matrix

---

## Critical Path (Minimum Viable Product)

**Sequential Tasks** (start with TEST, then DB, then DOC):

1. **TEST-005** → Test SQL-JSON export
2. **DB-001** → Create PostgreSQL schema
3. **DB-002** → Create import script
4. **DB-003** → Test PostgreSQL import
5. **DOC-001** → Create example workflow
6. **DOC-003** → Create query cookbook

**Estimated Timeline**:
- Testing: 4–6 hours (run 5-10 simulations, validate metrics)
- Database: 2–3 hours (DDL + import script + 3 test runs)
- Documentation: 3–4 hours (write guide + 10 queries + examples)
- **Total: 9–13 hours** for MVP

---

## Parallelizable Tasks

**Can start simultaneously** (no dependencies):
- TEST-001 through TEST-007 (all testing tasks)
- DOC-004, DOC-005 (code comments, troubleshooting)
- DB-006 (indexing is independent of import workflow)

**Parallel Example** (after TEST completes):
- DB-001/DB-002 (schema + import) in parallel with
- DOC-002 (tuning guide) using TEST-002 results

---

## Task Tracking Commands

### View all tasks by phase:
```sql
SELECT phase, COUNT(*) as task_count, 
  COUNT(CASE WHEN priority = 'P1' THEN 1 END) as p1_count
FROM sim_tasks
GROUP BY phase
ORDER BY CASE phase 
  WHEN 'Testing' THEN 1
  WHEN 'Database' THEN 2
  WHEN 'Integration' THEN 3
  WHEN 'Documentation' THEN 4
  WHEN 'Enhancement' THEN 5
END;
```

### View tasks ready to start:
```sql
SELECT id, title, phase, priority
FROM sim_tasks t
WHERE NOT EXISTS (
  SELECT 1 FROM sim_task_deps WHERE task_id = t.id
)
AND status = 'pending'
ORDER BY priority, phase;
```

### Mark a task complete:
```sql
UPDATE sim_tasks SET status = 'done' WHERE id = 'TEST-001';
```

### View task dependencies for a specific task:
```sql
SELECT 
  td.task_id as task,
  GROUP_CONCAT(td.depends_on, ', ') as blockers
FROM sim_task_deps td
WHERE td.task_id = 'DB-001'
GROUP BY td.task_id;
```

---

## Status Summary

| Phase | Total | Ready | In Progress | Done |
|-------|-------|-------|-------------|------|
| Testing | 8 | 8 | 0 | 0 |
| Database | 6 | 1 | 0 | 0 |
| Integration | 5 | 1 | 0 | 0 |
| Documentation | 5 | 2 | 0 | 0 |
| Enhancement | 5 | 0 | 0 | 0 |
| **TOTAL** | **29** | **12** | **0** | **0** |

**Next Action**: Start with **TEST-001** through **TEST-007** (all ready, no dependencies)
