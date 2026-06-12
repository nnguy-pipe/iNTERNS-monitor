/**
 * api.js
 *
 * Thin fetch helpers for the AHMS backend API.
 * Falls back gracefully when the backend or simulator daemon is unavailable.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function toBackendEnvironment(environment) {
  return environment === 'PROD' ? 'production' : 'ci';
}

/**
 * GET /api/simulator/metrics
 * Returns current CPU/RAM per subsystem from the running daemon.
 * Shape: { tick, timestamp, preset, uptime_seconds, subsystems: { web, app, db, cache } }
 */
export async function fetchSimulatorMetrics() {
  const res = await fetch(`${API_BASE}/api/simulator/metrics`, {
    signal: AbortSignal.timeout(4000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * GET /api/agents/check
 * Runs all backend agents and returns their statuses.
 * Shape: { count, agents: [{ agent, status, latest_finding, last_checked }] }
 */
export async function fetchAgentChecks() {
  const res = await fetch(`${API_BASE}/api/agents/check`, {
    signal: AbortSignal.timeout(10000),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * GET /api/reports/latest
 * Fetches the latest persisted health report for a system/environment pair.
 */
export async function fetchLatestReport(systemName, environment) {
  const backendEnv = toBackendEnvironment(environment);
  const res = await fetch(
    `${API_BASE}/api/reports/latest?system_name=${encodeURIComponent(systemName)}&environment=${encodeURIComponent(backendEnv)}`,
    {
      signal: AbortSignal.timeout(5000),
    },
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * POST /api/simulator/ingest
 * Pulls current simulator metrics into backend ingestion pipeline.
 */
export async function ingestSimulatorMetrics(systemName, environment) {
  const backendEnv = toBackendEnvironment(environment);
  const res = await fetch(
    `${API_BASE}/api/simulator/ingest?system_name=${encodeURIComponent(systemName)}&environment=${encodeURIComponent(backendEnv)}`,
    {
      method: 'POST',
      signal: AbortSignal.timeout(5000),
    },
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
