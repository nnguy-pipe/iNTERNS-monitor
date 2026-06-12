"""MVP tests for ingestion endpoint."""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient

from src.api.main import app
from src.store.sqlite import init_db, drop_db, SessionLocal
from src.services.persistence import PersistenceService


@pytest.fixture
def client():
    """Create a test client."""
    init_db()
    yield TestClient(app)
    drop_db()


@pytest.mark.unit
def test_ingest_metric_event(client):
    """Test ingesting a metric event."""
    payload = {
        "source": "observability",
        "source_id": "prom-001",
        "event_type": "metric",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "ci",
        "system_name": "test-service",
        "data": {
            "metric_name": "requests_per_second",
            "value": 42.5,
            "labels": {"instance": "prod-1"}
        }
    }
    
    response = client.post("/api/events", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingested"
    assert "event_id" in data


@pytest.mark.unit
def test_ingest_log_event(client):
    """Test ingesting a log event."""
    payload = {
        "source": "workflow",
        "source_id": "github-001",
        "event_type": "log",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "staging",
        "system_name": "test-service",
        "data": {
            "message": "Deployment successful",
            "level": "info",
            "source": "github-actions"
        }
    }
    
    response = client.post("/api/events", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingested"


@pytest.mark.unit
def test_ingest_missing_required_field(client):
    """Test that missing required fields are rejected."""
    payload = {
        "source": "observability",
        "source_id": "prom-001",
        # missing event_type
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "ci",
        "system_name": "test-service",
        "data": {}
    }
    
    response = client.post("/api/events", json=payload)
    assert response.status_code == 400
    assert "Ingestion failed" in response.json()["detail"]


@pytest.mark.unit
def test_list_events(client):
    """Test listing ingested events."""
    # First ingest an event
    payload = {
        "source": "observability",
        "source_id": "prom-001",
        "event_type": "metric",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production",
        "system_name": "api-gateway",
        "data": {"value": 100}
    }
    client.post("/api/events", json=payload)
    
    # Now list events
    response = client.get("/api/events?system_name=api-gateway&environment=production")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert len(data["events"]) >= 1


@pytest.mark.unit
def test_generate_report_persists_reasoning_fields(client):
    """Generated reports should persist reasoning, confidence, correlations, and anomalies."""
    now = datetime.utcnow().isoformat()
    base_payload = {
        "source": "observability",
        "environment": "ci",
        "system_name": "reporting-service",
        "timestamp": now,
    }

    events = [
        {
            **base_payload,
            "source_id": "e-1",
            "event_type": "log",
            "data": {
                "message": "database error",
                "level": "error",
                "timestamp": now,
            },
        },
        {
            **base_payload,
            "source_id": "e-2",
            "event_type": "trace",
            "data": {
                "trace_id": "trace-1",
                "duration_ms": 6500,
                "status": "error",
                "timestamp": now,
            },
        },
        {
            **base_payload,
            "source_id": "e-3",
            "event_type": "metric",
            "data": {
                "metric_name": "queue_depth",
                "value": -2,
                "timestamp": now,
            },
        },
    ]

    for payload in events:
        resp = client.post("/api/events", json=payload)
        assert resp.status_code == 200

    response = client.post(
        "/api/reports/generate",
        json={
            "system_name": "reporting-service",
            "environment": "ci",
            "lookback_minutes": 60,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "reasoning" in body
    assert "confidence" in body
    assert "anomalies" in body

    db = SessionLocal()
    try:
        report = PersistenceService.get_latest_health_report(
            db=db,
            system_name="reporting-service",
            environment="ci",
        )
        assert report is not None
        assert report.reasoning is not None
        assert report.confidence is not None
        assert isinstance(report.correlated_events, list)
        assert isinstance(report.anomalies_detected, list)
    finally:
        db.close()
