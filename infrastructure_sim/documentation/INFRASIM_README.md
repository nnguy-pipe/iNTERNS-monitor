INFRASIM — Infrastructure Simulator

Overview

A single-file Python simulator (infrastructure_simulator.py) models a system composed of subsystems (web, app, db, cache). It simulates CPU (%), RAM (MB), and active user count per subsystem over time. Supports presets for different load patterns: high_cpu, low_cpu, high_ram, low_ram, high_users, low_users.

Quick start

- Show help: python3 infrastructure_simulator.py --help
- Run 30s, 1s tick, print every 5 ticks: python3 infrastructure_simulator.py --duration 30 --tick 1 --print-every 5
- Save SQL-compatible JSON (default): python3 infrastructure_simulator.py --duration 60 --out sim.json --preset high_users
- Save both JSON + XML: python3 infrastructure_simulator.py --duration 60 --out sim_data --out-format both --preset high_users
- Save raw format: python3 infrastructure_simulator.py --duration 60 --out sim_raw.json --out-format raw
- Test high user load: python3 infrastructure_simulator.py --preset high_users --duration 60
- Test low user load: python3 infrastructure_simulator.py --preset low_users --duration 60

What the numeric parameters mean

- base_cpu: baseline CPU usage percent for a subsystem (0–100%).
- base_ram: baseline memory in megabytes for a subsystem.
- cpu_volatility / ram_volatility: noise magnitude (std dev) used when generating random fluctuations.
- external_load (per-subsystem): a 0..~1 value representing fraction of external traffic hitting that subsystem. CPU effect = external_load * 50 (percentage points), RAM effect = external_load * base_ram * 0.5.
- active_users: integer count of concurrent users hitting a subsystem (metric only; does not directly affect simulation but is tracked for monitoring).
- steady_i: background traffic intensity.
- lam: Poisson mean for "login" events per tick.
- per_login_load: incremental external_load added per login event.
- burst_prob / burst_mag: chance and magnitude of occasional large bursts.
- event_spikes: when external_load > 0.2, an immediate CPU spike is produced (val*100 capped at 50%).

Record (JSON) format — per tick

- t: simulation tick index
- timestamp: epoch seconds when tick recorded
- states: list of subsystem snapshots: {name, cpu (percent), ram (MB), active_users (int)}
- external: map subsystem → external_load (unitless, ~0..1+)
- event_spikes: map subsystem → CPU spike percent applied that tick

Interpreting results

- CPU values are instant estimates (0–100%). Use averages over windows to estimate sustained load.
- RAM values are absolute memory usage in MB. Compare to base_ram to see growth from load or leaks.
- active_users is a metric tracking concurrent users per subsystem (scale varies by preset).
- "avg_cpu" printed in summaries is mean of subsystem CPU values; "total_ram" sums subsystem RAM.

Available presets

| Preset | CPU | RAM | Users | Description |
|--------|-----|-----|-------|-------------|
| high_cpu | 70–90% sustained | baseline+jitter | low | High sustained CPU load across subsystems |
| low_cpu | 5–15% average | baseline+jitter | minimal | Minimal load, baseline behavior |
| high_ram | 10–30% | grows +0.5%/s | low | Simulates memory leak or growth (default: +0.5% of base_ram per second) |
| low_ram | 5–15% | decays -0.2%/s | minimal | Simulates memory cleanup or reclamation |
| high_users | 10–30% | grows +0.3%/s | 500–800 (web), 400–700 (app), 50–150 (db), 100–300 (cache) | High concurrent user load; subsystems scale user count per their role |
| low_users | 5–15% | decays -0.05%/s | 10–50 (web), 5–30 (app), 1–10 (db), 5–20 (cache) | Minimal user load; decay reflects session cleanup |
| default | 5–15% | baseline+jitter | 0–50 | Balanced default behavior |

CLI knobs for RAM behavior

- --ram-mode: one of default\|leak\|proportional\|cache (default: default)
- --leak-rate: MB per second of leak when --ram-mode=leak (default: 1.0)
- --preset: one of high_cpu, low_cpu, high_ram, low_ram, high_users, low_users, default

