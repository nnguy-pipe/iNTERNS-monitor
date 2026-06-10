import StatusBadge from '../ui/StatusBadge.jsx';

function AgentCard({ name, scope, status, latestFinding, lastChecked }) {
  return (
    <article className="h-full rounded-lg border border-slate-200 bg-white p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-semibold text-slate-900">{name}</h3>
          <p className="mt-1 text-sm text-slate-500">{scope}</p>
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="mt-6 space-y-4">
        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Latest finding</p>
          <p className="mt-2 text-slate-700">{latestFinding}</p>
        </div>
        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-slate-500">Last checked</p>
          <p className="mt-2 text-slate-700">{lastChecked}</p>
        </div>
      </div>
    </article>
  );
}

export default AgentCard;
