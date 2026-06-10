function MetricCard({ label, value, unit, trend, accent = 'normal' }) {
  const accentClass =
    accent === 'critical'
      ? 'border-l-4 border-l-red-600'
      : accent === 'warning'
      ? 'border-l-4 border-l-amber-600'
      : '';

  return (
    <div className={`rounded-lg bg-white p-5 border border-slate-200 ${accentClass}`}>
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-3 text-4xl font-semibold text-slate-900">
        {value}
        <span className="text-base font-medium text-slate-500">{unit}</span>
      </p>
      {trend && <p className="mt-2 text-sm text-slate-500">{trend}</p>}
    </div>
  );
}

export default MetricCard;
