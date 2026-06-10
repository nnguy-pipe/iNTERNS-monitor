import StatusBadge from '../ui/StatusBadge.jsx';

function AgentCard({ name, scope, status, latestFinding, lastChecked }) {
  return (
    <article className="h-full rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{name}</h3>
          <p className="mt-1 text-xs text-slate-500">{scope}</p>
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="mt-4 space-y-3">
        <div>
          <p className="text-xs text-slate-500 font-medium">Finding</p>
          <p className="mt-1 text-sm text-slate-700">{latestFinding}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 font-medium">Checked</p>
          <p className="mt-1 text-sm text-slate-700">{lastChecked}</p>
        </div>
      </div>
    </article>
  );
}

export default AgentCard;
