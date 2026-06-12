"""Agentic reasoning engine for health scoring."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

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
        
        score = 1.0
        now = datetime.utcnow()
        penalties_applied = []
        
        for event in events:
            # Weight recent events higher
            event_timestamp = event.get("timestamp")
            if isinstance(event_timestamp, str):
                try:
                    event_timestamp = datetime.fromisoformat(event_timestamp)
                except:
                    event_timestamp = now
            
            event_age_seconds = (now - event_timestamp).total_seconds()
            recency_weight = max(0, 1.0 - (event_age_seconds / 3600))  # Decay over 1 hour
            
            # Check event type and apply penalties
            event_type = event.get("type")
            
            if event_type == "log":
                level = event.get("level", "").lower()
                if level == "error":
                    penalty = 0.3 * recency_weight
                    score -= penalty
                    penalties_applied.append(f"error_log({penalty:.3f})")
                elif level == "warning":
                    penalty = 0.15 * recency_weight
                    score -= penalty
                    penalties_applied.append(f"warning_log({penalty:.3f})")
            
            elif event_type == "metric":
                value = float(event.get("value", 0))
                # Simple thresholds for MVP
                if value > 1000:  # Abnormally high
                    penalty = 0.2 * recency_weight
                    score -= penalty
                    penalties_applied.append(f"high_metric({value:.1f},{penalty:.3f})")
                elif value < 0:  # Invalid
                    penalty = 0.1 * recency_weight
                    score -= penalty
                    penalties_applied.append(f"invalid_metric({penalty:.3f})")
            
            elif event_type == "trace":
                duration = float(event.get("duration_ms", 0))
                status = event.get("status", "").lower()
                if status == "error":
                    penalty = 0.25 * recency_weight
                    score -= penalty
                    penalties_applied.append(f"error_trace({penalty:.3f})")
                elif duration > 5000:  # >5s duration
                    penalty = 0.1 * recency_weight
                    score -= penalty
                    penalties_applied.append(f"slow_trace({duration}ms,{penalty:.3f})")
        
        # Clamp to 0.0-1.0
        final_score = max(0.0, min(1.0, score))
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
