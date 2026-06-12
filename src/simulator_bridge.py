"""
simulator_bridge.py

Bridge module to integrate infrastructure simulator daemon with backend API.
Provides easy-to-use client for reading simulator metrics and converting to backend event format.

Usage:
  from src.simulator_bridge import SimulatorClient
  
  client = SimulatorClient("http://localhost:9999")
  metrics = client.get_current_metrics()
  event = client.metrics_to_event("my-service", "production")
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SimulatorClient:
    """Client for reading metrics from infrastructure simulator daemon."""
    
    def __init__(self, base_url: str = "http://localhost:9999", timeout: int = 5):
        """
        Initialize simulator client.
        
        Args:
            base_url: URL of running simulator daemon (default: http://localhost:9999)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """Verify connection to simulator daemon."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Connected to simulator at {self.base_url}")
            return True
        except Exception as e:
            logger.warning(f"Cannot connect to simulator at {self.base_url}: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if simulator daemon is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get current metrics (latest tick).
        
        Returns:
            {
                "tick": int,
                "timestamp": float,
                "preset": str,
                "uptime_seconds": float,
                "subsystems": {
                    "web": {"cpu": float, "ram": float, "active_users": int, ...},
                    "app": {...},
                    "db": {...},
                    "cache": {...}
                }
            }
        """
        try:
            response = requests.get(
                f"{self.base_url}/metrics",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return None
    
    def get_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get summary statistics (aggregated).
        
        Returns:
            {
                "preset": str,
                "total_ticks": int,
                "uptime_seconds": float,
                "subsystems": {
                    "web": {
                        "cpu_avg": float,
                        "cpu_min": float,
                        "cpu_max": float,
                        "ram_avg": float,
                        "ram_min": float,
                        "ram_max": float,
                        "users_avg": float,
                        "users_max": int
                    },
                    ...
                }
            }
        """
        try:
            response = requests.get(
                f"{self.base_url}/summary",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return None
    
    def export_json(self) -> Optional[Dict[str, Any]]:
        """
        Export full metrics history as SQL-compatible JSON.
        
        Returns:
            {
                "simulations": [...],
                "ticks": [...],
                "subsystem_metrics": [...]
            }
        """
        try:
            response = requests.get(
                f"{self.base_url}/export/json",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return None
    
    def export_xml(self) -> Optional[str]:
        """
        Export full metrics history as SQL-compatible XML.
        
        Returns:
            XML string with full simulation data
        """
        try:
            response = requests.get(
                f"{self.base_url}/export/xml",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to export XML: {e}")
            return None
    
    def set_preset(self, preset: str) -> Optional[Dict[str, Any]]:
        """
        Switch simulator to different preset.
        
        Args:
            preset: One of: default, high_cpu, low_cpu, high_ram, low_ram, high_users, low_users
        
        Returns:
            {"status": "ok", "preset": str} or error dict
        """
        valid_presets = ['default', 'high_cpu', 'low_cpu', 'high_ram', 'low_ram', 'high_users', 'low_users']
        if preset not in valid_presets:
            logger.error(f"Invalid preset '{preset}'. Valid: {valid_presets}")
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/preset/{preset}",
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Switched to preset: {preset}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to set preset: {e}")
            return None
    
    def metrics_to_event(self, system_name: str, environment: str = "ci") -> Optional[Dict[str, Any]]:
        """
        Convert current simulator metrics to backend event format.
        
        Args:
            system_name: Name of the system being monitored
            environment: Environment (ci, staging, production)
        
        Returns:
            Event payload ready for /api/events POST endpoint:
            {
                "source": "infrastructure_simulator",
                "source_id": str,
                "event_type": "metric",
                "timestamp": str (ISO 8601),
                "environment": str,
                "system_name": str,
                "data": {
                    "preset": str,
                    "subsystems": {...}
                }
            }
        """
        metrics = self.get_current_metrics()
        if not metrics:
            return None
        
        return {
            "source": "observability",
            "source_id": f"sim_{int(metrics['timestamp'])}_{metrics['tick']}",
            "event_type": "metric",
            "timestamp": datetime.fromtimestamp(metrics['timestamp']).isoformat() + "Z",
            "environment": environment,
            "system_name": system_name,
            "correlation_id": f"{system_name}_{environment}",
            "data": {
                "metric_name": "infrastructure_cpu_avg",
                "value": self._subsystem_summary(metrics['subsystems']).get("cpu_avg", 0),
                "timestamp": datetime.fromtimestamp(metrics['timestamp']).isoformat() + "Z",
                "labels": {
                    "preset": metrics['preset'],
                    "tick": metrics['tick'],
                    "uptime_seconds": metrics['uptime_seconds'],
                    "source": "simulator",
                },
                "subsystems": metrics['subsystems'],
                "summary": self._subsystem_summary(metrics['subsystems']),
            }
        }

    def metrics_to_event_chain(self, system_name: str, environment: str = "ci") -> List[Dict[str, Any]]:
        """
        Convert simulator metrics into a correlated event chain that exercises
        metric/log/trace reasoning, anomaly detection, and correlation paths.
        """
        metrics = self.get_current_metrics()
        if not metrics:
            return []

        subsystems = metrics.get("subsystems", {}) or {}
        summary = self._subsystem_summary(subsystems)
        tick = metrics.get("tick", 0)
        ts = datetime.fromtimestamp(metrics["timestamp"]).isoformat() + "Z"
        correlation_id = f"sim_chain_{system_name}_{environment}_{int(metrics['timestamp'])}_{tick}"

        events: List[Dict[str, Any]] = []

        # Emit at least 5 samples for the same metric name to unlock statistical anomaly checks.
        cpu_values: List[float] = []
        for subsystem, values in subsystems.items():
            cpu = float(values.get("cpu", 0))
            cpu_values.append(cpu)
            events.append(
                {
                    "source": "observability",
                    "source_id": f"sim-{tick}-{subsystem}-cpu",
                    "event_type": "metric",
                    "timestamp": ts,
                    "environment": environment,
                    "system_name": system_name,
                    "correlation_id": correlation_id,
                    "data": {
                        "metric_name": "cpu_usage_percent",
                        "value": cpu,
                        "timestamp": ts,
                        "labels": {
                            "subsystem": subsystem,
                            "preset": metrics.get("preset", "default"),
                        },
                    },
                }
            )

        # Add one aggregate sample with a deterministic outlier in high_cpu mode.
        cpu_avg = float(summary.get("cpu_avg", 0))
        preset = str(metrics.get("preset", "default"))
        cpu_outlier = min(100.0, cpu_avg + (35.0 if preset == "high_cpu" else 5.0))
        events.append(
            {
                "source": "observability",
                "source_id": f"sim-{tick}-aggregate-cpu",
                "event_type": "metric",
                "timestamp": ts,
                "environment": environment,
                "system_name": system_name,
                "correlation_id": correlation_id,
                "data": {
                    "metric_name": "cpu_usage_percent",
                    "value": round(cpu_outlier, 2),
                    "timestamp": ts,
                    "labels": {
                        "subsystem": "aggregate",
                        "preset": preset,
                    },
                },
            }
        )

        # Add a workflow log burst to trigger rule-based anomaly detection and issue identification.
        for idx in range(3):
            events.append(
                {
                    "source": "workflow",
                    "source_id": f"sim-{tick}-wf-error-{idx}",
                    "event_type": "log",
                    "timestamp": ts,
                    "environment": environment,
                    "system_name": system_name,
                    "correlation_id": correlation_id,
                    "data": {
                        "message": f"Pipeline stage failed on tick {tick} (attempt {idx + 1})",
                        "level": "error",
                        "timestamp": ts,
                        "source": "github_actions",
                        "context": {
                            "preset": preset,
                            "tick": tick,
                        },
                    },
                }
            )

        # Add a slow trace to create latency signal and cascading pattern detection.
        events.append(
            {
                "source": "batch",
                "source_id": f"sim-{tick}-trace",
                "event_type": "trace",
                "timestamp": ts,
                "environment": environment,
                "system_name": system_name,
                "correlation_id": correlation_id,
                "data": {
                    "trace_id": correlation_id,
                    "span_id": f"span-{tick}",
                    "operation": "deploy_validation",
                    "duration_ms": 6200 if preset == "high_cpu" else 5400,
                    "status": "error" if preset in {"high_cpu", "high_users", "high_ram"} else "ok",
                    "timestamp": ts,
                    "tags": {
                        "preset": preset,
                        "system": system_name,
                    },
                },
            }
        )

        return events
    
    @staticmethod
    def _subsystem_summary(subsystems: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate subsystem metrics."""
        cpus = [s['cpu'] for s in subsystems.values()]
        rams = [s['ram'] for s in subsystems.values()]
        users = [s['active_users'] for s in subsystems.values()]
        
        return {
            'cpu_avg': round(sum(cpus) / len(cpus), 2) if cpus else 0,
            'cpu_max': round(max(cpus), 2) if cpus else 0,
            'ram_avg': round(sum(rams) / len(rams), 2) if rams else 0,
            'ram_total': round(sum(rams), 2) if rams else 0,
            'active_users_total': sum(users),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Get daemon health status.
        
        Returns:
            {"status": "running"|"degraded", "tick": int, "preset": str, "uptime": float}
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unavailable", "error": str(e)}


class SimulatorEventBridge:
    """
    Bridge for automatically pulling simulator metrics and converting to events.
    Integrates with backend ingestion pipeline.
    """
    
    def __init__(self, simulator_url: str = "http://localhost:9999"):
        """Initialize event bridge."""
        self.client = SimulatorClient(simulator_url)
    
    def pull_metric_event(self, system_name: str, environment: str = "ci") -> Optional[Dict[str, Any]]:
        """
        Pull current metric from simulator and convert to event.
        
        Args:
            system_name: System being monitored
            environment: Environment name
        
        Returns:
            Event payload ready for backend /api/events endpoint
        """
        if not self.client.is_available():
            logger.warning("Simulator daemon not available")
            return None
        
        return self.client.metrics_to_event(system_name, environment)

    def pull_event_chain(self, system_name: str, environment: str = "ci") -> List[Dict[str, Any]]:
        """Pull current simulator state and convert it into a correlated event chain."""
        if not self.client.is_available():
            logger.warning("Simulator daemon not available")
            return []

        return self.client.metrics_to_event_chain(system_name, environment)
    
    def pull_all_preset_events(self, base_system_name: str = "simulator") -> List[Dict[str, Any]]:
        """
        Pull metrics and generate one event per preset.
        Useful for bulk testing all load patterns.
        
        Returns:
            List of event payloads (one per preset: high_cpu, high_ram, high_users, etc.)
        """
        if not self.client.is_available():
            logger.warning("Simulator daemon not available")
            return []
        
        events = []
        current_preset = self.client.get_current_metrics()
        if not current_preset:
            return events
        
        original_preset = current_preset.get('preset', 'default')
        presets = ['high_cpu', 'low_cpu', 'high_ram', 'low_ram', 'high_users', 'low_users']
        
        try:
            for preset in presets:
                self.client.set_preset(preset)
                event = self.client.metrics_to_event(
                    f"{base_system_name}_{preset}",
                    "ci"
                )
                if event:
                    events.append(event)
                    logger.info(f"Generated event for preset: {preset}")
        finally:
            # Restore original preset
            self.client.set_preset(original_preset)
        
        return events
    
    def continuous_monitoring(self, system_name: str, environment: str = "ci", 
                             interval: float = 1.0, callback=None):
        """
        Continuously pull metrics and invoke callback.
        
        Args:
            system_name: System name
            environment: Environment
            interval: Poll interval in seconds
            callback: Function(event) to invoke with each pulled event
        """
        import time
        
        logger.info(f"Starting continuous monitoring of {system_name} ({environment})")
        
        try:
            while True:
                event = self.pull_metric_event(system_name, environment)
                if event and callback:
                    callback(event)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")


# Convenience functions

def get_simulator_client(url: str = "http://localhost:9999") -> Optional[SimulatorClient]:
    """Get a simulator client if available."""
    try:
        client = SimulatorClient(url)
        if client.is_available():
            return client
    except:
        pass
    return None


def pull_simulator_metric(system_name: str, environment: str = "ci", 
                         simulator_url: str = "http://localhost:9999") -> Optional[Dict[str, Any]]:
    """
    Quick function to pull one metric event from simulator.
    
    Returns event ready for backend /api/events POST endpoint.
    """
    client = get_simulator_client(simulator_url)
    if not client:
        return None
    return client.metrics_to_event(system_name, environment)
