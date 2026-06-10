import StatusBadge from '../ui/StatusBadge.jsx';

function HealthSummary({ status, score, activeAlerts, environment, summary }) {
  return (
    <section id="dashboard" className="grid gap-8 rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200 lg:grid-cols-[1.5fr_1fr]">
      <div>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Health summary</p>
            <h2 className="mt-2 text-3xl font-semibold text-slate-900">System health</h2>
          </div>
          <StatusBadge status={status} />
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-3xl bg-slate-50 p-6">
            <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Health score</p>
            <p className="mt-3 text-5xl font-semibold text-slate-900">{score}</p>
            <p className="mt-2 text-sm text-slate-500">Score from 0 to 100</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Active alerts</p>
            <p className="mt-3 text-5xl font-semibold text-slate-900">{activeAlerts}</p>
            <p className="mt-2 text-sm text-slate-500">Alerts influence health score</p>
          </div>
          <div className="rounded-3xl bg-slate-50 p-6">
            <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Environment</p>
            <p className="mt-3 text-5xl font-semibold text-slate-900">{environment}</p>
            <p className="mt-2 text-sm text-slate-500">Current mock state</p>
          </div>
        </div>
      </div>

      <div className="rounded-3xl bg-slate-50 p-6">
        <h3 className="text-lg font-semibold text-slate-900">Current summary</h3>
        <p className="mt-4 text-slate-600 leading-7">{summary}</p>
      </div>
    </section>
  );
}

export default HealthSummary;
