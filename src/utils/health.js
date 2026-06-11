import { sortAlertsBySeverity } from './severity.js';

function clamp(value, min = 0, max = 100) {
  return Math.max(min, Math.min(max, value));
}

function normalizeStatus(status) {
  const normalized = String(status || '').toLowerCase();

  if (!normalized || normalized === 'default' || normalized === 'null' || normalized === 'unknown') {
    return null;
  }

  if (normalized === 'healthy' || normalized === 'running') return 'Healthy';
  if (normalized === 'warning' || normalized === 'degraded') return 'Degraded';
  if (normalized === 'critical' || normalized === 'error' || normalized === 'unavailable') return 'Critical';

  return null;
}

function mapBackendScoreToPercent(rawScore) {
  const value = Number(rawScore);
  if (Number.isNaN(value)) return null;

  // Preferred backend shape is 0..1, but tolerate 0..100 if backend changes.
  if (value >= 0 && value <= 1) return clamp(Math.round(value * 100));
  if (value > 1 && value <= 100) return clamp(Math.round(value));

  return null;
}

// Rule-based temporary UI fallback. Backend remains authoritative.
export function calculateHealthScore(alerts = [], agents = [], environment = 'PROD') {
  const alertPenalty = alerts.reduce((penalty, alert) => {
    const severity = String(alert?.severity || '').toLowerCase();
    if (severity === 'critical') return penalty + 20;
    if (severity === 'high') return penalty + 10;
    if (severity === 'medium') return penalty + 6;
    if (severity === 'low') return penalty + 3;
    return penalty;
  }, 0);

  const agentStatusPenalty = agents.reduce((penalty, agent) => {
    const status = normalizeStatus(agent?.status);
    if (status === 'Critical') return penalty + 12;
    if (status === 'Degraded') return penalty + 7;
    return penalty;
  }, 0);

  const telemetryPenalty = agents.reduce((penalty, agent) => {
    let next = penalty;

    const cpu = Number(agent?.cpu);
    const ram = Number(agent?.ram);
    const eventSpike = Number(agent?.event_spike);
    const externalLoad = Number(agent?.external_load);

    if (!Number.isNaN(cpu)) {
      if (cpu >= 90) next += 6;
      else if (cpu >= 80) next += 3;
    }

    if (!Number.isNaN(ram)) {
      if (ram >= 1000) next += 6;
      else if (ram >= 800) next += 3;
    }

    if (!Number.isNaN(eventSpike)) {
      if (eventSpike >= 5) next += 5;
      else if (eventSpike > 0) next += 2;
    }

    if (!Number.isNaN(externalLoad)) {
      if (externalLoad >= 0.9) next += 4;
      else if (externalLoad >= 0.75) next += 2;
    }

    return next;
  }, 0);

  const environmentBias = environment === 'PROD' ? 5 : 0;
  const totalPenalty = alertPenalty + Math.min(agentStatusPenalty, 35) + Math.min(telemetryPenalty, 35) + environmentBias;

  return clamp(100 - totalPenalty);
}

export function deriveStatusFromScore(score) {
  if (score < 50) return 'Critical';
  if (score < 80) return 'Degraded';
  return 'Healthy';
}

export function resolveDashboardHealth({
  backendReport,
  alerts = [],
  agents = [],
  environment = 'PROD',
  fallbackSummary = '',
}) {
  const backendScore = mapBackendScoreToPercent(backendReport?.health_score);
  const backendStatus = normalizeStatus(backendReport?.status);
  const backendSummary = backendReport?.primary_issue || '';

  const score = backendScore ?? calculateHealthScore(alerts, agents, environment);
  const status = backendStatus ?? deriveStatusFromScore(score);
  const summary = backendSummary || fallbackSummary || 'No primary issue detected.';

  return {
    score,
    status,
    summary,
    source: backendScore !== null ? 'backend' : 'fallback',
  };
}

export function getSortedAlerts(alerts) {
  return sortAlertsBySeverity(alerts);
}
