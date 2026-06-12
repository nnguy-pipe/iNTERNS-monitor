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
  type,
}) {
  const displayName = formatAgentName(name);

  const healthStatus = getHealthStatus({
    status,
    cpu,
    ram,
    event_spike,
  });

  const isSubsystem = type === 'subsystem';

  return (
    <article className="h-full rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-900">
            {displayName}
          </h3>
          {scope && <p className="mt-1 text-xs text-slate-500">{scope}</p>}
          {isSubsystem && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">CPU</p>
                <p className="text-sm font-medium text-slate-700">{formatNumber(cpu)}%</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">RAM</p>
                <p className="text-sm font-medium text-slate-700">{formatNumber(ram)} mb</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">Active Users</p>
                <p className="text-sm font-medium text-slate-700">{active_users ?? 'N/A'}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">Ext Load</p>
                <p className="text-sm font-medium text-slate-700">{formatNumber(external_load, 3)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-[10px] uppercase tracking-wider text-slate-400">Event Spike</p>
                <p className="text-sm font-medium text-slate-700">{event_spike ?? 'N/A'}</p>
              </div>
            </div>
          )}
          {latestFinding ? (
            <p className="mt-3 text-xs text-slate-600 leading-relaxed">{latestFinding}</p>
          ) : null}
          {lastChecked ? (
            <p className="mt-2 text-[11px] text-slate-500">Last checked: {lastChecked}</p>
          ) : null}
        </div>
        <StatusBadge status={healthStatus} />
      </div>
    </article>
  );
}

export default AgentCard;