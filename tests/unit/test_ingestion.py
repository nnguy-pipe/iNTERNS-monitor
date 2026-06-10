"""MVP tests for ingestion endpoint."""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient

from src.api.main import app
from src.store.sqlite import init_db, drop_db


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
