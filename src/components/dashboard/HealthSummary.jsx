import StatusBadge from '../ui/StatusBadge.jsx';

function HealthSummary({
  status,
  score,
  activeAlerts,
  environment,
  summary,
  scoreSource = 'backend',
  onOpenReport,
}) {
  const numericScore = Number(score) || 0;

  // Keep visual state consistent with score thresholds.
  const getVisualStatus = () => {
    if (numericScore >= 85) return 'Healthy';
    if (numericScore >= 70) return 'Warning';
    if (numericScore >= 50) return 'Degraded';
    return 'Critical';
  };

  const getHealthLabel = () => {
    if (numericScore >= 85) return 'Running smoothly';
    if (numericScore >= 70) return 'Mostly healthy with caution';
    if (numericScore >= 50) return 'Degraded - attention needed';
    return 'Critical - immediate action required';
  };

  const getProgressColor = () => {
    const visualStatus = getVisualStatus();
    if (visualStatus === 'Healthy') return 'bg-emerald-500';
    if (visualStatus === 'Warning' || visualStatus === 'Degraded') return 'bg-amber-500';
    return 'bg-red-500';
  };

  const getAlertAccent = () => {
    return activeAlerts > 0 ? 'text-amber-600' : 'text-slate-700';
  };

  const fallbackSummary =
    activeAlerts > 0
      ? `${activeAlerts} active alert${activeAlerts === 1 ? '' : 's'} detected in live telemetry.`
      : 'Live telemetry is within expected operating thresholds.';

  const displayStatus = getVisualStatus();
  const hasContradictorySummary =
    displayStatus === 'Healthy' &&
    typeof summary === 'string' &&
    /(error|fail|critical|degraded|incident)/i.test(summary);
  const displaySummary = hasContradictorySummary ? fallbackSummary : (summary || fallbackSummary);

  return (
    <section
      id="dashboard"
      className={`rounded-xl bg-white p-8 border lg:grid lg:grid-cols-[1fr_360px] lg:items-center ${
        environment === 'PROD'
          ? 'border-slate-200'
          : 'border-slate-200 bg-slate-50/50'
      }`}
      aria-labelledby="health-hero-title"
    >
      <div className="flex flex-col gap-6">
        <div className="flex items-start justify-between gap-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">{environment} Health</p>
            <h1 id="health-hero-title" className="mt-2 flex items-center gap-3">
              <StatusBadge status={displayStatus} />
            </h1>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex flex-col items-end">
              <p className="text-sm text-slate-500">Health score</p>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-6xl font-extrabold text-slate-900 leading-none">{Math.round(numericScore)}</span>
                <span className="text-sm font-medium text-slate-500">/100</span>
              </div>
              <p className="mt-2 text-xs text-slate-600">{getHealthLabel()}</p>
              <p
                className={`mt-1 text-[11px] font-medium uppercase tracking-[0.08em] ${
                  scoreSource === 'backend' ? 'text-emerald-700' : 'text-amber-700'
                }`}
              >
                Source: {scoreSource === 'backend' ? 'Backend' : 'Fallback'}
              </p>
              <div className="mt-3 w-24 h-1 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getProgressColor()}`}
                  style={{ width: `${Math.min(Math.max(numericScore, 0), 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        <p className="mt-4 max-w-3xl text-slate-700 text-lg leading-7">{displaySummary}</p>
      </div>

      <aside className="mt-6 lg:mt-0 lg:ml-6">
        <div className="rounded-lg bg-white p-6 text-slate-900 border border-slate-200 space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-slate-700">Status snapshot</h3>
            <div className="mt-3 space-y-2 text-sm">
              <div className={`flex justify-between ${activeAlerts > 0 ? 'p-2 rounded-md bg-amber-50' : ''}`}>
                <span className="text-slate-500">Active alerts</span>
                <span className={`font-semibold ${getAlertAccent()}`}>{activeAlerts}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Environment</span>
                <span className="font-semibold text-slate-900">{environment}</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700">Command center</h3>
            <p className="mt-2 text-sm text-slate-600">Acknowledge alerts, review agents, or open the detailed report.</p>
            <div className="mt-4 flex gap-3">
              <button className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-slate-900 ring-1 ring-slate-200">Acknowledge</button>
              <button
                className="rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white"
                onClick={onOpenReport}
              >
                Open report
              </button>
            </div>
          </div>
        </div>
      </aside>
    </section>
  );
}

export default HealthSummary;