Preset behavior examples

- High CPU + growth: python3 infrastructure_simulator.py --preset high_cpu --duration 120
- High user load with sustained metrics: python3 infrastructure_simulator.py --preset high_users --duration 120 --out sim_users.json
- Low user load with RAM decay: python3 infrastructure_simulator.py --preset low_users --duration 120
- Pronounced RAM growth: python3 infrastructure_simulator.py --preset high_ram --duration 120 --leak-rate 10.0

Output formats

Three export formats are supported via `--out-format`:

1. **sql-json** (default): Normalized JSON with schema metadata and three tables (simulations, ticks, subsystem_metrics)
   - Best for SQL import, analytics, BI tools
   - Schema includes foreign keys and primary key relationships
   - Example: `python3 infrastructure_simulator.py --out metrics.json --out-format sql-json`

2. **sql-xml**: Hierarchical XML 
   - Example: `python3 infrastructure_simulator.py --out metrics.xml --out-format sql-xml`

3. **raw**: Flat JSON array of tick records (original format)
   - Best for debugging, exploratory analysis
   - Example: `python3 infrastructure_simulator.py --out metrics_raw.json --out-format raw`

4. **both**: Generate both sql-json and sql-xml from a single base path
   - Example: `python3 infrastructure_simulator.py --out results --out-format both` → creates results.json + results.xml

SQL Import

See **SQL_IMPORT_GUIDE.md** for detailed instructions on importing JSON/XML into PostgreSQL, SQLite, MySQL, and SQL Server.

Quick import example (PostgreSQL):
```bash
# Generate data
python3 infrastructure_simulator.py --preset high_users --duration 120 --out sim.json --out-format sql-json

# Import to database (see SQL_IMPORT_GUIDE.md for DDL and Python import script)
```

Next step

The simulator now exports SQL-compatible JSON/XML formats. Use --out-format sql-json for SQL databases or --out-format both for multi-target pipelines. See SQL_IMPORT_GUIDE.md for database-specific import procedures.

Backend integration and recent changes

The simulator is integrated with the AHMS backend through API routes under /api/simulator/*.

What the simulator now does for backend testing

- Provides live subsystem metrics from the daemon on localhost:9999.
- Supports runtime preset switching (high_cpu, low_cpu, high_ram, low_ram, high_users, low_users, default).
- Can ingest one metric snapshot into the backend (single scenario).
- Can ingest a correlated full event chain (full scenario) to exercise:
   - normalization
   - reasoning and health scoring
   - anomaly detection
   - event correlation and cascading-pattern detection
   - report generation and audit logging

Important behavior changes made

1. Event source compatibility:
- Simulator-produced metric events now use source=observability for backend schema validation compatibility.

2. Full event chain support:
- A new chain generator emits multiple event types sharing one correlation id:
   - metric events (cpu_usage_percent)
   - workflow error logs (burst)
   - slow trace event
- This intentionally creates enough evidence for correlation and anomaly rules.

3. Simulator ingest endpoint enhancements:
- /api/simulator/ingest now supports:
   - scenario=single|full
   - generate_user_report=true|false
- full + generate_user_report=true ingests and immediately returns a user-facing report.

4. Run script reliability:
- run.sh now launches daemon with python3 infrastructure_sim/infrastructure_simulator_daemon.py --port 9999.

How to run end-to-end

1) Start backend and simulator daemon.

2) Ingest a full chain and generate report in one call:

```bash
curl -X POST "http://localhost:8000/api/simulator/ingest?system_name=infra-demo&environment=ci&scenario=full&generate_user_report=true"
```

3) Fetch latest user-facing report:

```bash
curl "http://localhost:8000/api/reports/user?system_name=infra-demo&environment=ci&format=markdown"
```

The report is reachable through both:
- inline response from /api/simulator/ingest with generate_user_report=true
- standalone retrieval from /api/reports/user and /api/reports/latest
