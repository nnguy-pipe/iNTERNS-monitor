function StatusBadge({ status }) {
  const colorClass =
    status === 'Healthy'
      ? 'bg-emerald-100 text-emerald-800'
      : status === 'Degraded'
      ? 'bg-amber-100 text-amber-800'
      : 'bg-red-100 text-red-800';

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${colorClass}`}>
      {status}
    </span>
  );
}

export default StatusBadge;
