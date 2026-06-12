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
        # Check if this is a simulator metric with subsystems structure
        if "subsystems" in data and isinstance(data.get("subsystems"), dict):
            # Aggregate metrics from subsystems
            return NormalizationPipeline._normalize_subsystem_metrics(data)
        
        # Fall back to simple metric normalization
        return {
            "type": "metric",
            "name": data.get("metric_name", "unknown"),
            "value": float(data.get("value", 0)),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "labels": data.get("labels", {}),
        }

    @staticmethod
    def _normalize_subsystem_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize simulator subsystem metrics to standard format.
        
        Uses WORST-CASE (max) values across subsystems to surface critical issues.
        This ensures a single critical subsystem doesn't get masked by healthy ones.
        """
        subsystems = data.get("subsystems", {})
        summary = data.get("summary", {})
        
        # Extract CPU and RAM data
        cpus = [float(s.get("cpu", 0)) for s in subsystems.values() if "cpu" in s]
        rams = [float(s.get("ram", 0)) for s in subsystems.values() if "ram" in s]
        users_list = [int(s.get("active_users", 0)) for s in subsystems.values() if "active_users" in s]
        loads = [float(s.get("external_load", 0)) for s in subsystems.values() if "external_load" in s]
        
        # Use WORST-CASE (max) metrics, not averages, to surface critical subsystems
        # This ensures: if 1 of 4 subsystems is critical, overall health shows critical
        cpu_max = max(cpus) if cpus else 0
        cpu_avg = (sum(cpus) / len(cpus)) if cpus else 0  # Keep for reference
        
        ram_max = max(rams) if rams else 0
        ram_avg = (sum(rams) / len(rams)) if rams else 0  # Keep for reference
        ram_total = sum(rams) if rams else 0
        
        users_total = sum(users_list) if users_list else 0
        load_max = max(loads) if loads else 0
        load_avg = (sum(loads) / len(loads)) if loads else 0
        
        # Calculate RAM percentage for WORST subsystem
        # Each subsystem has ~800-1600 MB max individually
        max_ram_per_subsystem = 3200  # Adjust based on actual subsystem capacity
        ram_percent_worst = min(100, (ram_max / max_ram_per_subsystem * 100)) if max_ram_per_subsystem > 0 else 0
        
        # Also compute avg RAM percent for reference
        ram_total_percent = min(200, (ram_total / (max_ram_per_subsystem) * 100)) if max_ram_per_subsystem > 0 else 0
        
        return {
            "type": "metric",
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "preset": data.get("preset", "unknown"),
            "tick": data.get("tick", 0),
            # CPU metrics (use MAX to surface worst subsystem)
            "cpu_percent": round(cpu_max, 2),  # Worst CPU
            "cpu_avg": round(cpu_avg, 2),      # For reference
            "cpu_max": round(cpu_max, 2),      # Worst CPU
            # RAM metrics (use MAX individual subsystem value)
            "ram": round(ram_max, 2),           # Worst individual subsystem RAM in MB
            "ram_percent": round(ram_percent_worst, 2),  # Worst subsystem as percent
            "ram_avg": round(ram_avg, 2),              # For reference
            "ram_total": round(ram_total, 2),          # All subsystems combined
            # User metrics
            "active_users": users_total,
            # External load (use worst)
            "external_load": round(load_max, 2),
            "external_load_avg": round(load_avg, 2),
            # Subsystem breakdown for detail
            "subsystems": subsystems,
            "summary": summary,
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
