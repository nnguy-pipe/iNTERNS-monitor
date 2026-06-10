#!/usr/bin/env python3
"""
infrastructure_simulator.py

Simple local simulator for an infrastructure system composed of subsystems.
Features:
- Subsystem-level CPU% and RAM (MB) simulation using configurable stochastic models
- External usage pattern simulation (e.g., user logins) that influence load
- CLI interface to run simulations, print live summaries, and save JSON output

Usage examples:
  python infrastructure_simulator.py --duration 60 --tick 1 --print-every 5 --out out.json
  python infrastructure_simulator.py --preset high_cpu --duration 30

Keep as a single-file local tool.
"""

import argparse
import time
import random
import math
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Callable, Optional

# ------------------------- Models -------------------------
@dataclass
class SubsystemState:
    name: str
    cpu: float  # percent 0..100
    ram: float  # MB

class Subsystem:
    """A subsystem with simple stochastic CPU and RAM models.

    The CPU model is: cpu = base + trend + burst + noise
    The RAM model slowly drifts up/down and may jump on events.
    """
    def __init__(self, name: str, base_cpu: float = 5.0, base_ram: float = 256.0,
                 cpu_volatility: float = 5.0, ram_volatility: float = 10.0,
                 ram_mode: str = 'default', leak_rate: float = 1.0):
        self.name = name
        self.base_cpu = base_cpu
        self.base_ram = base_ram
        self.cpu_volatility = cpu_volatility
        self.ram_volatility = ram_volatility
        # RAM behavior mode: 'default', 'leak', 'proportional', 'cache'
        self.ram_mode = ram_mode
        # leak_rate is MB per second (used when ram_mode == 'leak')
        self.leak_rate = leak_rate
        self.cpu = max(0.0, base_cpu + random.uniform(-cpu_volatility/2, cpu_volatility/2))
        self.ram = max(0.0, base_ram + random.uniform(-ram_volatility/2, ram_volatility/2))
        # internal state for trend
        self.cpu_trend = 0.0
        self.ram_trend = 0.0

    def step(self, dt: float, external_load: float = 0.0, event_spike: float = 0.0):
        """Advance simulation by dt seconds.

        external_load: a multiplier-like value (0..1) representing how much external usage
        affects this subsystem (e.g., fraction of user requests hitting it).
        event_spike: additive CPU% spike caused by discrete events (e.g. login handling)
        """
        # CPU trend: small random walk
        self.cpu_trend += random.gauss(0, 0.01) * dt
        # apply sinusoidal daily-ish cycle with very low frequency (for longer runs)
        cycle = math.sin(time.time() / 60.0 + hash(self.name) % 7)
        # base fluctuation + external influence
        noise = random.gauss(0, self.cpu_volatility) * math.sqrt(dt)
        external = external_load * 50.0  # scale external load to percent
        new_cpu = self.base_cpu + self.cpu_trend * 10.0 + cycle * (self.cpu_volatility/2) + noise + external + event_spike
        # clamp
        self.cpu = max(0.0, min(100.0, new_cpu))

        # RAM: slower changes; external load can increase ram usage too
        self.ram_trend += random.gauss(0, 0.05) * dt
        ram_noise = random.gauss(0, self.ram_volatility) * math.sqrt(dt)
        ram_external = external_load * (self.base_ram * 0.5)

        # RAM scaling modes
        if self.ram_mode == 'leak':
            # persistent leak: steadily increase RAM by leak_rate * dt (MB), plus normal drift
            leak = self.leak_rate * dt
            new_ram = self.ram + self.ram_trend + ram_noise + ram_external + leak
        elif self.ram_mode == 'proportional':
            # RAM proportional to external load and CPU: scale base by (1 + external_load + cpu/100)
            new_ram = self.base_ram * (1.0 + external_load + (self.cpu / 100.0)) + self.ram_trend + ram_noise
        elif self.ram_mode == 'cache':
            # cache-like: grow quickly on external load, decay slowly when load low
            decay_factor = 0.99 ** dt  # slow decay per second
            growth = ram_external * 1.2
            new_ram = (self.ram * decay_factor) + growth + self.ram_trend + ram_noise
            # ensure never below base
            if new_ram < self.base_ram:
                new_ram = self.base_ram + abs(random.gauss(0, self.ram_volatility))
        else:
            # default: baseline + trends + external influence
            new_ram = self.base_ram + self.ram_trend + ram_noise + ram_external

        self.ram = max(0.0, new_ram)

        return SubsystemState(self.name, round(self.cpu, 3), round(self.ram, 2))

