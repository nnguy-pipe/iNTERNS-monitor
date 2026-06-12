"""Integration tests for orchestration and CI evaluation endpoints."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.api.main import app
from src.store.sqlite import init_db, drop_db


@pytest.fixture
def client():
    init_db()
    yield TestClient(app)
    drop_db()


@pytest.mark.integration
def test_ci_evaluate_returns_machine_readable_rationale_without_report(client):
    response = client.post(
        "/api/ci/evaluate",
        json={
            "system_name": "svc-without-report",
            "environment": "ci",
            "deployment_context": {"sha": "abc"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["verdict"] == "warn"
    assert isinstance(payload["rationale"], dict)
    assert payload["rationale"]["reason_code"] == "NO_HEALTH_REPORT"


@pytest.mark.integration
def test_ci_evaluate_uses_latest_health_report_and_audits(client):
    now = datetime.utcnow().isoformat()
    system_name = "svc-ci-gate"

    # Ingest one event
    ingest_resp = client.post(
        "/api/events",
        json={
            "source": "observability",
            "source_id": "evt-001",
            "event_type": "log",
            "timestamp": now,
            "environment": "ci",
            "system_name": system_name,
            "data": {
                "message": "all good",
                "level": "info",
                "timestamp": now,
            },
        },
    )
    assert ingest_resp.status_code == 200

    # Generate a report
    report_resp = client.post(
        "/api/reports/generate",
        json={
            "system_name": system_name,
            "environment": "ci",
            "lookback_minutes": 60,
        },
    )
    assert report_resp.status_code == 200

    ci_resp = client.post(
        "/api/ci/evaluate",
        json={
            "system_name": system_name,
            "environment": "ci",
        },
    )
    assert ci_resp.status_code == 200
    body = ci_resp.json()
    assert body["verdict"] in ["pass", "warn", "fail"]
    assert isinstance(body["rationale"], dict)
    assert "reason_code" in body["rationale"]
    assert "health_score" in body["rationale"]

    logs_resp = client.get(f"/api/audit/logs?system_name={system_name}&limit=50")
    assert logs_resp.status_code == 200
    logs = logs_resp.json().get("logs", [])
    # reasoning event from report generation + decision event from CI evaluate
    event_types = {log.get("event_type") for log in logs}
    assert "reasoning" in event_types
    assert "decision" in event_types
