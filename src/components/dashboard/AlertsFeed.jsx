import { sortAlertsBySeverity } from '../../utils/severity.js';
import SeverityPill from '../ui/SeverityPill.jsx';

function AlertsFeed({ alerts, onSelectAlert }) {
  const sortedAlerts = sortAlertsBySeverity(alerts);

  if (sortedAlerts.length === 0) {
    return (
      <section id="alerts" className="rounded-xl bg-white p-8 border border-slate-200">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Alerts</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">No active alerts</h2>
          <p className="mt-4 text-slate-600">Everything looks healthy in this environment.</p>
        </div>
      </section>
    );
  }

  return (
    <section id="alerts" className="rounded-xl bg-white p-6 border border-slate-200">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Alerts</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-900">Active</h2>
        </div>
        <p className="text-xs text-slate-500">Click to inspect</p>
      </div>

      <div className="space-y-3">
        {sortedAlerts.map((alert) => (
          <button
            type="button"
            key={`${alert.title}-${alert.timestamp}`}
            onClick={() => onSelectAlert(alert)}
            className={`w-full rounded-lg border p-3 text-left transition focus:outline-none focus:ring-2 focus:ring-sky-500 ${
              alert.severity === 'Critical'
                ? 'border-l-4 border-l-red-600 border-slate-200 bg-red-50 hover:bg-red-50'
                : 'border-slate-200 bg-white hover:bg-slate-50'
            }`}
          >
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <SeverityPill level={alert.severity} />
                  </div>
                  <h3 className="mt-1 text-base font-semibold text-slate-900">{alert.title}</h3>
                  <p className="mt-1 text-sm text-slate-600">{alert.summary}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-3 text-xs text-slate-600">
                <p><span className="font-medium text-slate-700">Agent:</span> {alert.sourceAgent}</p>
                <p><span className="font-medium text-slate-700">Resource:</span> {alert.affectedResource}</p>
                <p className="text-slate-500">{alert.timestamp}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

export default AlertsFeed;
