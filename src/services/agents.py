"""Lightweight agent implementations for targeted health checks.

Each agent exposes a `check(db)` method returning a dict with:
- `status`: one of 'healthy', 'warning', 'critical', 'unknown'
- `latest_finding`: short human-readable finding
- `last_checked`: ISO timestamp

Agents reuse PersistenceService to persist a short `HealthReport` for traceability.
"""

from datetime import datetime
import os
import socket
import time
import json
from typing import Dict, Any, List, Optional

from src.services.persistence import PersistenceService


class BaseAgent:
    def __init__(self, system_name: str, environment: str = "ci"):
        self.system_name = system_name
        self.environment = environment

    def check(self, db) -> Dict[str, Any]:
        raise NotImplementedError()

    def _persist(self, db, status: str, health_score: float, primary_issue: Optional[str], suggestions: Optional[List[str]] = None):
        return PersistenceService.create_health_report(
            db=db,
            system_name=self.system_name,
            environment=self.environment,
            status=status,
            health_score=health_score,
            primary_issue=primary_issue,
            suggestions=suggestions or [],
        )


class InfrastructureAgent(BaseAgent):
    """Checks basic external network reachability (DNS/UDP port test)."""

    TEST_HOST = ("8.8.8.8", 53)

    def check(self, db) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()
        try:
            sock = socket.create_connection(self.TEST_HOST, timeout=2)
            sock.close()
            status = "healthy"
            finding = f"Outbound connectivity OK to {self.TEST_HOST[0]}:{self.TEST_HOST[1]}"
            score = 0.95
        except Exception as e:
            status = "critical"
            finding = f"Network probe failed: {str(e)}"
            score = 0.1

        # Persist a concise health report
        self._persist(db, status=status, health_score=score, primary_issue=finding)

        return {"status": status, "latest_finding": finding, "last_checked": ts}


# Max simulated RAM capacity: 2× sum of default base RAM values per subsystem
# web=512, app=256, db=1024, cache=512 → base=2304 MB → capacity=4608 MB
_SIM_MAX_RAM_MB = 4608.0


class MemoryAgent(BaseAgent):
    """Checks memory usage. Prefers infrastructure simulator daemon; falls back to host /proc/meminfo."""

    def _read_meminfo(self) -> Optional[Dict[str, int]]:
        try:
            with open("/proc/meminfo", "r") as fh:
                data = {}
                for line in fh:
                    parts = line.split(":")
                    if len(parts) != 2:
                        continue
                    key = parts[0].strip()
                    val = parts[1].strip().split()[0]
                    data[key] = int(val)
            return data
        except Exception:
            return None

    def check(self, db) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()

        # --- Primary: simulator daemon ---
        try:
            from src.simulator_bridge import get_simulator_client
            client = get_simulator_client()
            if client:
                metrics = client.get_current_metrics()
                if metrics and "subsystems" in metrics:
                    rams = {k: v["ram"] for k, v in metrics["subsystems"].items()}
                    total_ram = sum(rams.values())
                    ram_pct = round(min(100.0, (total_ram / _SIM_MAX_RAM_MB) * 100), 1)
                    detail = ", ".join(f"{k}={v:.0f}MB" for k, v in rams.items())
                    if ram_pct < 70:
                        status = "healthy"
                        score = 0.9
                    elif ram_pct < 90:
                        status = "warning"
                        score = 0.5
                    else:
                        status = "critical"
                        score = 0.1
                    finding = f"Daemon: total={total_ram:.0f}MB ({ram_pct}% of {_SIM_MAX_RAM_MB:.0f}MB capacity) [{detail}]"
                    self._persist(db, status=status, health_score=score, primary_issue=finding)
                    return {"status": status, "latest_finding": finding, "last_checked": ts}
        except Exception:
            pass

        # --- Fallback: host memory ---
        used_pct = None
        finding = "Unable to determine memory usage"
        try:
            import psutil

            vm = psutil.virtual_memory()
            used_pct = vm.percent
        except Exception:
            info = self._read_meminfo()
            if info and "MemTotal" in info and "MemAvailable" in info:
                total = info["MemTotal"]
                avail = info["MemAvailable"]
                used_pct = round((1 - (avail / total)) * 100, 1)

        if used_pct is None:
            status = "unknown"
            score = 0.5
        else:
            if used_pct < 70:
                status = "healthy"
                score = 0.9
            elif used_pct < 90:
                status = "warning"
                score = 0.5
            else:
                status = "critical"
                score = 0.1
            finding = f"Memory usage at {used_pct}%"

        self._persist(db, status=status, health_score=score, primary_issue=finding)
        return {"status": status, "latest_finding": finding, "last_checked": ts}


