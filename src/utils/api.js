/**
 * api.js
 *
 * Thin fetch helpers for the AHMS backend API.
 * Falls back gracefully when the backend or simulator daemon is unavailable.
 */

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
 * POST /api/simulator/ingest
 * Pulls current daemon metrics into backend ingestion so report scores can refresh from DB.
 */
export async function ingestSimulatorSnapshot(systemName, environment) {
  const query = new URLSearchParams({
    system_name: systemName,
    environment,
    scenario: 'single',
    generate_user_report: 'true',
  });

  const res = await fetch(`${API_BASE}/api/simulator/ingest?${query.toString()}`, {
    method: 'POST',
    signal: AbortSignal.timeout(8000),
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
 * GET /api/reports/user?format=markdown
 * Falls back to POST /api/reports/user/generate when no report exists.
 */
export async function fetchUserReport(systemName, environment) {
  // Generate or refresh in one call when supported.
  let generatedStatus = 'ERR';
  try {
    const generated = await fetch(`${API_BASE}/api/reports/user/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_name: systemName,
        environment,
        lookback_minutes: 60,
        format: 'markdown',
      }),
      signal: AbortSignal.timeout(15000),
    });

    generatedStatus = String(generated.status);
    if (generated.ok) {
      return generated.json();
    }
  } catch {
    // Fallback to read-only report endpoints.
  }

  // Fallback to latest user-facing report when generation is unavailable.
  const query = new URLSearchParams({
    system_name: systemName,
    environment,
    format: 'markdown',
  });

  let latestStatus = 'ERR';
  try {
    const latest = await fetch(`${API_BASE}/api/reports/user?${query.toString()}`, {
      signal: AbortSignal.timeout(10000),
    });
    latestStatus = String(latest.status);
    if (latest.ok) {
      return latest.json();
    }
  } catch {
    // Continue to final fallback.
  }

  const latestBasic = await fetch(`${API_BASE}/api/reports/latest?${query.toString()}`, {
    signal: AbortSignal.timeout(10000),
  });
  if (!latestBasic.ok) {
    throw new Error(`HTTP ${generatedStatus}/${latestStatus}/${latestBasic.status}`);
  }
  return latestBasic.json();
}
