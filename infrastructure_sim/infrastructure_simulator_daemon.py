#!/usr/bin/env python3
"""
infrastructure_simulator_daemon.py

Long-running infrastructure simulator service with live metrics, signal-based preset switching,
and real-time JSON/XML export. Designed to run continuously with dynamic control.

Usage:
  python infrastructure_simulator_daemon.py --port 9999
  python infrastructure_simulator_daemon.py --port 9999 --export-interval 5

Control via HTTP commands:
  curl http://localhost:9999/metrics          → Get current metrics
  curl -X POST http://localhost:9999/preset/high_cpu → Switch preset
  curl http://localhost:9999/health           → Check service status
"""

import argparse
import time
import random
import math
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import signal
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# ======================== Core Simulator Models ========================

@dataclass
class SubsystemState:
    name: str
    cpu: float
    ram: float
    active_users: int = 0

class Subsystem:
    """Subsystem with stochastic CPU/RAM models."""
    def __init__(self, name: str, base_cpu: float = 5.0, base_ram: float = 256.0,
                 cpu_volatility: float = 5.0, ram_volatility: float = 10.0,
                 ram_mode: str = 'default', leak_rate: float = 1.0):
        self.name = name
        self.base_cpu = base_cpu
        self.base_ram = base_ram
        self.cpu_volatility = cpu_volatility
        self.ram_volatility = ram_volatility
        self.ram_mode = ram_mode
        self.leak_rate = leak_rate
        self.cpu = max(0.0, base_cpu + random.uniform(-cpu_volatility/2, cpu_volatility/2))
        self.ram = max(0.0, base_ram + random.uniform(-ram_volatility/2, ram_volatility/2))
        self.cpu_trend = 0.0
        self.ram_trend = 0.0

    def step(self, dt: float, external_load: float = 0.0, event_spike: float = 0.0, active_users: int = 0):
        """Advance subsystem state by dt seconds."""
        self.cpu_trend += random.gauss(0, 0.01) * dt
        cycle = math.sin(time.time() / 60.0 + hash(self.name) % 7)
        noise = random.gauss(0, self.cpu_volatility) * math.sqrt(dt)
        external = external_load * 50.0
        new_cpu = self.base_cpu + self.cpu_trend * 10.0 + cycle * (self.cpu_volatility/2) + noise + external + event_spike
        self.cpu = max(0.0, min(100.0, new_cpu))

        self.ram_trend += random.gauss(0, 0.05) * dt
        ram_noise = random.gauss(0, self.ram_volatility) * math.sqrt(dt)
        ram_external = external_load * (self.base_ram * 0.5)

        if self.ram_mode == 'leak':
            leak = self.leak_rate * dt
            new_ram = self.ram + self.ram_trend + ram_noise + ram_external + leak
            if new_ram > 8000:
                new_ram = 8000 - abs(random.gauss(0, self.ram_volatility));
        elif self.ram_mode == 'proportional':
            new_ram = self.base_ram * (1.0 + external_load + (self.cpu / 100.0)) + self.ram_trend + ram_noise
        elif self.ram_mode == 'cache':
            decay_factor = 0.99 ** dt
            growth = ram_external * 1.2
            new_ram = (self.ram * decay_factor) + growth + self.ram_trend + ram_noise
            if new_ram < self.base_ram:
                new_ram = self.base_ram + abs(random.gauss(0, self.ram_volatility))
        else:  # default
            new_ram = self.base_ram + self.ram_trend + ram_noise + ram_external * 0.3

        self.ram = max(0.0, new_ram)
        return SubsystemState(self.name, self.cpu, self.ram, active_users)

