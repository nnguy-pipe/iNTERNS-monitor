"""Simple normalization pipeline for MVP."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure debug logging for pipeline tracing
_debug_logger = logging.getLogger(f"{__name__}.debug")
_debug_logger.setLevel(logging.DEBUG)


class NormalizationPipeline:
    """MVP normalization - handles metrics, logs, and basic events."""

    @staticmethod
    def normalize(event_data: Dict[str, Any], event_type: str) -> Optional[Dict[str, Any]]:
        """
        Normalize incoming event to unified schema.
        
        Returns normalized data or None if normalization fails.
        """
        _debug_logger.debug(f"[NORMALIZE] Starting normalization: event_type={event_type}, data_keys={list(event_data.keys())}")
        
        try:
            if event_type == "metric":
                result = NormalizationPipeline._normalize_metric(event_data)
                _debug_logger.debug(f"[NORMALIZE] Metric normalized: name={result.get('name')}, value={result.get('value')}, timestamp={result.get('timestamp')}")
                return result
            elif event_type == "log":
                result = NormalizationPipeline._normalize_log(event_data)
                _debug_logger.debug(f"[NORMALIZE] Log normalized: level={result.get('level')}, message={result.get('message')[:50]}, timestamp={result.get('timestamp')}")
                return result
            elif event_type == "trace":
                result = NormalizationPipeline._normalize_trace(event_data)
                _debug_logger.debug(f"[NORMALIZE] Trace normalized: operation={result.get('operation')}, duration_ms={result.get('duration_ms')}, status={result.get('status')}")
                return result
            else:
                # Pass through business events as-is
                _debug_logger.debug(f"[NORMALIZE] Business event passed through as-is")
                return event_data
        except Exception as e:
            logger.error(f"Normalization failed for event_type={event_type}: {e}")
            _debug_logger.error(f"[NORMALIZE] FAILED: event_type={event_type}, error={str(e)}")
            return None

    @staticmethod
    def _normalize_metric(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize metric event to standard format."""
        subsystems = data.get("subsystems") if isinstance(data.get("subsystems"), dict) else None

        aggregate_value = data.get("value", 0)
        if subsystems:
            cpu_values = []
            for stats in subsystems.values():
                if isinstance(stats, dict):
                    cpu_values.append(float(stats.get("cpu", 0)))
            if cpu_values:
                aggregate_value = max(cpu_values)

        return {
            "type": "metric",
            "name": data.get("metric_name", "simulator_subsystems" if subsystems else "unknown"),
            "value": float(aggregate_value),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "labels": data.get("labels", {}),
            "preset": data.get("preset"),
            "subsystems": subsystems,
        }

    @staticmethod
    def _normalize_log(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize log event to standard format."""
        return {
            "type": "log",
            "message": data.get("message", ""),
            "level": data.get("level", "info"),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "source": data.get("source", "unknown"),
            "context": data.get("context", {}),
        }

    @staticmethod
    def _normalize_trace(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize trace event to standard format."""
        return {
            "type": "trace",
            "trace_id": data.get("trace_id", ""),
            "span_id": data.get("span_id", ""),
            "operation": data.get("operation", "unknown"),
            "duration_ms": float(data.get("duration_ms", 0)),
            "status": data.get("status", "unknown"),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "tags": data.get("tags", {}),
        }
