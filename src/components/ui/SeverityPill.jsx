function SeverityPill({ level }) {
  const colorClass =
    level === 'Critical'
      ? 'bg-red-100 text-red-800'
      : level === 'High'
      ? 'bg-amber-100 text-amber-800'
      : level === 'Low'
      ? 'bg-emerald-100 text-emerald-800'
      : 'bg-slate-100 text-slate-800';

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${colorClass}`}>
      {level}
    </span>
  );
}

export default SeverityPill;
