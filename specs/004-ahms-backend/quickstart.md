# Quickstart: AHMS Backend

This quickstart shows how to run the backend and generate a user-facing health report.

## 1. Install dependencies

```bash
python3 -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## 2. Start API server

```bash
uvicorn src.api.main:app --reload
```

Open docs at:

- http://127.0.0.1:8000/api/docs

## 3. Ingest sample telemetry

```bash
curl -X POST "http://127.0.0.1:8000/api/events" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "observability",
    "source_id": "evt-001",
    "event_type": "log",
    "timestamp": "2026-06-12T10:00:00",
    "environment": "ci",
    "system_name": "demo-service",
    "data": {
      "message": "timeout on database",
      "level": "error",
      "timestamp": "2026-06-12T10:00:00"
    }
  }'
```

## 4. Generate health report

```bash
curl -X POST "http://127.0.0.1:8000/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "demo-service",
    "environment": "ci",
    "lookback_minutes": 60
  }'
```

## 5. Generate user-facing report output

Structured JSON:

```bash
curl "http://127.0.0.1:8000/api/reports/user?system_name=demo-service&environment=ci&format=json"
```

Readable markdown report:

```bash
curl "http://127.0.0.1:8000/api/reports/user?system_name=demo-service&environment=ci&format=markdown"
```

One-shot generation plus markdown output in one call:

```bash
curl -X POST "http://127.0.0.1:8000/api/reports/user/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "demo-service",
    "environment": "ci",
    "lookback_minutes": 60,
    "format": "markdown"
  }'
```

## 6. CI deployment verdict call

```bash
curl -X POST "http://127.0.0.1:8000/api/ci/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "system_name": "demo-service",
    "environment": "ci",
    "deployment_context": {
      "sha": "abc123"
    }
  }'
```

## 7. View audit logs

```bash
curl "http://127.0.0.1:8000/api/audit/logs?system_name=demo-service&limit=50"
```

## Notes

- Database file defaults to ahms.db in the project root.
- You can reset local state by deleting ahms.db.
- For simulator integration, start the simulator daemon before simulator endpoints.
