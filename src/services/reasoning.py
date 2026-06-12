"""Agentic reasoning engine for health scoring."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    MVP reasoning engine that computes health scores and generates diagnostics.
    
    Separates objective findings (what was detected) from reasoning chain.
    """

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        """Best-effort timestamp parsing for normalized payloads and tests."""
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc).replace(tzinfo=None)
            return value
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is not None:
                    return parsed.astimezone(timezone.utc).replace(tzinfo=None)
                return parsed
            except Exception:
                return datetime.utcnow()
        return datetime.utcnow()

    @staticmethod
    def compute_health_score(events: List[Dict[str, Any]]) -> float:
        """
        Compute health score based on recent normalized events.
        
        Returns: 0.0 (critical) to 1.0 (healthy)
        
        MVP logic:
        - Count errors/warnings in logs → penalty
        - Check metric values against thresholds → penalty
        - Consider recency (recent events weighted higher)
        """
        if not events:
            return 0.5  # Unknown state
        
        score = 1.0
        now = datetime.utcnow()
        
        for event in events:
            # Weight recent events higher
            event_time = ReasoningEngine._parse_timestamp(event.get("timestamp", now))
            event_age_seconds = (now - event_time).total_seconds()
            recency_weight = max(0, 1.0 - (event_age_seconds / 3600))  # Decay over 1 hour
            
            # Check event type and apply penalties
            event_type = event.get("type")
            
            if event_type == "log":
                level = event.get("level", "").lower()
                if level == "error":
                    score -= 0.3 * recency_weight
                elif level == "warning":
                    score -= 0.15 * recency_weight
            
            elif event_type == "metric":
                value = float(event.get("value", 0))
                # Simple thresholds for MVP
                if value > 1000:  # Abnormally high
                    score -= 0.2 * recency_weight
                elif value < 0:  # Invalid
                    score -= 0.1 * recency_weight
            
            elif event_type == "trace":
                duration = float(event.get("duration_ms", 0))
                status = event.get("status", "").lower()
                if status == "error":
                    score -= 0.25 * recency_weight
                elif duration > 5000:  # >5s duration
                    score -= 0.1 * recency_weight
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def identify_primary_issue(events: List[Dict[str, Any]]) -> Optional[str]:
        """
        Identify the primary issue from event patterns.
        
        Objective finding: "What is the main problem detected?"
        """
        if not events:
            return None
        
        # Look for error logs first (highest priority)
        error_logs = [e for e in events if e.get("type") == "log" and e.get("level") == "error"]
        if error_logs:
            return f"Error detected: {error_logs[0].get('message', 'Unknown error')}"
        
        # Check for high-latency traces
        slow_traces = [e for e in events if e.get("type") == "trace" and float(e.get("duration_ms", 0)) > 5000]
        if slow_traces:
            duration = slow_traces[0].get("duration_ms")
            return f"High latency detected: {duration}ms (threshold: 5000ms)"
        
        # Check for abnormal metrics
        abnormal_metrics = [e for e in events if e.get("type") == "metric" and float(e.get("value", 0)) > 1000]
        if abnormal_metrics:
            metric_name = abnormal_metrics[0].get("name")
            value = abnormal_metrics[0].get("value")
            return f"Abnormal metric detected: {metric_name}={value}"
        
        return None

    @staticmethod
    def generate_reasoning_narrative(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate reasoning narrative explaining the health assessment.
        
        Separated from objective findings for clarity.
        """
        if not events:
            return {"reasoning": "Insufficient data", "evidence": []}
        
        reasoning_steps = []
        
        # Count event types
        logs = [e for e in events if e.get("type") == "log"]
        metrics = [e for e in events if e.get("type") == "metric"]
        traces = [e for e in events if e.get("type") == "trace"]
        
        reasoning_steps.append(f"Analyzed {len(events)} events: {len(logs)} logs, {len(metrics)} metrics, {len(traces)} traces")
        
        # Error analysis
        errors = [e for e in logs if e.get("level") == "error"]
        if errors:
            reasoning_steps.append(f"Found {len(errors)} error logs (weight: -0.3 each)")
        
        # Performance analysis
        slow = [e for e in traces if float(e.get("duration_ms", 0)) > 5000]
        if slow:
            avg_duration = sum(float(e.get("duration_ms", 0)) for e in slow) / len(slow)
            reasoning_steps.append(f"Found {len(slow)} slow traces (avg: {avg_duration:.0f}ms)")
        
        return {
            "reasoning_chain": reasoning_steps,
            "evidence_count": len(events),
            "recommendation": "Monitor closely if score < 0.5, escalate if < 0.3",
        }

    @staticmethod
    def generate_suggestions(score: float, issue: Optional[str]) -> List[Dict[str, Any]]:
        """
        Generate remediation suggestions based on health score and issue.
        """
        suggestions = []
        
        if score < 0.3:
            suggestions.append({
                "action": "Trigger immediate incident response",
                "severity": "critical",
                "confidence": 0.95,
            })
        elif score < 0.5:
            suggestions.append({
                "action": "Investigate recent issues and review logs",
                "severity": "high",
                "confidence": 0.85,
            })
        elif score < 0.7:
            suggestions.append({
                "action": "Monitor system more closely for trends",
                "severity": "medium",
                "confidence": 0.75,
            })
        
        # Issue-specific suggestions
        if issue and "latency" in issue.lower():
            suggestions.append({
                "action": "Scale up resources or optimize queries",
                "severity": "medium",
                "confidence": 0.7,
            })
        elif issue and "error" in issue.lower():
            suggestions.append({
                "action": "Review error logs and application traces",
                "severity": "high",
                "confidence": 0.8,
            })
        
        return suggestions

    @staticmethod
    def compute_confidence(events: List[Dict[str, Any]], issue: Optional[str]) -> float:
        """Compute confidence score for this reasoning output."""
        if not events:
            return 0.35

        confidence = 0.5
        evidence_boost = min(0.3, len(events) * 0.02)
        confidence += evidence_boost

        if issue:
            confidence += 0.1

        # Blend across diverse signal types (logs, metrics, traces).
        signal_types = {e.get("type") for e in events if e.get("type")}
        confidence += min(0.1, len(signal_types) * 0.04)

        return max(0.0, min(1.0, round(confidence, 2)))

    @staticmethod
    def evaluate_health(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Single-call API returning issue, reasoning, suggestions, and confidence."""
        score = ReasoningEngine.compute_health_score(events)
        issue = ReasoningEngine.identify_primary_issue(events)
        reasoning = ReasoningEngine.generate_reasoning_narrative(events)
        suggestions = ReasoningEngine.generate_suggestions(score, issue)
        confidence = ReasoningEngine.compute_confidence(events, issue)

        return {
            "health_score": score,
            "primary_issue": issue,
            "reasoning": reasoning,
            "suggestions": suggestions,
            "confidence": confidence,
        }
