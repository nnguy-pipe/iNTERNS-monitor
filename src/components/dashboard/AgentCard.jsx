import StatusBadge from '../ui/StatusBadge.jsx';

function formatAgentName(name) {
  if (!name) return 'Unknown';

  const specialNames = {
    db: 'DB',
    api: 'API',
    ci: 'CI',
    cpu: 'CPU',
    ram: 'RAM',
  };

  const normalized = String(name).toLowerCase();

  if (specialNames[normalized]) {
    return specialNames[normalized];
  }

  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function getHealthStatus({ status, cpu, ram, event_spike }) {
  const normalizedStatus = String(status || '').toLowerCase();

  // Use backend status only when it is a meaningful value.
  if (
    normalizedStatus &&
    normalizedStatus !== 'default' &&
    normalizedStatus !== 'null' &&
    normalizedStatus !== 'unknown'
  ) {
    return status;
  }

  const cpuValue = Number(cpu ?? 0);
  const ramValue = Number(ram ?? 0);
  const eventSpikeValue = Number(event_spike ?? 0);

  const hasAnyTelemetry =
    cpu !== undefined && cpu !== null ||
    ram !== undefined && ram !== null ||
    event_spike !== undefined && event_spike !== null;

  // If backend status is unknown/default and there is no telemetry, keep it Unknown.
  if (!hasAnyTelemetry) {
    return 'Unknown';
  }

  // You can tune these thresholds later.
  if (cpuValue >= 85 || ramValue >= 4000 || eventSpikeValue >= 5) {
    return 'Critical';
  }

  if (cpuValue >= 60 || ramValue >= 2000 || eventSpikeValue > 0) {
    return 'Warning';
  }

  return 'Healthy';
}

function formatNumber(value, decimals = 2) {
  if (value === undefined || value === null) return 'N/A';

  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return value;
  }

  return numericValue.toFixed(decimals);
}

function AgentCard({
  name,
  scope,
  status,
  latestFinding,
  lastChecked,
  cpu,
  ram,
  active_users,
  external_load,
  event_spike,
}) {
  const displayName = formatAgentName(name);

  const healthStatus = getHealthStatus({
    status,
    cpu,
    ram,
    event_spike,
  });

  return (
    <article className="h-full rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            {displayName}
          </h3>
          {scope && <p className="mt-1 text-xs text-slate-500">{scope}</p>}
          <div className="mt-3 space-y-1">
            <p className="text-xs text-slate-500">
              CPU: {formatNumber(cpu)}%
            </p>
            <p className="text-xs text-slate-500">
              RAM: {formatNumber(ram)} mb
            </p>
            <p className="text-xs text-slate-500">
              Active Users: {active_users ?? 'N/A'}
            </p>
            <p className="text-xs text-slate-500">
              External Load: {formatNumber(external_load, 3)}
            </p>
            <p className="text-xs text-slate-500">
              Event Spike: {event_spike ?? 'N/A'}
            </p>
          </div>
        </div>
        <StatusBadge status={healthStatus} />
      </div>
    </article>
  );
}

export default AgentCard;