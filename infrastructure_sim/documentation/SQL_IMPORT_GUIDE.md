# SQL Import Guide for Infrastructure Simulator

This guide explains how to import JSON and XML simulation output into SQL databases.

## Export Formats

The simulator supports three SQL-compatible export formats:

### 1. SQL-JSON Format (Recommended)
- **File extension**: `.json`
- **CLI flag**: `--out-format sql-json` (default)
- **Structure**: Normalized 3-table schema with metadata section
- **Best for**: Direct import to SQL or NoSQL, analytical queries

### 2. SQL-XML Format
- **File extension**: `.xml`
- **CLI flag**: `--out-format sql-xml`
- **Structure**: Hierarchical XML with schema version
- **Best for**: ETL pipelines, XML-native databases
- XML format has easily readable data to be displayed in excel for easy visualization. 

### 3. Raw Format
- **File extension**: `.json`
- **CLI flag**: `--out-format raw`
- **Structure**: Flat array of tick records (original format)
- **Best for**: Debugging, raw data analysis

### 4. Both Formats
- **CLI flag**: `--out-format both`
- **Output**: Generates both `.json` and `.xml` files from base path
- **Best for**: Multi-target pipelines

## SQL-JSON Structure

The SQL-JSON format outputs a single JSON file with three normalized tables:

```json
{
  "schema": {
    "simulations": [...],
    "ticks": [...],
    "subsystem_metrics": [...]
  },
  "data": {
    "simulations": [...],
    "ticks": [...],
    "subsystem_metrics": [...]
  }
}
```

### Table 1: `simulations`
Metadata about each simulation run.

**Columns:**
- `simulation_id` (PK): Unique identifier (e.g., "sim_001")
- `start_timestamp`: Epoch seconds when run started
- `end_timestamp`: Epoch seconds when run ended
- `total_ticks`: Number of ticks in run
- `tick_interval_seconds`: Duration per tick (default 1.0)

**Example:**
```json
{
  "simulation_id": "sim_001",
  "start_timestamp": 1781110381.6885266,
  "end_timestamp": 1781110381.6886833,
  "total_ticks": 5,
  "tick_interval_seconds": 1.0
}
```

### Table 2: `ticks`
Each tick/time step in the simulation.

**Columns:**
- `tick_id` (PK): Unique tick identifier (e.g., "sim_001_t0")
- `simulation_id` (FK): Reference to simulations table
- `tick_number`: Sequential tick index (0, 1, 2, ...)
- `timestamp`: Epoch seconds for this tick

**Example:**
```json
{
  "tick_id": "sim_001_t0",
  "simulation_id": "sim_001",
  "tick_number": 0,
  "timestamp": 1781110381.6885266
}
```

### Table 3: `subsystem_metrics`
Per-subsystem metrics for each tick (4+ rows per tick, one per subsystem).

**Columns:**
- `metric_id` (PK): Unique metric identifier (e.g., "sim_001_t0_web")
- `tick_id` (FK): Reference to ticks table
- `simulation_id` (FK): Reference to simulations table
- `subsystem`: Subsystem name (web, app, db, cache)
- `tick_number`: Sequential tick index
- `timestamp`: Epoch seconds for this tick
- `cpu_percent`: CPU utilization (0–100%)
- `ram_mb`: RAM usage in megabytes
- `active_users`: Count of active users
- `external_load`: External load factor (0..~1+)
- `event_spike_percent`: CPU spike from events (0–100%)

**Example:**
```json
{
  "metric_id": "sim_001_t0_web",
  "tick_id": "sim_001_t0",
  "simulation_id": "sim_001",
  "subsystem": "web",
  "tick_number": 0,
  "timestamp": 1781110381.6885266,
  "cpu_percent": 18.286,
  "ram_mb": 285.32,
  "active_users": 801,
  "external_load": 0.18,
  "event_spike_percent": 0.0
}
```

## Importing to PostgreSQL

