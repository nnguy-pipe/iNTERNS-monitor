function ReportPreview({ report }) {
  return (
    <section id="reports" className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Report preview</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Latest health report</h2>
        </div>
        <p className="text-sm text-slate-500">Review production and CI summary details.</p>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl bg-slate-50 p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Health score</p>
          <p className="mt-3 text-5xl font-semibold text-slate-900">{report.healthScore}</p>
          <p className="mt-2 text-sm text-slate-600">{report.result}</p>
        </div>

        <div className="rounded-3xl bg-slate-50 p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Summary</p>
          <p className="mt-3 text-slate-600">{report.summary}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Areas of concern</h3>
          <ul className="mt-4 space-y-3 text-slate-600">
            {report.areasOfConcern.map((item) => (
              <li key={item} className="list-disc pl-5">{item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Suggested improvements</h3>
          <ul className="mt-4 space-y-3 text-slate-600">
            {report.suggestedImprovements.map((item) => (
              <li key={item} className="list-disc pl-5">{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default ReportPreview;
