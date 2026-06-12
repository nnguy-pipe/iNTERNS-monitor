# ⚡ QUICK START: AHMS Backend

## What This Backend Does

The Agentic Health Monitoring System (AHMS) backend:

1. **Ingests Telemetry**: Accepts metrics, logs, traces, and events from observability systems, workflows, and batch processes
2. **Normalizes Data**: Converts raw events into a unified schema for consistent analysis
3. **Runs Reasoning Engine**: Computes health scores (0.0–1.0), identifies primary issues, detects anomalies, and correlates events across systems
4. **Generates Reports**: Produces user-facing health reports with reasoning chains, suggestions, and confidence scores
5. **CI Integration**: Provides `pass|warn|fail` verdicts for deployment gating
6. **Audit Trail**: Records all decisions and actions for governance and compliance

**Key Outputs**:
- Health Score (0.0–1.0): System health assessment
- Primary Issue: Main problem detected
- Reasoning Chain: Why the health score was assigned
- Suggestions: Recommended remediation actions
- Anomalies: Detected unusual patterns
- Correlated Events: Related signals across systems

---

## Option 1: Use System Python (Simplest for Testing)

```bash
cd /path/to/iNTERNS-monitor

# Install to system Python
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
  fastapi uvicorn sqlalchemy pydantic

# Run
python3 -m uvicorn src.api.main:app --reload --port 8000
```

**Pros**: No venv issues, works immediately  
**Cons**: Global package installation

---

## Option 2: Virtual Environment (Recommended)

```bash
cd /path/to/iNTERNS-monitor

# Create & activate venv
python3 -m venv venv
source venv/bin/activate

# Install with trusted hosts (avoids SSL issues)
pip install --upgrade pip
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
  -r requirements.txt

# Run
python -m uvicorn src.api.main:app --reload --port 8000
```

**Pros**: Isolated environment, clean project  
**Cons**: Requires venv activation

---

## Option 3: Docker (Most Reliable)

```bash
cd /path/to/iNTERNS-monitor

# Build
docker build -t ahms-backend .

# Run
docker run -p 8000:8000 ahms-backend
```

**Pros**: No Python/pip issues, reproducible, production-ready  
**Cons**: Requires Docker

---

## 🧪 Test It Works

Once running (any option above), in a new terminal:

```bash
# Health check
curl http://localhost:8000/health

# Welcome message
curl http://localhost:8000/

# API docs (copy URL to browser)
curl http://localhost:8000/api/docs
```

**Expected output:**
```json
{
  "message": "Welcome to AHMS Backend",
  "version": "0.1.0",
  "docs": "/api/docs"
}
```

---

## 🆘 If You Get "ModuleNotFoundError"

### Quick Fix #1: Use --trusted-host
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Quick Fix #2: Check You're in venv
```bash
which python  # Should show "venv/bin/python"
```

### Quick Fix #3: Reinstall pip
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Quick Fix #4: Use Docker (Foolproof)
```bash
docker-compose up
```

---

## Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_health.py -v

# With coverage
pytest tests/ --cov=src
```

---

## Common Commands

```bash
# Activate venv
source venv/bin/activate

# Run server (development)
python -m uvicorn src.api.main:app --reload

# Run server (production)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Check health
curl http://localhost:8000/health | jq
```

---

## Backend API Endpoints

Once running, here's a complete flow to generate a report:

### Step 1: Ingest Events

```bash
# Ingest a metric event
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "observability",
    "source_id": "prom-001",
    "event_type": "metric",
    "timestamp": "2026-06-12T17:37:27Z",
    "environment": "ci",
    "system_name": "my-service",
    "data": {
      "metric_name": "cpu_usage",
      "value": 85
    }
  }'

# Ingest an error log
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "observability",
    "source_id": "log-001",
    "event_type": "log",
    "timestamp": "2026-06-12T17:37:28Z",
    "environment": "ci",
    "system_name": "my-service",
    "data": {
      "message": "Database connection timeout",
      "level": "error"
    }
  }'
```

### Step 2: Generate Health Report

The backend analyzes ingested events and produces a comprehensive health assessment:

```bash
# Generate report (stored in database)
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "my-service",
    "environment": "ci",
    "lookback_minutes": 60
  }'
```

**Response includes:**
- `health_score`: Float 0.0–1.0 (0.1 = critical, 0.5 = warning, 0.9 = healthy)
- `primary_issue`: String describing the main problem
- `reasoning`: Object with reasoning_chain and evidence_count
- `confidence`: Float 0.0–1.0 indicating assessment confidence
- `suggestions`: Array of recommended remediation actions
- `anomalies`: List of detected unusual patterns
- `correlated_events`: Event IDs linked by time or trace ID
- `created_at`: Timestamp of report generation

### Step 3: Retrieve Latest Report

Get the most recent report for a system:

```bash
curl "http://localhost:8000/api/reports/latest?system_name=my-service&environment=ci"
```

**Response:** Latest health report with status, score, issue, and suggestions.

### Step 4: Get User-Friendly Report (JSON or Markdown)

**JSON format:**
```bash
curl "http://localhost:8000/api/reports/user?system_name=my-service&environment=ci&format=json"
```

**Markdown format (readable):**
```bash
curl "http://localhost:8000/api/reports/user?system_name=my-service&environment=ci&format=markdown"
```

Output includes the report in human-readable markdown with health status, issue, suggestions, reasoning chain, anomalies, and correlations.

### Step 5: One-Shot Report Generation + Rendering

Generate a report AND immediately get user output in one call:

```bash
# Generate + return as markdown
curl -X POST http://localhost:8000/api/reports/user/generate \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "my-service",
    "environment": "ci",
    "lookback_minutes": 60,
    "format": "markdown"
  }'
