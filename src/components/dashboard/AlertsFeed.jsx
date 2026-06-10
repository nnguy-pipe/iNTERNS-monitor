import { sortAlertsBySeverity } from '../../utils/severity.js';
import SeverityPill from '../ui/SeverityPill.jsx';

function AlertsFeed({ alerts, onSelectAlert }) {
  const sortedAlerts = sortAlertsBySeverity(alerts);

  if (sortedAlerts.length === 0) {
    return (
      <section id="alerts" className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Alerts</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">No active alerts</h2>
          <p className="mt-4 text-slate-600">Everything looks healthy in this environment.</p>
        </div>
      </section>
    );
  }

  return (
    <section id="alerts" className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Alerts</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Active alert feed</h2>
        </div>
        <p className="text-sm text-slate-500">Click an alert to inspect it.</p>
      </div>

      <div className="space-y-4">
        {sortedAlerts.map((alert) => (
          <button
            type="button"
            key={`${alert.title}-${alert.timestamp}`}
            onClick={() => onSelectAlert(alert)}
            className={`w-full rounded-3xl border p-5 text-left transition hover:border-slate-300 hover:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 ${
              alert.severity === 'Critical'
                ? 'border-red-300 bg-red-50 border-l-4 pl-6'
                : 'border-slate-200 bg-slate-50'
            }`}
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityPill level={alert.severity} />
                  {alert.severity === 'Critical' && (
                    <span className="rounded-full bg-red-100 px-2 py-1 text-xs font-semibold text-red-700">Critical path</span>
                  )}
                </div>
                <h3 className="text-xl font-semibold text-slate-900">{alert.title}</h3>
                <p className="text-sm text-slate-600">{alert.summary}</p>
              </div>
              <div className="grid gap-2 text-sm text-slate-600 sm:text-right">
                <p><span className="font-semibold text-slate-800">Env:</span> {alert.environment}</p>
                <p><span className="font-semibold text-slate-800">Agent:</span> {alert.sourceAgent}</p>
                <p><span className="font-semibold text-slate-800">Resource:</span> {alert.affectedResource}</p>
                <p><span className="font-semibold text-slate-800">Time:</span> {alert.timestamp}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

export default AlertsFeed;
