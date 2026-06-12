import StatusBadge from '../ui/StatusBadge.jsx';
import { getSubsystemHealthStatus } from '../../utils/health.js';

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

function getHealthStatus({ status, cpu, ram, external_load, event_spike }) {
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

  return getSubsystemHealthStatus({ cpu, ram, external_load, event_spike });
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
    external_load,
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

          <p className="mt-2 text-xs text-slate-600">
            Health: <span className="font-semibold text-slate-900">{healthStatus}</span>
          </p>

          <div className="mt-3 space-y-1">
            {latestFinding && (
              <p className="text-xs text-slate-500">
                Finding: {latestFinding}
              </p>
            )}
            {lastChecked && String(lastChecked).toLowerCase() !== 'null' && (
              <p className="text-xs text-slate-500">
                Checked: {lastChecked}
              </p>
            )}
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