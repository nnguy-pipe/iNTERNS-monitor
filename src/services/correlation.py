"""Correlation engine for cross-system event linking."""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    MVP correlation engine that links related events across systems.
    
    Enables detection of cascading failures across observability, workflow, and batch systems.
    """

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        """Best-effort timestamp parsing for normalized events and persisted payloads."""
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
    def correlate_by_time_window(
        events: List[Dict[str, Any]],
        system_name: Optional[str] = None,
        window_minutes: int = 5,
    ) -> List[List[Dict[str, Any]]]:
        """
        Group events into correlated clusters based on time proximity.
        
        Events within N minutes of each other likely related.
        """
        if not events:
            return []
        
        # Sort by timestamp
        sorted_events = sorted(
            events,
            key=lambda e: CorrelationEngine._parse_timestamp(e.get("timestamp"))
        )
        
        clusters = []
        current_cluster = [sorted_events[0]]
        window = timedelta(minutes=window_minutes)
        
        for event in sorted_events[1:]:
            event_time = CorrelationEngine._parse_timestamp(event.get("timestamp"))
            cluster_start = CorrelationEngine._parse_timestamp(current_cluster[0].get("timestamp"))
            
            if event_time - cluster_start <= window:
                current_cluster.append(event)
            else:
                if current_cluster:
                    clusters.append(current_cluster)
                current_cluster = [event]
        
        if current_cluster:
            clusters.append(current_cluster)
        
        return clusters

    @staticmethod
    def correlate_by_trace_id(events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group events by correlation_id or trace_id for explicit tracing.
        """
        correlations = defaultdict(list)
        
        for event in events:
            trace_id = event.get("correlation_id") or event.get("trace_id")
            if trace_id:
                correlations[trace_id].append(event)
        
        return dict(correlations)

    @staticmethod
    def detect_cascading_failures(
        events: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Detect patterns that suggest cascading failures.
        
        Examples:
        - Error in observability system triggers workflow failure
        - One service's latency spike causes dependent service's errors
        """
        cascades = []
        
        # Simple pattern: error log followed by slow traces
        error_logs = [e for e in events if e.get("type") == "log" and e.get("level") == "error"]
        slow_traces = [e for e in events if e.get("type") == "trace" and float(e.get("duration_ms", 0)) > 5000]
        
        if error_logs and slow_traces:
            cascades.append({
                "pattern": "Error leading to latency",
                "error_count": len(error_logs),
                "slow_trace_count": len(slow_traces),
                "likelihood": "high",
            })
        
        # Pattern: multiple systems affected
        sources = set(e.get("source") for e in events if e.get("source"))
        if len(sources) > 1:
            cascades.append({
                "pattern": "Multi-system impact",
                "affected_systems": len(sources),
                "likelihood": "medium",
            })
        
        return cascades

    @staticmethod
    def identify_related_events(
        pivot_event: Dict[str, Any],
        all_events: List[Dict[str, Any]],
        max_distance_seconds: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        Find events related to a pivot event.
        
        Heuristics:
        - Same system name
        - Same trace ID
        - Within time window
        - Same environment
        """
        related = []
        pivot_time = CorrelationEngine._parse_timestamp(pivot_event.get("timestamp"))
        pivot_system = pivot_event.get("system_name")
        pivot_trace = pivot_event.get("correlation_id") or pivot_event.get("trace_id")
        
        for event in all_events:
            if event.get("id") == pivot_event.get("id"):
                continue  # Skip self
            
            event_time = CorrelationEngine._parse_timestamp(event.get("timestamp"))
            time_diff = abs((event_time - pivot_time).total_seconds())
            
            # Same trace ID is strong signal
            if pivot_trace and (event.get("correlation_id") or event.get("trace_id")) == pivot_trace:
                related.append(event)
            # Same system + same time window
            elif (event.get("system_name") == pivot_system and 
                  time_diff <= max_distance_seconds and
                  event.get("environment") == pivot_event.get("environment")):
                related.append(event)
        
        return related

    @staticmethod
    def build_event_graph(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a graph representation showing event relationships.
        
        Returns: {nodes: [...], edges: [...]}
        """
        nodes = []
        edges = []
        
        # Create nodes for each event
        for i, event in enumerate(events):
            nodes.append({
                "id": event.get("id", f"event-{i}"),
                "type": event.get("type"),
                "source": event.get("source"),
                "system": event.get("system_name"),
                "timestamp": event.get("timestamp"),
            })
        
        # Create edges for related events (trace ID or time window)
        trace_groups = defaultdict(list)
        for i, event in enumerate(events):
            trace_id = event.get("correlation_id") or event.get("trace_id")
            if trace_id:
                trace_groups[trace_id].append(i)
        
        for trace_id, indices in trace_groups.items():
            for i, j in zip(indices[:-1], indices[1:]):
                edges.append({
                    "from": events[i].get("id", f"event-{i}"),
                    "to": events[j].get("id", f"event-{j}"),
                    "relation": "same-trace",
                })
        
        return {"nodes": nodes, "edges": edges}
