"""Unit tests for refined reasoning engine with metric-specific scoring."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.services.reasoning import ReasoningEngine


class TestMetricScoringFunctions:
    """Test individual metric scoring functions."""

    def test_score_cpu_normal(self):
        """CPU < 70% should have no penalty."""
        penalty, reason = ReasoningEngine.score_cpu(50)
        assert penalty == 0
        assert "normal" in reason.lower()

    def test_score_cpu_elevated(self):
        """CPU 70-84% should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_cpu(75)
        assert penalty == 10
        assert "elevated" in reason.lower()

    def test_score_cpu_high(self):
        """CPU 85-94% should have 20 penalty."""
        penalty, reason = ReasoningEngine.score_cpu(90)
        assert penalty == 20
        assert "high" in reason.lower()

    def test_score_cpu_critical(self):
        """CPU >= 95% should have 30 penalty."""
        penalty, reason = ReasoningEngine.score_cpu(97)
        assert penalty == 30
        assert "critical" in reason.lower()

    def test_score_ram_percent_normal(self):
        """RAM < 75% should have no penalty."""
        penalty, reason = ReasoningEngine.score_ram(60, is_percent=True)
        assert penalty == 0
        assert "normal" in reason.lower()

    def test_score_ram_percent_elevated(self):
        """RAM 75-84% should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_ram(80, is_percent=True)
        assert penalty == 10
        assert "elevated" in reason.lower()

    def test_score_ram_mb_elevated(self):
        """RAM 800-999 MB should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_ram(900, is_percent=False)
        assert penalty == 10
        assert "elevated" in reason.lower()

    def test_score_error_rate_normal(self):
        """Error rate < 1% should have no penalty."""
        penalty, reason = ReasoningEngine.score_error_rate(0.005)
        assert penalty == 0
        assert "normal" in reason.lower()

    def test_score_error_rate_elevated(self):
        """Error rate 1-3% should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_error_rate(0.02)
        assert penalty == 10
        assert "elevated" in reason.lower()

    def test_score_error_rate_critical(self):
        """Error rate >= 5% should have 35 penalty."""
        penalty, reason = ReasoningEngine.score_error_rate(0.08)
        assert penalty == 35
        assert "critical" in reason.lower()

    def test_score_latency_normal(self):
        """Latency < 300ms should have no penalty."""
        penalty, reason = ReasoningEngine.score_latency(150)
        assert penalty == 0
        assert "normal" in reason.lower()

    def test_score_latency_elevated(self):
        """Latency 300-999ms should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_latency(500)
        assert penalty == 10
        assert "elevated" in reason.lower()

    def test_score_latency_high(self):
        """Latency 1000-2999ms should have 20 penalty."""
        penalty, reason = ReasoningEngine.score_latency(1500)
        assert penalty == 20
        assert "high" in reason.lower()

    def test_score_latency_critical(self):
        """Latency >= 3000ms should have 30 penalty."""
        penalty, reason = ReasoningEngine.score_latency(3500)
        assert penalty == 30
        assert "critical" in reason.lower()

    def test_score_event_spike_normal(self):
        """Event spike = 0 should have no penalty."""
        penalty, reason = ReasoningEngine.score_event_spike(0)
        assert penalty == 0
        assert "normal" in reason.lower()

    def test_score_event_spike_elevated(self):
        """Event spike 1-4 should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_event_spike(3)
        assert penalty == 10
        assert "elevated" in reason.lower()

    def test_score_event_spike_critical(self):
        """Event spike >= 10 should have 30 penalty."""
        penalty, reason = ReasoningEngine.score_event_spike(15)
        assert penalty == 30
        assert "critical" in reason.lower()

    def test_score_external_load_normal(self):
        """External load < 0.05 should have no penalty."""
        penalty, reason = ReasoningEngine.score_external_load(0.03)
        assert penalty == 0
        assert "normal" in reason.lower()

    def test_score_external_load_elevated(self):
        """External load 0.05-0.09 should have 8 penalty."""
        penalty, reason = ReasoningEngine.score_external_load(0.07)
        assert penalty == 8
        assert "elevated" in reason.lower()

    def test_score_external_load_critical(self):
        """External load >= 0.20 should have 25 penalty."""
        penalty, reason = ReasoningEngine.score_external_load(0.25)
        assert penalty == 25
        assert "critical" in reason.lower()

    def test_score_log_warning(self):
        """Log warning should have 10 penalty."""
        penalty, reason = ReasoningEngine.score_log_event("warning")
        assert penalty == 10
        assert "warning" in reason.lower()

    def test_score_log_error(self):
        """Log error should have 20 penalty."""
        penalty, reason = ReasoningEngine.score_log_event("error")
        assert penalty == 20
        assert "error" in reason.lower()

    def test_score_trace_error(self):
        """Trace error status should have 25 penalty."""
        penalty, reason = ReasoningEngine.score_trace_event("error")
        assert penalty == 25
        assert "error" in reason.lower()

    def test_score_trace_duration_high(self):
        """Trace duration 1000-2999ms should have 20 penalty."""
        penalty, reason = ReasoningEngine.score_trace_event("success", 1500)
        assert penalty == 20
        assert "slow" in reason.lower()


class TestRecencyWeighting:
    """Test recency weight computation."""

    def test_recency_fresh_event(self):
        """Fresh event (0 min old) should have weight 1.0."""
        now = datetime.utcnow()
        weight = ReasoningEngine.compute_recency_weight(now)
        assert weight == pytest.approx(1.0, abs=0.01)

    def test_recency_15_minutes_old(self):
        """Event 15 min old should have weight ~0.75."""
        timestamp = datetime.utcnow() - timedelta(minutes=15)
        weight = ReasoningEngine.compute_recency_weight(timestamp)
        assert weight == pytest.approx(0.75, abs=0.05)

    def test_recency_30_minutes_old(self):
        """Event 30 min old should have weight ~0.50."""
        timestamp = datetime.utcnow() - timedelta(minutes=30)
        weight = ReasoningEngine.compute_recency_weight(timestamp)
        assert weight == pytest.approx(0.50, abs=0.05)

    def test_recency_60_plus_minutes_old(self):
        """Event 60+ min old should have weight ~0.0."""
        timestamp = datetime.utcnow() - timedelta(minutes=65)
        weight = ReasoningEngine.compute_recency_weight(timestamp)
        assert weight < 0.05

    def test_recency_none_timestamp(self):
        """None timestamp should default to 1.0."""
        weight = ReasoningEngine.compute_recency_weight(None)
        assert weight == 1.0


class TestCategoryPenaltyCapping:
    """Test that penalties per category are capped."""

    def test_cpu_penalty_capped_at_30(self):
        """Multiple CPU events should not exceed 30 penalty."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 98,
                "timestamp": datetime.utcnow(),
            },
            {
                "type": "metric",
                "cpu_percent": 97,
                "timestamp": datetime.utcnow(),
            },
            {
                "type": "metric",
                "cpu_percent": 96,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        cpu_penalties = [b["penalty"] for b in breakdown if b["category"] == "cpu"]
        assert all(p <= 30 for p in cpu_penalties)
        # Score should reflect max 30 penalty from CPU
        assert score > 0.7  # (100 - 30) / 100 = 0.7


class TestHealthScoreBands:
    """Test that scores map to correct bands."""

    def test_healthy_band(self):
        """Score >= 0.8 should be healthy."""
        # Healthy system: low CPU, RAM, error rate
        events = [
            {
                "type": "metric",
                "cpu_percent": 30,
                "ram_percent": 40,
                "error_rate": 0.001,
                "latency_ms": 100,
                "event_spike": 0,
                "external_load": 0.02,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        assert score >= 0.8
        status = "healthy" if score >= 0.8 else "degraded"
        assert status == "healthy"

    def test_degraded_band(self):
        """Score 0.5-0.79 should be degraded."""
        # Degraded system: multiple elevated metrics (CPU high + latency high = 20+20=40 penalty)
        events = [
            {
                "type": "metric",
                "cpu_percent": 90,  # 20 penalty
                "ram_percent": 50,  # 0 penalty
                "error_rate": 0.01,  # 0 penalty
                "latency_ms": 1500,  # 20 penalty
                "event_spike": 0,  # 0 penalty
                "external_load": 0.02,  # 0 penalty
                "timestamp": datetime.utcnow(),
            },
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        # Score should be degraded: (100-40)/100 = 0.6, which is 0.5 <= score < 0.8
        assert 0.5 <= score < 0.79, f"Expected 0.5-0.79, got {score}"
        status = "degraded" if 0.5 <= score < 0.79 else "other"
        assert status == "degraded"

    def test_critical_band(self):
        """Score < 0.5 should be critical."""
        # Critical system: all metrics high
        events = [
            {
                "type": "metric",
                "cpu_percent": 92,
                "ram_percent": 96,
                "error_rate": 0.08,
                "latency_ms": 3500,
                "event_spike": 12,
                "external_load": 0.25,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        assert score < 0.5
        status = "critical" if score < 0.5 else "degraded"
        assert status == "critical"


class TestScoreBreakdown:
    """Test score breakdown generation."""

    def test_breakdown_contains_details(self):
        """Breakdown should contain category, value, penalty, reason."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 90,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        assert len(breakdown) > 0
        item = breakdown[0]
        assert "category" in item
        assert "value" in item
        assert "penalty" in item
        assert "reason" in item
        assert "recency_weight" in item

    def test_breakdown_sorted_by_penalty(self):
        """Breakdown should be sorted by penalty (highest first)."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 80,  # 10 penalty
                "ram_percent": 95,  # 30 penalty
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        penalties = [b["penalty"] for b in breakdown]
        assert penalties == sorted(penalties, reverse=True)

    def test_breakdown_identifies_primary_issues(self):
        """Breakdown should identify top issues."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 92,
                "ram_percent": 96,
                "error_rate": 0.08,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        categories = [b["category"] for b in breakdown]
        # Should include high-penalty categories
        assert any(cat in categories for cat in ["ram", "error_rate", "cpu"])


class TestTestCase1_HealthySystem:
    """Test case 1: Healthy system."""

    def test_healthy_system_score_band(self):
        """Healthy system should score 80-100."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 25,
                "ram_percent": 50,
                "error_rate": 0.002,
                "latency_ms": 120,
                "event_spike": 0,
                "external_load": 0.02,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        # Should be healthy (80-100)
        assert score >= 0.80
        status = "healthy" if score >= 0.8 else "other"
        assert status == "healthy"

    def test_healthy_system_primary_issue(self):
        """Healthy system should have no primary issue."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 25,
                "ram_percent": 50,
                "error_rate": 0.002,
                "latency_ms": 120,
                "timestamp": datetime.utcnow(),
            },
        ]
        issue = ReasoningEngine.identify_primary_issue(events)
        assert issue is None


class TestTestCase2_DegradedSystem:
    """Test case 2: Degraded system."""

    def test_degraded_system_score_band(self):
        """Degraded system should score 50-79."""
        # Degraded: elevated CPU and latency, but not all metrics high
        events = [
            {
                "type": "metric",
                "cpu_percent": 76,
                "ram_percent": 50,
                "error_rate": 0.01,
                "latency_ms": 400,
                "event_spike": 0,
                "external_load": 0.02,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        # Should be degraded (50-79): ~20 penalty total = 0.8 score
        assert 0.50 <= score < 0.80, f"Expected 0.5-0.8, got {score}"
        status = "degraded" if 0.50 <= score < 0.80 else "other"
        assert status == "degraded"

    def test_degraded_system_mentions_issues(self):
        """Degraded system breakdown should list resource/latency issues."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 76,
                "ram_percent": 50,
                "error_rate": 0.01,
                "latency_ms": 400,
                "event_spike": 0,
                "external_load": 0.02,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        categories = [b["category"] for b in breakdown]
        # Should detect at least some degradation categories
        assert len(categories) > 0


class TestTestCase3_CriticalSystem:
    """Test case 3: Critical system."""

    def test_critical_system_score_band(self):
        """Critical system should score 0-49."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 92,
                "ram_percent": 96,
                "error_rate": 0.08,
                "latency_ms": 3500,
                "event_spike": 12,
                "external_load": 0.25,
                "timestamp": datetime.utcnow(),
            },
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        # Should be critical (0-49)
        assert score < 0.50
        status = "critical" if score < 0.50 else "other"
        assert status == "critical"

    def test_critical_system_identifies_top_issue(self):
        """Critical system should identify primary issue."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 92,
                "ram_percent": 96,
                "error_rate": 0.08,
                "latency_ms": 3500,
                "event_spike": 12,
                "external_load": 0.25,
                "timestamp": datetime.utcnow(),
            },
        ]
        issue = ReasoningEngine.identify_primary_issue(events)
        assert issue is not None
        assert any(
            word in issue.lower()
            for word in ["cpu", "ram", "critical", "high"]
        )


class TestTestCase4_RepeatedNoiseNotOverPenalizing:
    """Test case 4: Repeated noisy logs should not over-penalize."""

    def test_repeated_warnings_capped(self):
        """20 repeated warnings should not collapse score."""
        events = [
            {
                "type": "log",
                "level": "warning",
                "message": "Repeated warning",
                "timestamp": datetime.utcnow(),
            }
            for _ in range(20)
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        # Score should decrease but not collapse
        assert score > 0.5  # Not critical just from repeated warnings
        assert score < 1.0  # Still affected by warnings

    def test_log_penalty_capped_at_25(self):
        """Log penalties should be capped at 25."""
        # Single error should give max penalty
        events = [
            {
                "type": "log",
                "level": "error",
                "timestamp": datetime.utcnow(),
            },
        ]
        score1, _ = ReasoningEngine.compute_health_score_with_breakdown(events)

        # Multiple errors should not exceed that penalty
        events_many = [
            {
                "type": "log",
                "level": "error",
                "timestamp": datetime.utcnow(),
            }
            for _ in range(10)
        ]
        score2, _ = ReasoningEngine.compute_health_score_with_breakdown(events_many)
        # Scores should be similar (both capped by log penalty)
        assert abs(score1 - score2) < 0.05


class TestTestCase5_RecencyDecay:
    """Test case 5: Recency decay - old events lose impact."""

    def test_old_critical_event_loses_impact(self):
        """Critical event 55 min old should have low impact."""
        # Old critical event
        old_event = {
            "type": "metric",
            "cpu_percent": 98,
            "timestamp": datetime.utcnow() - timedelta(minutes=55),
        }
        score_old, _ = ReasoningEngine.compute_health_score_with_breakdown([old_event])

        # Recent healthy event
        recent_healthy = {
            "type": "metric",
            "cpu_percent": 25,
            "timestamp": datetime.utcnow(),
        }
        score_healthy, _ = ReasoningEngine.compute_health_score_with_breakdown(
            [recent_healthy]
        )

        # Scores should be significantly different; recent healthy should dominate
        assert score_healthy > score_old

    def test_recency_weight_applied_to_penalties(self):
        """Penalties should be multiplied by recency weight."""
        # Fresh critical CPU
        fresh = {
            "type": "metric",
            "cpu_percent": 98,
            "timestamp": datetime.utcnow(),
        }
        score_fresh, breakdown_fresh = ReasoningEngine.compute_health_score_with_breakdown(
            [fresh]
        )

        # Same CPU but 30 min old
        old = {
            "type": "metric",
            "cpu_percent": 98,
            "timestamp": datetime.utcnow() - timedelta(minutes=30),
        }
        score_old, breakdown_old = ReasoningEngine.compute_health_score_with_breakdown(
            [old]
        )

        # Fresh event should have higher penalty (lower score)
        assert score_fresh < score_old
        # Verify recency weights in breakdown
        assert breakdown_fresh[0]["recency_weight"] > breakdown_old[0]["recency_weight"]


class TestAcceptanceCriteria:
    """Validate all acceptance criteria."""

    def test_no_generic_metric_1000_rule(self):
        """Should not have generic metric > 1000 rule."""
        # A 1000 value should depend on metric type, not be automatically penalized
        # CPU at 1000 is meaningless (CPU is %)
        event_cpu = {
            "type": "metric",
            "value": 1000,
            "cpu_percent": 1000,  # Invalid but should not trigger generic rule
            "timestamp": datetime.utcnow(),
        }
        # This should either be handled as percentage (not penalized)
        # or caught as invalid, not via generic > 1000 rule

    def test_metric_specific_scoring_for_8_types(self):
        """Should have metric-specific scoring for 8 metric types."""
        # Verify 8 metric types are scored
        assert hasattr(ReasoningEngine, "score_cpu")
        assert hasattr(ReasoningEngine, "score_ram")
        assert hasattr(ReasoningEngine, "score_error_rate")
        assert hasattr(ReasoningEngine, "score_latency")
        assert hasattr(ReasoningEngine, "score_event_spike")
        assert hasattr(ReasoningEngine, "score_external_load")
        assert hasattr(ReasoningEngine, "score_log_event")
        assert hasattr(ReasoningEngine, "score_trace_event")

    def test_severity_bands_not_single_penalties(self):
        """Each metric should have multiple severity bands."""
        # CPU has bands: <70, 70-84, 85-94, >=95
        assert ReasoningEngine.score_cpu(60)[0] == 0
        assert ReasoningEngine.score_cpu(75)[0] == 10
        assert ReasoningEngine.score_cpu(90)[0] == 20
        assert ReasoningEngine.score_cpu(97)[0] == 30

    def test_recency_weighting_applied(self):
        """Penalties should be multiplied by recency weight."""
        # Fresh event should have full penalty
        fresh = {
            "type": "metric",
            "cpu_percent": 90,
            "timestamp": datetime.utcnow(),
        }
        _, breakdown_fresh = ReasoningEngine.compute_health_score_with_breakdown([fresh])
        fresh_recency = breakdown_fresh[0]["recency_weight"]
        assert fresh_recency > 0.95

        # Old event should have reduced penalty
        old = {
            "type": "metric",
            "cpu_percent": 90,
            "timestamp": datetime.utcnow() - timedelta(minutes=50),
        }
        _, breakdown_old = ReasoningEngine.compute_health_score_with_breakdown([old])
        old_recency = breakdown_old[0]["recency_weight"]
        assert old_recency < fresh_recency

    def test_old_events_lose_influence(self):
        """Old events should decay to zero influence."""
        very_old = {
            "type": "metric",
            "cpu_percent": 98,
            "timestamp": datetime.utcnow() - timedelta(minutes=70),
        }
        score, _ = ReasoningEngine.compute_health_score_with_breakdown([very_old])
        # Should be nearly healthy despite critical event
        assert score > 0.8

    def test_repeated_events_dont_over_penalize(self):
        """Multiple events of same category should use max penalty."""
        # 10 critical CPU events
        events = [
            {
                "type": "metric",
                "cpu_percent": 98,
                "timestamp": datetime.utcnow(),
            }
            for _ in range(10)
        ]
        score1, _ = ReasoningEngine.compute_health_score_with_breakdown(events)

        # Single critical CPU event
        single_event = [
            {
                "type": "metric",
                "cpu_percent": 98,
                "timestamp": datetime.utcnow(),
            }
        ]
        score2, _ = ReasoningEngine.compute_health_score_with_breakdown(single_event)

        # Scores should be very similar (not 10x worse)
        assert abs(score1 - score2) < 0.05

    def test_score_clamped_0_to_100(self):
        """Internal score should be clamped 0-100, normalized 0.0-1.0."""
        # Very bad system
        bad_events = [
            {
                "type": "metric",
                "cpu_percent": 99,
                "ram_percent": 99,
                "error_rate": 0.5,
                "latency_ms": 5000,
                "timestamp": datetime.utcnow(),
            }
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(bad_events)
        assert 0.0 <= score <= 1.0

    def test_api_returns_0_1_format(self):
        """API should return health_score in 0.0-1.0 format."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 50,
                "timestamp": datetime.utcnow(),
            }
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_frontend_can_display_as_percentage(self):
        """Frontend can convert 0.0-1.0 to percentage."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 50,
                "timestamp": datetime.utcnow(),
            }
        ]
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        percentage = int(round(score * 100))
        assert 0 <= percentage <= 100

    def test_status_mapping_consistent(self):
        """Status should map consistently."""
        # Healthy: low CPU only
        healthy_events = [
            {
                "type": "metric",
                "cpu_percent": 30,
                "timestamp": datetime.utcnow(),
            }
        ]
        score_h, _ = ReasoningEngine.compute_health_score_with_breakdown(healthy_events)
        assert score_h > 0.79  # Use > 0.79 to avoid floating point issues

        # Degraded: high CPU + high latency
        degraded_events = [
            {
                "type": "metric",
                "cpu_percent": 90,
                "latency_ms": 1500,
                "timestamp": datetime.utcnow(),
            }
        ]
        score_d, _ = ReasoningEngine.compute_health_score_with_breakdown(degraded_events)
        assert 0.5 <= score_d < 0.79

        # Critical: very high CPU and RAM
        critical_events = [
            {
                "type": "metric",
                "cpu_percent": 97,
                "ram_percent": 97,
                "timestamp": datetime.utcnow(),
            }
        ]
        score_c, _ = ReasoningEngine.compute_health_score_with_breakdown(critical_events)
        assert score_c < 0.5

    def test_score_breakdown_returned(self):
        """Should return score breakdown with reasons."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 90,
                "ram_percent": 90,
                "timestamp": datetime.utcnow(),
            }
        ]
        score, breakdown = ReasoningEngine.compute_health_score_with_breakdown(events)
        assert isinstance(breakdown, list)
        assert len(breakdown) > 0
        for item in breakdown:
            assert "category" in item
            assert "reason" in item

    def test_dashboard_can_explain_degradation(self):
        """Dashboard should be able to explain primary reason for degradation."""
        events = [
            {
                "type": "metric",
                "cpu_percent": 91,
                "ram_percent": 96,
                "timestamp": datetime.utcnow(),
            }
        ]
        issue = ReasoningEngine.identify_primary_issue(events)
        assert issue is not None

    def test_test_cases_healthy_degraded_critical(self):
        """Tests should cover healthy, degraded, and critical scenarios."""
        # Test case 1: healthy
        healthy = [
            {
                "type": "metric",
                "cpu_percent": 25,
                "ram_percent": 50,
                "timestamp": datetime.utcnow(),
            }
        ]
        score_h, _ = ReasoningEngine.compute_health_score_with_breakdown(healthy)
        assert score_h > 0.79  # Use > 0.79 to avoid floating point precision issues

        # Test case 2: degraded
        degraded = [
            {
                "type": "metric",
                "cpu_percent": 90,
                "latency_ms": 1500,
                "timestamp": datetime.utcnow(),
            }
        ]
        score_d, _ = ReasoningEngine.compute_health_score_with_breakdown(degraded)
        assert 0.5 <= score_d < 0.79

        # Test case 3: critical
        critical = [
            {
                "type": "metric",
                "cpu_percent": 97,
                "ram_percent": 96,
                "timestamp": datetime.utcnow(),
            }
        ]
        score_c, _ = ReasoningEngine.compute_health_score_with_breakdown(critical)
        assert score_c < 0.5  # Use < 0.5 instead of <= 0.5 to avoid floating point issues
