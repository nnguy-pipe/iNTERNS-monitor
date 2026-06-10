INFRASIM — Infrastructure Simulator

Overview

A single-file Python simulator (infrastructure_simulator.py) models a system composed of subsystems (web, app, db, cache). It simulates CPU (%) and RAM (MB) per-subsystem over time and supports presets for different external load patterns (high_cpu, low_cpu, high_ram, low_ram).

Quick start

- Show help: python infrastructure_simulator.py --help
- Run 30s, 1s tick, print every 5 ticks: python infrastructure_simulator.py --duration 30 --tick 1 --print-every 5
- Save output JSON: python infrastructure_simulator.py --duration 60 --out sim.json --preset high_cpu

What the numeric parameters mean

- base_cpu: baseline CPU usage percent for a subsystem (0–100%).
- base_ram: baseline memory in megabytes for a subsystem.
- cpu_volatility / ram_volatility: noise magnitude (std dev) used when generating random fluctuations.
- external_load (per-subsystem): a 0..~1 value representing fraction of external traffic hitting that subsystem. In the simulation this is scaled: CPU effect = external_load * 50 (percentage points), RAM effect = external_load * base_ram * 0.5.
- steady_i: background traffic intensity.
- lam: Poisson mean for "login" events per tick.
- per_login_load: incremental external_load added per login event.
- burst_prob / burst_mag: chance and magnitude of occasional large bursts.
- event_spikes: when external_load > 0.2, an immediate CPU spike is produced (val*100 capped at 50%).

Record (JSON) format — per tick

- t: simulation tick index
- timestamp: epoch seconds when tick recorded
- states: list of subsystem snapshots: {name, cpu (percent), ram (MB)}
- external: map subsystem -> external_load (unitless, ~0..1+)
- event_spikes: map subsystem -> CPU spike percent applied that tick

Interpreting results

- CPU values are instant estimates (0–100%). Use averages over windows to estimate sustained load.
- RAM values are absolute memory usage in MB. Compare to base_ram to see growth from load or leaks.
- "avg_cpu" printed in summaries is mean of subsystem CPU values; "total_ram" sums subsystem RAM.

RAM behavior options

The simulator can apply different RAM scaling behaviors. Choose one to implement (see the prompt in the CLI session):
- Ephemeral spikes: RAM increases briefly during bursts then returns to baseline (default behavior).
- Persistent memory leak: RAM increases slowly every tick and is not reclaimed.
- Proportional scaling: RAM scales proportionally to external/CPU load (ephemeral).
- Cache-like growth with gradual eviction: RAM grows on load and decays slowly when load subsides.

CLI knobs for RAM behavior

- --ram-mode: one of default|leak|proportional|cache (default: default)
- --leak-rate: MB per second of leak when --ram-mode=leak (default: 1.0)

Next step

The simulator has been updated for the selected behavior. Run with --ram-mode=leak to simulate a persistent memory leak; adjust --leak-rate to tune severity.
