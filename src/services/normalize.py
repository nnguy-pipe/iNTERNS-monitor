"""Simple normalization pipeline for MVP."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NormalizationPipeline:
    """MVP normalization - handles metrics, logs, and basic events."""

    @staticmethod
    def normalize(event_data: Dict[str, Any], event_type: str) -> Optional[Dict[str, Any]]:
        """
        Normalize incoming event to unified schema.
        
        Returns normalized data or None if normalization fails.
        """
        try:
            if event_type == "metric":
                return NormalizationPipeline._normalize_metric(event_data)
            elif event_type == "log":
                return NormalizationPipeline._normalize_log(event_data)
            elif event_type == "trace":
                return NormalizationPipeline._normalize_trace(event_data)
            else:
                # Pass through business events as-is
                return event_data
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return None

    @staticmethod
    def _normalize_metric(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize metric event to standard format."""
        return {
            "type": "metric",
            "name": data.get("metric_name", "unknown"),
            "value": float(data.get("value", 0)),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "labels": data.get("labels", {}),
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
