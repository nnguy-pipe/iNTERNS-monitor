# ⚡ QUICK START: 3 Ways to Run AHMS Backend

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

Once running, try these:

```bash
# 1. Ingest an event
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "observability",
    "source_id": "prom-001",
    "event_type": "metric",
    "timestamp": "2026-06-10T17:37:27Z",
    "environment": "ci",
    "system_name": "test-service",
    "data": {"value": 42}
  }'

# 2. List events
curl http://localhost:8000/api/events

# 3. Generate health report
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "test-service",
    "environment": "ci"
  }'

# 4. Evaluate for CI
curl -X POST http://localhost:8000/api/ci/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "test-service",
    "environment": "ci"
  }'
```

---

**Choose Option 1, 2, or 3 above and you'll be running in seconds! 🚀**

See `DEPLOYMENT.md` for full production deployment guide.

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
