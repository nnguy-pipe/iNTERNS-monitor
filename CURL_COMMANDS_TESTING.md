# Curl Commands for Event Simulation and Report Generation

This document provides comprehensive `curl` commands for testing the AHMS backend with the infrastructure simulator. Use these to generate events, trigger report generation, and verify the full end-to-end flow.

## Prerequisites

Ensure both the simulator daemon and backend are running:

```bash
# Terminal 1: Start infrastructure simulator daemon
python3 infrastructure_sim/infrastructure_simulator_daemon.py

# Terminal 2: Start backend API
python3 -m uvicorn src.api.main:app --reload --port 8000
```

---

## 1. Single Event Ingestion (CI Environment)

Ingests a single snapshot of simulator metrics as an event without report generation.

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=single" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "status": "ok",
  "events_ingested": 1,
  "message": "Single metric snapshot ingested"
}
```

---

## 2. Single Event Ingestion with Report Generation (CI)

Ingests a single event AND generates a user-facing report.

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=single&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "status": "ok",
  "events_ingested": 1,
  "report": {
    "id": "...",
    "system_name": "infra-demo",
    "environment": "ci",
    "status": "healthy",
    "health_score": 0.85,
    "primary_issue": "...",
    "reasoning": "...",
    "suggestions": [...],
    "ci_verdict": "...",
    "correlated_events": "...",
    "anomalies_detected": "...",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

---

## 3. Full Event Chain (CI Environment)

Ingests a correlated event chain (metric, log, and trace events) that exercises reasoning, correlation, and anomaly detection.

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "status": "ok",
  "events_ingested": 12,
  "message": "Full event chain ingested (metric, log, trace)"
}
```

---

## 4. Full Event Chain with Report Generation (CI)

Ingests a full event chain AND generates a comprehensive report with reasoning, correlation, and anomaly detection.

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 5. Production Environment - Single Event with Report

Ingests an event for the production environment (filters out CI-specific content).

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infrastructure&environment=production&scenario=single&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 6. Production Environment - Full Event Chain with Report

Full correlated event chain for production with comprehensive report generation.

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infrastructure&environment=production&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 7. High CPU Preset - Report Generation

Simulate high CPU load and generate report (includes CPU anomalies).

```bash
# First, set preset
curl -X POST "http://localhost:9999/preset/high_cpu" \
  -H "Content-Type: application/json"

# Wait 3-5 seconds for simulator to adjust metrics

# Then ingest and generate report
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected:** Report will show high CPU, threshold warnings, and anomaly detection.

---

## 8. High Memory Preset - Report Generation

Simulate high memory usage and generate report.

```bash
# Set high memory preset
curl -X POST "http://localhost:9999/preset/high_ram" \
  -H "Content-Type: application/json"

# Wait for metrics to adjust
sleep 3

# Ingest and generate report
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 9. High Users Preset - Report Generation

Simulate high user load and generate report (includes active user metrics).

```bash
# Set high users preset
curl -X POST "http://localhost:9999/preset/high_users" \
  -H "Content-Type: application/json"

sleep 3

# Ingest and generate report
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected:** Report will include active user counts per subsystem and user-load-based recommendations.

---

## 10. Return to Default Preset

Reset simulator to default (normal) metrics.

```bash
curl -X POST "http://localhost:9999/preset/default" \
  -H "Content-Type: application/json"
```

---

## 11. Fetch Generated Report (CI)

Retrieve the most recent generated report for CI environment.

```bash
curl -X GET "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci" \
  -H "Content-Type: application/json"
```

**Expected Response:** JSON report object with reasoning, correlation, anomalies.

---

## 12. Fetch Generated Report (Production)

Retrieve the most recent generated report for production environment.

```bash
curl -X GET "http://localhost:8000/api/reports/user?system_name=infrastructure&environment=production" \
  -H "Content-Type: application/json"
