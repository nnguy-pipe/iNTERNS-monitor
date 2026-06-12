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
  // Generate or refresh in one call to avoid noisy 404 logs when no report exists yet.
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

  if (generated.ok) {
    return generated.json();
  }

  // Fallback to latest if generation is unavailable.
  const query = new URLSearchParams({
    system_name: systemName,
    environment,
    format: 'markdown',
  });

  const latest = await fetch(`${API_BASE}/api/reports/user?${query.toString()}`, {
    signal: AbortSignal.timeout(10000),
  });

  if (!latest.ok) {
    throw new Error(`HTTP ${generated.status}/${latest.status}`);
  }

  return latest.json();
}
