function StatusBadge({ status }) {
  const borderClass =
    status === 'Healthy'
      ? 'border-l-2 border-emerald-600 text-emerald-700'
      : status === 'Degraded'
      ? 'border-l-2 border-amber-600 text-amber-700'
      : 'border-l-2 border-red-600 text-red-700';

  return (
    <span className={`inline-flex items-center gap-2 pl-2 text-sm font-semibold ${borderClass}`}>
      {status}
    </span>
  );
}

export default StatusBadge;
