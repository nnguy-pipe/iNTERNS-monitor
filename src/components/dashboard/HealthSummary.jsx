import StatusBadge from '../ui/StatusBadge.jsx';

function HealthSummary({ status, score, activeAlerts, environment, summary }) {
  const statusLabel = `${environment} Health: ${status}`;

  return (
    <section
      id="dashboard"
      className="rounded-xl bg-white p-8 border border-slate-200 lg:grid lg:grid-cols-[1fr_360px] lg:items-center"
      aria-labelledby="health-hero-title"
    >
      <div className="flex flex-col gap-6">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Overview</p>
            <h1 id="health-hero-title" className="mt-2 text-2xl font-semibold text-slate-900">
              <span className="inline-block mr-3 text-sm text-slate-500">{statusLabel}</span>
              <StatusBadge status={status} />
            </h1>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end">
              <p className="text-sm text-slate-500">Health score</p>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-6xl font-extrabold text-slate-900 leading-none">{score}</span>
                <span className="text-sm font-medium text-slate-500">/100</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <div className="px-4 py-2 text-sm font-medium text-slate-700">Active alerts: <span className="font-semibold text-slate-900">{activeAlerts}</span></div>
          <div className="px-4 py-2 text-sm font-medium text-slate-700">Environment: <span className="font-semibold text-slate-900">{environment}</span></div>
        </div>

        <p className="mt-4 max-w-3xl text-slate-700 text-lg leading-7">{summary}</p>
      </div>

      <aside className="mt-6 lg:mt-0 lg:ml-6">
        <div className="rounded-lg bg-white p-6 text-slate-900 border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-700">Command center</h3>
          <p className="mt-3 text-sm text-slate-600">Actions: acknowledge alerts, review agents, or open the detailed report.</p>
          <div className="mt-6 flex gap-3">
            <button className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-slate-900 ring-1 ring-slate-200">Acknowledge</button>
            <button className="rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white">Open report</button>
          </div>
        </div>
      </aside>
    </section>
  );
}

export default HealthSummary;
