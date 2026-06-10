function MetricCard({ label, value, unit, trend }) {
  return (
    <div className="rounded-3xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
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
