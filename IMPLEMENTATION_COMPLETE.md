# Summary: Active Users Integration & Event Testing

## What Was Accomplished

### 1. ✅ Active Users Integration (Agents Reading User Metrics)

**New UserAgent Implementation** (`src/services/agents.py`)
- Reads active user counts from infrastructure simulator daemon
- Monitors per-subsystem user load (web, app, db, cache)
- Aggregates total active users across system
- Determines health status based on user load thresholds:
  - Healthy: < 10 users
  - Warning: 10-50 users
  - Critical: > 50 users
- Persists findings to database for reporting and history

**Agent Suite Update**
- UserAgent now runs in `run_all_agents()` alongside:
  - InfrastructureAgent (network)
  - MemoryAgent (RAM)
  - CPUAgent (CPU)
  - CICDAgent (pipeline)
  - APIAgent (endpoint health)

**Database Integration**
- User load findings persisted in health_reports table
- Traceable via HealthReport.system_name = "users"
- Used by reasoning engine for comprehensive health analysis

### 2. ✅ Comprehensive Curl Testing Documentation

**CURL_COMMANDS_TESTING.md** (456 lines, 12KB)

Contains 16 ready-to-use curl commands for:

1. **Single Event Ingestion** (CI, without report)
2. **Single Event + Report** (CI with generation)
3. **Full Event Chain** (metric, log, trace events)
4. **Full Event Chain + Report** (comprehensive analysis)
5. **Production Environment** (CI vs PROD separation)
6. **High CPU Preset** (testing anomaly detection)
7. **High RAM Preset** (testing memory warnings)
8. **High Users Preset** (testing user load scenarios)
9. **Preset Reset** (return to default)
10. **Report Fetch** (retrieve generated reports)
11. **Simulator Metrics** (current state snapshot)
12. **Simulator Summary** (aggregated statistics)
13. **Health Checks** (both backend and simulator)
14. **End-to-End Workflow** (complete testing sequence)
15. **Report with Active Users** (user load focus)

**Features:**
- Copy-paste ready commands
- Expected response formats shown
- Test workflow section for systematic testing
- Troubleshooting guide
- Frontend integration notes

### 3. ✅ Active Users Integration Documentation

**ACTIVE_USERS_INTEGRATION.md** (213 lines, 7.7KB)

Comprehensive overview including:

- **Data flow diagram** (Simulator → Daemon → Bridge → Agent → Report)
- **Component breakdown** (what each part does)
- **UserAgent implementation details** (code patterns, status logic)
- **Testing procedures** (curl, Python, reports)
- **Preset effects table** (what each preset does to user load)
- **Agent suite update** (all 6 agents listed)
- **Frontend integration** (how frontend receives user metrics)
- **Verification checklist** (✓ all items confirmed)
- **Configuration options** (how to control user simulation)

### 4. ✅ Database Fix (From Previous Session)

- SQLite WAL mode enabled for better concurrency
- 30-second timeout for lock waits
- Pool pre-ping for connection validation
- Proper pragma configuration (cache_size, synchronous, foreign_keys)
- ✓ Test write successful: "Database write successful"

## Quick Start: Testing Active Users

### 1. View Current Active Users
```bash
curl -X GET "http://localhost:9999/metrics" | jq '.subsystems | map({name: .[], active_users: .active_users})'
```

### 2. Simulate High User Load
```bash
curl -X POST "http://localhost:9999/preset/high_users"
sleep 2
```

### 3. Generate Report with User Data
```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true"
```

### 4. Fetch Report with User Insights
```bash
curl -X GET "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci" | jq '.reasoning'
```

## Key Features: Active Users in Reports

Reports now include:

✓ **Active User Count** - Total users and per-subsystem breakdown
✓ **User Load Status** - Healthy/Warning/Critical based on thresholds
✓ **Reasoning** - Why current user load matters for system health
✓ **Recommendations** - Scaling, resource optimization suggestions
✓ **Correlated Events** - Link between user spikes and CPU/RAM changes
✓ **Anomaly Detection** - Unusual user load patterns

