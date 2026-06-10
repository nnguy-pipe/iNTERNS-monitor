# Infrastructure Simulator — Export & SQL Integration Summary

## Overview

The infrastructure simulator has been fully implemented with SQL-compatible export capabilities. The simulator generates infrastructure metrics (CPU, RAM, active users) for subsystems and exports them in formats designed for easy SQL import.

## What's Implemented

### ✅ Simulator Features
- **Subsystems**: web, app, db, cache (4 independent systems)
- **Metrics**: CPU (%), RAM (MB), active user count
- **Presets**:
  - `high_cpu`: 70–90% sustained CPU with minimal RAM growth
  - `low_cpu`: 5–15% baseline load
  - `high_ram`: Consistent RAM growth (+0.5% per second)
  - `low_ram`: Steady RAM decay (-0.2% per second)
  - `high_users`: 500–800 users (web), 400–700 (app), with RAM growth
  - `low_users`: 10–50 users, minimal load with RAM decay
  - `default`: Balanced baseline behavior

### ✅ Export Formats (SQL-Compatible)
1. **SQL-JSON** (default): Normalized 3-table schema with metadata
   - `simulations`: Run metadata
   - `ticks`: Time steps
   - `subsystem_metrics`: Per-subsystem metrics per tick
   - Foreign key relationships included in schema

2. **SQL-XML**: Hierarchical XML structure
   - Suitable for ETL, XML-native databases
   - Schema version tracking
   - Element-per-value structure for easy parsing

3. **Raw JSON**: Flat tick array (original format)
   - For debugging, exploratory analysis
   - No schema metadata

4. **Both**: Generate JSON + XML from single invocation

### ✅ CLI Interface
```bash
# Basic examples
python3 infrastructure_simulator.py --help
python3 infrastructure_simulator.py --preset high_users --duration 120 --out metrics.json

# Export formats
python3 infrastructure_simulator.py --out data.json --out-format sql-json      # Default
python3 infrastructure_simulator.py --out data.xml --out-format sql-xml        # XML only
python3 infrastructure_simulator.py --out data.json --out-format raw           # Raw flat
python3 infrastructure_simulator.py --out data --out-format both               # Both JSON + XML

# Advanced options
python3 infrastructure_simulator.py \
  --preset high_cpu \
  --duration 300 \
  --tick 1 \
  --out sim_results.json \
  --out-format sql-json \
  --sim-id "load_test_001" \
  --print-every 10
```

## File Structure

```
infrastructure_sim/
├── infrastructure_simulator.py       # Main simulator (single-file, ~450 lines)
├── INFRASIM_README.md               # Quick start & parameters guide
├── SQL_IMPORT_GUIDE.md              # Detailed SQL import instructions (PostgreSQL, SQLite, MySQL)
└── EXPORT_SUMMARY.md                # This file
```

## SQL Schema (Normalized)

### Table: `simulations`
Metadata about simulation runs.
```
simulation_id        VARCHAR(50)   PRIMARY KEY
start_timestamp      DOUBLE PRECISION
end_timestamp        DOUBLE PRECISION
total_ticks          INTEGER
tick_interval_seconds DOUBLE PRECISION
created_at           TIMESTAMP (added on import)
```

### Table: `ticks`
Individual time steps.
```
tick_id              VARCHAR(100)  PRIMARY KEY
simulation_id        VARCHAR(50)   FOREIGN KEY → simulations
tick_number          INTEGER
timestamp            DOUBLE PRECISION
created_at           TIMESTAMP (added on import)
```

### Table: `subsystem_metrics`
Per-subsystem measurements at each tick.
```
metric_id            VARCHAR(100)  PRIMARY KEY
tick_id              VARCHAR(100)  FOREIGN KEY → ticks
simulation_id        VARCHAR(50)   FOREIGN KEY → simulations
subsystem            VARCHAR(50)   (web, app, db, cache)
tick_number          INTEGER
timestamp            DOUBLE PRECISION
cpu_percent          DOUBLE PRECISION (0–100)
ram_mb               DOUBLE PRECISION
active_users         INTEGER
external_load        DOUBLE PRECISION (0..~1+)
event_spike_percent  DOUBLE PRECISION (0–100)
created_at           TIMESTAMP (added on import)
```

## Data Volume Examples

For a 120-second simulation at 1-second intervals:
- **Simulations table**: 1 row
- **Ticks table**: 120 rows
- **Subsystem_metrics table**: 480 rows (120 ticks × 4 subsystems)
- **JSON file size**: ~60–80 KB
- **XML file size**: ~120–160 KB

