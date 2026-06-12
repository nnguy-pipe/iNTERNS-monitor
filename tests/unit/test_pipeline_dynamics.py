"""Enhanced tests for pipeline verification - Health score dynamics."""

import pytest
from datetime import datetime, timedelta
from src.services.reasoning import ReasoningEngine
from src.services.normalize import NormalizationPipeline


@pytest.mark.unit
def test_health_score_changes_with_new_metrics():
    """
    Verify that health score CHANGES when different metrics are provided.
    
    This test addresses: T015 - Verify health score changes when metric values change
    """
    # Baseline - all healthy
    baseline_events = [
        {"type": "metric", "name": "cpu", "value": 50, "timestamp": datetime.utcnow()},
        {"type": "log", "level": "info", "message": "OK", "timestamp": datetime.utcnow()},
    ]
    baseline_score = ReasoningEngine.compute_health_score(baseline_events)
    assert baseline_score > 0.8, "Baseline should be healthy (>0.8)"
    
    # Now add error logs
    degraded_events = baseline_events + [
        {"type": "log", "level": "error", "message": "Database error", "timestamp": datetime.utcnow()},
        {"type": "log", "level": "error", "message": "Connection failed", "timestamp": datetime.utcnow()},
    ]
    degraded_score = ReasoningEngine.compute_health_score(degraded_events)
    
    # Score MUST be lower than baseline
    assert degraded_score < baseline_score, f"Score should decrease with errors: baseline={baseline_score}, degraded={degraded_score}"
    assert degraded_score < 0.5, "Degraded score should be low (<0.5)"
    
    print(f"✅ Health score changed: {baseline_score:.2f} → {degraded_score:.2f}")


@pytest.mark.unit
def test_health_score_determinism():
    """
    Verify that health score is deterministic (same metrics → same score).
    
    This test addresses: T018 - Ensure reasoning engine is deterministic
    """
    events = [
        {"type": "metric", "name": "requests", "value": 100, "timestamp": datetime.utcnow()},
        {"type": "log", "level": "info", "message": "Processing", "timestamp": datetime.utcnow()},
        {"type": "trace", "duration_ms": 500, "status": "success", "timestamp": datetime.utcnow()},
    ]
    
    # Compute score multiple times
    score1 = ReasoningEngine.compute_health_score(events)
    score2 = ReasoningEngine.compute_health_score(events)
    score3 = ReasoningEngine.compute_health_score(events)
    
    # All should be identical
    assert score1 == score2 == score3, f"Scores should be deterministic: {score1}, {score2}, {score3}"
    print(f"✅ Health score is deterministic: {score1}")


@pytest.mark.unit
def test_metric_normalization_preserves_value():
    """
    Verify that metric normalization preserves the value correctly.
    
    This test addresses: T010 - Verify simulator metrics are normalized to backend model
    """
    raw_metric = {
        "metric_name": "cpu_usage_percent",
        "value": 75.5,
        "labels": {"host": "prod-1"}
    }
    
    normalized = NormalizationPipeline.normalize(raw_metric, "metric")
    
    assert normalized is not None, "Normalization should not return None"
    assert normalized["type"] == "metric"
    assert normalized["name"] == "cpu_usage_percent"
    assert normalized["value"] == 75.5, "Value should be preserved in normalization"
    assert "timestamp" in normalized, "Normalized metric should have timestamp"
    print(f"✅ Metric normalization preserves value: {raw_metric['value']} → {normalized['value']}")


