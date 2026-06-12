#!/usr/bin/env python3
"""Test that health scores change when degraded metrics are sent."""

import json
import requests
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

def send_event(system_name: str, event_type: str, data: dict):
    """Send an event to the backend."""
    payload = {
        "source": "observability",
        "source_id": f"test-{datetime.utcnow().timestamp()}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "ci",
        "system_name": system_name,
        "data": data
    }
    
    response = requests.post(f"{BACKEND_URL}/api/events", json=payload)
    return response.json()

def get_report(system_name: str):
    """Get the latest health report."""
    response = requests.get(
        f"{BACKEND_URL}/api/reports/latest",
        params={"system_name": system_name, "environment": "ci"}
    )
    if response.status_code == 200:
        return response.json()
    return None

if __name__ == "__main__":
    # Test 1: Healthy metric
    print("=" * 80)
    print("TEST 1: Sending healthy metric (cpu=45%)")
    print("=" * 80)

    send_event("dynamic-test", "metric", {
        "metric_name": "cpu_usage_percent",
        "value": 45.0,
        "labels": {"host": "prod-1"}
    })

    report = get_report("dynamic-test")
    print(f"✓ Health Score: {report['health_score']:.2f}")
    print(f"✓ Status: {report['status']}")
    print(f"✓ Issue: {report.get('primary_issue', 'None')}")
    healthy_score = report['health_score']

    # Test 2: Error log
    print("\n" + "=" * 80)
    print("TEST 2: Sending error log")
    print("=" * 80)

    send_event("dynamic-test", "log", {
        "message": "Database connection failed",
        "level": "error",
        "source": "app"
    })

    report = get_report("dynamic-test")
    print(f"✓ Health Score: {report['health_score']:.2f}")
    print(f"✓ Status: {report['status']}")
    print(f"✓ Issue: {report.get('primary_issue', 'None')}")
    degraded_score = report['health_score']

    # Test 3: High latency trace
    print("\n" + "=" * 80)
    print("TEST 3: Sending high-latency trace (8000ms)")
    print("=" * 80)

    send_event("dynamic-test", "trace", {
        "trace_id": "trace-001",
        "span_id": "span-001",
        "operation": "database_query",
        "duration_ms": 8000,
        "status": "error"
    })

    report = get_report("dynamic-test")
    print(f"✓ Health Score: {report['health_score']:.2f}")
    print(f"✓ Status: {report['status']}")
    print(f"✓ Issue: {report.get('primary_issue', 'None')}")
    final_score = report['health_score']

    # Verification
    print("\n" + "=" * 80)
    print("SUMMARY: Health Score Dynamics")
    print("=" * 80)
    print(f"Healthy metric score:     {healthy_score:.2f}")
    print(f"After error log:          {degraded_score:.2f}")
    print(f"After high-latency trace: {final_score:.2f}")
    print(f"\n{'✅ PASS' if final_score < degraded_score < healthy_score else '❌ FAIL'}: Scores changed appropriately")
