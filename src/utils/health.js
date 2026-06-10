import { sortAlertsBySeverity } from './severity.js';

export function calculateHealthScore(alerts, environment) {
  const baseScore = environment === 'PROD' ? 70 : 92;
  const severityPenalty = alerts.reduce((penalty, alert) => {
    if (alert.severity === 'Critical') return penalty + 25;
    if (alert.severity === 'High') return penalty + 15;
    if (alert.severity === 'Medium') return penalty + 8;
    if (alert.severity === 'Low') return penalty + 4;
    return penalty;
  }, 0);

  return Math.max(0, Math.min(100, baseScore - severityPenalty));
}

export function getSortedAlerts(alerts) {
  return sortAlertsBySeverity(alerts);
}
