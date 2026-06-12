"""Tests for anomaly detection engine."""

import pytest
from datetime import datetime

from src.services.anomaly import AnomalyEngine


@pytest.mark.unit
def test_detect_rule_based_anomalies_error_burst():
    events = [
        {"id": "1", "type": "log", "level": "error", "timestamp": datetime.utcnow().isoformat()},
        {"id": "2", "type": "log", "level": "error", "timestamp": datetime.utcnow().isoformat()},
        {"id": "3", "type": "log", "level": "error", "timestamp": datetime.utcnow().isoformat()},
    ]

    anomalies = AnomalyEngine.detect_rule_based_anomalies(events)

    assert len(anomalies) >= 1
    assert any(a.get("rule") == "error-log-burst" for a in anomalies)


@pytest.mark.unit
def test_detect_statistical_anomalies_metric_outlier():
    events = [
        {"id": "1", "type": "metric", "name": "cpu", "value": 10, "timestamp": datetime.utcnow().isoformat()},
        {"id": "2", "type": "metric", "name": "cpu", "value": 11, "timestamp": datetime.utcnow().isoformat()},
        {"id": "3", "type": "metric", "name": "cpu", "value": 9, "timestamp": datetime.utcnow().isoformat()},
        {"id": "4", "type": "metric", "name": "cpu", "value": 10, "timestamp": datetime.utcnow().isoformat()},
        {"id": "5", "type": "metric", "name": "cpu", "value": 10.5, "timestamp": datetime.utcnow().isoformat()},
        {"id": "6", "type": "metric", "name": "cpu", "value": 40, "timestamp": datetime.utcnow().isoformat()},
    ]

    anomalies = AnomalyEngine.detect_statistical_anomalies(events, z_threshold=2.0, min_samples=5)

    assert len(anomalies) >= 1
    assert any(a.get("metric") == "cpu" for a in anomalies)


@pytest.mark.unit
def test_detect_anomalies_combines_detectors():
    events = [
        {"id": "a1", "type": "log", "level": "error", "timestamp": datetime.utcnow().isoformat()},
        {"id": "a2", "type": "log", "level": "error", "timestamp": datetime.utcnow().isoformat()},
        {"id": "a3", "type": "log", "level": "error", "timestamp": datetime.utcnow().isoformat()},
        {"id": "m1", "type": "metric", "name": "latency", "value": -1, "timestamp": datetime.utcnow().isoformat()},
    ]

    anomalies = AnomalyEngine.detect_anomalies(events)

    assert len(anomalies) >= 2
    reasons = " ".join(a.get("reason", "") for a in anomalies).lower()
    assert "error" in reasons or "invalid" in reasons
