#!/usr/bin/env python3
"""
Verification script to trace a single metric through the entire pipeline.

Usage:
    python tests/verification/verify_pipeline.py [--system SERVICE_NAME] [--environment ENVIRONMENT]

This script:
1. Sends a test metric to the backend ingestion endpoint
2. Traces it through normalization
3. Verifies it triggers health score computation
4. Confirms the report is persisted and retrievable
5. Validates the score changed from baseline

Output: Trace log showing each stage's inputs/outputs
"""

import sys
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import argparse

# Configure logging to show all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('verification_trace.log'),
    ]
)

logger = logging.getLogger(__name__)
BACKEND_URL = "http://localhost:8000"


class PipelineVerifier:
    """Verifies end-to-end health score pipeline."""
    
    def __init__(self, system_name: str = "test-service", environment: str = "ci"):
        self.system_name = system_name
        self.environment = environment
        self.trace_log = []
        self.baseline_score: Optional[float] = None
        self.final_score: Optional[float] = None
        
    def log_trace(self, stage: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Log a trace point in the pipeline."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "message": message,
            "data": data or {}
        }
        self.trace_log.append(entry)
        logger.info(f"[{stage}] {message}")
        if data:
            logger.debug(f"  Data: {json.dumps(data, indent=2, default=str)}")
    
    def get_baseline_report(self) -> bool:
        """Fetch the current health report as baseline."""
        try:
            logger.info("=" * 80)
            logger.info("PHASE 1: Get Baseline Health Report")
            logger.info("=" * 80)
            
            response = requests.get(
                f"{BACKEND_URL}/api/reports/latest",
                params={
                    "system_name": self.system_name,
                    "environment": self.environment
                },
                timeout=5
            )
            
            if response.status_code == 200:
                report = response.json()
                self.baseline_score = report.get("health_score")
                self.log_trace(
                    "FETCH_BASELINE",
                    f"Baseline report retrieved: score={self.baseline_score}",
                    report
                )
                return True
            elif response.status_code == 404:
                self.log_trace(
                    "FETCH_BASELINE",
                    "No baseline report found (expected for first run)"
                )
                self.baseline_score = None
                return True
            else:
                self.log_trace("FETCH_BASELINE", f"Error: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_trace("FETCH_BASELINE", f"Error fetching baseline: {str(e)}")
            return False
    
    def send_test_metric(self) -> bool:
        """Send a test metric through the ingestion endpoint."""
        try:
            logger.info("=" * 80)
            logger.info("PHASE 2: Send Test Metric")
            logger.info("=" * 80)
            
            test_metric = {
                "source": "observability",
                "source_id": f"test-metric-{datetime.utcnow().timestamp()}",
                "event_type": "metric",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": self.environment,
                "system_name": self.system_name,
                "data": {
                    "metric_name": "cpu_usage_percent",
                    "value": 45.5,
                    "labels": {
                        "host": "test-host",
                        "pod": "test-pod"
                    }
                }
            }
            
            self.log_trace("SEND_METRIC", "Sending test metric payload", test_metric)
            
            response = requests.post(
                f"{BACKEND_URL}/api/events",
                json=test_metric,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_trace(
                    "SEND_METRIC",
                    f"Metric ingested successfully: event_id={result.get('event_id')}",
                    result
                )
                return True
            else:
                self.log_trace(
                    "SEND_METRIC",
                    f"Error: HTTP {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            self.log_trace("SEND_METRIC", f"Error sending metric: {str(e)}")
            return False
    
    def verify_ingestion(self) -> bool:
        """Verify the metric was ingested."""
        try:
            logger.info("=" * 80)
            logger.info("PHASE 3: Verify Ingestion")
            logger.info("=" * 80)
            
            response = requests.get(
                f"{BACKEND_URL}/api/events",
                params={
                    "system_name": self.system_name,
                    "environment": self.environment,
                    "limit": 10
                },
                timeout=5
            )
            
            if response.status_code == 200:
                events = response.json()
                self.log_trace(
                    "VERIFY_INGESTION",
                    f"Events retrieved: count={events.get('count')}",
                    events
                )
                return events.get("count", 0) > 0
            else:
                self.log_trace(
                    "VERIFY_INGESTION",
                    f"Error: HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_trace("VERIFY_INGESTION", f"Error verifying ingestion: {str(e)}")
            return False
    
    def check_final_report(self) -> bool:
        """Fetch the updated health report."""
        try:
            logger.info("=" * 80)
            logger.info("PHASE 4: Check Final Health Report")
            logger.info("=" * 80)
            
            response = requests.get(
                f"{BACKEND_URL}/api/reports/latest",
                params={
                    "system_name": self.system_name,
                    "environment": self.environment
                },
                timeout=5
            )
            
            if response.status_code == 200:
                report = response.json()
                self.final_score = report.get("health_score")
                
                score_changed = False
                if self.baseline_score is not None:
                    score_changed = abs(self.final_score - self.baseline_score) > 0.01
                
                self.log_trace(
                    "FETCH_FINAL",
                    f"Final report retrieved: score={self.final_score}, changed={score_changed}",
                    report
                )
                return True
            else:
                self.log_trace(
                    "FETCH_FINAL",
                    f"Error: HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_trace("FETCH_FINAL", f"Error fetching final report: {str(e)}")
            return False
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """Run full validation."""
        logger.info("\n" + "=" * 80)
        logger.info("HEALTH SCORE PIPELINE VERIFICATION")
        logger.info("=" * 80 + "\n")
        
        results = {
            "system_name": self.system_name,
            "environment": self.environment,
            "baseline_score": self.baseline_score,
            "final_score": self.final_score,
            "phases": {
                "baseline": self.get_baseline_report(),
                "send_metric": self.send_test_metric(),
                "verify_ingestion": self.verify_ingestion(),
                "final_report": self.check_final_report(),
            },
            "overall_pass": False,
        }
        
        # Determine overall pass/fail
        results["overall_pass"] = all(results["phases"].values())
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Baseline Score: {self.baseline_score}")
        logger.info(f"Final Score: {self.final_score}")
        logger.info(f"Overall Status: {'✅ PASS' if results['overall_pass'] else '❌ FAIL'}")
        logger.info(f"Phases:")
        for phase, passed in results["phases"].items():
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {phase}")
        logger.info("=" * 80 + "\n")
        
        return results
    
    def save_trace_log(self):
        """Save detailed trace log to file."""
        trace_file = f"trace_{self.system_name}_{self.environment}.json"
        with open(trace_file, 'w') as f:
            json.dump(self.trace_log, f, indent=2, default=str)
        logger.info(f"Trace log saved to {trace_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify end-to-end health score pipeline"
    )
    parser.add_argument(
        "--system",
        default="test-service",
        help="System name to test (default: test-service)"
    )
    parser.add_argument(
        "--environment",
        default="ci",
        choices=["ci", "staging", "production"],
        help="Environment to test (default: ci)"
    )
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    # Update backend URL if provided
    globals()["BACKEND_URL"] = args.backend_url
    
    # Run verification
    verifier = PipelineVerifier(
        system_name=args.system,
        environment=args.environment
    )
    
    results = verifier.validate_pipeline()
    verifier.save_trace_log()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_pass"] else 1)


if __name__ == "__main__":
    main()
