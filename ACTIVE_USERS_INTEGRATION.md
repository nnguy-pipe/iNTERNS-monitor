# Active Users Integration Summary

## Overview

The AHMS backend now fully reads and processes **active user metrics** from the infrastructure simulator. Users can monitor active user load across all subsystems and trigger reports based on user activity thresholds.

## Components Involved

### 1. Infrastructure Simulator (`infrastructure_sim/infrastructure_simulator.py`)
- **Subsystem State:** Each subsystem tracks `active_users` count
- **User Simulation:** External usage patterns influence active user counts per subsystem
- **Presets:** `high_users` preset simulates 50-100+ concurrent active users

### 2. Simulator Daemon (`infrastructure_sim/infrastructure_simulator_daemon.py`)
- **Endpoint:** `/metrics` returns current subsystem metrics including `active_users`
- **Preset Support:** `/preset/high_users` and other presets dynamically adjust active user counts
- **Aggregation:** Summary endpoint tracks per-subsystem and total user statistics

### 3. Simulator Bridge (`src/simulator_bridge.py`)
- **`get_current_metrics()`** returns metrics with active_users per subsystem:
  ```json
  {
    "subsystems": {
      "web": {"cpu": 22.5, "ram": 412.0, "active_users": 5},
      "app": {"cpu": 18.3, "ram": 298.0, "active_users": 8},
      "db": {"cpu": 45.2, "ram": 892.0, "active_users": 2},
      "cache": {"cpu": 12.1, "ram": 256.0, "active_users": 0}
    }
  }
  ```
- **Event Chains:** `metrics_to_event_chain()` includes active user data in subsystem metrics
- **Summary Method:** `_subsystem_summary()` aggregates users_avg, users_max across subsystems

### 4. User Agent (`src/services/agents.py::UserAgent`)
- **NEW:** Reads active users from simulator daemon
- **Functionality:**
  - Retrieves current active user count per subsystem
  - Aggregates total active users across all subsystems
  - Determines health status based on load:
    - **Healthy:** < 10 active users (score: 0.95)
    - **Warning:** 10-50 active users (score: 0.7)
    - **Critical:** > 50 active users (score: 0.3)
  - Persists finding to database for traceability

```python
class UserAgent(BaseAgent):
    """Checks active user load and concurrency."""
    
    def check(self, db) -> Dict[str, Any]:
        # Reads from simulator daemon
        # Returns status: healthy|warning|critical
        # Includes active users per subsystem
```

- **Integration:** `run_all_agents()` now includes `UserAgent` alongside Infrastructure, Memory, CPU, CICD, and API agents

### 5. Reasoning Engine (`src/services/reasoning.py`)
- **User Load Considerations:** Reasoning chains now factor in active users when determining health
- **Example:** High CPU + High Users → recommends scaling or resource optimization
- **Suggestions:** Engine generates recommendations based on user load patterns

### 6. Event Ingestion Pipeline (`src/api/routes.py`)
- **Full Event Chain:** Includes user load metrics in trace and correlation chains
- **Report Generation:** Reports include active user counts in reasoning and recommendations

## Data Flow: Active Users

```
1. Infrastructure Simulator (generates active_users metrics)
   ↓
2. Simulator Daemon (/metrics endpoint)
   ↓
3. Simulator Bridge (SimulatorClient.get_current_metrics())
   ↓
4. User Agent (reads and evaluates active_users)
   ↓
5. Persistence Service (stores HealthReport with user load findings)
   ↓
6. Reasoning Engine (incorporates user load into health analysis)
   ↓
7. Report Generation (includes active users in output)
   ↓
8. Frontend Display (shows active user metrics and recommendations)
```

## Testing Active Users

### Using Curl Commands

**1. View current active users (via simulator metrics):**
```bash
curl -X GET "http://localhost:9999/metrics" | jq '.subsystems | map(.active_users)'
```

