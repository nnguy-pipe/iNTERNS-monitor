"""Tests for reasoning and correlation engines."""

import pytest
from datetime import datetime, timedelta
from src.services.reasoning import ReasoningEngine
from src.services.correlation import CorrelationEngine


@pytest.mark.unit
def test_health_score_all_healthy_events():
    """Test health score with all healthy events."""
    events = [
        {"type": "log", "level": "info", "message": "OK", "timestamp": datetime.utcnow()},
        {"type": "metric", "name": "cpu", "value": 50, "timestamp": datetime.utcnow()},
        {"type": "trace", "duration_ms": 100, "status": "success", "timestamp": datetime.utcnow()},
    ]
    score = ReasoningEngine.compute_health_score(events)
    assert score > 0.9, "Healthy events should result in high score"


@pytest.mark.unit
def test_health_score_with_errors():
    """Test health score decreases with errors."""
    events = [
        {"type": "log", "level": "error", "message": "Failed", "timestamp": datetime.utcnow()},
        {"type": "log", "level": "error", "message": "Failed", "timestamp": datetime.utcnow()},
    ]
    score = ReasoningEngine.compute_health_score(events)
    assert score < 0.5, "Error events should result in low score"


@pytest.mark.unit
def test_health_score_with_high_subsystem_cpu():
    """Simulator subsystem metrics should penalize health score under high CPU load."""
    events = [
        {
            "type": "metric",
            "name": "simulator_subsystems",
            "timestamp": datetime.utcnow(),
            "subsystems": {
                "web": {"cpu": 92, "ram": 500, "active_users": 80},
                "app": {"cpu": 88, "ram": 400, "active_users": 120},
            },
        }
    ]
    score = ReasoningEngine.compute_health_score(events)
    assert score < 0.25, "High subsystem CPU should produce a very low health score"


@pytest.mark.unit
def test_identify_primary_issue():
    """Test that primary issue is identified correctly."""
    events = [
        {"type": "log", "level": "error", "message": "Database connection failed"},
        {"type": "metric", "name": "requests", "value": 10},
    ]
    issue = ReasoningEngine.identify_primary_issue(events)
    assert issue and "error" in issue.lower()


@pytest.mark.unit
def test_generate_suggestions():
    """Test that suggestions are generated based on score."""
    low_score_suggestions = ReasoningEngine.generate_suggestions(0.2, "Critical error")
    high_score_suggestions = ReasoningEngine.generate_suggestions(0.9, None)
    
    assert len(low_score_suggestions) > 0, "Low score should generate suggestions"
    assert any("incident" in s.get("action", "").lower() for s in low_score_suggestions)


@pytest.mark.unit
def test_correlation_by_time_window():
    """Test time-based event correlation."""
    now = datetime.utcnow()
    events = [
        {"id": "1", "timestamp": now, "type": "log"},
        {"id": "2", "timestamp": now + timedelta(seconds=30), "type": "metric"},
        {"id": "3", "timestamp": now + timedelta(minutes=10), "type": "trace"},
    ]
    
    clusters = CorrelationEngine.correlate_by_time_window(events, window_minutes=5)
    
    # First two events should be in same cluster (within 5 min window)
    # Third event should be separate
    assert len(clusters) == 2


@pytest.mark.unit
def test_cascade_failure_detection():
    """Test detection of cascading failures."""
    events = [
        {"type": "log", "level": "error", "message": "Error"},
        {"type": "trace", "duration_ms": 6000, "status": "error"},
        {"type": "log", "level": "warning", "message": "Warning"},
    ]
    
    cascades = CorrelationEngine.detect_cascading_failures(events)
    assert len(cascades) > 0, "Should detect cascading failure pattern"


@pytest.mark.unit
def test_trace_correlation():
    """Test correlation by trace ID."""
    events = [
        {"id": "1", "trace_id": "trace-123", "type": "log"},
        {"id": "2", "trace_id": "trace-123", "type": "metric"},
        {"id": "3", "trace_id": "trace-456", "type": "log"},
    ]
    
    correlations = CorrelationEngine.correlate_by_trace_id(events)
    assert "trace-123" in correlations
    assert len(correlations["trace-123"]) == 2
    assert len(correlations["trace-456"]) == 1


@pytest.mark.unit
def test_evaluate_health_returns_full_reasoning_payload():
    """Test consolidated reasoning output includes confidence and suggestions."""
    events = [
        {
            "type": "log",
            "level": "error",
            "message": "database timeout",
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "type": "trace",
            "duration_ms": 6100,
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
        },
    ]

    result = ReasoningEngine.evaluate_health(events)

    assert "health_score" in result
    assert "primary_issue" in result
    assert "reasoning" in result
    assert "suggestions" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
