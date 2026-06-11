import { sortAlertsBySeverity } from './severity.js';

const severityRank = {
  Critical: 1,
  High: 2,
  Medium: 3,
  Low: 4,
};

const metricRules = [
  {
    key: 'cpu',
    label: 'CPU',
    unit: '%',
    warning: 75,
    critical: 90,
    weight: 0.45,
    relatedSkill: 'High CPU Usage Investigation',
    action: 'Review CPU saturation and rebalance the workload.',
    format: (value) => `${Math.round(value)}%`,
  },
  {
    key: 'ram',
    label: 'RAM',
    unit: 'MB',
    warning: 3500,
    critical: 6000,
    weight: 0.35,
    relatedSkill: 'Memory Leak Detection',
    action: 'Inspect memory growth and reclaim unnecessary cache.',
    format: (value) => `${Math.round(value)} MB`,
  },
  {
    key: 'active_users',
    label: 'users',
    unit: 'active users',
    warning: 250,
    critical: 600,
    weight: 0.2,
    relatedSkill: 'Traffic Spike Analysis',
    action: 'Validate the traffic pattern and scale if demand is sustained.',
    format: (value) => `${Math.round(value)}`,
  },
];

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function toTitleCase(value) {
  if (!value) return 'Subsystem';
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function scoreMetric(value, warning, critical) {
  if (value <= warning) return 100;
  if (value >= critical) return 20;

  const ratio = (value - warning) / (critical - warning);
  return Math.round(100 - ratio * 80);
}

function metricSeverity(value, warning, critical) {
  if (value >= critical) return 'Critical';
  if (value >= warning) return 'High';
  return null;
}

function summarizeMetric(rule, value) {
  return `${rule.label} ${rule.format(value)}`;
}

function buildSubsystemAlert(subsystem, index) {
  const monitored = metricRules
    .map((rule) => {
      const rawValue = Number(subsystem?.[rule.key] ?? 0);
      const severity = metricSeverity(rawValue, rule.warning, rule.critical);

      return severity
        ? {
            ...rule,
            rawValue,
            severity,
            score: scoreMetric(rawValue, rule.warning, rule.critical),
          }
        : null;
    })
    .filter(Boolean);

  if (monitored.length === 0) return null;

  const subsystemName = toTitleCase(subsystem?.name);
  const severity = monitored.some((item) => item.severity === 'Critical') ? 'Critical' : 'High';
  const summaryMetrics = monitored.map((item) => summarizeMetric(item, item.rawValue)).join(', ');
  const primaryMetric = monitored.reduce((current, item) => (item.score < current.score ? item : current), monitored[0]);

  return {
    id: `${subsystem?.name ?? 'subsystem'}-${index}-${monitored.map((item) => item.key).join('-')}`,
    severity,
    title: `${subsystemName} subsystem under load`,
    environment: 'Live',
    sourceAgent: `${subsystemName} Agent`,
    affectedResource: `${subsystemName} subsystem`,
    timestamp: 'Just now',
    summary: `${subsystemName} is elevated on ${summaryMetrics}.`,
    reasoning: `Live telemetry shows ${summaryMetrics}, which is above the safe operating range.`,
    suggestedActions:
      severity === 'Critical'
        ? `Reduce load on the ${subsystemName.toLowerCase()} subsystem, inspect ${primaryMetric.label.toLowerCase()} first, and watch for spillover into neighboring services.`
        : `Review the elevated ${primaryMetric.label.toLowerCase()} value and continue monitoring the ${subsystemName.toLowerCase()} subsystem.`,
    relatedSkill: primaryMetric.relatedSkill,
    confidence: clamp(78 + monitored.length * 6 + (severity === 'Critical' ? 8 : 0), 80, 99),
    status: 'Open',
  };
}

export function buildAlertsFromSubsystems(subsystems = []) {
  return subsystems
    .map((subsystem, index) => buildSubsystemAlert(subsystem, index))
    .filter(Boolean)
    .sort((a, b) => {
      const priorityA = severityRank[a.severity] || 99;
      const priorityB = severityRank[b.severity] || 99;
      return priorityA - priorityB;
    });
}

export function calculateHealthScore(subsystems = []) {
  if (!subsystems.length) return 100;

  const scores = subsystems.map((subsystem) => {
    const cpuScore = scoreMetric(Number(subsystem?.cpu ?? 0), 75, 90);
    const ramScore = scoreMetric(Number(subsystem?.ram ?? 0), 3500, 6000);
    const userScore = scoreMetric(Number(subsystem?.active_users ?? 0), 250, 600);

    return Math.round(
      cpuScore * metricRules[0].weight +
        ramScore * metricRules[1].weight +
        userScore * metricRules[2].weight,
    );
  });

  return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length);
}

export function deriveHealthSnapshot(subsystems = []) {
  const alerts = buildAlertsFromSubsystems(subsystems);
  const healthScore = calculateHealthScore(subsystems);
  const hasCriticalAlert = alerts.some((alert) => alert.severity === 'Critical');
  const status = hasCriticalAlert || healthScore < 50 ? 'Critical' : alerts.length > 0 || healthScore < 80 ? 'Degraded' : 'Healthy';

  return {
    alerts,
    healthScore,
    status,
    result:
      status === 'Healthy'
        ? 'All monitored subsystems are within safe operating ranges.'
        : status === 'Degraded'
          ? 'One or more subsystem metrics are elevated.'
          : 'One or more subsystems need immediate attention.',
    summary:
      alerts.length === 0
        ? 'CPU, RAM, and user counts are within safe thresholds across all subsystems.'
        : `${alerts.length} alert${alerts.length === 1 ? '' : 's'} surfaced from live CPU, RAM, and user data across the monitored subsystems.`,
    areasOfConcern:
      alerts.length > 0
        ? alerts.map((alert) => `${alert.sourceAgent}: ${alert.title}`)
        : ['No active concerns'],
    suggestedImprovements:
      alerts.length > 0
        ? alerts.map((alert) => alert.suggestedActions)
        : ['Continue monitoring live subsystem telemetry.'],
  };
}

export function getSortedAlerts(alerts) {
  return sortAlertsBySeverity(alerts);
}