class LiveSimulation:
    """Continuously running simulation with state management."""
    def __init__(self, tick_interval: float = 1.0, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.tick_interval = tick_interval
        self.tick_number = 0
        self.start_time = time.time()
        self.last_export = self.start_time
        self.subsystems = {
            'web': Subsystem('web', 10.0, 512.0),
            'app': Subsystem('app', 8.0, 256.0),
            'db': Subsystem('db', 15.0, 1024.0),
            'cache': Subsystem('cache', 5.0, 512.0),
        }
        self.metrics_history = []
        self.preset = 'default'
        self.sustained_base_ext = {}
        self.user_counts = {s: 0 for s in self.subsystems}
        
        self._apply_preset('default')

    def _apply_preset(self, preset: str):
        """Apply preset configuration to all subsystems."""
        self.preset = preset
        
        if preset == 'high_cpu':
            for name, sub in self.subsystems.items():
                sub.base_cpu = 50.0
                sub.cpu_volatility = 5.0
                sub.ram_mode = 'default'
            self.sustained_base_ext = {s: random.uniform(0.7, 0.9) for s in self.subsystems}
            self.user_counts = {s: random.randint(10, 50) for s in self.subsystems}
        elif preset == 'low_cpu':
            for name, sub in self.subsystems.items():
                sub.base_cpu = 10.0
                sub.cpu_volatility = 3.0
                sub.ram_mode = 'default'
            self.sustained_base_ext = {s: random.uniform(0.01, 0.1) for s in self.subsystems}
            self.user_counts = {s: random.randint(0, 20) for s in self.subsystems}
        elif preset == 'high_ram':
            for name, sub in self.subsystems.items():
                sub.ram_mode = 'leak'
                sub.leak_rate = sub.base_ram * 0.005
            self.sustained_base_ext = {
                name: random.uniform(0.3, 0.5)
                for name in self.subsystems
            }
            self.user_counts = {
                name: random.randint(500, 800) if name == 'web' else random.randint(50, 150)
                for name in self.subsystems
            }
        elif preset == 'low_ram':
            for name, sub in self.subsystems.items():
                sub.ram_mode = 'leak'
                sub.leak_rate = sub.base_ram * -0.002
            self.sustained_base_ext = {s: random.uniform(0.05, 0.15) for s in self.subsystems}
            self.user_counts = {s: random.randint(1, 30) for s in self.subsystems}
        elif preset == 'high_users':
            for name, sub in self.subsystems.items():
                sub.base_cpu = 40.0
                sub.ram_mode = 'proportional'
            self.sustained_base_ext = {s: random.uniform(0.4, 0.7) for s in self.subsystems}
            self.user_counts = {
                'web': random.randint(500, 800),
                'app': random.randint(400, 700),
                'db': random.randint(50, 150),
                'cache': random.randint(100, 300),
            }
        elif preset == 'low_users':
            for name, sub in self.subsystems.items():
                sub.base_cpu = 8.0
                sub.ram_mode = 'default'
            self.sustained_base_ext = {s: random.uniform(0.01, 0.05) for s in self.subsystems}
            self.user_counts = {
                'web': random.randint(10, 50),
                'app': random.randint(5, 30),
                'db': random.randint(1, 10),
                'cache': random.randint(5, 20),
            }
        else:  # default
            for name, sub in self.subsystems.items():
                sub.base_cpu = 10.0
                sub.cpu_volatility = 5.0
                sub.ram_mode = 'default'
            self.sustained_base_ext = {s: random.uniform(0.01, 0.1) for s in self.subsystems}
            self.user_counts = {s: random.randint(0, 50) for s in self.subsystems}

    def step(self):
        """Execute one simulation tick."""
        dt = self.tick_interval
        timestamp = self.start_time + (self.tick_number * self.tick_interval)
        
        tick_data = {
            'tick_number': self.tick_number,
            'timestamp': timestamp,
            'subsystems': {},
        }
        
        for name, sub in self.subsystems.items():
            ext_load = self.sustained_base_ext.get(name, 0.1)
            ext_load += random.gauss(0, 0.02)
            event_spike = 5.0 if random.random() > 0.95 and ext_load > 0.2 else 0.0
            
            # Update user count with small random drift
            self.user_counts[name] += random.randint(-5, 5)
            self.user_counts[name] = max(0, self.user_counts[name])
            
            state = sub.step(dt, ext_load, event_spike, self.user_counts[name])
            tick_data['subsystems'][name] = {
                'cpu': round(state.cpu, 2),
                'ram': round(state.ram, 2),
                'active_users': state.active_users,
                'external_load': round(ext_load, 3),
                'event_spike': round(event_spike, 2),
            }
        
        self.metrics_history.append(tick_data)
        # Keep last 3600 ticks (~1 hour at 1s interval)
        if len(self.metrics_history) > 3600:
            self.metrics_history = self.metrics_history[-3600:]
        
        self.tick_number += 1

    def get_current_metrics(self) -> Dict[str, Any]:
        """Return current state as metrics."""
        if not self.metrics_history:
            return {'error': 'No metrics yet'}
        
        latest = self.metrics_history[-1]
        return {
            'tick': latest['tick_number'],
            'timestamp': latest['timestamp'],
            'preset': self.preset,
            'uptime_seconds': time.time() - self.start_time,
            'subsystems': latest['subsystems'],
        }

    def get_summary(self) -> Dict[str, Any]:
        """Return aggregated metrics."""
        if not self.metrics_history:
            return {'error': 'No metrics'}
        
        all_ticks = self.metrics_history
        summary = {
            'preset': self.preset,
            'total_ticks': self.tick_number,
            'uptime_seconds': time.time() - self.start_time,
            'subsystems': {},
        }
        
        for subsys in ['web', 'app', 'db', 'cache']:
            cpus = [t['subsystems'][subsys]['cpu'] for t in all_ticks]
            rams = [t['subsystems'][subsys]['ram'] for t in all_ticks]
            users = [t['subsystems'][subsys]['active_users'] for t in all_ticks]
            
            summary['subsystems'][subsys] = {
                'cpu_avg': round(sum(cpus) / len(cpus), 2),
                'cpu_min': round(min(cpus), 2),
                'cpu_max': round(max(cpus), 2),
                'ram_avg': round(sum(rams) / len(rams), 2),
                'ram_min': round(min(rams), 2),
                'ram_max': round(max(rams), 2),
                'users_avg': round(sum(users) / len(users), 2),
                'users_max': max(users),
            }
        
        return summary

    def export_json(self) -> str:
        """Export metrics as SQL-compatible JSON."""
        if not self.metrics_history:
            return json.dumps({'error': 'No metrics'})
        
        sim_id = f"sim_{int(self.start_time)}"
        output = {
            'simulations': [{
                'simulation_id': sim_id,
                'start_timestamp': self.start_time,
                'end_timestamp': time.time(),
                'total_ticks': self.tick_number,
                'tick_interval_seconds': self.tick_interval,
                'preset': self.preset,
            }],
            'ticks': [],
            'subsystem_metrics': [],
        }
        
        for tick_data in self.metrics_history:
            tick_id = f"{sim_id}_t{tick_data['tick_number']}"
            output['ticks'].append({
                'tick_id': tick_id,
                'simulation_id': sim_id,
                'tick_number': tick_data['tick_number'],
                'timestamp': tick_data['timestamp'],
            })
            
            for subsys, metrics in tick_data['subsystems'].items():
                metric_id = f"{sim_id}_t{tick_data['tick_number']}_{subsys}"
                output['subsystem_metrics'].append({
                    'metric_id': metric_id,
                    'tick_id': tick_id,
                    'simulation_id': sim_id,
                    'subsystem': subsys,
                    'tick_number': tick_data['tick_number'],
                    'timestamp': tick_data['timestamp'],
                    'cpu_percent': metrics['cpu'],
                    'ram_mb': metrics['ram'],
                    'active_users': metrics['active_users'],
                    'external_load': metrics['external_load'],
                    'event_spike_percent': metrics['event_spike'],
                })
        
        return json.dumps(output, indent=2)

    def export_xml(self) -> str:
        """Export metrics as SQL-compatible XML."""
        if not self.metrics_history:
            return '<error>No metrics</error>'
        
        sim_id = f"sim_{int(self.start_time)}"
        root = ET.Element('simulation_export')
        root.set('schema_version', '1.0')
        root.set('preset', self.preset)
        root.set('exported_at', str(datetime.now().isoformat()))
        
        # Simulations
        sims_elem = ET.SubElement(root, 'simulations')
        sim_elem = ET.SubElement(sims_elem, 'simulation')
        sim_elem.set('simulation_id', sim_id)
        sim_elem.set('start_timestamp', str(self.start_time))
        sim_elem.set('end_timestamp', str(time.time()))
        sim_elem.set('total_ticks', str(self.tick_number))
        sim_elem.set('tick_interval_seconds', str(self.tick_interval))
        
        # Ticks
        ticks_elem = ET.SubElement(root, 'ticks')
        for tick_data in self.metrics_history:
            tick_id = f"{sim_id}_t{tick_data['tick_number']}"
            tick_elem = ET.SubElement(ticks_elem, 'tick')
            tick_elem.set('tick_id', tick_id)
            tick_elem.set('simulation_id', sim_id)
            tick_elem.set('tick_number', str(tick_data['tick_number']))
            tick_elem.set('timestamp', str(tick_data['timestamp']))
        
        # Metrics
        metrics_elem = ET.SubElement(root, 'subsystem_metrics')
        for tick_data in self.metrics_history:
            tick_id = f"{sim_id}_t{tick_data['tick_number']}"
            for subsys, metrics in tick_data['subsystems'].items():
                metric_id = f"{sim_id}_t{tick_data['tick_number']}_{subsys}"
                metric_elem = ET.SubElement(metrics_elem, 'metric')
                metric_elem.set('metric_id', metric_id)
                metric_elem.set('tick_id', tick_id)
                metric_elem.set('simulation_id', sim_id)
                metric_elem.set('subsystem', subsys)
                metric_elem.set('cpu_percent', str(metrics['cpu']))
                metric_elem.set('ram_mb', str(metrics['ram']))
                metric_elem.set('active_users', str(metrics['active_users']))
                metric_elem.set('external_load', str(metrics['external_load']))
                metric_elem.set('event_spike_percent', str(metrics['event_spike']))
        
        # Pretty print
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ')


# ======================== HTTP Server ========================

class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP request handler for metrics and control."""
    
    simulation: LiveSimulation = None
    lock: threading.Lock = None
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/metrics':
                self.send_json(self.simulation.get_current_metrics())
            elif path == '/summary':
                self.send_json(self.simulation.get_summary())
            elif path == '/export/json':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(self.simulation.export_json().encode())
            elif path == '/export/xml':
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(self.simulation.export_xml().encode())
            elif path == '/health':
                self.send_json({
                    'status': 'running',
                    'tick': self.simulation.tick_number,
                    'preset': self.simulation.preset,
                    'uptime': time.time() - self.simulation.start_time,
                })
            else:
                self.send_error(404, 'Not found')
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def do_POST(self):
        """Handle POST requests for preset changes."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path.startswith('/preset/'):
                preset = path.split('/')[-1]
                valid_presets = ['default', 'high_cpu', 'low_cpu', 'high_ram', 'low_ram', 'high_users', 'low_users']
                if preset in valid_presets:
                    with self.lock:
                        self.simulation._apply_preset(preset)
                    self.send_json({'status': 'ok', 'preset': preset})
                else:
                    self.send_json({'error': f'Invalid preset. Valid: {valid_presets}'}, 400)
            else:
                self.send_error(404, 'Not found')
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def send_json(self, data: Dict[str, Any], status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


# ======================== Main Service ========================

def run_daemon(port: int = 9999, export_interval: float = 5.0, export_dir: str = '.'):
    """Run the continuous simulator with HTTP server."""
    
    simulation = LiveSimulation(tick_interval=1.0)
    lock = threading.Lock()
    
    # Set class variables for handler
    MetricsHandler.simulation = simulation
    MetricsHandler.lock = lock
    
    # Start simulation thread
    running = True
    
    def simulate():
        nonlocal running
        last_export = time.time()
        while running:
            with lock:
                simulation.step()
            time.sleep(1.0)
    
    # Start HTTP server
    server = HTTPServer(('localhost', port), MetricsHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    sim_thread = threading.Thread(target=simulate, daemon=True)
    
    def signal_handler(sig, frame):
        nonlocal running
        print('\nShutting down...', file=sys.stderr)
        running = False
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f'Starting simulator daemon on http://localhost:{port}', file=sys.stderr)
    print(f'Commands:', file=sys.stderr)
    print(f'  curl http://localhost:{port}/metrics         → Current metrics', file=sys.stderr)
    print(f'  curl http://localhost:{port}/summary         → Summary stats', file=sys.stderr)
    print(f'  curl http://localhost:{port}/export/json     → Full JSON export', file=sys.stderr)
    print(f'  curl http://localhost:{port}/export/xml      → Full XML export', file=sys.stderr)
    print(f'  curl -X POST http://localhost:{port}/preset/high_cpu → Switch preset', file=sys.stderr)
    print(f'  curl http://localhost:{port}/health          → Check status', file=sys.stderr)
    print(f'Valid presets: default, high_cpu, low_cpu, high_ram, low_ram, high_users, low_users', file=sys.stderr)
    print()
    
    server_thread.start()
    sim_thread.start()
    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Infrastructure simulator daemon with live metrics')
    parser.add_argument('--port', type=int, default=9999, help='HTTP server port')
    parser.add_argument('--export-interval', type=float, default=5.0, help='Export interval (seconds)')
    parser.add_argument('--export-dir', type=str, default='.', help='Directory for metric exports')
    args = parser.parse_args()
    
    run_daemon(port=args.port, export_interval=args.export_interval, export_dir=args.export_dir)
