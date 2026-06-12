function ReportPreview({ report }) {
  const concerns = report?.areasOfConcern || [];
  const improvements = report?.suggestedImprovements || [];
  const attachedReport = report?.attachedReport || '';
  const reasoningItems = report?.reasoningItems || [];
  const correlatedEvents = report?.correlatedEvents || [];
  const anomalyItems = report?.anomalyItems || [];

  return (
    <section id="reports" className="rounded-xl bg-white p-8 border border-slate-200 h-full">
      <div className="flex flex-col gap-2">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Report</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-900">Latest health</h2>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-slate-50 p-6 border border-slate-200">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Health score</p>
          <p className="mt-3 text-5xl font-semibold text-slate-900">{report?.healthScore}</p>
          <p className="mt-2 text-sm text-slate-600">{report?.result}</p>
        </div>

        <div className="rounded-lg bg-slate-50 p-6 border border-slate-200">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Summary</p>
          <p className="mt-3 text-slate-600">{report?.summary}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Areas of concern</h3>
          <ul className="mt-4 space-y-2 text-slate-600 list-none">
            {concerns.map((item) => (
              <li key={item} className="text-sm leading-relaxed">• {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Suggested improvements</h3>
          <ul className="mt-4 space-y-2 text-slate-600 list-none">
            {improvements.map((item) => (
              <li key={item} className="text-sm leading-relaxed">• {item}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Reasoning</h3>
          {reasoningItems.length ? (
            <ul className="mt-3 space-y-2 text-slate-600 list-none">
              {reasoningItems.map((item, idx) => (
                <li key={`${idx}-${item}`} className="text-sm leading-relaxed">• {item}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-500">No reasoning chain available for this report.</p>
          )}
        </div>

        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Correlation</h3>
          <p className="mt-3 text-sm text-slate-600">Correlated events: {correlatedEvents.length}</p>
          {correlatedEvents.length ? (
            <ul className="mt-3 space-y-2 text-slate-600 list-none">
              {correlatedEvents.slice(0, 5).map((id) => (
                <li key={id} className="text-xs leading-relaxed">• {id}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-500">No correlated event chain detected.</p>
          )}
        </div>

        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Anomalies</h3>
          <p className="mt-3 text-sm text-slate-600">Detected: {anomalyItems.length}</p>
          {anomalyItems.length ? (
            <ul className="mt-3 space-y-2 text-slate-600 list-none">
              {anomalyItems.slice(0, 5).map((item, idx) => (
                <li key={`${idx}-${item.rule}`} className="text-xs leading-relaxed">
                  • [{item.severity}] {item.reason}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-500">No anomalies detected in current report window.</p>
          )}
        </div>
      </div>

      {attachedReport ? (
        <div className="mt-6 rounded-lg bg-slate-50 p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Attached backend report</h3>
          <pre className="mt-3 whitespace-pre-wrap text-xs leading-relaxed text-slate-700">{attachedReport}</pre>
        </div>
      ) : null}
    </section>
  );
}

export default ReportPreview;
