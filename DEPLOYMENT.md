# AHMS Backend: Deployment Guide

**Version**: 0.1.0  
**Updated**: 2026-06-10  
**Status**: Production-Ready (MVP)

---

## Table of Contents

1. [Quick Start (Local Development)](#quick-start-local-development)
2. [Troubleshooting](#troubleshooting)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Database Migration](#database-migration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Common Issues](#common-issues)

---

## Quick Start (Local Development)

### Prerequisites

- **Python 3.12+** (Check: `python3 --version`)
- **pip** or **pip3** (Check: `pip3 --version`)
- **Git** (Check: `git --version`)
- **Linux/Mac/WSL2** (Windows: use WSL2)

### Step 1: Navigate to Project

```bash
cd /path/to/iNTERNS-monitor
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate it (Linux/Mac/WSL2)
source venv/bin/activate

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1

# Verify activation (should show venv prefix)
which python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install production dependencies
pip install -r requirements.txt

# For development (includes pytest, black, flake8, mypy)
pip install -r requirements-dev.txt

# Verify installation
pip list | grep -E "fastapi|uvicorn|sqlalchemy"
```

### Step 4: Run the Server

```bash
# Development mode (with auto-reload)
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# OR production mode (no reload)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Output should be:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 5: Test the API

**In another terminal:**

```bash
# Health check
curl http://localhost:8000/health

# API docs (open in browser)
open http://localhost:8000/api/docs

# Root endpoint
curl http://localhost:8000/
```

**Expected response:**
```json
{
  "message": "Welcome to AHMS Backend",
  "docs": "/api/docs",
  "health": "/health",
  "version": "0.1.0"
}
```

### Step 6: Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html
```

---

## Troubleshooting

### Issue: "No module named uvicorn"

**Root Cause**: Dependencies not installed or wrong Python environment

**Solution**:
```bash
# 1. Check Python version (should be 3.12+)
python3 --version

# 2. Verify virtual environment is activated
which python  # Should show path with 'venv' in it

# 3. If not activated:
source venv/bin/activate

# 4. Check pip location
which pip

# 5. Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verify installation
python -m pip show uvicorn  # Should show version
```

### Issue: "Database lock" errors

**Root Cause**: SQLite locked by another process

**Solution**:
```bash
# 1. Kill any running instances
pkill -f "uvicorn"

# 2. Remove lock file (if exists)
rm -f ahms.db-wal ahms.db-shm

# 3. Restart server
python -m uvicorn src.api.main:app --reload
```

### Issue: "Permission denied" when activating venv

**Solution**:
```bash
# Make activate script executable
chmod +x venv/bin/activate

# Then activate
source venv/bin/activate
```

### Issue: Events not normalizing

**Root Cause**: Event timestamp format incorrect

**Solution**: Use ISO 8601 format in requests:
```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "observability",
    "source_id": "prom-001",
    "event_type": "metric",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "environment": "ci",
    "system_name": "test-service",
    "data": {"value": 42}
  }'
```

---

## Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run app
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create .dockerignore

```
.git
.gitignore
.pytest_cache
.mypy_cache
__pycache__
*.pyc
venv/
.venv/
ahms.db
ahms.db-wal
ahms.db-shm
.env
.env.local
```

### Step 3: Build & Run

```bash
# Build image
docker build -t ahms-backend:0.1.0 .

# Run container
docker run -p 8000:8000 \
  -e ENVIRONMENT=development \
  -e DATABASE_DIR=/data \
  -v ahms-data:/data \
  ahms-backend:0.1.0

# Run with custom config
docker run -p 8000:8000 \
  -e ENVIRONMENT=staging \
  -e DATABASE_DIR=/data \
  -e CORS_ORIGINS=https://my-frontend.com \
  -v ahms-data:/data \
  ahms-backend:0.1.0
```

### Step 4: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: development
      DATABASE_DIR: /data
      LOG_LEVEL: INFO
    volumes:
      - ahms-data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ahms-data:
```

**Run with Docker Compose:**
```bash
docker-compose up
```

---

## Production Deployment

### Prerequisites

- PostgreSQL 13+ (for production)
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- SSL certificate (Let's Encrypt recommended)

### Step 1: Install Production Dependencies

```bash
pip install gunicorn psycopg2-binary  # PostgreSQL driver
```

### Step 2: Switch to PostgreSQL

**Update `.env.production`:**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@localhost:5432/ahms
SQL_ECHO=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://my-frontend.com
REQUIRE_ACTION_APPROVAL=true
ENABLE_AUDIT_LOGGING=true
```

### Step 3: Run with Gunicorn

```bash
# Basic (4 workers)
gunicorn \
  -w 4 \
  -b 0.0.0.0:8000 \
  -k uvicorn.workers.UvicornWorker \
  src.api.main:app

# With logging
gunicorn \
  -w 4 \
  -b 0.0.0.0:8000 \
  -k uvicorn.workers.UvicornWorker \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  src.api.main:app
```

### Step 4: Nginx Configuration

Create `/etc/nginx/sites-available/ahms`:

```nginx
upstream ahms_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://ahms_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/docs {
        proxy_pass http://ahms_backend;
    }

    location /health {
        proxy_pass http://ahms_backend;
    }
}
```

### Step 5: SSL with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d api.example.com

# Auto-renew
sudo systemctl enable certbot.timer
```

### Step 6: Systemd Service

Create `/etc/systemd/system/ahms-backend.service`:

```ini
[Unit]
Description=AHMS Backend
After=network.target postgresql.service

[Service]
Type=notify
User=ahms
WorkingDirectory=/opt/ahms
Environment="PATH=/opt/ahms/venv/bin"
ExecStart=/opt/ahms/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:8000 \
    -k uvicorn.workers.UvicornWorker \
    src.api.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl enable ahms-backend
sudo systemctl start ahms-backend
sudo systemctl status ahms-backend
```

---

## Database Migration

### Local SQLite → PostgreSQL

#### Step 1: Export SQLite Data

```bash
# Create migration script
cat > migrate_to_postgres.py << 'EOF'
import sqlite3
import psycopg2
from datetime import datetime

# Connect to SQLite
sqlite_conn = sqlite3.connect('ahms.db')
sqlite_conn.row_factory = sqlite3.Row

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    "dbname=ahms user=postgres password=password host=localhost"
)

# Migrate each table
# (schema and data migration logic here)
sqlite_conn.close()
pg_conn.close()
EOF
```

#### Step 2: Use Alembic

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply to PostgreSQL
alembic upgrade head
```

---

## Monitoring & Logging

### Application Logs

```bash
# View logs
tail -f logs/app.log

# Filter by level
grep ERROR logs/app.log

# Real-time monitoring
python -m uvicorn src.api.main:app --reload --log-level debug 2>&1 | tee app.log
```

### Health Monitoring

```bash
# Continuous health check
watch -n 5 'curl -s http://localhost:8000/health | jq'

# Alerting script
#!/bin/bash
while true; do
  status=$(curl -s http://localhost:8000/health | jq -r '.status')
  if [ "$status" != "ok" ]; then
    echo "ALERT: Backend health is $status at $(date)"
  fi
  sleep 30
done
```

### Agents

The backend provides lightweight agents that perform focused health checks and write concise `HealthReport` entries:

- `infrastructure`: network/DNS connectivity checks
- `memory`: memory utilization and container pressure
- `cpu`: CPU load and per-core utilization
- `ci`: CI/CD pipeline health (analyzes recent workflow events)
- `api`: public API latency and availability

Invoke all agents on-demand:

```bash
curl http://localhost:8000/api/agents/check
```

Use `/api/reports/latest` to fetch persisted reports per system.

### Metrics Collection

```bash
# Prometheus-compatible metrics endpoint
# (Add to routes in future phase)

# Check database size
ls -lh ahms.db

# Check database queries
sqlite3 ahms.db "SELECT COUNT(*) as total_events FROM ci_events;"
```

---

## Common Issues

### Issue: Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python -m uvicorn src.api.main:app --port 8001
```

### Issue: CORS Errors in Frontend

**Update `.env`:**
```bash
CORS_ORIGINS=http://localhost:3000,https://my-frontend.com
```

### Issue: Slow Queries on Large Datasets

```bash
# Add database indexes
sqlite3 ahms.db << 'EOF'
CREATE INDEX idx_ci_events_timestamp ON ci_events(timestamp DESC);
CREATE INDEX idx_ci_events_system ON ci_events(system_name);
CREATE INDEX idx_health_reports_system ON health_reports(system_name);
EOF
```

### Issue: High Memory Usage

```bash
# Check memory
ps aux | grep uvicorn

# Reduce workers (if using Gunicorn)
gunicorn -w 2 -b 0.0.0.0:8000 src.api.main:app
```

---

## Environment Variables Reference

```bash
# Application
ENVIRONMENT=development|staging|production
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Database
DATABASE_DIR=.
DATABASE_URL=sqlite:///ahms.db  # or postgresql://...
SQL_ECHO=false

# API
CORS_ORIGINS=*
PYTHONUNBUFFERED=1

# Thresholds
CI_PASS_THRESHOLD=0.8
CI_WARN_THRESHOLD=0.5
HEALTH_SCORE_WARNING_THRESHOLD=0.5
HEALTH_SCORE_CRITICAL_THRESHOLD=0.2

# Governance
REQUIRE_ACTION_APPROVAL=true
ENABLE_AUDIT_LOGGING=true
```

---

## Verification Checklist

Before going live, verify:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linting errors: `flake8 src/`
- [ ] Types check: `mypy src/`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] API docs load: `curl http://localhost:8000/api/docs`
- [ ] Database connects: `python -c "from src.store.sqlite import engine; print(engine.execute('SELECT 1'))"`
- [ ] Events ingest successfully
- [ ] Reports generate correctly
- [ ] CI verdicts return consistent values
- [ ] Audit logs are created

---

## Support

For issues:
1. Check logs: `tail -f uvicorn.log`
2. Review troubleshooting above
3. Check GitHub issues
4. Review API docs: `http://localhost:8000/api/docs`

---

**Deployment Guide - v0.1.0 | Last Updated: 2026-06-10**