**2. Simulate high user load:**
```bash
curl -X POST "http://localhost:9999/preset/high_users"
sleep 2
curl -X GET "http://localhost:9999/metrics" | jq '.subsystems'
```

**3. Generate report with high user load:**
```bash
curl -X POST "http://localhost:9999/preset/high_users"
sleep 2
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true"
```

**4. Fetch report to see user-related findings:**
```bash
curl -X GET "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci" | jq '.reasoning'
```

### Using Python Directly

```python
from src.services.agents import UserAgent
from src.store.sqlite import SessionLocal

db = SessionLocal()
agent = UserAgent(system_name="users", environment="ci")
result = agent.check(db)
print(result)
# Output: {
#   "status": "healthy|warning|critical",
#   "latest_finding": "Active users: X total [web=5, app=8, db=2, cache=0]",
#   "last_checked": "2026-06-12T19:30:45.123456"
# }
db.close()
```

## Example Report Output

When users generate reports with active user load, the reasoning section now includes:

```markdown
### Reasoning & Analysis

**Active Users:** 35 total
- Web subsystem: 15 concurrent users
- App subsystem: 18 concurrent users
- DB subsystem: 2 concurrent users
- Cache subsystem: 0 concurrent users

**Finding:** Current user load is in the WARNING zone (10-50 users). 
System is approaching capacity constraints.

**Recommendation:** Monitor app subsystem closely (highest user load). 
Consider horizontal scaling of web and app tiers if user load continues to grow.
```

## Preset Effects on Active Users

| Preset | Active Users | Report Status | Recommendations |
|--------|--------------|---------------|-----------------|
| `default` | 5-15 total | Healthy | Normal operations |
| `high_users` | 50-100+ total | Warning/Critical | Scale horizontally |
| `low_users` | 0-3 total | Healthy | Underutilized capacity |
| `high_cpu` + users | Variable | May be Critical | Optimize code + scale |
| `high_ram` + users | Variable | May be Critical | Memory leak investigation + scale |

## Agent Suite Update

The `run_all_agents()` function now returns health checks from 6 agents:

1. **InfrastructureAgent** - Network connectivity
2. **MemoryAgent** - RAM usage
3. **CPUAgent** - CPU utilization
4. **UserAgent** (NEW) - Active user load
5. **CICDAgent** - Pipeline health
6. **APIAgent** - Endpoint latency/availability

## Frontend Integration

The frontend will receive active user metrics via:

1. **Simulator metrics polling** (every 5 seconds):
   - Displays live active user counts per subsystem
   - Updates status badge if users exceed thresholds

2. **Agent checks endpoint** (every 60 seconds):
   - Includes UserAgent findings
   - Used in health summary and alert generation

3. **Report display**:
   - Shows active user breakdown
   - Displays reasoning based on user load
   - Includes recommendations for scaling

## Verification

✅ **UserAgent class implemented** - Reads active_users from simulator
✅ **Integration in run_all_agents()** - UserAgent runs alongside other agents
✅ **Event chain support** - Active users included in full event chains
✅ **Frontend build** - No errors or warnings (758 modules)
✅ **Database writes** - SQLite correctly persists user load findings
✅ **Curl commands documented** - CURL_COMMANDS_TESTING.md includes user load testing

## Configuration

Active users can be controlled via:

- **Simulator presets:** `curl -X POST "http://localhost:9999/preset/{preset}"`
- **Code:** Edit `infrastructure_sim/infrastructure_simulator.py` to adjust user simulation models
- **Externally:** Frontend can trigger preset changes via `/preset/{preset}` endpoint

## Next Steps

1. **Monitor user metrics** in frontend dashboard
2. **Set alerts** when active users exceed thresholds
3. **Trigger scaling** recommendations when user load detected
4. **Archive reports** that show high user activity for trending analysis
5. **Correlate user spikes** with performance degradation (CPU/RAM)