class SystemModel:
    def __init__(self, subsystems: List[Subsystem]):
        self.subsystems = subsystems

    def step(self, dt: float, external_pattern: Dict[str, float], event_spikes: Dict[str, float]):
        states = []
        for s in self.subsystems:
            ext = external_pattern.get(s.name, 0.0)
            spike = event_spikes.get(s.name, 0.0)
            states.append(s.step(dt, ext, spike))
        return states

# ---------------------- External Patterns ----------------------
class ExternalPatternGenerator:
    """Generates a distribution of external load across subsystems.

    Example patterns:
      - poisson logins: some number of login events per tick
      - steady background: constant low-level traffic
      - burst: periodic spikes
    """
    def __init__(self, subsystems: List[str], seed: Optional[int] = None):
        self.subs = subsystems
        self.rng = random.Random(seed)

    def steady(self, intensity: float = 0.02) -> Dict[str, float]:
        # uniform steady intensity applied to all
        return {name: intensity for name in self.subs}

    def poisson_logins(self, lam: float = 1.0, per_login_load: float = 0.05) -> Dict[str, float]:
        # draw number of logins (per tick) and distribute randomly
        k = self.rng.poisson(lam) if hasattr(self.rng, 'poisson') else self._poisson_fallback(lam)
        pattern = {name: 0.0 for name in self.subs}
        for _ in range(k):
            target = self.rng.choice(self.subs)
            pattern[target] += per_login_load
        return pattern

    def burst(self, prob: float = 0.05, magnitude: float = 0.5) -> Dict[str, float]:
        pattern = {name: 0.0 for name in self.subs}
        if self.rng.random() < prob:
            # choose one subsystem to hit
            target = self.rng.choice(self.subs)
            pattern[target] = magnitude
        return pattern

    def combined(self, steady_i: float = 0.01, lam: float = 0.5, per_login_load: float = 0.03,
                 burst_prob: float = 0.02, burst_mag: float = 0.4) -> Dict[str, float]:
        p = self.steady(steady_i)
        # add poisson logins
        k = self._poisson_fallback(lam)
        for _ in range(k):
            t = self.rng.choice(self.subs)
            p[t] += per_login_load
        # possibly add burst
        if self.rng.random() < burst_prob:
            t = self.rng.choice(self.subs)
            p[t] += burst_mag
        return p

    def _poisson_fallback(self, lam: float) -> int:
        # simple Poisson via Knuth
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= self.rng.random()
        return k - 1

# ---------------------- Simulation Engine ----------------------
class Simulation:
    def __init__(self, system: SystemModel, pattern_gen: ExternalPatternGenerator,
                 duration: float = 60.0, tick: float = 1.0, seed: Optional[int] = None):
        self.system = system
        self.pattern_gen = pattern_gen
        self.duration = duration
        self.tick = tick
        self.seed = seed
        self.records: List[Dict[str, Any]] = []
        if seed is not None:
            random.seed(seed)

    def run(self, print_every: Optional[int] = None, realtime: bool = False, preset: Optional[str] = None):
        steps = max(1, int(self.duration / self.tick))
        names = [s.name for s in self.system.subsystems]

        # For sustained presets (like high_cpu) construct a persistent external base once
        sustained_base_ext = None
        if preset == 'high_cpu':
            rng = self.pattern_gen.rng
            # target sustained external load 0.7..0.9 per subsystem
            sustained_base_ext = {n: rng.uniform(0.7, 0.9) for n in names}

        for i in range(steps):
            # generate external pattern for this tick
            if sustained_base_ext is not None:
                # apply small per-tick jitter and minor stochastic extra traffic
                jitter = {n: self.pattern_gen.rng.uniform(-0.03, 0.03) for n in names}
                ext = {n: max(0.0, sustained_base_ext[n] + jitter[n]) for n in names}
                extra = self.pattern_gen.combined(steady_i=0.0, lam=0.2, per_login_load=0.005, burst_prob=0.01, burst_mag=0.05)
                for n, v in extra.items():
                    ext[n] = ext.get(n, 0.0) + v
            else:
                if preset == 'high_cpu':
                    ext = self.pattern_gen.combined(steady_i=0.05, lam=2.0, per_login_load=0.05, burst_prob=0.15, burst_mag=0.6)
                elif preset == 'low_cpu':
                    ext = self.pattern_gen.combined(steady_i=0.005, lam=0.1, per_login_load=0.01, burst_prob=0.005, burst_mag=0.1)
                elif preset == 'high_ram':
                    # larger external values so RAM_external = external * base_ram * 0.5 grows noticeably
                    ext = self.pattern_gen.combined(steady_i=0.03, lam=1.0, per_login_load=0.02, burst_prob=0.2, burst_mag=0.8)
                elif preset == 'low_ram':
                    ext = self.pattern_gen.combined(steady_i=0.002, lam=0.05, per_login_load=0.005, burst_prob=0.001, burst_mag=0.05)
                else:
                    ext = self.pattern_gen.combined()

            # compute event spikes (simulate immediate CPU spikes per login event)
            # initialize
            event_spikes = {name: 0.0 for name in names}
            # For sustained high_cpu avoid extra large spikes from thresholding; keep small transient spikes only
            if sustained_base_ext is not None:
                # small transient jitter-based spikes
                for name, val in ext.items():
                    # if the jitter pushed it above 0.95, add a small spike
                    if val > 0.95:
                        event_spikes[name] = min(20.0, (val - 0.9) * 100.0)
            else:
                # emulate a simple mapping: external pattern entries above threshold cause spike
                for name, val in ext.items():
                    if val > 0.2:
                        event_spikes[name] = min(50.0, val * 100.0)  # scale to CPU percent

            states = self.system.step(self.tick, ext, event_spikes)
            timestamp = time.time()
            rec = {
                't': i,
                'timestamp': timestamp,
                'states': [asdict(s) for s in states],
                'external': ext,
                'event_spikes': event_spikes
            }
            self.records.append(rec)

            if print_every and (i % print_every == 0):
                agg_cpu = sum(s.cpu for s in states) / max(1, len(states))
                agg_ram = sum(s.ram for s in states)
                print(f"tick={i}, avg_cpu={agg_cpu:.2f}%, total_ram={agg_ram:.1f}MB")

            if realtime:
                time.sleep(self.tick)

        return self.records

