function ReportPreview({ report }) {
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
          <p className="mt-3 text-5xl font-semibold text-slate-900">{report.healthScore}</p>
          <p className="mt-2 text-sm text-slate-600">{report.result}</p>
        </div>

        <div className="rounded-lg bg-slate-50 p-6 border border-slate-200">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Summary</p>
          <p className="mt-3 text-slate-600">{report.summary}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Areas of concern</h3>
          <ul className="mt-4 space-y-2 text-slate-600 list-none">
            {report.areasOfConcern.map((item) => (
              <li key={item} className="text-sm leading-relaxed">• {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg bg-white p-6 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Suggested improvements</h3>
          <ul className="mt-4 space-y-2 text-slate-600 list-none">
            {report.suggestedImprovements.map((item) => (
              <li key={item} className="text-sm leading-relaxed">• {item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default ReportPreview;