```

---

## 13. Get Simulator Metrics (Current State)

Retrieve the current metrics snapshot from the simulator daemon.

```bash
curl -X GET "http://localhost:9999/metrics" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "tick": 42,
  "timestamp": 1718200820.5,
  "preset": "default",
  "uptime_seconds": 256.3,
  "subsystems": {
    "web": {
      "cpu": 22.5,
      "ram": 412.0,
      "active_users": 5
    },
    "app": {
      "cpu": 18.3,
      "ram": 298.0,
      "active_users": 8
    },
    "db": {
      "cpu": 45.2,
      "ram": 892.0,
      "active_users": 2
    },
    "cache": {
      "cpu": 12.1,
      "ram": 256.0,
      "active_users": 0
    }
  }
}
```

---

## 14. Get Simulator Summary Statistics

Retrieve aggregated summary statistics from the simulator.

```bash
curl -X GET "http://localhost:9999/summary" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "preset": "default",
  "total_ticks": 256,
  "uptime_seconds": 256.3,
  "subsystems": {
    "web": {
      "cpu_avg": 20.5,
      "cpu_min": 5.2,
      "cpu_max": 78.3,
      "ram_avg": 410.0,
      "ram_min": 356.0,
      "ram_max": 456.0,
      "users_avg": 4.5,
      "users_max": 12
    },
    ...
  }
}
```

---

## 15. Backend Health Check

Verify backend API is healthy and database is accessible.

```bash
curl -X GET "http://localhost:8000/health" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "status": "ok",
  "database": "ok",
  "version": "0.1.0",
  "environment": "development"
}
```

---

## 16. Simulator Daemon Health Check

Verify simulator daemon is running and accepting requests.

```bash
curl -X GET "http://localhost:9999/health" \
  -H "Content-Type: application/json"
```

---

## Testing Workflow

### Complete End-to-End Test

Run this sequence to test the full pipeline:

```bash
# 1. Verify both services are running
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:9999/health"

# 2. Get current simulator metrics
curl -X GET "http://localhost:9999/metrics"

# 3. Ingest and generate CI report
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" -d '{}'

# 4. Fetch the generated CI report
curl -X GET "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci"

# 5. Change preset and re-test
curl -X POST "http://localhost:9999/preset/high_cpu"
sleep 3

curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" -d '{}'

# 6. Fetch updated CI report
curl -X GET "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci"

# 7. Test production environment
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infrastructure&environment=production&scenario=full&generate_user_report=true" \
  -H "Content-Type: application/json" -d '{}'

curl -X GET "http://localhost:8000/api/reports/user?system_name=infrastructure&environment=production"

# 8. Reset to default
curl -X POST "http://localhost:9999/preset/default"
```

---

## Event Scenarios Explained

### Single Event (`scenario=single`)
- Ingests a single metric snapshot from the current simulator state
- Does NOT trigger anomaly detection (requires multiple samples)
- Quick test for ingestion pipeline

### Full Event Chain (`scenario=full`)
- Ingests 12+ correlated events:
  - 4 subsystem CPU metrics
  - 1 aggregate CPU metric
  - 3 workflow log events
  - 1 trace event
  - Additional data points
- Triggers reasoning, correlation, and anomaly detection
- Comprehensive test of all backend processing

---

## Preset Effects on Events and Reports

| Preset | Effect | Report Impact |
|--------|--------|----------------|
| `default` | Balanced CPU, RAM, users | Healthy status |
| `high_cpu` | CPU 70-95%, outliers | Critical CPU, recommendations for optimization |
| `low_cpu` | CPU 5-20% | Healthy CPU, underutilized resources |
| `high_ram` | RAM 70-95% of capacity | Memory leak warnings, cache recommendations |
| `low_ram` | RAM 20-40% of capacity | Healthy memory, excess capacity |
| `high_users` | Active users 50-100+ | User load warnings, scaling recommendations |
| `low_users` | Active users 0-3 | Healthy, low concurrency |

---

## Frontend Integration

Use these curl commands to simulate the data flow that the frontend dashboard consumes:

1. **Generate report:** `curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=...&environment=ci&scenario=full&generate_user_report=true"`
2. **Frontend polls metrics:** `curl -X GET "http://localhost:9999/metrics"`
3. **Frontend fetches report:** `curl -X GET "http://localhost:8000/api/reports/user?system_name=...&environment=ci"`
4. **Frontend displays:**
   - Health score and status
   - Reasoning chain
   - Correlated events
   - Anomaly details

---

## Troubleshooting

**`Connection refused` on port 9999:**
- Ensure simulator daemon is running: `python3 infrastructure_sim/infrastructure_simulator_daemon.py`

**`Connection refused` on port 8000:**
- Ensure backend is running: `python3 -m uvicorn src.api.main:app --reload --port 8000`

**`404 Not Found` on `/api/reports/user`:**
- Ensure report was generated with `generate_user_report=true`
- Check that the `system_name` and `environment` match the ingestion call

**`attempt to write a readonly database`:**
- Database permissions issue; see SETUP_TROUBLESHOOTING.md for fixes

**Empty report fields (reasoning, correlation, anomalies):**
- These fields populate after reasoning/correlation/anomaly engines process events
- Ensure `scenario=full` for full event chain ingestion
- Check backend logs for processing errors

---

## Notes

- All commands use `localhost` by default; adjust host/port if services run on different machines
- Timestamps in responses are ISO 8601 format
- Report markdown can be downloaded via frontend "Open Report" button
- Active users metrics are read from simulator per-subsystem and aggregated by agents
- Each environment (CI, production) maintains separate report history