```

Returns the generated report with an additional `report_markdown` field containing the formatted report.

### Step 6: CI Deployment Gating

Get a `pass|warn|fail` verdict for deployment decisions:

```bash
curl -X POST http://localhost:8000/api/ci/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "my-service",
    "environment": "ci",
    "deployment_context": {
      "sha": "abc123",
      "branch": "main"
    }
  }'
```

**Response:**
```json
{
  "system_name": "my-service",
  "environment": "ci",
  "verdict": "pass",
  "rationale": {
    "summary": "Health assessment complete",
    "reason_code": "HEALTHY_SCORE",
    "health_score": 0.92,
    "primary_issue": null,
    "report_id": "uuid-123"
  },
  "timestamp": "2026-06-12T17:40:00Z"
}
```

### Step 7: Audit Trail

View all decisions and reasoning events:

```bash
curl "http://localhost:8000/api/audit/logs?system_name=my-service&limit=50"
```

Shows event_type (ingestion, reasoning, decision), timestamp, and rationale for each action.

### List All Events

```bash
# All events for a system
curl "http://localhost:8000/api/events?system_name=my-service&environment=ci&limit=100"


---

## 📊 Understanding Report Information

Every health report contains:

| Field | Type | Meaning |
|-------|------|---------|
| `health_score` | Float 0.0–1.0 | Overall system health (0.1=critical, 0.5=warning, 0.9=healthy) |
| `primary_issue` | String | Main problem detected (e.g., "Error detected: timeout") |
| `status` | String | Category: `healthy`, `warning`, `critical`, or `unknown` |
| `confidence` | Float 0.0–1.0 | Confidence in this assessment based on evidence |
| `reasoning` | Object | Chain of reasoning steps explaining the score |
| `suggestions` | Array | Recommended remediation actions |
| `anomalies` | Array | Unusual patterns detected (statistical + rule-based) |
| `correlated_events` | Array | Event IDs grouped by time/trace for root-cause analysis |
| `created_at` | Timestamp | When the report was generated |

**Example interpretation:**
```json
{
  "health_score": 0.35,
  "status": "critical",
  "primary_issue": "Error detected: database timeout",
  "confidence": 0.87,
  "suggestions": [
    "Trigger immediate incident response",
    "Review database logs and query performance"
  ],
  "anomalies": [
    {"type": "statistical", "metric": "latency", "z_score": 3.2},
    {"type": "rule", "rule": "error-log-burst", "severity": "high"}
  ]
}
```

→ **Action**: This system needs immediate attention. High confidence (87%) that there's a database issue. 3 error logs detected; latency is 3.2 standard deviations above normal.

---

## 💾 How Reports Are Stored

All ingested events and generated reports are persisted in **SQLite** (`ahms.db`):

1. **Events Table** (`ci_events`): Raw telemetry from observability systems
2. **Reports Table** (`health_reports`): Computed health assessments with reasoning chains
3. **Audit Table** (`audit_logs`): All decisions and actions for compliance

When you call `/api/reports/generate`:
- Backend queries recent events from the database
- Runs reasoning engine on normalized data
- **Saves the report** to the database (queryable later)
- Logs the decision to audit trail

You can retrieve saved reports anytime:
- `/api/reports/latest` - Most recent report for a system
- `/api/reports/user` - Retrieve and format stored report as JSON or markdown

**For details**, see [DATABASE.md](DATABASE.md).

---

## Agents

This backend exposes lightweight runtime agents for targeted checks:

- `infrastructure`: external network/DNS reachability
- `memory`: host/container memory usage
- `cpu`: CPU load and per-core utilization
- `ci`: CI/CD pipeline health (recent workflow events)
- `api`: public API latency and availability

Trigger agents on-demand:

```bash
# Run all agents and return quick summaries
curl http://localhost:8000/api/agents/check
```

Each agent also persists a concise `HealthReport` in the database; retrieve persisted reports with `/api/reports/latest`.

---

## 📚 Additional Resources

- **[DATABASE.md](DATABASE.md)**: Detailed schema, queries, and integration with report generation
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment and configuration
- **[specs/004-ahms-backend/quickstart.md](specs/004-ahms-backend/quickstart.md)**: Backend-specific quickstart
- **[specs/004-ahms-backend/contracts/report-api.md](specs/004-ahms-backend/contracts/report-api.md)**: Complete API contract for all report endpoints
- **[BACKEND_README.md](BACKEND_README.md)**: Backend architecture and features
