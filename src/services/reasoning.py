"""Refined agentic reasoning engine for health scoring with metric-specific scoring."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure debug logging for pipeline tracing
_debug_logger = logging.getLogger(f"{__name__}.debug")
_debug_logger.setLevel(logging.DEBUG)


class ReasoningEngine:
    """
    Refined reasoning engine with metric-specific scoring and explainability.
    
    Scoring model (internal 0-100 scale, normalized to 0.0-1.0 for API):
    - Start at 100 points
    - Apply metric-specific penalties with severity bands
    - Multiply by recency weight (linear decay over 60 min)
    - Cap penalties per category (avoid over-penalizing repeated issues)
    - Return normalized score (0.0-1.0) and score breakdown
    
    Status mapping (internal 0-100):
    - 80-100: healthy
    - 50-79: degraded
    - 0-49: critical
    """
    
    # Category penalty caps (max deduction per category)
    CATEGORY_CAPS = {
        "cpu": 30,
        "ram": 30,
        "error_rate": 35,
        "latency": 30,
        "event_spike": 30,
        "external_load": 25,
        "logs": 25,
        "traces": 30,
        "active_users": 15,
    }

    @staticmethod
    def compute_recency_weight(timestamp: Any) -> float:
        """
        Compute recency weight: 1.0 (fresh) to 0.0 (1+ hour old).
        
        Linear decay over 60 minutes:
        - 0 min: 1.0
        - 15 min: 0.75
        - 30 min: 0.50
        - 45 min: 0.25
        - 60+ min: 0.0
        """
        if not timestamp:
            return 1.0
        
        try:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).replace(tzinfo=None)
            
            age_seconds = (datetime.utcnow() - timestamp).total_seconds()
            age_minutes = age_seconds / 60
            return max(0.0, 1.0 - (age_minutes / 60))
        except Exception:
            return 1.0

    @staticmethod
    def score_cpu(cpu_percent: float) -> Tuple[int, str]:
        """Score CPU with severity bands."""
        cpu = float(cpu_percent) if cpu_percent is not None else 0
        
        if cpu < 70:
            return 0, "CPU normal"
        elif cpu < 85:
            return 10, "CPU elevated 70-84%"
        elif cpu < 95:
            return 20, "CPU high 85-94%"
        else:
            return 30, "CPU critical >=95%"

    @staticmethod
    def score_ram(ram_value: float, is_percent: bool = True) -> Tuple[int, str]:
        """Score RAM with severity bands. Can be percentage or MB."""
        ram = float(ram_value) if ram_value is not None else 0
        
        if is_percent or ram <= 100:  # Assume percentage if <= 100
            if ram < 75:
                return 0, "RAM normal"
            elif ram < 85:
                return 10, "RAM elevated 75-84%"
            elif ram < 95:
                return 20, "RAM high 85-94%"
            else:
                return 30, "RAM critical >=95%"
        else:  # MB-based thresholds (temporary until RAM % is available)
            if ram < 800:
                return 0, "RAM normal"
            elif ram < 1000:
                return 10, "RAM elevated 800-999 MB"
            elif ram < 1200:
                return 20, "RAM high 1000-1199 MB"
            else:
                return 30, "RAM critical >=1200 MB"

    @staticmethod
    def score_error_rate(error_rate: float) -> Tuple[int, str]:
        """Score error rate. Accepts decimal (0.05) or percentage (5)."""
        rate = float(error_rate) if error_rate is not None else 0
        
        # Normalize to percentage if needed
        if rate <= 1:
            rate = rate * 100
        
        if rate < 1:
            return 0, "Error rate normal"
        elif rate < 3:
            return 10, "Error rate elevated 1-3%"
        elif rate < 5:
            return 20, "Error rate high 3-5%"
        else:
            return 35, "Error rate critical >=5%"

    @staticmethod
    def score_latency(latency_ms: float) -> Tuple[int, str]:
        """Score latency. Threshold reduced to 1000ms (was 5000ms)."""
        latency = float(latency_ms) if latency_ms is not None else 0
        
        if latency < 300:
            return 0, "Latency normal"
        elif latency < 1000:
            return 10, "Latency elevated 300-999ms"
        elif latency < 3000:
            return 20, "Latency high 1000-2999ms"
        else:
            return 30, "Latency critical >=3000ms"

    @staticmethod
    def score_event_spike(spike: float) -> Tuple[int, str]:
        """Score event spike magnitude."""
        spike_val = float(spike) if spike is not None else 0
        
        if spike_val == 0:
            return 0, "Event spike normal"
        elif spike_val < 5:
            return 10, f"Event spike elevated {spike_val:.0f}"
        elif spike_val < 10:
            return 20, f"Event spike high {spike_val:.0f}"
        else:
            return 30, f"Event spike critical {spike_val:.0f}"

    @staticmethod
    def score_external_load(load: float) -> Tuple[int, str]:
        """Score external load."""
        load_val = float(load) if load is not None else 0
        
        if load_val < 0.05:
            return 0, "External load normal"
        elif load_val < 0.10:
            return 8, f"External load elevated {load_val:.2f}"
        elif load_val < 0.20:
            return 15, f"External load high {load_val:.2f}"
        else:
            return 25, f"External load critical {load_val:.2f}"

    @staticmethod
    def score_active_users(users: float) -> Tuple[int, str]:
        """Score active user count. Simulator baseline ~300-400 users."""
        user_count = float(users) if users is not None else 0
        
        if user_count < 300:
            return 0, "Active users normal"
        elif user_count < 500:
            return 5, f"Active users elevated {user_count:.0f}"
        elif user_count < 700:
            return 10, f"Active users high {user_count:.0f}"
        else:
            return 15, f"Active users critical {user_count:.0f}"

    @staticmethod
    def score_log_event(level: str) -> Tuple[int, str]:
        """Score log events."""
        level_lower = str(level).lower() if level else ""
        
        if level_lower == "warning":
            return 10, "Log warning"
        elif level_lower == "error":
            return 20, "Log error"
        else:
            return 0, "Log info/debug"

    @staticmethod
    def score_trace_event(status: str, duration_ms: float = None) -> Tuple[int, str]:
        """Score trace events."""
        status_lower = str(status).lower() if status else ""
        
        if status_lower == "error":
            return 25, "Trace error status"
        elif duration_ms and float(duration_ms) > 3000:
            return 30, f"Trace very slow {duration_ms:.0f}ms"
        elif duration_ms and float(duration_ms) > 1000:
            return 20, f"Trace slow {duration_ms:.0f}ms"
        else:
            return 0, "Trace normal"

    @staticmethod
    def compute_health_score_with_breakdown(
        events: List[Dict[str, Any]],
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Compute refined health score (0.0-1.0) with detailed score breakdown.
        
        Returns: (score, breakdown)
        - score: normalized 0.0-1.0
        - breakdown: list of penalty entries explaining the score
        """
        base_score = 100
        
        if not events:
            return 0.5, []  # Unknown state
        
        category_penalties = {
            "cpu": 0,
            "ram": 0,
            "error_rate": 0,
            "latency": 0,
            "event_spike": 0,
            "external_load": 0,
            "logs": 0,
            "traces": 0,
            "active_users": 0,
        }
        
        breakdown_items = []
        
        for event in events:
            timestamp = event.get("timestamp")
            recency = ReasoningEngine.compute_recency_weight(timestamp)
            
            # CPU
            cpu = event.get("cpu_percent") or event.get("cpu")
            if cpu is not None:
                raw_penalty, reason = ReasoningEngine.score_cpu(float(cpu))
                penalty = raw_penalty * recency
                if penalty > category_penalties["cpu"]:
                    category_penalties["cpu"] = penalty
                    breakdown_items.append({
                        "category": "cpu",
                        "value": float(cpu),
                        "unit": "%",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # RAM
            ram = event.get("ram_percent") or event.get("ram")
            if ram is not None:
                is_percent = event.get("ram_percent") is not None
                raw_penalty, reason = ReasoningEngine.score_ram(float(ram), is_percent)
                penalty = raw_penalty * recency
                if penalty > category_penalties["ram"]:
                    category_penalties["ram"] = penalty
                    breakdown_items.append({
                        "category": "ram",
                        "value": float(ram),
                        "unit": "%" if is_percent else "MB",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # Error rate
            error_rate = event.get("error_rate")
            if error_rate is not None:
                raw_penalty, reason = ReasoningEngine.score_error_rate(float(error_rate))
                penalty = raw_penalty * recency
                if penalty > category_penalties["error_rate"]:
                    category_penalties["error_rate"] = penalty
                    breakdown_items.append({
                        "category": "error_rate",
                        "value": float(error_rate),
                        "unit": "%",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # Latency
            latency_ms = event.get("latency_ms") or event.get("duration_ms")
            if latency_ms is not None and event.get("type") != "log":
                raw_penalty, reason = ReasoningEngine.score_latency(float(latency_ms))
                penalty = raw_penalty * recency
                if penalty > category_penalties["latency"]:
                    category_penalties["latency"] = penalty
                    breakdown_items.append({
                        "category": "latency",
                        "value": float(latency_ms),
                        "unit": "ms",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # Event spike
            event_spike = event.get("event_spike")
            if event_spike is not None:
                raw_penalty, reason = ReasoningEngine.score_event_spike(float(event_spike))
                penalty = raw_penalty * recency
                if penalty > category_penalties["event_spike"]:
                    category_penalties["event_spike"] = penalty
                    breakdown_items.append({
                        "category": "event_spike",
                        "value": float(event_spike),
                        "unit": "count",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # External load
            external_load = event.get("external_load")
            if external_load is not None:
                raw_penalty, reason = ReasoningEngine.score_external_load(float(external_load))
                penalty = raw_penalty * recency
                if penalty > category_penalties["external_load"]:
                    category_penalties["external_load"] = penalty
                    breakdown_items.append({
                        "category": "external_load",
                        "value": float(external_load),
                        "unit": "load",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # Active users
            active_users = event.get("active_users")
            if active_users is not None:
                raw_penalty, reason = ReasoningEngine.score_active_users(float(active_users))
                penalty = raw_penalty * recency
                if penalty > category_penalties["active_users"]:
                    category_penalties["active_users"] = penalty
                    breakdown_items.append({
                        "category": "active_users",
                        "value": float(active_users),
                        "unit": "count",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # Log events
            if event.get("type") == "log":
                level = event.get("level")
                raw_penalty, reason = ReasoningEngine.score_log_event(level)
                penalty = raw_penalty * recency
                if penalty > category_penalties["logs"]:
                    category_penalties["logs"] = penalty
                    breakdown_items.append({
                        "category": "logs",
                        "value": level,
                        "unit": "level",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
            
            # Trace events
            if event.get("type") == "trace":
                status = event.get("status")
                duration = event.get("duration_ms")
                raw_penalty, reason = ReasoningEngine.score_trace_event(status, duration)
                penalty = raw_penalty * recency
                if penalty > category_penalties["traces"]:
                    category_penalties["traces"] = penalty
                    breakdown_items.append({
                        "category": "traces",
                        "value": f"{status} ({duration}ms)" if duration else status,
                        "unit": "status",
                        "raw_penalty": raw_penalty,
                        "recency_weight": round(recency, 2),
                        "penalty": round(penalty, 2),
                        "reason": reason,
                    })
        
        # Cap penalties per category
        capped_penalties = {
            cat: min(penalty, ReasoningEngine.CATEGORY_CAPS.get(cat, 30))
            for cat, penalty in category_penalties.items()
        }
        
        total_penalty = sum(capped_penalties.values())
        final_score_100 = max(0, min(100, base_score - total_penalty))
        normalized_score = final_score_100 / 100.0
        
        # Sort breakdown by penalty (highest first)
        breakdown_items.sort(key=lambda x: x["penalty"], reverse=True)
        
        return normalized_score, breakdown_items

    @staticmethod
    def compute_health_score(events: List[Dict[str, Any]]) -> float:
        """
        Compute refined health score (0.0-1.0) without breakdown.
        """
        score, _ = ReasoningEngine.compute_health_score_with_breakdown(events)
        return score

    @staticmethod
    def identify_primary_issue(events: List[Dict[str, Any]]) -> Optional[str]:
        """Identify primary issue with improved logic and recency awareness."""
        if not events:
            _debug_logger.debug(f"[REASONING] No events to identify issue from")
            return None
        
        # Priority: recent critical conditions first
        for event in events:
            recency = ReasoningEngine.compute_recency_weight(event.get("timestamp"))
            if recency < 0.1:  # Skip very old events
                continue
            
            if event.get("type") == "log":
                level = event.get("level", "").lower()
                if level == "error":
                    return f"Error detected: {event.get('message', 'Unknown error')}"
            
            elif event.get("type") == "trace":
                status = event.get("status", "").lower()
                if status == "error":
                    return f"Trace error detected: {event.get('operation', 'unknown')}"
                duration = float(event.get("duration_ms", 0))
                if duration > 3000:
                    return f"Critical latency: {duration:.0f}ms"
            
            elif event.get("type") == "metric":
                # Check metric-based issues
                cpu = event.get("cpu_percent")
                ram = event.get("ram_percent") or event.get("ram")
                error_rate = event.get("error_rate")
                
                if cpu and float(cpu) >= 90:
                    return f"Critical CPU usage: {cpu:.1f}%"
                if ram:
                    ram_float = float(ram)
                    if ram_float > 100:  # MB-based
                        if ram_float >= 1200:
                            return f"Critical RAM usage: {ram_float:.0f} MB"
                    else:  # Percentage-based
                        if ram_float >= 95:
                            return f"Critical RAM usage: {ram_float:.0f}%"
                if error_rate and float(error_rate) >= 0.05:
                    return f"Critical error rate: {error_rate}"
        
        _debug_logger.debug(f"[REASONING] No issues identified")
        return None

    @staticmethod
    def generate_reasoning_narrative(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate reasoning narrative."""
        if not events:
            return {"reasoning": "Insufficient data", "evidence": []}
        
        reasoning_steps = []
        
        logs = [e for e in events if e.get("type") == "log"]
        traces = [e for e in events if e.get("type") == "trace"]
        metrics = [e for e in events if e.get("type") == "metric"]
        
        if metrics:
            reasoning_steps.append(f"Analyzed {len(metrics)} metric events")
        if logs:
            error_count = len([e for e in logs if e.get("level") == "error"])
            if error_count:
                reasoning_steps.append(f"Found {error_count} error logs")
        if traces:
            slow_traces = [e for e in traces if float(e.get("duration_ms", 0)) > 1000]
            if slow_traces:
                reasoning_steps.append(f"Found {len(slow_traces)} slow traces (>1000ms)")
        
        return {
            "reasoning_chain": reasoning_steps,
            "evidence_count": len(events),
            "recommendation": "Monitor metrics and logs closely; escalate if critical conditions persist.",
        }

    @staticmethod
    def generate_suggestions(score: float, issue: Optional[str]) -> List[Dict[str, Any]]:
        """Generate suggestions based on refined scoring."""
        suggestions = []
        
        if score < 0.3:
            suggestions.append({
                "action": "Trigger immediate incident response and page on-call team",
                "severity": "critical",
                "confidence": 0.95,
            })
        elif score < 0.5:
            suggestions.append({
                "action": "Investigate degradation and prepare escalation",
                "severity": "high",
                "confidence": 0.85,
            })
        elif score < 0.8:
            suggestions.append({
                "action": "Monitor system closely for trends",
                "severity": "medium",
                "confidence": 0.75,
            })
        
        if issue:
            if "CPU" in issue:
                suggestions.append({
                    "action": "Review CPU utilization; check for runaway processes",
                    "severity": "high",
                    "confidence": 0.8,
                })
            elif "RAM" in issue or "Memory" in issue:
                suggestions.append({
                    "action": "Inspect memory usage and check for memory leaks",
                    "severity": "high",
                    "confidence": 0.8,
                })
            elif "latency" in issue.lower():
                suggestions.append({
                    "action": "Analyze slow queries, network latency, and database performance",
                    "severity": "high",
                    "confidence": 0.75,
                })
            elif "error" in issue.lower():
                suggestions.append({
                    "action": "Review application logs and error traces for root cause",
                    "severity": "high",
                    "confidence": 0.8,
                })
        
        return suggestions
