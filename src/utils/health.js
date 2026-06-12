import { sortAlertsBySeverity } from './severity.js';

const severityRank = {
  Critical: 1,
  High: 2,
  Medium: 3,
  Low: 4,
};

const subsystemThresholds = {
  cpu: { warning: 60, critical: 85 },
  ram: { warning: 2000, critical: 4000 },
  external_load: { warning: 0.2, critical: 0.35 },
  event_spike: { warning: 1, critical: 5 },
};

const subsystemMetricWeights = {
  cpu: 0.35,
  ram: 0.35,
  external_load: 0.2,
  event_spike: 0.1,
};

const statusRiskWeights = {
  Healthy: 1.0,
  Warning: 1.8,
  Critical: 3.0,
};

const metricRules = [
  {
    key: 'cpu',
    label: 'CPU',
    unit: '%',
    warning: 60,
    critical: 85,
    weight: 0.35,
    relatedSkill: 'High CPU Usage Investigation',
    action: 'Review CPU saturation and rebalance the workload.',
    format: (value) => `${Math.round(value)}%`,
  },
  {
    key: 'ram',
    label: 'RAM',
    unit: 'MB',
    warning: 2000,
    critical: 4000,
    weight: 0.35,
    relatedSkill: 'Memory Leak Detection',
    action: 'Inspect memory growth and reclaim unnecessary cache.',
    format: (value) => `${Math.round(value)} MB`,
  },
  {
    key: 'external_load',
    label: 'External load',
    unit: 'load',
    warning: 0.2,
    critical: 0.35,
    weight: 0.2,
    relatedSkill: 'Traffic Spike Analysis',
    action: 'Inspect external dependency pressure and request fan-out.',
    format: (value) => `${Number(value).toFixed(3)}`,
  },
  {
    key: 'event_spike',
    label: 'Event spike',
    unit: 'events',
    warning: 1,
    critical: 5,
    weight: 0.1,
    relatedSkill: 'Incident Correlation',
    action: 'Investigate the source of burst events and correlated failures.',
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

export function getSubsystemHealthStatus(subsystem = {}) {
  const cpuValue = Number(subsystem?.cpu ?? 0);
  const ramValue = Number(subsystem?.ram ?? 0);
  const eventSpikeValue = Number(subsystem?.event_spike ?? 0);
  const externalLoadValue = Number(subsystem?.external_load ?? 0);

  const hasAnyTelemetry =
    subsystem?.cpu !== undefined && subsystem?.cpu !== null ||
    subsystem?.ram !== undefined && subsystem?.ram !== null ||
    subsystem?.event_spike !== undefined && subsystem?.event_spike !== null ||
    subsystem?.external_load !== undefined && subsystem?.external_load !== null;

  if (!hasAnyTelemetry) return 'Unknown';

  if (
    cpuValue >= subsystemThresholds.cpu.critical ||
    ramValue >= subsystemThresholds.ram.critical ||
    eventSpikeValue >= subsystemThresholds.event_spike.critical ||
    externalLoadValue >= subsystemThresholds.external_load.critical
  ) {
    return 'Critical';
  }

  if (
    cpuValue >= subsystemThresholds.cpu.warning ||
    ramValue >= subsystemThresholds.ram.warning ||
    eventSpikeValue >= subsystemThresholds.event_spike.warning ||
    externalLoadValue >= subsystemThresholds.external_load.warning
  ) {
    return 'Warning';
  }

  return 'Healthy';
}

function scoreSubsystem(subsystem = {}) {
  const cpuScore = scoreMetric(
    Number(subsystem?.cpu ?? 0),
    subsystemThresholds.cpu.warning,
    subsystemThresholds.cpu.critical,
  );
  const ramScore = scoreMetric(
    Number(subsystem?.ram ?? 0),
    subsystemThresholds.ram.warning,
    subsystemThresholds.ram.critical,
  );
  const externalLoadScore = scoreMetric(
    Number(subsystem?.external_load ?? 0),
    subsystemThresholds.external_load.warning,
    subsystemThresholds.external_load.critical,
  );
  const eventSpikeScore = scoreMetric(
    Number(subsystem?.event_spike ?? 0),
    subsystemThresholds.event_spike.warning,
    subsystemThresholds.event_spike.critical,
  );

  return Math.round(
    cpuScore * subsystemMetricWeights.cpu +
      ramScore * subsystemMetricWeights.ram +
      externalLoadScore * subsystemMetricWeights.external_load +
      eventSpikeScore * subsystemMetricWeights.event_spike,
  );
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

  // Severity-weighted aggregation: critical agents carry substantially more weight.
  const statuses = subsystems.map((subsystem) => getSubsystemHealthStatus(subsystem));
  const criticalCount = statuses.filter((status) => status === 'Critical').length;
  const warningCount = statuses.filter((status) => status === 'Warning').length;

  const weighted = subsystems.map((subsystem) => {
    const status = getSubsystemHealthStatus(subsystem);
    const baseScore = scoreSubsystem(subsystem);
    const riskWeight = statusRiskWeights[status] || 1.0;

    return { baseScore, riskWeight };
  });

  const weightedScoreSum = weighted.reduce((sum, item) => sum + item.baseScore * item.riskWeight, 0);
  const totalWeight = weighted.reduce((sum, item) => sum + item.riskWeight, 0);
  let aggregate = Math.round(weightedScoreSum / totalWeight);

  // Severity guardrails: presence of critical agents must hard-limit final score.
  if (criticalCount >= 2) {
    aggregate = Math.min(aggregate, 45);
  } else if (criticalCount === 1) {
    aggregate = Math.min(aggregate, 60);
  } else if (warningCount >= 2) {
    aggregate = Math.min(aggregate, 75);
  }

  return aggregate;
}

export function deriveHealthSnapshot(subsystems = []) {
  const alerts = buildAlertsFromSubsystems(subsystems);
  const healthScore = calculateHealthScore(subsystems);
  const perAgentStatuses = subsystems.map((subsystem) => getSubsystemHealthStatus(subsystem));
  const criticalCount = perAgentStatuses.filter((s) => s === 'Critical').length;
  const warningCount = perAgentStatuses.filter((s) => s === 'Warning').length;

  const status =
    criticalCount >= 1 || healthScore < 50
      ? 'Critical'
      : warningCount > 0 || alerts.length > 0 || healthScore < 80
        ? 'Degraded'
        : 'Healthy';

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
        ? 'CPU, RAM, external load, and event spikes are within safe thresholds across all subsystems.'
        : criticalCount > 0
          ? `${criticalCount} critical and ${warningCount} warning agent${criticalCount + warningCount === 1 ? '' : 's'} detected from live CPU, RAM, external load, and event-spike telemetry.`
          : `${alerts.length} alert${alerts.length === 1 ? '' : 's'} surfaced from live CPU, RAM, external load, and event-spike telemetry across the monitored subsystems.`,
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