# ---------------------- Helpers and CLI ----------------------
def build_default_system(ram_mode: str = 'default', leak_rate: float = 1.0) -> SystemModel:
    subs = [
        Subsystem('web', base_cpu=5.0, base_ram=256.0, cpu_volatility=8.0, ram_volatility=20.0, ram_mode=ram_mode, leak_rate=leak_rate),
        Subsystem('app', base_cpu=10.0, base_ram=512.0, cpu_volatility=12.0, ram_volatility=30.0, ram_mode=ram_mode, leak_rate=leak_rate),
        Subsystem('db', base_cpu=3.0, base_ram=1024.0, cpu_volatility=3.0, ram_volatility=50.0, ram_mode=ram_mode, leak_rate=leak_rate),
        Subsystem('cache', base_cpu=1.0, base_ram=256.0, cpu_volatility=2.0, ram_volatility=10.0, ram_mode=ram_mode, leak_rate=leak_rate),
    ]
    return SystemModel(subs)

def save_json(path: str, records: List[Dict[str, Any]]):
    with open(path, 'w') as f:
        json.dump(records, f, indent=2, default=str)

def parse_args():
    p = argparse.ArgumentParser(description='Infrastructure simulator')
    p.add_argument('--duration', type=float, default=60.0, help='total simulation duration in seconds')
    p.add_argument('--tick', type=float, default=1.0, help='tick interval in seconds')
    p.add_argument('--print-every', type=int, default=5, help='print summary every N ticks (0 disable)')
    p.add_argument('--out', type=str, default=None, help='path to save JSON output')
    p.add_argument('--preset', choices=['high_cpu', 'low_cpu', 'high_ram', 'low_ram', 'default'], default='default')
    p.add_argument('--ram-mode', choices=['default','leak','proportional','cache'], default='default', help='RAM scaling mode for simulation')
    p.add_argument('--leak-rate', type=float, default=1.0, help='leak MB per second when --ram-mode=leak')
    p.add_argument('--realtime', action='store_true', help='sleep realtime between ticks')
    p.add_argument('--seed', type=int, default=None, help='random seed')
    return p.parse_args()

# ---------------------- Main ----------------------
if __name__ == '__main__':
    args = parse_args()
    system = build_default_system(ram_mode=args.ram_mode, leak_rate=args.leak_rate)
    gen = ExternalPatternGenerator([s.name for s in system.subsystems], seed=args.seed)
    sim = Simulation(system, gen, duration=args.duration, tick=args.tick, seed=args.seed)

    print(f"Starting simulation: duration={args.duration}s, tick={args.tick}s, preset={args.preset}")
    records = sim.run(print_every=(args.print_every if args.print_every > 0 else None), realtime=args.realtime, preset=(None if args.preset=='default' else args.preset))

    if args.out:
        save_json(args.out, records)
        print(f"Saved output to {args.out}")
    else:
        # print a short summary
        last = records[-1]
        print('\nFinal snapshot:')
        for s in last['states']:
            print(f"  {s['name']}: cpu={s['cpu']}% ram={s['ram']}MB")

    print('Done.')