### 1. Create Tables

```sql
CREATE TABLE simulations (
  simulation_id VARCHAR(50) PRIMARY KEY,
  start_timestamp DOUBLE PRECISION NOT NULL,
  end_timestamp DOUBLE PRECISION NOT NULL,
  total_ticks INTEGER NOT NULL,
  tick_interval_seconds DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ticks (
  tick_id VARCHAR(100) PRIMARY KEY,
  simulation_id VARCHAR(50) NOT NULL REFERENCES simulations(simulation_id),
  tick_number INTEGER NOT NULL,
  timestamp DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticks_simulation ON ticks(simulation_id);
CREATE INDEX idx_ticks_timestamp ON ticks(timestamp);

CREATE TABLE subsystem_metrics (
  metric_id VARCHAR(100) PRIMARY KEY,
  tick_id VARCHAR(100) NOT NULL REFERENCES ticks(tick_id),
  simulation_id VARCHAR(50) NOT NULL REFERENCES simulations(simulation_id),
  subsystem VARCHAR(50) NOT NULL,
  tick_number INTEGER NOT NULL,
  timestamp DOUBLE PRECISION NOT NULL,
  cpu_percent DOUBLE PRECISION NOT NULL,
  ram_mb DOUBLE PRECISION NOT NULL,
  active_users INTEGER NOT NULL,
  external_load DOUBLE PRECISION NOT NULL,
  event_spike_percent DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_simulation ON subsystem_metrics(simulation_id);
CREATE INDEX idx_metrics_subsystem ON subsystem_metrics(subsystem);
CREATE INDEX idx_metrics_timestamp ON subsystem_metrics(timestamp);
```

### 2. Import JSON Using Python

```python
import json
import psycopg2

# Read JSON file
with open('sim_output.json', 'r') as f:
    data = json.load(f)

# Connect to database
conn = psycopg2.connect("dbname=monitor user=postgres")
cur = conn.cursor()

# Insert simulations
for sim in data['data']['simulations']:
    cur.execute("""
        INSERT INTO simulations (simulation_id, start_timestamp, end_timestamp, total_ticks, tick_interval_seconds)
        VALUES (%(simulation_id)s, %(start_timestamp)s, %(end_timestamp)s, %(total_ticks)s, %(tick_interval_seconds)s)
        ON CONFLICT (simulation_id) DO NOTHING
    """, sim)

# Insert ticks
for tick in data['data']['ticks']:
    cur.execute("""
        INSERT INTO ticks (tick_id, simulation_id, tick_number, timestamp)
        VALUES (%(tick_id)s, %(simulation_id)s, %(tick_number)s, %(timestamp)s)
        ON CONFLICT (tick_id) DO NOTHING
    """, tick)

# Insert metrics
for metric in data['data']['subsystem_metrics']:
    cur.execute("""
        INSERT INTO subsystem_metrics
        (metric_id, tick_id, simulation_id, subsystem, tick_number, timestamp, cpu_percent, ram_mb, active_users, external_load, event_spike_percent)
        VALUES (%(metric_id)s, %(tick_id)s, %(simulation_id)s, %(subsystem)s, %(tick_number)s, %(timestamp)s, %(cpu_percent)s, %(ram_mb)s, %(active_users)s, %(external_load)s, %(event_spike_percent)s)
        ON CONFLICT (metric_id) DO NOTHING
    """, metric)

conn.commit()
cur.close()
conn.close()
print("Import complete!")
```

### 3. Example Queries

**Average CPU per subsystem:**
```sql
SELECT subsystem, AVG(cpu_percent) as avg_cpu
FROM subsystem_metrics
WHERE simulation_id = 'sim_001'
GROUP BY subsystem
ORDER BY avg_cpu DESC;
```

