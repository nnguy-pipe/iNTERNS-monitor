#!/usr/bin/env python3
"""
test_backend_integration.py

Test script to verify simulator daemon integrates properly with backend API.
Run after both daemon and backend are started.

Usage:
  python3 test_backend_integration.py --daemon-url http://localhost:9999 --backend-url http://localhost:8000
"""

import argparse
import requests
import json
import time
import sys
from typing import Dict, Any, List

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}► {name}{Colors.END}")

def print_pass(msg: str):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.END}")

def print_fail(msg: str):
    print(f"  {Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"  {Colors.YELLOW}ℹ {msg}{Colors.END}")

class BackendIntegrationTester:
    def __init__(self, daemon_url: str, backend_url: str):
        self.daemon_url = daemon_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/')
        self.results = []
    
    def test_daemon_connection(self) -> bool:
        """Test connection to simulator daemon."""
        print_test("Daemon Connection")
        try:
            response = requests.get(f"{self.daemon_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            print_pass(f"Daemon running: {data.get('status')}")
            print_info(f"Preset: {data.get('preset')}, Tick: {data.get('tick')}")
            self.results.append(('daemon_connection', True))
            return True
        except Exception as e:
            print_fail(f"Cannot connect to daemon: {e}")
            self.results.append(('daemon_connection', False))
            return False
    
    def test_backend_connection(self) -> bool:
        """Test connection to backend API."""
        print_test("Backend Connection")
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            print_pass(f"Backend running: {data.get('status')}")
            print_info(f"Database: {data.get('database')}")
            self.results.append(('backend_connection', True))
            return True
        except Exception as e:
            print_fail(f"Cannot connect to backend: {e}")
            self.results.append(('backend_connection', False))
            return False
    
    def test_simulator_health_endpoint(self) -> bool:
        """Test /api/simulator/health endpoint."""
        print_test("Backend Simulator Health Endpoint")
        try:
            response = requests.get(f"{self.backend_url}/api/simulator/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'running':
                print_pass("Simulator accessible from backend")
                print_info(f"Preset: {data.get('simulator', {}).get('preset')}")
                self.results.append(('simulator_health_endpoint', True))
                return True
            else:
                print_fail(f"Simulator status: {data.get('status')}")
                self.results.append(('simulator_health_endpoint', False))
                return False
        except Exception as e:
            print_fail(f"Health endpoint failed: {e}")
            self.results.append(('simulator_health_endpoint', False))
            return False
    
    def test_metrics_endpoint(self) -> bool:
        """Test /api/simulator/metrics endpoint."""
        print_test("Metrics Endpoint")
        try:
            response = requests.get(f"{self.backend_url}/api/simulator/metrics", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Validate structure
            assert 'tick' in data
            assert 'timestamp' in data
            assert 'preset' in data
            assert 'subsystems' in data
            
            # Check subsystems
            subsystems = data['subsystems']
            assert 'web' in subsystems
            assert 'app' in subsystems
            assert 'db' in subsystems
            assert 'cache' in subsystems
            
            # Check metrics per subsystem
            for name, metrics in subsystems.items():
                assert 'cpu' in metrics
                assert 'ram' in metrics
                assert 'active_users' in metrics
            
            print_pass(f"Metrics structure valid, tick {data['tick']}")
            print_info(f"Preset: {data['preset']}")
            self.results.append(('metrics_endpoint', True))
            return True
        except AssertionError as e:
            print_fail(f"Metrics structure invalid: {e}")
            self.results.append(('metrics_endpoint', False))
            return False
        except Exception as e:
            print_fail(f"Metrics endpoint failed: {e}")
            self.results.append(('metrics_endpoint', False))
            return False
    
    def test_preset_switch(self) -> bool:
        """Test preset switching."""
        print_test("Preset Switching")
        try:
            # Switch to high_cpu
            response = requests.post(f"{self.backend_url}/api/simulator/preset/high_cpu", timeout=5)
            response.raise_for_status()
            data = response.json()
            assert data['status'] == 'ok'
            assert data['preset'] == 'high_cpu'
            print_pass("Switched to high_cpu preset")
            
            # Verify preset changed
            time.sleep(1)
            response = requests.get(f"{self.backend_url}/api/simulator/metrics", timeout=5)
            metrics = response.json()
            if metrics['preset'] == 'high_cpu':
                print_pass("Preset change verified")
                self.results.append(('preset_switch', True))
                return True
            else:
                print_fail(f"Preset mismatch: {metrics['preset']}")
                self.results.append(('preset_switch', False))
                return False
        except Exception as e:
            print_fail(f"Preset switching failed: {e}")
            self.results.append(('preset_switch', False))
            return False
    
    def test_ingest_endpoint(self) -> bool:
        """Test /api/simulator/ingest endpoint."""
        print_test("Event Ingestion Endpoint")
        try:
            # First check current metrics
            response = requests.get(f"{self.backend_url}/api/simulator/metrics", timeout=5)
            current_preset = response.json()['preset']
            
            # Ingest metric as event
            response = requests.post(
                f"{self.backend_url}/api/simulator/ingest?system_name=test-system&environment=ci",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            assert data['status'] == 'ingested'
            assert 'event_id' in data
            assert data['system_name'] == 'test-system'
            
            print_pass(f"Event ingested: {data['event_id']}")
            print_info(f"Preset captured: {data['preset']}")
            self.results.append(('ingest_endpoint', True))
            return True
        except AssertionError as e:
            print_fail(f"Ingestion response invalid: {e}")
            self.results.append(('ingest_endpoint', False))
            return False
        except Exception as e:
            print_fail(f"Ingestion failed: {e}")
            self.results.append(('ingest_endpoint', False))
            return False
    
    def test_export_endpoints(self) -> bool:
        """Test JSON and XML export endpoints."""
        print_test("Export Endpoints")
        success = True
        
        # Test JSON export
        try:
            response = requests.get(f"{self.backend_url}/api/simulator/export/json", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            assert 'simulations' in data
            assert 'ticks' in data
            assert 'subsystem_metrics' in data
            assert len(data['simulations']) > 0
            
            print_pass(f"JSON export valid: {len(data['ticks'])} ticks, {len(data['subsystem_metrics'])} metrics")
        except Exception as e:
            print_fail(f"JSON export failed: {e}")
            success = False
        
        # Test XML export
        try:
            response = requests.get(f"{self.backend_url}/api/simulator/export/xml", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            assert 'xml' in data
            xml_str = data['xml']
            assert 'simulation' in xml_str
            assert 'subsystem_metrics' in xml_str
            
            print_pass(f"XML export valid: {len(xml_str)} chars")
        except Exception as e:
            print_fail(f"XML export failed: {e}")
            success = False
        
        self.results.append(('export_endpoints', success))
        return success
    
    def test_all_presets(self) -> bool:
        """Test switching through all presets."""
        print_test("All Presets")
        presets = ['default', 'high_cpu', 'low_cpu', 'high_ram', 'low_ram', 'high_users', 'low_users']
        success = True
        
        try:
            for preset in presets:
                response = requests.post(f"{self.backend_url}/api/simulator/preset/{preset}", timeout=5)
                if response.status_code == 200:
                    print_info(f"✓ {preset}")
                else:
                    print_info(f"✗ {preset}")
                    success = False
                time.sleep(0.5)
            
            if success:
                print_pass("All presets available")
            self.results.append(('all_presets', success))
            return success
        except Exception as e:
            print_fail(f"Preset test failed: {e}")
            self.results.append(('all_presets', False))
            return False
    
    def run_all(self):
        """Run all tests."""
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"SIMULATOR-BACKEND INTEGRATION TEST SUITE")
        print(f"{'='*60}{Colors.END}\n")
        print(f"Daemon: {self.daemon_url}")
        print(f"Backend: {self.backend_url}\n")
        
        # Run tests
        if not self.test_daemon_connection():
            print_fail("Cannot proceed - daemon not running")
            return False
        
        if not self.test_backend_connection():
            print_fail("Cannot proceed - backend not running")
            return False
        
        self.test_simulator_health_endpoint()
        self.test_metrics_endpoint()
        self.test_preset_switch()
        self.test_ingest_endpoint()
        self.test_all_presets()
        self.test_export_endpoints()
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"TEST RESULTS")
        print(f"{'='*60}{Colors.END}\n")
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for test_name, result in self.results:
            status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
            print(f"  {status} - {test_name}")
        
        print(f"\n{Colors.BLUE}Summary: {passed}/{total} tests passed{Colors.END}\n")
        
        if passed == total:
            print(f"{Colors.GREEN}✓ All tests passed! Integration is working.{Colors.END}\n")
            return True
        else:
            print(f"{Colors.YELLOW}⚠ Some tests failed. Review above for details.{Colors.END}\n")
            return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test simulator-backend integration')
    parser.add_argument('--daemon-url', default='http://localhost:9999', help='Simulator daemon URL')
    parser.add_argument('--backend-url', default='http://localhost:8000', help='Backend API URL')
    args = parser.parse_args()
    
    tester = BackendIntegrationTester(args.daemon_url, args.backend_url)
    success = tester.run_all()
    sys.exit(0 if success else 1)
