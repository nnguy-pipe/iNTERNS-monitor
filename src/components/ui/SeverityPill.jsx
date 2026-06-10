function SeverityPill({ level }) {
  const textClass =
    level === 'Critical'
      ? 'text-red-700'
      : level === 'High'
      ? 'text-amber-700'
      : level === 'Low'
      ? 'text-emerald-700'
      : 'text-slate-700';

  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-sm font-medium border border-slate-300 ${textClass}`}>
      {level}
    </span>
  );
}

export default SeverityPill;