**Peak RAM usage:**
```sql
SELECT subsystem, MAX(ram_mb) as peak_ram, timestamp
FROM subsystem_metrics
WHERE simulation_id = 'sim_001'
GROUP BY subsystem, timestamp
ORDER BY peak_ram DESC
LIMIT 10;
```

**Active users over time:**
```sql
SELECT tick_number, subsystem, active_users
FROM subsystem_metrics
WHERE simulation_id = 'sim_001'
ORDER BY tick_number, subsystem;
```

**Correlate CPU spikes with external load:**
```sql
SELECT tick_number, subsystem, cpu_percent, event_spike_percent, external_load
FROM subsystem_metrics
WHERE simulation_id = 'sim_001' AND event_spike_percent > 0
ORDER BY tick_number;
```

## Importing to SQLite

Similar approach; use SQLite pragmas for better performance:

```python
import json
import sqlite3

with open('sim_output.json', 'r') as f:
    data = json.load(f)

conn = sqlite3.connect(':memory:')  # or 'metrics.db'
cur = conn.cursor()

# Enable foreign keys and bulk insert
cur.execute("PRAGMA foreign_keys = ON")
cur.execute("PRAGMA journal_mode = WAL")

# Create tables (adapt from PostgreSQL DDL above)
# ... (see schema creation SQL)

# Bulk insert simulations
cur.executemany("""
    INSERT INTO simulations VALUES (?, ?, ?, ?, ?)
""", [(s['simulation_id'], s['start_timestamp'], s['end_timestamp'], s['total_ticks'], s['tick_interval_seconds'])
      for s in data['data']['simulations']])

conn.commit()
conn.close()
```

## Importing to MySQL

```sql
CREATE TABLE simulations (
  simulation_id VARCHAR(50) PRIMARY KEY,
  start_timestamp DOUBLE NOT NULL,
  end_timestamp DOUBLE NOT NULL,
  total_ticks INT NOT NULL,
  tick_interval_seconds DOUBLE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Load JSON using JSON functions (MySQL 5.7+)
INSERT INTO simulations
SELECT 
  JSON_UNQUOTE(JSON_EXTRACT(d, '$.simulation_id')) as simulation_id,
  JSON_EXTRACT(d, '$.start_timestamp') as start_timestamp,
  JSON_EXTRACT(d, '$.end_timestamp') as end_timestamp,
  JSON_EXTRACT(d, '$.total_ticks') as total_ticks,
  JSON_EXTRACT(d, '$.tick_interval_seconds') as tick_interval_seconds
FROM JSON_TABLE(
  (SELECT data FROM simulation_json),
  '$.data.simulations[*]' COLUMNS (d JSON PATH '$')
) jt;
```

## CLI Examples

**Generate high-user-load simulation with SQL-JSON export:**
```bash
python3 infrastructure_simulator.py \
  --preset high_users \
  --duration 120 \
  --tick 1 \
  --out metrics_high_users.json \
  --out-format sql-json \
  --sim-id "load_test_001"
```

**Generate both JSON and XML for dual-target pipeline:**
```bash
python3 infrastructure_simulator.py \
  --preset high_cpu \
  --duration 60 \
  --out sim_results \
  --out-format both \
  --sim-id "cpu_test_001"
# Creates: sim_results.json, sim_results.xml
```

**High RAM growth scenario for database testing:**
```bash
python3 infrastructure_simulator.py \
  --preset high_ram \
  --duration 300 \
  --leak-rate 5.0 \
  --out ram_leak_test.json \
  --out-format sql-json \
  --sim-id "ram_leak_001"
```

## Notes

- All timestamps are in epoch seconds (UNIX time)
- CPU and RAM metrics are real-valued; consider rounding for display
- `active_users` is integer; use for aggregations or user-centric queries
- `external_load` ranges 0..~1+ (can exceed 1.0 under high load)
- Foreign key constraints ensure referential integrity; import simulations before ticks before metrics
- The `metric_id` uses format `{sim_id}_t{tick}__{subsystem}` for easy decomposition