For 1-hour simulations (3,600 seconds):
- **Subsystem_metrics table**: 14,400 rows
- **JSON file size**: ~1.8–2.2 MB
- **XML file size**: ~3.6–4.8 MB

## Import Workflows

### Quick Start (PostgreSQL)
```bash
# 1. Generate data
python3 infrastructure_simulator.py --preset high_users --duration 120 \
  --out metrics.json --out-format sql-json --sim-id "run_001"

# 2. Create tables (from SQL_IMPORT_GUIDE.md DDL)
psql -U postgres < schema.sql

# 3. Import JSON via Python script (see SQL_IMPORT_GUIDE.md)
python3 import_json.py metrics.json
```

### Multi-Target Pipeline
```bash
# Generate both formats
python3 infrastructure_simulator.py --preset high_cpu --duration 300 \
  --out /data/results --out-format both --sim-id "perf_test_001"

# Results:
# - /data/results.json  → PostgreSQL, SQLite
# - /data/results.xml   → XML-native DB, ETL tools
```

### Time-Series Analysis
```bash
# High-resolution 1-minute run
python3 infrastructure_simulator.py \
  --preset high_users \
  --duration 60 \
  --tick 1 \
  --out timeseries.json \
  --out-format sql-json

# Then query in SQL:
# SELECT subsystem, AVG(cpu_percent), MAX(ram_mb), COUNT(active_users)
# FROM subsystem_metrics
# WHERE simulation_id = 'sim_001'
# GROUP BY subsystem;
```

## Key Features

✅ **SQL-Ready**: Normalized schema eliminates duplication, enables easy joins  
✅ **Foreign Keys**: Enforces referential integrity (when imported)  
✅ **Metrics-Rich**: Tracks CPU, RAM, users, external load, event spikes  
✅ **Identifiable**: All records have globally-unique IDs (simulation_id, tick_id, metric_id)  
✅ **Timestamped**: Epoch seconds for easy temporal queries  
✅ **Dual Format**: JSON for relational DBs, XML for ETL/document stores  
✅ **Readable**: Formatted with indentation, human-inspectable  
✅ **Lightweight**: 60–80 KB for 2-minute simulations  

## Usage in Analytics

### Example: Detect Performance Issues
```sql
-- Find subsystems with sustained high CPU (>80%)
SELECT simulation_id, subsystem, COUNT(*) as high_cpu_ticks, AVG(cpu_percent) as avg_cpu
FROM subsystem_metrics
WHERE cpu_percent > 80
GROUP BY simulation_id, subsystem
HAVING COUNT(*) > 5
ORDER BY avg_cpu DESC;
```

### Example: Memory Leak Detection
```sql
-- Track RAM growth per subsystem
SELECT 
  subsystem,
  tick_number,
  ram_mb,
  LAG(ram_mb) OVER (PARTITION BY subsystem ORDER BY tick_number) as prev_ram,
  ram_mb - LAG(ram_mb) OVER (PARTITION BY subsystem ORDER BY tick_number) as ram_delta
FROM subsystem_metrics
WHERE simulation_id = 'leak_test_001'
ORDER BY subsystem, tick_number;
```

### Example: User Load Correlation
```sql
-- Correlate active users with CPU usage
SELECT 
  tick_number,
  subsystem,
  active_users,
  cpu_percent,
  ROUND(cpu_percent / NULLIF(active_users, 0), 2) as cpu_per_user
FROM subsystem_metrics
WHERE simulation_id = 'high_users_001'
ORDER BY tick_number, subsystem;
```

## Next Steps

1. **Choose your database**: PostgreSQL recommended for complex queries, SQLite for local analysis
2. **Create tables**: Use DDL from SQL_IMPORT_GUIDE.md
3. **Generate simulation data**: Run simulator with `--out-format sql-json`
4. **Import**: Use Python script or SQL LOAD DATA for bulk import
5. **Query**: Run analytics to detect patterns, anomalies, correlations

## Documentation Files

- **INFRASIM_README.md**: Simulator usage, presets, parameters
- **SQL_IMPORT_GUIDE.md**: Database-specific DDL, import scripts, example queries
- **EXPORT_SUMMARY.md**: This file — overview of export capabilities and integration

## Support for Multiple SQL Engines

- ✅ PostgreSQL (tested)
- ✅ SQLite (tested)
- ✅ MySQL 5.7+ (DDL provided)
- ✅ SQL Server (schema portable)
- ✅ Generic SQL (ANSI-compatible)

---

**Status**: ✅ Production Ready  
**No frontend**: ✅ CLI + SQL output only  
**Single file**: ✅ infrastructure_simulator.py (~450 lines)