class CPUAgent(BaseAgent):
    """Checks CPU utilisation. Prefers infrastructure simulator daemon; falls back to host load average."""

    def check(self, db) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()

        # --- Primary: simulator daemon ---
        try:
            from src.simulator_bridge import get_simulator_client
            client = get_simulator_client()
            if client:
                metrics = client.get_current_metrics()
                if metrics and "subsystems" in metrics:
                    cpus = {k: v["cpu"] for k, v in metrics["subsystems"].items()}
                    avg_cpu = round(sum(cpus.values()) / len(cpus), 1)
                    max_cpu = round(max(cpus.values()), 1)
                    detail = ", ".join(f"{k}={v:.1f}%" for k, v in cpus.items())
                    if avg_cpu < 50 and max_cpu < 70:
                        status = "healthy"
                        score = 0.9
                    elif avg_cpu < 70 or max_cpu < 90:
                        status = "warning"
                        score = 0.5
                    else:
                        status = "critical"
                        score = 0.1
                    finding = f"Daemon: avg={avg_cpu}% peak={max_cpu}% [{detail}]"
                    self._persist(db, status=status, health_score=score, primary_issue=finding)
                    return {"status": status, "latest_finding": finding, "last_checked": ts}
        except Exception:
            pass

        # --- Fallback: host load average ---
        try:
            load1, _, _ = os.getloadavg()
            cores = os.cpu_count() or 1
            load_per_core = load1 / cores
            pct = round(load_per_core * 100, 1)
            if load_per_core < 0.7:
                status = "healthy"
                score = 0.9
            elif load_per_core < 1.0:
                status = "warning"
                score = 0.5
            else:
                status = "critical"
                score = 0.1
            finding = f"1m load={load1:.2f} across {cores} cores (per-core {pct}%)"
        except Exception as e:
            status = "unknown"
            score = 0.5
            finding = f"CPU check failed: {str(e)}"

        self._persist(db, status=status, health_score=score, primary_issue=finding)
        return {"status": status, "latest_finding": finding, "last_checked": ts}


class CICDAgent(BaseAgent):
    """Examines recent workflow events to determine pipeline health."""

    def __init__(self, system_name: str = "ci", environment: str = "ci"):
        super().__init__(system_name=system_name, environment=environment)

    def check(self, db) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()
        try:
            events = PersistenceService.get_ci_events(db=db, environment=self.environment, limit=100)
            # Heuristic: inspect event payloads for failure indicators
            total = len(events)
            failures = 0
            latest_issue = None
            for e in events:
                d = e.data or {}
                s = None
                if isinstance(d, dict):
                    s = (d.get("status") or d.get("result") or d.get("conclusion"))
                if s and isinstance(s, str) and s.lower() in ("failed", "failure", "error", "fail"):
                    failures += 1
                    if not latest_issue:
                        latest_issue = f"Recent pipeline failure in event {e.id}"

            if total == 0:
                status = "unknown"
                score = 0.5
                finding = "No recent CI events"
            else:
                fail_rate = failures / total
                if fail_rate == 0:
                    status = "healthy"
                    score = 0.95
                elif fail_rate < 0.2:
                    status = "warning"
                    score = 0.6
                else:
                    status = "critical"
                    score = 0.2
                finding = latest_issue or f"CI failure rate {fail_rate:.2%} ({failures}/{total})"
        except Exception as e:
            status = "unknown"
            score = 0.5
            finding = f"CICD check failed: {str(e)}"

        self._persist(db, status=status, health_score=score, primary_issue=finding)
        return {"status": status, "latest_finding": finding, "last_checked": ts}


class APIAgent(BaseAgent):
    """Measures latency and availability of a target API endpoint."""

    def __init__(self, system_name: str = "api", environment: str = "ci", target_url: Optional[str] = None):
        super().__init__(system_name=system_name, environment=environment)
        self.target_url = target_url or os.getenv("TARGET_API", "http://localhost:8000/health")

    def check(self, db) -> Dict[str, Any]:
        ts = datetime.utcnow().isoformat()
        try:
            import urllib.request

            start = time.time()
            with urllib.request.urlopen(self.target_url, timeout=3) as resp:
                latency = (time.time() - start) * 1000.0
                code = resp.getcode()
            if 200 <= code < 300:
                status = "healthy" if latency < 300 else "warning"
                score = 0.95 if latency < 300 else 0.6
            else:
                status = "critical"
                score = 0.1
            finding = f"HTTP {code} in {latency:.1f}ms for {self.target_url}"
        except Exception as e:
            status = "critical"
            score = 0.1
            finding = f"Probe failed for {self.target_url}: {str(e)}"

        self._persist(db, status=status, health_score=score, primary_issue=finding)
        return {"status": status, "latest_finding": finding, "last_checked": ts}


def run_all_agents(db) -> List[Dict[str, Any]]:
    agents = [
        InfrastructureAgent(system_name="infrastructure"),
        MemoryAgent(system_name="memory"),
        CPUAgent(system_name="cpu"),
        CICDAgent(system_name="ci"),
        APIAgent(system_name="api"),
    ]
    results = []
    for a in agents:
        try:
            res = a.check(db)
        except Exception as e:
            res = {"status": "unknown", "latest_finding": f"agent error: {str(e)}", "last_checked": datetime.utcnow().isoformat()}
        results.append({"agent": a.system_name, **res})
    return results