@pytest.mark.unit
def test_multiple_error_logs_compound_penalty():
    """
    Verify that multiple errors compound the health score penalty.
    
    This test addresses: T015 - Verify health score changes based on metric values
    """
    # Single error
    single_error = [
        {"type": "log", "level": "error", "message": "Error 1", "timestamp": datetime.utcnow()},
    ]
    score_one_error = ReasoningEngine.compute_health_score(single_error)
    
    # Multiple errors
    multiple_errors = [
        {"type": "log", "level": "error", "message": "Error 1", "timestamp": datetime.utcnow()},
        {"type": "log", "level": "error", "message": "Error 2", "timestamp": datetime.utcnow()},
        {"type": "log", "level": "error", "message": "Error 3", "timestamp": datetime.utcnow()},
    ]
    score_many_errors = ReasoningEngine.compute_health_score(multiple_errors)
    
    # Multiple errors should result in lower score
    assert score_many_errors < score_one_error, f"Multiple errors should lower score more: {score_one_error} vs {score_many_errors}"
    print(f"✅ Multiple errors compound: 1 error→{score_one_error:.2f}, 3 errors→{score_many_errors:.2f}")


@pytest.mark.unit
def test_primary_issue_separated_from_reasoning():
    """
    Verify that primary issue is clearly separated from reasoning narrative.
    
    This test addresses: T016 - Verify primary issue is separated from reasoning
    """
    events = [
        {"type": "log", "level": "error", "message": "Database connection failed", "timestamp": datetime.utcnow()},
        {"type": "metric", "name": "response_time", "value": 8000, "timestamp": datetime.utcnow()},
        {"type": "trace", "duration_ms": 7500, "status": "error", "timestamp": datetime.utcnow()},
    ]
    
    # Get primary issue (objective finding)
    primary_issue = ReasoningEngine.identify_primary_issue(events)
    
    # Get reasoning narrative (reasoning chain)
    narrative = ReasoningEngine.generate_reasoning_narrative(events)
    
    # Primary issue should be concrete and objective
    assert primary_issue is not None, "Should identify primary issue"
    assert isinstance(primary_issue, str), "Primary issue should be a string"
    assert len(primary_issue) > 0, "Primary issue should not be empty"
    
    # Narrative should provide reasoning context
    assert narrative is not None, "Should generate reasoning narrative"
    assert isinstance(narrative, dict), "Narrative should be a dict"
    
    print(f"✅ Primary issue separated from reasoning:")
    print(f"   Issue: {primary_issue}")
    print(f"   Reasoning keys: {list(narrative.keys())}")


@pytest.mark.unit
def test_recent_events_weighted_higher():
    """
    Verify that recent events have higher impact on health score than old events.
    
    This test addresses: MVP requirement for recency weighting
    """
    now = datetime.utcnow()
    
    # Old error (1 hour ago)
    old_error = {"type": "log", "level": "error", "message": "Error", "timestamp": now - timedelta(hours=1)}
    
    # Recent error (1 minute ago)
    recent_error = {"type": "log", "level": "error", "message": "Error", "timestamp": now - timedelta(minutes=1)}
    
    score_old = ReasoningEngine.compute_health_score([old_error])
    score_recent = ReasoningEngine.compute_health_score([recent_error])
    
    # Recent error should have higher penalty (lower score)
    assert score_recent < score_old, f"Recent errors should have higher impact: old={score_old:.2f}, recent={score_recent:.2f}"
    print(f"✅ Recent events weighted higher: old error→{score_old:.2f}, recent error→{score_recent:.2f}")


@pytest.mark.unit
def test_health_score_always_in_range():
    """
    Verify that health score always stays within 0.0 to 1.0 range.
    
    This test addresses: T015 - Ensure health score is valid
    """
    # Extreme case: many errors
    extreme_events = [
        {"type": "log", "level": "error", "message": f"Error {i}", "timestamp": datetime.utcnow()}
        for i in range(100)
    ]
    
    score = ReasoningEngine.compute_health_score(extreme_events)
    
    assert 0.0 <= score <= 1.0, f"Health score must be between 0.0 and 1.0, got {score}"
    assert score == 0.0, "Extreme errors should result in score of 0.0"
    
    print(f"✅ Health score always in valid range [0.0, 1.0]: {score}")
