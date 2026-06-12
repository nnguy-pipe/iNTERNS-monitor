"""Agentic reasoning engine for health scoring."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# Configure debug logging for pipeline tracing
_debug_logger = logging.getLogger(f"{__name__}.debug")
_debug_logger.setLevel(logging.DEBUG)


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
        _debug_logger.debug(f"[REASONING] Computing health score from {len(events)} events")
        
        if not events:
            _debug_logger.warning(f"[REASONING] No events provided, returning default score 0.5")
            return 0.5  # Unknown state
        
        weighted_health_sum = 0.0
        total_weight = 0.0
        now = datetime.utcnow()
        penalties_applied = []
        
        for event in events:
            # Weight recent events higher
            event_time = ReasoningEngine._parse_timestamp(event.get("timestamp", now))
            event_age_seconds = (now - event_time).total_seconds()
            recency_weight = max(0, 1.0 - (event_age_seconds / 3600))  # Decay over 1 hour
            
            # Check event type and apply penalties
            event_type = event.get("type")
            
            event_penalty = 0.0

            if event_type == "log":
                level = event.get("level", "").lower()
                if level == "error":
                    event_penalty += 0.65
                    penalties_applied.append(f"error_log({0.65 * recency_weight:.3f})")
                elif level == "warning":
                    event_penalty += 0.35
                    penalties_applied.append(f"warning_log({0.35 * recency_weight:.3f})")
            
            elif event_type == "metric":
                subsystem_penalty, detail = ReasoningEngine._subsystem_metric_penalty(event)
                if subsystem_penalty > 0:
                    event_penalty += subsystem_penalty
                    penalties_applied.append(
                        f"subsystem_metric({detail},{subsystem_penalty * recency_weight:.3f})"
                    )
                else:
                    value = float(event.get("value", 0))
                    # Simple thresholds for MVP
                    if value > 1000:  # Abnormally high
                        event_penalty += 0.45
                        penalties_applied.append(f"high_metric({value:.1f},{0.45 * recency_weight:.3f})")
                    elif value < 0:  # Invalid
                        event_penalty += 0.3
                        penalties_applied.append(f"invalid_metric({0.3 * recency_weight:.3f})")
            
            elif event_type == "trace":
                duration = float(event.get("duration_ms", 0))
                status = event.get("status", "").lower()
                if status == "error":
                    event_penalty += 0.6
                    penalties_applied.append(f"error_trace({0.6 * recency_weight:.3f})")
                elif duration > 5000:  # >5s duration
                    event_penalty += 0.25
                    penalties_applied.append(f"slow_trace({duration}ms,{0.25 * recency_weight:.3f})")

            event_penalty = min(1.0, event_penalty)
            event_health = 1.0 - event_penalty
            weighted_health_sum += event_health * recency_weight
            total_weight += recency_weight
        
        if total_weight <= 0:
            _debug_logger.warning("[REASONING] No weighted events after scoring, returning default score 0.5")
            return 0.5

        # Clamp to 0.0-1.0
        final_score = max(0.0, min(1.0, weighted_health_sum / total_weight))
        _debug_logger.debug(f"[REASONING] Health score computed: {final_score:.3f} (penalties: {', '.join(penalties_applied)})")
        return final_score

    @staticmethod
    def identify_primary_issue(events: List[Dict[str, Any]]) -> Optional[str]:
        """
        Identify the primary issue from event patterns.
        
        Objective finding: "What is the main problem detected?"
        """
        _debug_logger.debug(f"[REASONING] Identifying primary issue from {len(events)} events")
        
        if not events:
            _debug_logger.debug(f"[REASONING] No events to identify issue from")
            return None
        
        # Look for error logs first (highest priority)
        error_logs = [e for e in events if e.get("type") == "log" and e.get("level") == "error"]
        if error_logs:
            issue = f"Error detected: {error_logs[0].get('message', 'Unknown error')}"
            _debug_logger.debug(f"[REASONING] Primary issue identified: {issue}")
            return issue
        
        # Check for high-latency traces
        slow_traces = [e for e in events if e.get("type") == "trace" and float(e.get("duration_ms", 0)) > 5000]
        if slow_traces:
            duration = slow_traces[0].get("duration_ms")
            issue = f"High latency detected: {duration}ms (threshold: 5000ms)"
            _debug_logger.debug(f"[REASONING] Primary issue identified: {issue}")
            return issue
        
        # Check for abnormal metrics
        subsystem_metrics = [e for e in events if e.get("type") == "metric" and isinstance(e.get("subsystems"), dict)]
        if subsystem_metrics:
            worst_event = max(
                subsystem_metrics,
                key=lambda e: ReasoningEngine._subsystem_metric_penalty(e)[0],
            )
            penalty, detail = ReasoningEngine._subsystem_metric_penalty(worst_event)
            if penalty > 0:
                issue = f"Subsystem pressure detected ({detail})"
                _debug_logger.debug(f"[REASONING] Primary issue identified: {issue}")
                return issue

        abnormal_metrics = [e for e in events if e.get("type") == "metric" and float(e.get("value", 0)) > 1000]
        if abnormal_metrics:
            metric_name = abnormal_metrics[0].get("name")
            value = abnormal_metrics[0].get("value")
            issue = f"Abnormal metric detected: {metric_name}={value}"
            _debug_logger.debug(f"[REASONING] Primary issue identified: {issue}")
            return issue
        
        _debug_logger.debug(f"[REASONING] No issues identified")
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