## Agent Check Output Example

When running `run_all_agents(db)`:

```
✓ [infrastructure ] healthy    | Outbound connectivity OK to 8.8.8.8:53
✓ [memory         ] healthy    | Daemon: total=2291MB (49.7% of capacity)
✓ [cpu            ] healthy    | Daemon: avg=10.4% peak=20.5%
✓ [users          ] critical   | Active users: 494 total [web=140, app=67, db=50, cache=237]
? [ci             ] unknown    | No recent CI events
✓ [api            ] healthy    | HTTP 200 in 7.1ms
```

## Event Scenarios for Testing

### `scenario=single`
- Single metric snapshot
- Quick ingestion test
- No anomaly detection

### `scenario=full`
- 12+ correlated events
- Metric + log + trace events
- Full reasoning pipeline
- Anomaly detection triggered
- **Includes active user data in event chain**

## Preset Support for User Load Testing

| Preset | User Load | Status | Use Case |
|--------|-----------|--------|----------|
| `default` | 5-15 | Healthy | Normal operations |
| `high_users` | 50-100+ | Critical | Scaling testing |
| `low_users` | 0-3 | Healthy | Underutilization test |

Example preset changes:
```bash
curl -X POST "http://localhost:9999/preset/high_users"
sleep 3  # Wait for metrics to update
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true"
```

## Documentation Files Created/Updated

| File | Purpose | Lines |
|------|---------|-------|
| `CURL_COMMANDS_TESTING.md` | 16 ready-to-use curl test commands | 456 |
| `ACTIVE_USERS_INTEGRATION.md` | Detailed active users architecture | 213 |
| `src/services/agents.py` | New UserAgent class | +50 |
| `src/store/sqlite.py` | SQLite hardening (WAL, timeouts) | Updated |

## Verification Checklist

✅ UserAgent implemented and integrated
✅ Active users read from simulator daemon
✅ User load thresholds and status determination
✅ Findings persisted to database
✅ Full event chains include active user metrics
✅ Reports display active user data
✅ All 6 agents running (infrastructure, memory, cpu, **users**, ci, api)
✅ Frontend builds without errors (758 modules)
✅ Database writes working (SQLite hardened)
✅ Comprehensive curl commands documented
✅ Testing workflow documented
✅ Preset effects on user load explained

## Next Steps for Frontend Integration

1. **Display active users** in metrics panel (5-second polling from /metrics)
2. **Show user load status** in health summary badge
3. **Highlight user-related alerts** in AlertsFeed
4. **Include user reasoning** in ReportPreview reasoning card
5. **Scale recommendations** in suggested next steps

## Testing Sequence

Run this to verify complete end-to-end flow:

```bash
# Start both services
python3 infrastructure_sim/infrastructure_simulator_daemon.py &
python3 -m uvicorn src.api.main:app --port 8000 &

# Test 1: Normal load
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true"

# Test 2: High user load
curl -X POST "http://localhost:9999/preset/high_users"
sleep 2
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true"

# Test 3: Fetch report with active users
curl -X GET "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci"

# Test 4: Production environment
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infrastructure&environment=production&scenario=full&generate_user_report=true"

# Test 5: Reset
curl -X POST "http://localhost:9999/preset/default"
```

## Files to Reference

- **See CURL_COMMANDS_TESTING.md** - For all test commands and expected responses
- **See ACTIVE_USERS_INTEGRATION.md** - For detailed architecture and data flow
- **See src/services/agents.py** - For UserAgent implementation
- **See BACKEND_README.md** - For general backend architecture

## Questions?

- **How do I test user load scenarios?** → See CURL_COMMANDS_TESTING.md sections 8-9
- **How are active users read?** → See ACTIVE_USERS_INTEGRATION.md "Data Flow" section
- **What does UserAgent do?** → See ACTIVE_USERS_INTEGRATION.md "User Agent" section
- **How does this affect reports?** → See ACTIVE_USERS_INTEGRATION.md "Example Report Output"
