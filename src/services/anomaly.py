"""Anomaly detection engine for normalized telemetry streams."""

import logging
from collections import defaultdict
from datetime import datetime
from math import sqrt
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnomalyEngine:
    """Detect anomalies using statistical and rule-based hooks."""

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except Exception:
                return datetime.utcnow()
        return datetime.utcnow()

    @staticmethod
    def detect_statistical_anomalies(
        events: List[Dict[str, Any]],
        z_threshold: float = 2.5,
        min_samples: int = 5,
    ) -> List[Dict[str, Any]]:
        """Use a simple z-score approach for metric streams grouped by metric name."""
        metric_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        anomalies: List[Dict[str, Any]] = []

        for event in events:
            if event.get("type") != "metric":
                continue
            name = str(event.get("name", "unknown"))
            try:
                _ = float(event.get("value", 0))
            except (TypeError, ValueError):
                continue
            metric_groups[name].append(event)

        for metric_name, rows in metric_groups.items():
            if len(rows) < min_samples:
                continue

            values = [float(r.get("value", 0)) for r in rows]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = sqrt(variance)

            if std_dev == 0:
                continue

            for row in rows:
                value = float(row.get("value", 0))
                z_score = abs((value - mean) / std_dev)
                if z_score >= z_threshold:
                    anomalies.append(
                        {
                            "type": "statistical",
                            "metric": metric_name,
                            "value": value,
                            "z_score": round(z_score, 2),
                            "severity": "high" if z_score >= (z_threshold * 1.5) else "medium",
                            "reason": f"Metric '{metric_name}' deviates from baseline",
                            "timestamp": AnomalyEngine._parse_timestamp(row.get("timestamp")).isoformat(),
                            "event_id": row.get("id"),
                        }
                    )

        return anomalies

    @staticmethod
    def detect_rule_based_anomalies(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect deterministic anomaly patterns in logs/traces/metrics."""
        anomalies: List[Dict[str, Any]] = []

        error_logs = [
            e
            for e in events
            if e.get("type") == "log" and str(e.get("level", "")).lower() == "error"
        ]
        if len(error_logs) >= 3:
            latest_ts = max(AnomalyEngine._parse_timestamp(e.get("timestamp")) for e in error_logs)
            anomalies.append(
                {
                    "type": "rule",
                    "rule": "error-log-burst",
                    "severity": "high",
                    "reason": f"Detected {len(error_logs)} error logs in recent stream",
                    "timestamp": latest_ts.isoformat(),
                }
            )

        for event in events:
            etype = event.get("type")
            if etype == "trace":
                duration = float(event.get("duration_ms", 0))
                status = str(event.get("status", "")).lower()
                if duration > 5000 or status == "error":
                    anomalies.append(
                        {
                            "type": "rule",
                            "rule": "trace-latency-or-error",
                            "severity": "high" if duration > 8000 or status == "error" else "medium",
                            "reason": f"Trace anomaly: duration={duration}ms status={status or 'unknown'}",
                            "timestamp": AnomalyEngine._parse_timestamp(event.get("timestamp")).isoformat(),
                            "event_id": event.get("id"),
                        }
                    )
            elif etype == "metric":
                name = str(event.get("name", "metric"))
                value = float(event.get("value", 0))
                if value < 0:
                    anomalies.append(
                        {
                            "type": "rule",
                            "rule": "negative-metric",
                            "severity": "medium",
                            "reason": f"Metric '{name}' has invalid negative value {value}",
                            "timestamp": AnomalyEngine._parse_timestamp(event.get("timestamp")).isoformat(),
                            "event_id": event.get("id"),
                        }
                    )

        return anomalies

    @staticmethod
    def detect_anomalies(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run both anomaly detectors and deduplicate equivalent findings."""
        statistical = AnomalyEngine.detect_statistical_anomalies(events)
        rule_based = AnomalyEngine.detect_rule_based_anomalies(events)

        combined = statistical + rule_based
        deduped: List[Dict[str, Any]] = []
        seen = set()

        for item in combined:
            key = (
                item.get("type"),
                item.get("rule"),
                item.get("metric"),
                item.get("event_id"),
                item.get("reason"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)

        return deduped
